# CLAUDE.md

## Project

Central ops monitoring system. Pull-only: backend polls `/health` + `/system` endpoints, stores snapshots in PostgreSQL, Vue 3 dashboard, MS Teams alerts. See `README.md` for full architecture and data schemas.

## Commands

```bash
# Frontend
pnpm dev / build / lint / type-check / test:run

# Backend (Docker)
docker compose -f docker-compose.dev.yml up
bash scripts/deploy.sh              # deploy (auto-detect compose stack)
docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli users create
docker exec ops-monitor-app python -m cli monitor status          # latest health/system per site (Rich table); add --errors-only for problems only
docker exec -it ops-monitor-app python -m cli        # interactive

# Agent (standalone)
cd agent && pip install -r requirements.txt
cp .env.example .env && python agent.py

# Linting — REQUIRED before every commit
pnpm lint                                             # frontend
docker exec ops-monitor-app python -m black . && docker exec ops-monitor-app python -m ruff check . && docker exec ops-monitor-app python -m mypy .  # backend
```

**CRITICAL:** Never run `docker` commands if the project directory starts with `_` (underscore = production server dev copy).

## Shared Core

This repo shares a copied core with **gear-stack** (`backend/app/core` + `app/common` + `cli`, and frontend `src/shared` + `src/components/ui`). It has drifted — any change to a shared-core file should be mirrored to gear-stack, and brand/domain values belong in config/env, not code. Inventory, current drift, and sync rules: **[docs/SHARED_CORE.md](docs/SHARED_CORE.md)** (companion: gear-stack `docs/REVIEW_AND_REFACTOR_PLAN.md`).

## Structure

```
src/modules/        auth | user | settings | admin | monitor
backend/app/modules auth | users | admin | settings | logs | two_factor | monitor
agent/              Standalone psutil agent (agent.py)
```

Each frontend module: `pages/ components/ store/ services/ composables/ types/ routes.ts i18n/`
Each backend module: `router.py service.py repositories.py schemas.py db_models.py`

## Code Style

**Frontend (ESLint enforced):**
- No semicolons, single quotes
- Imports sorted alphabetically (Perfectionist plugin)
- Self-closing tags required
- No line break before `else` / `catch` / `finally`
- `size-{n}` not `w-{n} h-{n}`; Button has `flex gap-2` — no `mr-2` on icons

**Vue components:**
- `<script setup lang="ts">` always
- `defineModel<T>()` for two-way binding
- Destructured props are reactive (no `toRefs`)
- Prop shorthand: `<Dialog :open />` not `<Dialog :open="open" />`
- Declaration order: composables → props → model → emits → state → functions

**TypeScript:**
- `@/` alias for `src/`
- Interfaces for object shapes, types for unions/primitives
- Types in module `types/` directories

**Backend (black + mypy enforced)**

**Reka-ui Checkbox:** `v-model` not `v-model:checked`

## Monitoring Statuses

| Type | Values |
|---|---|
| App | `ok` / `degraded` / `failed` |
| Reboot | `ok` / `reboot_required` |
| Updates | `up_to_date` / `outdated` |

## Key Rules

- No AI, billing, gear modules — removed in reboot
- Admin = users only
- New monitoring code → `src/modules/monitor/` and `backend/app/modules/monitor/`
- Server state via TanStack Query; client state (UI prefs) via Pinia
- Business logic in service classes, not stores or components
- `docker compose` (V2), never `docker-compose`
