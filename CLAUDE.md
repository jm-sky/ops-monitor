# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Ops Monitor** is a central operations monitoring system. It polls remote servers (pull-only model) for health and system metrics, stores snapshots in PostgreSQL, and presents a Vue 3 dashboard. It sends alerts via MS Teams webhooks when thresholds are breached.

### Architecture

- **Frontend**: Vue 3.5+ SPA with Pinia, TanStack Query, Vue Router, Tailwind CSS v4, shadcn-vue (reka-ui)
- **Backend**: FastAPI (Python) + SQLAlchemy async + PostgreSQL + APScheduler
- **Agent**: Lightweight `agent.py` (psutil) deployed on monitored servers — exposes `/health` and `/system` endpoints
- **Polling**: Central service polls agents at configurable intervals (default 300s); never agents pushing
- **Alerts**: MS Teams Adaptive Cards via webhook when thresholds exceeded

## Commands

### Development
```bash
pnpm dev              # Start frontend dev server
pnpm build            # Build for production (type-check + build)
pnpm build-only       # Build without type checking
pnpm preview          # Preview production build
```

### Code Quality
```bash
pnpm type-check       # Run TypeScript compiler check
pnpm lint             # Run ESLint with auto-fix and cache
```

### Testing
```bash
pnpm test             # Run tests in watch mode
pnpm test:ui          # Run tests with Vitest UI
pnpm test:run         # Run tests once (CI mode)
pnpm test:coverage    # Run tests with coverage report
```

### Package Manager
This project uses **pnpm**. Always use `pnpm` instead of `npm` or `yarn`.

### Backend Development

**CRITICAL - Docker Safety Rule:**
- **NEVER run Docker commands if the project directory name starts with underscore (e.g., `_ops-monitor-dev`)**
- Underscore prefix indicates a development directory on the production server
- If the current working directory starts with `_`, do not execute any `docker` or `docker compose` commands

```bash
docker compose -f backend/docker-compose.dev.yml up    # Start backend in development mode
docker compose -f backend/docker-compose.dev.yml down  # Stop backend
```

**Important:**
- Use `docker compose` (V2 syntax), NOT `docker-compose` (deprecated V1)
- Backend runs at `http://localhost:8000`; auto-reload enabled via WatchFiles
- Restart container only when changing `.env` or `requirements.txt`

### Backend Linting (REQUIRED before commit)
```bash
cd backend
python -m black .   # Format Python code
python -m mypy .    # Type checking
```

### Backend CLI Commands

```bash
# Database
docker exec ops-monitor-app python -m cli db init
docker exec ops-monitor-app python -m cli db migrate
docker exec ops-monitor-app python -m cli db migrate-status

# Users
docker exec ops-monitor-app python -m cli users create
docker exec ops-monitor-app python -m cli users list
docker exec ops-monitor-app python -m cli users set-role
docker exec ops-monitor-app python -m cli users toggle-admin

# Interactive mode
docker exec -it ops-monitor-app python -m cli

# Test integrations
docker exec ops-monitor-app python -m cli test sentry
docker exec ops-monitor-app python -m cli test email
```

### Backend Testing
```bash
docker exec ops-monitor-app python -m pytest tests/ -v
python -m pytest tests/ -v  # using venv
```

## Architecture

### Module-Based Structure

Each feature is self-contained in `src/modules/`. Each module contains:

- `pages/` - Vue page components
- `components/` - Module-specific components
- `store/` - Pinia stores
- `services/` - Business logic / API calls
- `composables/` - Reusable composition functions
- `types/` - TypeScript type definitions
- `routes.ts` - Route definitions
- `i18n/` - Module translations (en + pl)

**Current modules:**
- `auth` - Authentication (JWT + WebAuthn/passkeys + TOTP)
- `user` - User profile management
- `settings` - Application settings
- `admin` - Admin dashboard (users only)
- `monitor` *(to be built)* - Site/server monitoring dashboard

### Core Directories

- `src/components/` - Shared UI components (`ui/`, `data-table/`, `layout/`)
- `src/pages/` - Top-level pages (Landing, Dashboard, NotFound, etc.)
- `src/layouts/` - Layout wrappers (`authenticated`, `guest`, `public`)
- `src/shared/` - Shared utilities, composables, services, stores, types
- `src/router/` - Vue Router configuration
- `src/i18n/` - App-level i18n instance (merges module translations)

### Monitoring Data Schemas

