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

```bash
docker build -t ops-monitor-agent .
docker run -d \
  -p 9100:9100 \
  -e AGENT_TOKEN=your-secret \
  --mount type=bind,src=/var/lib/apt/lists,dst=/var/lib/apt/lists,readonly \
  --mount type=bind,src=/var/lib/update-notifier,dst=/var/lib/update-notifier,readonly \
  --mount type=bind,src=/var/run,dst=/host/var/run,readonly \
  --mount type=bind,src=/var/log/apt,dst=/host/var/log/apt,readonly \
  --name ops-monitor-agent \
  ops-monitor-agent
```

The host bind mounts give the agent access to the host's package state. Without them the counts will always be 0 (container has no updates pending). Mounting `/var/run` as a directory avoids accidental host path creation and still lets the agent read reboot markers if they exist.

### Docker Compose

If you use `[docker-compose.yml](docker-compose.yml)` in this directory, the container is intentionally named `ops-monitor-agent` (so `docker ps` clearly shows it belongs to ops-monitor). The compose project name is set via `.env` as `COMPOSE_PROJECT_NAME=ops-monitor-agent`.


## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENT_TOKEN` | _(empty)_ | Static Bearer token. Empty = no auth (dev only) |
| `AGENT_HOST` | `0.0.0.0` | Listen address |
| `AGENT_PORT` | `9100` | Agent listen port inside the container/process |
| `AGENT_APT_LOG_TZ` | _(empty)_ | IANA timezone of the server clock, used to interpret apt's zone-less timestamps. Empty = agent process zone — set it in Docker if the container runs in UTC |
| `AGENT_APT_LOG_DIR` | _(empty)_ | Directory with `history.log*`. Empty = `/host/var/log/apt`, then `/var/log/apt` |
| `AGENT_BIND_PORT` | `19100` | Host loopback port published by Docker for local reverse proxying |

## `/system` Response

```json
{
  "version": "1.2.0",
  "cpu_percent": 42.5,
  "memory": { "total_mb": 16384, "used_mb": 8192, "percent": 50.0 },
  "disk": { "total_gb": 500.0, "used_gb": 200.0, "percent": 40.0 },
  "load_avg": [0.5, 0.8, 1.2],
  "uptime_seconds": 123456,
  "reboot_required": true,
  "reboot_reason": "linux-image-6.8.0-107-generic",
  "reboot_detected_at": "2026-04-11T08:00:00+00:00",
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

Reboot detection and update counts are Debian/Ubuntu specific (`/var/run/reboot-required`, APT notifier files). On other platforms these fields return `false`/`null`/`0` gracefully.

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
