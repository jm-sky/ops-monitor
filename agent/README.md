# Ops Monitor Agent

Lightweight psutil agent. Runs on each monitored server, exposes `/health` and `/system` over HTTP. Pull-only — the central ops-monitor service polls it.

## Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `GET /health` | none | Liveness probe |
| `GET /system` | Bearer token | Full system metrics |

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
  -v /var/lib/apt/lists:/var/lib/apt/lists:ro \
  -v /var/lib/update-notifier:/var/lib/update-notifier:ro \
  -v /var/run/reboot-required:/var/run/reboot-required:ro \
  -v /var/run/reboot-required.pkgs:/var/run/reboot-required.pkgs:ro \
  --name ops-monitor-agent \
  ops-monitor-agent
```

The host volume mounts give the agent access to the host's package state. Without them the counts will always be 0 (container has no updates pending).


## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENT_TOKEN` | _(empty)_ | Static Bearer token. Empty = no auth (dev only) |
| `AGENT_HOST` | `0.0.0.0` | Listen address |
| `AGENT_PORT` | `9100` | Listen port |

## `/system` Response

```json
{
  "version": "1.0.0",
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
