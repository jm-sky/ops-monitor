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

docker compose -f backend/docker-compose.dev.yml up -d

docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli users create
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
│   │   └── monitor/        # Monitoring dashboard (to be built)
│   ├── components/         # Shared UI components
│   ├── layouts/            # authenticated / guest / public
│   ├── router/
│   └── i18n/               # EN + PL
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── core/           # Config, DB, email, auth middleware
│   │   └── modules/        # auth, users, admin, settings, logs, two_factor
│   ├── migrations/
│   ├── cli/                # Management CLI (db, users, test)
│   └── docker-compose.dev.yml
├── agent.py                # Standalone psutil agent (to be built)
└── docker-compose.yml      # Production stack
```

## Monitoring Data

### App `/health` (self-reporting)

```json
{
  "schema_version": 1,
  "status": "ok|degraded|failed",
  "version": "1.2.3",
  "environment": "production",
  "components": {
    "database": {
      "status": "failed",
      "reason": "Connection timeout after 5s",
      "since": "2026-04-11T09:45:00Z"
    },
    "cache": { "status": "ok" }
  },
  "last_activity": "2026-04-11T10:00:00Z",
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
  "system_state": "outdated",
  "timestamp": "2026-04-11T10:00:00Z"
}
```

## Polling

Intervals configured per site in Postgres, default **300s**. Four types: `health`, `system`, `updates`, `reboot`.

**Live mode**: when dashboard is open, frontend sends heartbeat → backend increases polling frequency globally (configurable, e.g. 30s). Reverts after inactivity timeout.

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
