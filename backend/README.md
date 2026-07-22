# Ops Monitor – Backend

FastAPI backend for the Ops Monitor central monitoring system. Handles polling, snapshot storage, alert delivery, and REST API for the Vue dashboard.

## Stack

- **FastAPI** + SQLAlchemy async + PostgreSQL
- **APScheduler** — polling job queue
- **httpx** — async HTTP client for polling agents
- **alembic-style migrations** — custom migration runner
- **JWT auth** + WebAuthn/passkeys + TOTP (2FA)
- **Redis** — token blacklist, WebAuthn challenge storage

## Development

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD

# From repo root:
docker compose -f docker-compose.dev.yml up -d

docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli users create
```

Backend runs at `http://localhost:8000`. Auto-reload via WatchFiles — no restart needed after code changes. Restart only when changing `.env` or `requirements.txt`.

## Linting (required before commit)

```bash
python -m black .
python -m mypy .
```

## CLI

```bash
# Interactive mode
docker exec -it ops-monitor-app python -m cli

# Database
docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli db migrate-status

# Users
docker exec ops-monitor-app python -m cli users create
docker exec ops-monitor-app python -m cli users list
docker exec ops-monitor-app python -m cli users set-role
docker exec ops-monitor-app python -m cli users toggle-admin

# Test integrations
docker exec ops-monitor-app python -m cli test sentry
docker exec ops-monitor-app python -m cli test email
docker exec ops-monitor-app python -m cli test storage
```

## Testing

```bash
docker exec ops-monitor-app python -m pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── core/           # Config, DB, email, auth, middleware, storage
│   ├── common/         # Pagination, search, shared utilities
│   ├── exceptions/     # Custom exceptions + handlers
│   └── modules/
│       ├── auth/       # JWT, OAuth, passkeys, password reset
│       ├── users/      # User management
│       ├── admin/      # Admin endpoints (users only)
│       ├── settings/   # App settings
│       ├── logs/       # Audit logs
│       └── two_factor/ # TOTP + WebAuthn 2FA
├── cli/                # Management CLI (Typer)
│   └── commands/       # db, users, test
├── migrations/         # SQL migration files
├── tests/
├── .env.example
├── docker-compose.dev.yml
└── docker-compose.yml
```

## Environment Variables

See `.env.example` for the full list. Minimum required for development:

```env
SECRET_KEY=<random 32+ chars>
POSTGRES_PASSWORD=<strong password>
REDIS_PASSWORD=<strong password>
```
