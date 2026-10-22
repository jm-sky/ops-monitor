# Runbook: migrate a Dockerized agent to the hardened setup (agent 1.3.0)

**Applies to:** servers running the agent container with the old `/var/run:/host/var/run:ro` mount
and root user (agent ≤ 1.2.0). Commands below assume the typical layout: `agent/docker-compose.yml`
run from `/var/www/ops-monitor/agent`, container `ops-monitor-agent`, network `ops-monitor-network`,
host port `127.0.0.1:19100` (nginx on `:9100`) and the token in `agent/.env`. Adjust paths if yours differ.

**Downtime:** monitoring of this host only, for the container rebuild (~1 min). No other
services are affected.

**Why:** see [agent/README.md → Security](../../agent/README.md#security).

## 0. Pre-flight

```bash
cd /var/www/ops-monitor
git status --short                    # must be clean
git rev-parse HEAD                    # note it for rollback: PREV=<sha>
ls -l /var/log/apt /var/lib/update-notifier
```

The new container runs as uid 10001. `history.log*` and `updates-available` must be world-readable,
which is the Ubuntu default (`-rw-r--r--`). If any is `0640 root:adm`, see Troubleshooting first.

Check that no leftover **directories** named `/run/reboot-required*` exist. The sync ignores them,
but they hide real flags:

```bash
sudo bash scripts/fix-reboot-flag.sh
```

## 1. Install the host sync

```bash
git pull
sudo bash scripts/agent-host-sync-install.sh
```

Verify:

```bash
ls -la /run/ops-monitor-agent/reboot          # .last-sync present (+ flag copies if a reboot is pending)
systemctl status ops-monitor-reboot-sync.path --no-pager
systemctl list-timers ops-monitor-reboot-sync.timer --no-pager
```

If `/run/reboot-required` exists on the host, compare the copy:

```bash
stat -c '%y %n' /run/reboot-required /run/ops-monitor-agent/reboot/reboot-required   # same mtime
```

The old container keeps running unchanged during this step.

## 2. Redeploy the agent

```bash
cd /var/www/ops-monitor/agent
docker compose up -d --build
```

## 3. Verify

```bash
TOKEN=$(grep -E '^AGENT_TOKEN=' .env | cut -d= -f2-)

curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:19100/health        # 200
docker exec ops-monitor-agent id -u                                            # 10001 (not 0)
docker exec ops-monitor-agent ls /host/var/run                                 # "No such file or directory"
docker exec ops-monitor-agent sh -c 'test -S /var/run/docker.sock || echo no-docker-sock'   # no-docker-sock
docker inspect ops-monitor-agent --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.CapDrop}} {{.HostConfig.SecurityOpt}}'
#   true [ALL] [no-new-privileges:true]

curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:19100/system \
  | jq '{version, cpu_percent, reboot_required, reboot_source, reboot_flags_synced_at, updates_available}'
#   version "1.3.0", reboot_source "/host/reboot", reboot_flags_synced_at not null

curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:19100/package-history | jq '.sources'   # non-empty

docker logs ops-monitor-agent 2>&1 | grep -i 'reboot flags'
#   INFO ... Reboot flags: reading from /host/reboot   (no WARNING)
```

In the ops-monitor dashboard, trigger **Poll** for this site and check that the system card shows
metrics.

## 4. Test reboot detection (without touching the host's /run)

Write only into the copy directory, never into `/run/reboot-required`:

```bash
sudo touch /run/ops-monitor-agent/reboot/reboot-required
curl -s -H "Authorization: Bearer $TOKEN" 'http://127.0.0.1:19100/system?no_cache=1' \
  | jq '{reboot_required, reboot_reason, reboot_detected_at}'
#   reboot_required true, reboot_reason "kernel update"

sudo systemctl start ops-monitor-reboot-sync.service   # sync removes the fake copy
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:19100/system | jq .reboot_required
#   false (or true if the host really has /run/reboot-required)
```

Expect a matching reboot alert or recovery in Teams on the next system poll if the poll interval
overlaps the test. Mention this to the channel beforehand if needed.

## 5. Rollback

**Fast (config only, keeps the new image):**

```bash
cd /var/www/ops-monitor/agent
docker compose -f docker-compose.yml -f docker-compose.legacy-varrun.yml -f docker-compose.legacy-root.yml up -d
```

This restores the `/var/run` mount and root user. It is ⚠️ dangerous for the reasons above, so
treat it as temporary.

**Full (previous commit):**

```bash
cd /var/www/ops-monitor
git checkout "$PREV" -- agent docker-compose.yml docker-compose.dev.yml docker-compose.prod.yml
cd agent && docker compose up -d --build
git checkout HEAD -- .     # afterwards, when the issue is understood
```

**Optionally remove the host sync:**

```bash
sudo bash scripts/agent-host-sync-install.sh --uninstall
```

The legacy setup does not need the sync.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Log: `host sync not installed` | Step 1 skipped or failed → run the install script; check `journalctl -u ops-monitor-reboot-sync.service` |
| Log: `no reboot flag directory found` | `/host/reboot` not mounted (old compose file or custom `docker run`) → use the current `agent/docker-compose.yml` |
| `reboot_flags_synced_at` older than ~5 min | Timer not running → `systemctl enable --now ops-monitor-reboot-sync.timer` |
| `/package-history` empty, `sources: []` or update counts 0 | uid 10001 cannot read the files → `ls -l /var/log/apt /var/lib/update-notifier`; add an override with `group_add: ["4"]` (adm) or fix permissions; `docker-compose.legacy-root.yml` as last resort |
| Container exits with `Read-only file system` | Something writes outside `/tmp` → report it; temporary workaround `docker-compose.legacy-root.yml` |
| Root compose stack (`--profile agent`) instead of `agent/docker-compose.yml` | Same steps, run from the repo root: `docker compose --profile agent up -d --build agent`; the host port is `127.0.0.1:${AGENT_PORT:-9100}` |
