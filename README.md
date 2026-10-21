# Ops Monitor

Central operations monitoring system. Polls remote servers and applications for health and system metrics, stores snapshots in PostgreSQL, and presents a Vue 3 dashboard. Sends alerts via MS Teams webhooks.

## Architecture

```
[agent.py on each server]  →  GET /system
[app /health endpoint]     →  GET /health
           ↑ polling (httpx async, APScheduler)
    [FastAPI – central service]
    ├── Scheduler (APScheduler)
    ├── PostgreSQL (config + snapshots)
    ├── REST API for Vue dashboard
    └── Alert engine → MS Teams webhook
           ↑ API calls
    [Vue 3 dashboard]
    ├── Server + app list
    ├── Host details (metrics, reboot, updates)
    ├── App details (components, errors)
    └── Status history + alerts
```

**Agent** runs standalone on each monitored server as a systemd service — outside Docker Compose.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3.5+, TypeScript, Pinia, TanStack Query, Tailwind CSS v4, shadcn-vue |
| Backend | FastAPI, SQLAlchemy async, PostgreSQL, APScheduler, httpx |
| Auth | JWT + WebAuthn/passkeys + TOTP |
| Agent | Python + psutil (single file) |
| Infrastructure | Docker Compose |

## Quick Start

### Prerequisites

- Node.js `^20.19.0` or `>=22.12.0`
- pnpm
- Docker & Docker Compose

### Frontend

```bash
pnpm install
pnpm dev        # http://localhost:5176
pnpm build
pnpm lint
pnpm type-check
```

### Backend

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set SECRET_KEY at minimum

docker compose -f docker-compose.dev.yml up -d

# Optional: include agent in development stack
docker compose -f docker-compose.dev.yml --profile agent up -d

docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli users create
```

### Production backend stack (without frontend runtime container)

```bash
docker compose -f docker-compose.prod.yml up -d

# Optional: include agent in production stack
docker compose -f docker-compose.prod.yml --profile agent up -d
```

### Agent (on monitored server)

```bash
pip install psutil
# Configure .env with port and token
python agent.py
# Or install as systemd service
```

## Project Structure

```
ops-monitor/
├── src/                    # Frontend (Vue 3)
│   ├── modules/
│   │   ├── auth/           # JWT + WebAuthn + TOTP
│   │   ├── user/           # User profile
│   │   ├── settings/       # App settings
│   │   ├── admin/          # Admin (users only)
│   │   └── monitor/        # Monitoring dashboard
│   ├── components/         # Shared UI components
│   ├── layouts/            # authenticated / guest / public
│   ├── router/
│   └── i18n/               # EN + PL
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── core/           # Config, DB, email, auth middleware
│   │   └── modules/        # auth, users, admin, settings, logs, two_factor, monitor
│   ├── migrations/
│   ├── cli/                # Management CLI (db, users, test)
├── agent/                  # Standalone psutil agent
├── docker-compose.dev.yml  # Dev full stack (backend + frontend, optional agent)
└── docker-compose.prod.yml # Prod backend stack (optional agent)
```

## Monitoring Data

### App `/health` (self-reporting)

See **[docs/health-schema.md](docs/health-schema.md)** for the full specification, including component fields, on-demand integration handling, and the `stale` freshness pattern.

Quick reference:

```json
{
  "schema_version": 1,
  "status": "ok|degraded|failed",
  "version": "1.2.3",
  "environment": "production",
  "components": {
    "database": { "status": "ok" },
    "cache": { "status": "degraded", "reason": "High miss rate", "since": "2026-04-13T08:00:00Z" },
    "frontend": { "status": "ok" },
    "ocr": { "status": "ok", "checked_at": "2026-04-11T14:23:00Z", "stale": true }
  },
  "last_activity": "2026-04-13T10:00:00Z",
  "errors": []
}
```

### Agent `/system` (psutil)

```json
{
  "cpu_percent": 42.5,
  "memory": { "total_mb": 16384, "used_mb": 8192, "percent": 50.0 },
  "disk": { "total_gb": 500, "used_gb": 200, "percent": 40.0 },
  "load_avg": [0.5, 0.8, 1.2],
  "uptime_seconds": 123456,
  "reboot_required": true,
  "reboot_reason": "kernel update",
  "updates_available": 12,
  "security_updates": 3,
  "security_packages": ["linux-image-generic", "openssl", "libssl3"],
  "system_state": "outdated",
  "timestamp": "2026-04-11T10:00:00Z"
}
```

### Agent `/package-history`

apt transactions parsed from `/var/log/apt/history.log*` (incl. rotated `.gz`), same Bearer auth as `/system`. Query: `?since=<ISO>`. Details and response shape: [agent/README.md](agent/README.md#package-history-response).

## Package update history

The backend pulls `/package-history` from each site's agent (URL derived from `systemUrl`: `…/system` → `…/package-history`) every `pollingUpdates` seconds (default 43200) and on manual **Poll now**. Only events newer than the last stored `started_at` are requested; rows are deduplicated on `(site_id, started_at)` in table `package_update_events`. Older agents without the endpoint (HTTP 404) are skipped silently. The site detail page shows them under **Update history**.

### Read-only API for external tools (e.g. worklog-automation)

Users authenticate with JWT + 2FA, so machine access uses **API keys**: random `opsm_…` tokens, stored only as a SHA-256 hash, with a scope (`read:package-updates`), optional expiry, and revocation. The plaintext key is shown once at creation.

```bash
docker exec ops-monitor-app python -m cli monitor api-keys create worklog-automation --expires-in-days 365
docker exec ops-monitor-app python -m cli monitor api-keys list
docker exec ops-monitor-app python -m cli monitor api-keys revoke <id>
```

Admins can do the same over HTTP: `POST/GET /api/monitor/api-keys`, `DELETE /api/monitor/api-keys/{id}`.

```bash
curl -H "Authorization: Bearer opsm_…" \
  "https://<host>/api/monitor/package-updates?from=2026-07-01T00:00:00Z&to=2026-07-31T23:59:59Z&include_automatic=false"
