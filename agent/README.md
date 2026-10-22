# Ops Monitor Agent

Lightweight psutil agent. Runs on each monitored server, exposes `/health` and `/system` over HTTP. Pull-only — the central ops-monitor service polls it.

## Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `GET /health` | none | Liveness probe |
| `GET /system` | Bearer token | Full system metrics |
| `GET /package-history?since=<ISO>` | Bearer token | apt install/upgrade/remove/purge history parsed from `history.log` + rotated `history.log.N.gz`. `since` is inclusive (`started_at >= since`); `no_cache=1` skips the 5-minute parse cache |
| `GET /system?no_cache=1` | Bearer token | Same as `/system`, but skips the 5-minute update cache and reads package state via `apt list --upgradable` (used by manual Poll from ops-monitor) |

Default port: **9100**

## Install (systemd)

```bash
sudo bash scripts/agent-install.sh
# Then edit /opt/ops-monitor-agent/.env — set AGENT_TOKEN
sudo systemctl restart ops-monitor-agent
```

## Run manually

```bash
pip install -r requirements.txt
cp .env.example .env   # set AGENT_TOKEN
python agent.py
```

## Docker

The container runs hardened by default (see [Security](#security)). Reboot detection needs a
small host-side sync installed **once per host, before** starting the container:

```bash
sudo bash scripts/agent-host-sync-install.sh   # from the repo root; idempotent, --uninstall to remove
```

### Docker Compose

```bash
cd agent
cp .env.example .env   # set AGENT_TOKEN
docker compose up -d --build
```

The container is intentionally named `ops-monitor-agent` (so `docker ps` clearly shows it belongs to ops-monitor). The compose project name is set via `.env` as `COMPOSE_PROJECT_NAME=ops-monitor-agent`.

### docker run

```bash
docker build -t ops-monitor-agent .
docker run -d \
  -p 127.0.0.1:19100:9100 \
  -e AGENT_TOKEN=your-secret \
  --read-only --tmpfs /tmp \
  --cap-drop ALL --security-opt no-new-privileges:true \
  --mount type=bind,src=/var/lib/apt/lists,dst=/var/lib/apt/lists,readonly \
  --mount type=bind,src=/var/lib/update-notifier,dst=/var/lib/update-notifier,readonly \
  --mount type=bind,src=/run/ops-monitor-agent/reboot,dst=/host/reboot,readonly \
  --mount type=bind,src=/var/log/apt,dst=/host/var/log/apt,readonly \
  --name ops-monitor-agent \
  ops-monitor-agent
```

The host bind mounts give the agent access to the host's package state. Without them the counts will always be 0 (container has no updates pending).

## Security

### Threat model

The agent listens on the network (port 9100, usually behind nginx). If it is compromised, the
attacker gets whatever the container can reach. The old setup mounted the host's whole
`/var/run` and ran as root. That exposed `docker.sock`, `containerd.sock` and the D-Bus system
socket. A `:ro` bind mount does **not** restrict socket APIs, so a compromised agent meant
**root on the host**. The agent only ever needed two files from there:
`reboot-required` and `reboot-required.pkgs`.

### Hardened default

| Measure | Where |
|---|---|
| Only a dedicated directory with copies of the 2 flag files is mounted (`/run/ops-monitor-agent/reboot` → `/host/reboot`) | compose |
| Non-root user `opsagent`, fixed uid/gid **10001** | `Dockerfile` |
| `read_only: true` root filesystem, `tmpfs: /tmp` | compose |
| `cap_drop: [ALL]`, `no-new-privileges:true` | compose |
| No `pid: host` (metrics come from `/proc`, which shows host-wide CPU/memory/load anyway) | root compose files |

**Host sync** (`scripts/agent-host-sync-install.sh`, run as root):

- `ops-monitor-reboot-sync.path` (`PathChanged=` on `/run/reboot-required*`) copies the flags within seconds of apt raising them.
- `ops-monitor-reboot-sync.timer` re-syncs every 5 min and 30 s after boot. This catches removals and missed events.
- Copies keep their mtime (`cp -p`), so `reboot_detected_at` is unchanged.
- A copy is removed once its original is gone. `.last-sync` is touched on every run.
- The directory lives on tmpfs (`/run`) and is created by `tmpfiles.d` at boot, so a reboot clears the copies together with the originals.
- Only directories are bind-mounted, never single files. A missing host file can no longer turn into a directory created by Docker (see `scripts/fix-reboot-flag.sh`).

At startup the agent logs which directory it reads the flags from. It logs a **WARNING** (once per change) when:

- no flag directory exists;
- the sync directory has no `.last-sync` marker ("host sync not installed");
- the agent runs in a container but would read the container's own `/var/run`.

`/system` reports this via `reboot_source` and `reboot_flags_synced_at`.

### Opt-outs (not recommended)

| Override | Effect |
|---|---|
| `docker-compose.legacy-varrun.yml` | ⚠️ **Dangerous.** Mounts the whole host `/var/run` again (`AGENT_REBOOT_FLAG_DIR=/host/var/run`). With the default non-root user `docker.sock` (`root:docker 0660`) stays unusable, but D-Bus and other sockets are exposed. |
| `docker-compose.legacy-root.yml` | Runs as root with a writable root filesystem (capabilities stay dropped). Only if host files the agent needs are not world-readable — prefer `group_add` instead. |

```bash
docker compose -f docker-compose.yml -f docker-compose.legacy-varrun.yml up -d
# or persistently, in agent/.env:
COMPOSE_FILE=docker-compose.yml:docker-compose.legacy-varrun.yml
```

The overrides also work with the root compose files (`-f docker-compose.yml -f agent/docker-compose.legacy-varrun.yml --profile agent`).

### Files the non-root agent reads

Typical Debian/Ubuntu permissions:

- `/var/lib/apt/lists/*`, `/var/lib/update-notifier/updates-available` and `/var/log/apt/history.log*` are `0644`;
- `/proc` is world-readable.

If a host differs (e.g. `history.log` is `0640 root:adm`), add `group_add: ["4"]` in an override instead of running as root.

### systemd install

`scripts/agent-install.sh` runs the agent as the unprivileged `ops-agent` user. It reads `/run/reboot-required*` directly, so no sync is needed. The unit is sandboxed with:

- `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `PrivateDevices`;
- an empty `CapabilityBoundingSet`;
- `ProtectKernel*`, `ProtectControlGroups`;
- `RestrictSUIDSGID`, `RestrictNamespaces`, `RestrictAddressFamilies`, `LockPersonality`.

Migration of existing servers: [docs/runbooks/agent-hardening-migration.md](../docs/runbooks/agent-hardening-migration.md).

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENT_TOKEN` | _(empty)_ | Static Bearer token. Empty = no auth (dev only) |
| `AGENT_HOST` | `0.0.0.0` | Listen address |
| `AGENT_PORT` | `9100` | Agent listen port inside the container/process |
| `AGENT_APT_LOG_TZ` | _(empty)_ | IANA timezone of the server clock, used to interpret apt's zone-less timestamps. Empty = agent process zone — set it in Docker if the container runs in UTC |
| `AGENT_APT_LOG_DIR` | _(empty)_ | Directory with `history.log*`. Empty = `/host/var/log/apt`, then `/var/log/apt` |
| `AGENT_REBOOT_FLAG_DIR` | _(empty)_ | Directory with `reboot-required` / `reboot-required.pkgs`. Empty = first existing of `/host/reboot` (hardened mount), `/host/var/run` (legacy mount), `/var/run` (systemd install). When set, only this directory is used — no fallback |
| `AGENT_BIND_PORT` | `19100` | Host loopback port published by Docker for local reverse proxying |

## `/system` Response

```json
{
  "version": "1.3.0",
  "cpu_percent": 42.5,
  "memory": { "total_mb": 16384, "used_mb": 8192, "percent": 50.0 },
  "disk": { "total_gb": 500.0, "used_gb": 200.0, "percent": 40.0 },
  "load_avg": [0.5, 0.8, 1.2],
  "uptime_seconds": 123456,
  "reboot_required": true,
  "reboot_reason": "linux-image-6.8.0-107-generic",
  "reboot_detected_at": "2026-04-11T08:00:00+00:00",
  "reboot_source": "/host/reboot",
  "reboot_flags_synced_at": "2026-04-11T09:58:30+00:00",
  "updates_available": 20,
  "security_updates": 1,
  "security_packages": ["some-package"],
  "system_state": "outdated",
  "timestamp": "2026-04-11T10:00:00+00:00"
}
```

- `updates_available` — total upgradable packages (including security)
- `security_updates` — security-only count
- `security_packages` — list of security package names
- `reboot_detected_at` — mtime of the `reboot-required` flag
- `reboot_source` — directory the reboot flags were read from; `null` when none exists (detection disabled)
- `reboot_flags_synced_at` — last run of the host sync (`.last-sync` mtime); `null` outside the hardened Docker setup or when the sync is not installed

Reboot detection and update counts are Debian/Ubuntu specific (`/run/reboot-required`, APT notifier files). On other platforms these fields return `false`/`null`/`0` gracefully.

### Known issue: `apt list --upgradable` fallback in Docker

The agent falls back to `apt list --upgradable` when `no_cache=1` is set (manual Poll) or `updates-available` has no data. Inside the container `apt` combines the **host's** package lists (`/var/lib/apt/lists`) with the **container's** dpkg database. The resulting counts do not describe the host. In Docker only the `update-notifier` path (`/var/lib/update-notifier/updates-available`) is reliable. Not fixed yet.

## Registration

Add the server to ops-monitor via the dashboard (Sites → Add) or directly in the DB. Set the same `AGENT_TOKEN` value in both places.

## `/package-history` Response

```json
{
  "events": [
    {
      "started_at": "2026-07-02T06:15:01+02:00",
      "finished_at": "2026-07-02T06:15:40+02:00",
      "commandline": "/usr/bin/unattended-upgrade",
      "requested_by": null,
      "automatic": true,
      "packages": {
        "upgrade": [
          { "name": "openssl", "arch": "amd64", "from_version": "3.0.13-1", "to_version": "3.0.13-2", "auto_installed": false }
        ]
      }
    }
  ],
  "sources": ["/host/var/log/apt/history.log"],
  "generated_at": "2026-07-02T08:00:00+00:00"
}
```

- Events are sorted oldest first. `packages` has only the keys present in the block (`install`, `upgrade`, `remove`, `purge`); `auto_installed` is apt's `automatic` flag (installed as a dependency).
- `finished_at` is `null` when the block has no `End-Date` (interrupted run).
- `automatic` is `true` when `Commandline` contains `unattended-upgrade` **or** there is no `Requested-By`. Caveat: apt omits `Requested-By` when run from a root login shell without sudo, so such manual runs are classified as automatic.
- Timestamps in `history.log` carry no zone — see `AGENT_APT_LOG_TZ`.
- Docker needs `/var/log/apt` mounted at `/host/var/log/apt` (already in the compose files here).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