**Agent `/health` endpoint:**
```json
{
  "status": "ok" | "degraded" | "critical",
  "uptime_seconds": 123456,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**Agent `/system` endpoint:**
```json
{
  "cpu_percent": 42.5,
  "memory": { "total_mb": 16384, "used_mb": 8192, "percent": 50.0 },
  "disk": { "total_gb": 500, "used_gb": 200, "percent": 40.0 },
  "load_avg": [0.5, 0.8, 1.2],
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**PostgreSQL snapshot table** (`site_snapshots`):
```
site_id, polled_at, status, cpu_percent, mem_percent, disk_percent, raw_json
```

### Polling & Live Mode

- Default polling interval: 300 seconds per site (configurable in DB)
- Live mode: frontend sends heartbeat → backend reduces polling to ~30s for that site
- APScheduler manages the polling job queue

### Alerting

- MS Teams Adaptive Cards sent via webhook URL stored per site in DB
- Threshold breach triggers alert (configurable per site): CPU > X%, mem > X%, status != "ok"
- Cooldown period to avoid alert spam

### State Management

**Server state (TanStack Query):**
```typescript
const { data, isLoading } = useQuery({
  queryKey: ['sites'],
  queryFn: fetchSites,
  staleTime: 30_000,
})
```

**Client state (Pinia):** only for UI preferences (theme, locale, etc.)

### Routing & Layouts

Routes are defined per-module, merged in `src/router/routes.ts`. Each route uses `meta.layout`:

```typescript
{ path: '/dashboard', component: DashboardPage, meta: { layout: 'authenticated' } }
```

Available layouts: `authenticated`, `guest`, `public`

**Route Guards:**
- Auth guard protects authenticated routes
- Admin guard restricts admin pages (`src/modules/admin/guards/adminGuard.ts`)

### Internationalization (i18n)

- Languages: **English (en)** and **Polish (pl)**
- Each module has `i18n/locales/en.ts` + `i18n/locales/pl.ts`
- App-level `src/i18n/index.ts` merges all module translations
- Locale persisted in localStorage via `useLocale()` composable

## Tech Stack

### Frontend
- **Vue 3.5+** with `<script setup>` and Composition API
- **TypeScript** (strict mode)
- **Pinia** for client state
- **TanStack Query** for server state
- **Vue Router** for navigation
- **Vite** as build tool
- **Tailwind CSS v4** (via `@tailwindcss/vite`)
- **shadcn-vue** components (reka-ui)
- **lucide-vue-next** icons
- **vue-sonner** toasts
- **vee-validate** + **zod** form validation
- **@simplewebauthn/browser** WebAuthn
- **vite-plugin-pwa** PWA support

### Backend
- **FastAPI** + **SQLAlchemy async** + **PostgreSQL**
- **APScheduler** for polling jobs
- **httpx** async HTTP client for polling agents
- **alembic** migrations
- **pytest** + **pytest-asyncio** testing
- **black** + **mypy** linting

## Code Style & Conventions

### Linting (MUST RUN BEFORE COMMIT)
- **Frontend**: `pnpm lint`
- **Backend**: `python -m black .` and `python -m mypy .` in `backend/`

### ESLint (frontend)
- No semicolons (`semi: never`)
- Single quotes
- Import sorting via Perfectionist plugin (alphabetical, grouped)
- Self-closing tags required
- No line breaks before `else`, `catch`, `finally`

### TypeScript
- Use `@/` alias for imports from `src/`
- Dedicated union types, no inline definitions
- Prefer interfaces for object shapes, types for unions/primitives
- Types in module-specific `types/` directories

### Vue Component Patterns
- `<script setup lang="ts">` for all components
- `defineModel<T>()` for two-way binding (Vue 3.5+)
- Destructured props are reactive — no need for `toRefs`
- Prop shortcuts: `<Dialog :open />` instead of `<Dialog :open="open" />`

**Declaration order in `<script setup>`:**
1. Composables (`useI18n()`, `useRouter()`, etc.)
2. `defineProps()`
3. `defineModel()`
4. `defineEmits()`
5. Computed properties and reactive state
6. Functions and methods

### TailwindCSS
- Prefer `size-{n}` over `w-{n} h-{n}` when both are equal
- Button component already has `flex gap-2` — no `mr-2` on icons inside buttons
- Mobile-first responsive design

### Reka-ui / shadcn-vue Checkbox
- Use `v-model`, **NOT** `v-model:checked`

## Environment Variables

```
VITE_PORT              # Dev server port (default: 5176)
VITE_API_PROXY_URL     # API proxy target (default: http://localhost:8000)
```

## Important Notes

- **Pull-only**: central service polls agents — agents never push
- **No AI module** — removed in reboot
- **No billing/gear modules** — removed in reboot
- **Admin = users only** — no containers, items, limits pages
- **All new monitoring features** go into `src/modules/monitor/` and `backend/app/modules/monitor/`
- **Service layer**: business logic in service classes, not stores or components
- **Type safety**: all data structures have TypeScript interfaces in `types/` directories
- **PWA**: service workers cache assets for offline functionality