```

| Param | Default | Description |
|---|---|---|
| `from`, `to` | — | Filter on `started_at` (inclusive, ISO 8601; no zone = UTC) |
| `site_id` | — | Limit to one site |
| `include_automatic` | `false` | Include `automatic=true` runs (unattended-upgrade / no `Requested-By`) |
| `limit`, `offset` | `200`, `0` | Pagination (`limit` ≤ 1000); results are newest first |

Response: `{ "items": [...], "total": n }`; each item has `siteId`, `siteName`, `serverLabel`, `host` (hostname from the site's `systemUrl`), `startedAt`, `finishedAt`, `durationSeconds` (`null` without end time), `commandline`, `requestedBy`, `automatic`, `packages`. A missing, unknown, revoked, expired or wrong-scope key returns `401`.

## Polling

Intervals are configurable per site in Postgres. Recommended default is background mode at **300s (5 min)**. Four types: `health`, `system`, `updates`, `reboot`. `updates` currently drives the package history sync (see below); update counts themselves come with `/system`.

UI data refresh runs in two modes:
- **Normal mode**: monitor queries refetch every **300s (5 min)**.
- **Active mode**: while user is on monitor list/detail and tab is visible, refetch interval is **120s (2 min)**.

These UI intervals and heartbeat cadence are now provided by backend config (`GET /api/monitor/config`) and can be overridden via environment variables:
- `MONITOR_UI_BACKGROUND_REFETCH_SECONDS`
- `MONITOR_UI_ACTIVE_REFETCH_SECONDS`
- `MONITOR_HEARTBEAT_INTERVAL_SECONDS`
- `MONITOR_CHECK_INTERVAL_SECONDS`
- `MONITOR_LIVE_POLL_INTERVAL_SECONDS`
- `MONITOR_LIVE_MODE_TTL_SECONDS`

**Heartbeat live mode**: frontend sends heartbeat to `/monitor/heartbeat` while monitor list/detail is actively viewed (visible tab). Backend uses heartbeat to keep live mode on and can poll due sites more aggressively during its live-mode TTL window. When heartbeat stops, backend returns to background behavior after TTL expiry.

Frontend refresh interval and backend poll cadence are intentionally separate:
- frontend controls how often dashboard data is re-fetched from API,
- backend controls how often remote site endpoints are polled.

## Alerts

MS Teams Adaptive Cards via Incoming Webhook. Triggers: app status `degraded`/`failed`, `reboot_required`, system `outdated`. Deduplication: no repeat alerts while status is unchanged.

## CLI

```bash
docker exec -it ops-monitor-app python -m cli          # interactive mode

docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli db migrate-status

docker exec ops-monitor-app python -m cli users create
docker exec ops-monitor-app python -m cli users list
docker exec ops-monitor-app python -m cli users set-role

docker exec ops-monitor-app python -m cli monitor api-keys create <name>
docker exec ops-monitor-app python -m cli monitor api-keys list
docker exec ops-monitor-app python -m cli monitor api-keys revoke <id>

docker exec ops-monitor-app python -m cli test sentry
docker exec ops-monitor-app python -m cli test email
```

## Environment Variables

See `backend/.env.example` for the full list. Minimum required:

```env
SECRET_KEY=<random 32+ chars>
POSTGRES_PASSWORD=<strong password>
REDIS_PASSWORD=<strong password>
```
