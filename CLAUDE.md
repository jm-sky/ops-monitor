# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gear Stack is a Vue 3 application for managing survival gear and bug-out bag equipment. The app uses a hybrid architecture with both client-side localStorage and backend API integration for features like authentication, AI assistance, and admin functionality.

## Commands

### Development
```bash
pnpm dev              # Start development server (default port: 5176)
pnpm build            # Build for production (runs type-check + build-only)
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
This project uses **pnpm** (version 10.18.3+). Always use `pnpm` instead of `npm` or `yarn`.

### Backend Development

**CRITICAL - Docker Safety Rule:**
- **NEVER run Docker commands if the project directory name starts with underscore (e.g., `_gear-stack-dev`)**
- Underscore prefix indicates a development directory on the production server
- Running Docker in such directories can cause conflicts with production services
- If the current working directory starts with `_`, do not execute any `docker` or `docker compose` commands

```bash
docker compose -f backend/docker-compose.dev.yml up    # Start backend in development mode
docker compose -f backend/docker-compose.dev.yml down  # Stop backend
```

**Important:**
- Use `docker compose` (Docker Compose V2 syntax), NOT `docker-compose` (deprecated V1 syntax)
- In development, the backend typically runs in a Docker container via `docker-compose.dev.yml`. This ensures consistent environment and dependencies. The backend is accessible at `http://localhost:8000` (or the port specified in `VITE_API_PROXY_URL`).
- **Auto-reload is enabled** - FastAPI uses WatchFiles to automatically reload when Python files change. No need to restart the container after code changes during development.
- Only restart the container when changing environment variables (`.env`) or dependencies (`requirements.txt`).

### Backend Testing
The backend uses **pytest** for testing with async support via `pytest-asyncio`.

**Running tests:**
```bash
# Option 1: Using Docker (recommended - ensures consistent environment)
docker exec gear-stack-app python -m pytest tests/ -v

# Option 2: Using venv (if dependencies are installed)
cd backend
source .venv/bin/activate
python -m pytest tests/ -v

# Run specific test file
docker exec gear-stack-app python -m pytest tests/integration/gear/test_containers_crud.py -v

# Run single test
docker exec gear-stack-app python -m pytest tests/integration/gear/test_containers_crud.py::TestContainerCreate::test_create_container_minimal_data -v

# Run with coverage
docker exec gear-stack-app python -m pytest tests/ --cov=app --cov-report=html
```

**Test structure:**
- `backend/tests/` - Test files
  - `integration/gear/` - Integration tests for gear module (PHASE 0 baseline tests)
  - `conftest.py` - Pytest configuration and fixtures

**Test Database:**
- Integration tests use PostgreSQL test database (`backend_test`)
- Tests run against real PostgreSQL features (JSONB, arrays, etc.)
- Use `python -m cli db init-test` to initialize test database

### Backend CLI Commands

The backend includes a Django-inspired CLI for database and user management.

**Database Management:**
```bash
# Initialize main database
docker exec gear-stack-app python -m cli db init

# Initialize test database (PostgreSQL)
docker exec gear-stack-app python -m cli db init-test
docker exec gear-stack-app python -m cli db init-test --force  # Recreate

# Run migrations
docker exec gear-stack-app python -m cli db migrate
docker exec gear-stack-app python -m cli db migrate-status

# Seed database
docker exec gear-stack-app python -m cli db seed catalogue
docker exec gear-stack-app python -m cli db seed-remove catalogue
```

**User Management:**
```bash
# Create user
docker exec gear-stack-app python -m cli users create

# List users
docker exec gear-stack-app python -m cli users list

# Set roles
docker exec gear-stack-app python -m cli users set-role
docker exec gear-stack-app python -m cli users toggle-admin
```

**Interactive Mode:**
```bash
# Run CLI without arguments for interactive menu
docker exec -it gear-stack-app python -m cli
docker exec -it gear-stack-app python -m cli db
docker exec -it gear-stack-app python -m cli users
```

**Testing & Debugging:**
```bash
# Test Sentry error reporting
docker exec gear-stack-app python -m cli test sentry

# Test storage adapter
docker exec gear-stack-app python -m cli test storage

# Test email sending
docker exec gear-stack-app python -m cli test email
```

## Architecture

### Module-Based Structure

The application follows a **modular architecture** where each feature is self-contained in `src/modules/`. Each module contains:

- `pages/` - Vue page components
- `components/` - Module-specific components
- `store/` - Pinia stores for state management
- `services/` - Business logic layer (e.g., `gearService.ts`)
- `composables/` - Reusable composition functions
- `types/` - TypeScript type definitions
- `routes.ts` - Module route definitions
- `i18n/` - Module-specific translations

Current modules:
- `gear` - Core gear/container management
- `user` - User profile management
- `settings` - Application settings
- `auth` - Authentication with WebAuthn/passkeys support
- `ai` - AI assistance with chat, history, and context management
- `admin` - Admin dashboard for managing users and containers
- `stats` - Statistics and analytics

### Core Directories

- `src/components/` - Shared UI components
  - `ui/` - shadcn-vue components
  - `data-table/` - Table components
  - `layout/` - Layout-related components
- `src/pages/` - Top-level/shared pages (Landing, Privacy, Cookies, Contact, NotFound, Dashboard, Settings)
- `src/layouts/` - Layout wrappers (authenticated, guest, public)
- `src/shared/` - Shared utilities, types, composables, and infrastructure
  - `components/` - Shared components
  - `composables/` - Shared composables
  - `config/` - Shared configuration
  - `i18n/` - i18n infrastructure
  - `services/` - API client, interceptors (auth, error)
  - `store/` - Shared stores (e.g., token refresh)
  - `types/` - Shared TypeScript types
  - `utils/` - Shared utility functions
- `src/router/` - Vue Router configuration
- `src/i18n/` - Application i18n instance (merges module translations)

### State Management Pattern

The app uses a dual state management approach:

**1. Client-Side State (Pinia)**
- **Pinia stores** handle client-side state persistence with localStorage sync
- **Service classes** contain business logic, validation, and calculations

Example:
```typescript
// Service creates/validates, store persists
const container = gearService.createContainer(data)
// Service handles weight calculations
const totalWeight = gearService.calculateTotalWeight(containerId)
```

**2. Server State (TanStack Query)**
- **@tanstack/vue-query** manages server state with caching and invalidation
- Used for authentication, AI features, admin operations
- Provides automatic background refetching, optimistic updates, and error handling

Example:
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['user'],
  queryFn: fetchUser,
  staleTime: 5 * 60 * 1000,
})
```

### Data Persistence

The app uses a hybrid persistence model:

**Client-Side (localStorage)**
- Gear containers: `gear-stack:containers`
- Settings: `gear-stack:settings`
- AI chat history and context
- Stores handle load/save operations automatically

**Server-Side (Backend API)**
- User authentication and session tokens
- User profiles and preferences
- Admin data and analytics
- AI model interactions
- Communication via axios with `/api` proxy to backend

### Routing & Layouts

Routes are defined per-module and merged in `src/router/routes.ts`. Each route specifies a layout via `meta.layout`:

```typescript
{
  path: '/gear',
  component: () => import('@/modules/gear/pages/ContainersListPage.vue'),
  meta: { layout: 'authenticated' }
}
```

Available layouts: `authenticated`, `guest`, `public`

**Route Guards:**
- Authentication guard checks user session before accessing protected routes
- Admin guard restricts access to admin-only pages (e.g., `src/modules/admin/guards/adminGuard.ts`)
- Guards are applied per-module and can be composed

### Internationalization (i18n)

The app uses **vue-i18n** with a registry pattern:

1. Each module defines translations in `i18n/locales/` (en, pl)
2. Module translations are exported from `i18n/index.ts`
3. App-level `src/i18n/index.ts` merges all module translations + shared registry
4. Shared i18n utilities are in `src/shared/i18n/`

Locale is persisted in localStorage and synced via `useLocale()` composable.

## Tech Stack & Configuration

### Core Technologies
- **Vue 3.5+** with `<script setup>` and Composition API
- **TypeScript** (strict mode)
- **Pinia** for client-side state management
- **TanStack Query** (@tanstack/vue-query) for server state management
- **Vue Router** for navigation
- **Vite** as build tool

### UI & Styling
- **Tailwind CSS v4** (via `@tailwindcss/vite`)
- **shadcn-vue** components (based on reka-ui)
- **lucide-vue-next** for icons
- **vue-sonner** for toast notifications
- **floating-vue** for tooltips (registered as `v-tooltip` directive)

### Data & Visualization
- **@tanstack/vue-table** for advanced table features
- **@unovis/ts & @unovis/vue** for data visualization and charts

### Form Handling
- **vee-validate** + **@vee-validate/zod** for form validation
- **zod** for schema validation

### Backend & API
- **axios** for HTTP client
- **@simplewebauthn/browser** for WebAuthn/passkeys authentication
- **jwt-decode** for JWT token parsing
- API client with auth and error interceptors (`src/shared/services/`)

### Utilities
- **@vueuse/core** for Vue composition utilities
- **date-fns** for date manipulation
- **markdown-it** for Markdown parsing
- **qrcode** for QR code generation
- **md5** for hashing

### PWA
- **vite-plugin-pwa** for Progressive Web App support
- **workbox-window** for service worker management
- Configuration in `pwa.config.ts`

### Development Tools
- **ESLint** with Vue, TypeScript, and Perfectionist plugins
- **vue-tsc** for TypeScript type checking
- **vite-plugin-vue-devtools** for Vue DevTools

### Testing
- **vitest** for unit testing with happy-dom environment
- **@vitest/ui** for test UI
- **@playwright/test** for end-to-end testing
- Test coverage with v8 provider

## Code Style & Conventions

### ESLint Configuration (eslint.config.ts)

- **No semicolons** (`semi: never`)
- **Single quotes** with escape avoidance
- **Import sorting** (Perfectionist plugin) - alphabetical order with specific groups
- **Self-closing tags** required for all HTML/SVG/Vue components
- **Max attributes per line**: 3 for single-line, 1 for multi-line
- Unused variables starting with `_` are allowed
- **No line breaks before `else`, `catch`, `finally`** - Keep control flow keywords on the same line as closing brace
  - ✅ Use: `} else {`, `} catch (error) {`, `} finally {`
  - ❌ Avoid: Line breaks before these keywords

### TypeScript Conventions

- Use `@/` alias for absolute imports from `src/`
- Create **dedicated union types** instead of inline definitions (per global CLAUDE.md)
- Prefer interfaces for object shapes, types for unions/primitives
- All types are defined in module-specific `types/` directories

### Vue Component Patterns

- Use `<script setup lang="ts">` for all components
- Import order: external packages → internal modules (alphabetical, enforced by ESLint)
- Use composables for reusable logic (e.g., `useGearStore`, `useLocale`)
- Layouts are rendered via `<RouterView />` in App.vue

### Vue 3.5+ Best Practices

**v-model with defineModel:**
- ✅ Use: `const open = defineModel<boolean>('open', { required: true })`
- ❌ Avoid: `defineProps<{ open: boolean }>()` + `emit('update:open')`
- Benefits: Simpler syntax, automatic reactivity, less boilerplate

**Reactive Destructured Props:**
- Destructured props are reactive in Vue 3.5+ (no need for `toRefs`)
- ✅ Use: `const { item } = defineProps<{ item: IGearItem }>()`
- Props can be used directly in computed/watch without losing reactivity

**Prop Shortcuts:**
- When passing a prop with the same name as the variable
- ✅ Use: `<Dialog :open />` instead of `<Dialog :open="open" />`

**TypeScript Generics:**
- Always provide explicit types for `ref<T>`, `computed<T>`, `reactive<T>`
- ✅ Use: `const count = ref<number>(0)`, `const label = computed<string>(() => ...)`
- ❌ Avoid: `const count = ref(0)` (implicit types)

**Declaration Order in `<script setup>`:**
1. Composables (e.g., `useI18n()`, `useRouter()`)
2. `defineProps()`
3. `defineModel()`
4. `defineEmits()`
5. Computed properties and reactive state
6. Functions and methods

**Routing:**
- Use route helper functions from `routes.ts` instead of hardcoded paths
- ✅ Use: `GearRoutePath.ItemEditById(containerId, itemId)`
- ❌ Avoid: `` `/gear/${containerId}/items/${itemId}/edit` ``

## Environment & Configuration

### Environment Variables
- `VITE_PORT` - Development server port (default: 5176)
- `VITE_API_PROXY_URL` - API proxy target (default: http://localhost:8000)

The Vite config proxies `/api` requests to the configured backend URL.

### Node.js Requirements
- Node.js `^20.19.0` or `>=22.12.0` (specified in package.json)

## Key Features

### Gear Management
1. **Container Management** - Create/edit multiple gear lists (bug-out bags, EDC, etc.)
2. **Item Tracking** - Track items with status (owned/missing/toBuy), priority, weight, expiration
3. **Weight Calculations** - Automatic total pack weight calculation (supports g/kg units)
4. **Readiness Indicators** - Kit completeness tracking
5. **Data Import/Export** - JSON and Markdown import/export for backup/restore
6. **Category Organization** - Organize items by categories with custom icons

### Authentication & Security
7. **WebAuthn/Passkeys** - Modern passwordless authentication
8. **JWT Tokens** - Secure token-based authentication with auto-refresh
9. **Route Guards** - Protected routes for authenticated and admin users
10. **Session Management** - Automatic token refresh and logout on expiration

### AI Assistance
11. **AI Chat** - Conversational AI for gear recommendations and advice
12. **Context Management** - AI maintains context of your gear setup
13. **History Tracking** - Chat history persistence
14. **Multiple AI Models** - Support for different AI models

### Admin Features
15. **User Management** - Admin dashboard for managing users
16. **Container Management** - Admin oversight of all containers
17. **Analytics** - Statistics and usage analytics

### User Experience
18. **Progressive Web App** - Installable as native app with offline support
19. **Dark Mode** - System-synced theme via settings store
20. **Multi-language** - English and Polish (extensible via i18n registry)
21. **Responsive Design** - Mobile-first design with tablet/desktop optimization
22. **Advanced Tables** - Sortable, filterable tables with TanStack Table

## Important Notes

- **Hybrid Architecture** - App uses both client-side localStorage (gear data) and backend API (auth, AI, admin)
- **Data Persistence** - Client-side data stored in localStorage; server-side data via API
- **API Integration** - Backend API proxied at `/api/*` (configured in vite.config.ts)
- **Authentication Required** - Many features require backend authentication (WebAuthn/passkeys)
- **Module Independence** - Modules should be self-contained and reusable
- **Service Layer** - Business logic belongs in service classes, not in stores or components
- **Type Safety** - All data structures have TypeScript interfaces in `types/` directories
- **Guard Composition** - Route guards can be composed for complex authorization logic
- **PWA Offline Support** - Service workers cache assets for offline functionality

## UI Component Notes

### Action Icons

**CRITICAL:** Action icons must use the centralized mapping from `src/modules/gear/utils/actionIcons.ts`. This is the single source of truth for all action icons.

✅ **Correct usage:**
```vue
<script setup>
import { getActionIcon } from '@/modules/gear/utils/actionIcons'

const ExportIcon = getActionIcon('exportToPrompt')
const CreateIcon = getActionIcon('create')
</script>

<template>
  <Button>
    <ExportIcon class="size-4" />
    Export to Prompt
  </Button>
</template>
```

❌ **Incorrect usage:**
```vue
<!-- DO NOT import icons directly -->
<script setup>
import { MessageSquare, Sparkles } from 'lucide-vue-next'
</script>

<template>
  <Button>
    <MessageSquare class="size-4" />
    Export to Prompt
  </Button>
</template>
```

**Notes:**
- Always use `getActionIcon(actionKey)` instead of importing icons directly
- This ensures consistency across the application (e.g., `exportToPrompt` always uses `Sparkles`, not `MessageSquare`)
- Available action keys: `back`, `moreActions`, `create`, `addItem`, `addContainer`, `edit`, `delete`, `deleteAll`, `export`, `import`, `importFromMarkdown`, `exportToPrompt`, `exportAllToPrompt`, `recognizeParameters`, `recognizeParametersAll`
- Similar pattern exists for category icons in `src/modules/gear/utils/categoryIcons.ts`

### Reka-ui / shadcn-vue Checkbox

**CRITICAL:** In Reka-ui (shadcn-vue), Checkbox uses standard `v-model`, **NOT** `v-model:checked`.

✅ **Correct usage:**
```vue
<script setup>
const checked = ref(true)
</script>

<template>
  <Checkbox v-model="checked" />
</template>
```

❌ **Incorrect usage:**
```vue
<!-- DOES NOT WORK -->
<Checkbox v-model:checked="checked" />
<Checkbox :checked="checked" @update:checked="..." />
```

**Notes:**
- `v-model:checked` only works with `defineModel()` (as in `ContainersFilters.vue`)
- For regular `ref`, use standard `v-model`
- Checkbox in Reka-ui uses `modelValue` and `@update:model-value` under the hood

## TailwindCSS Best Practices

**Sizing:**
- Prefer `size-{value}` utility class instead of separate `w-{value} h-{value}` when width and height are the same
- ✅ **Correct:** `size-4`, `size-8`, `size-12`
- ❌ **Avoid:** `w-4 h-4`, `w-8 h-8`, `w-12 h-12`

**Button Component Spacing:**
- The Button component already includes `flex` and `gap-2` classes
- Icons inside buttons do **NOT** need `mr-2` or similar margin utilities
- ✅ **Correct:** `<Button><Icon />Label</Button>` (gap handled automatically)
- ❌ **Avoid:** `<Button><Icon class="mr-2" />Label</Button>`

## Responsive Design

**Always consider mobile-first responsive design:**
- Start with mobile styles (base classes)
- Add desktop variants using Tailwind breakpoint prefixes (eg. `sm:`)
- Example: `text-sm sm:text-base lg:text-lg` (small on mobile, base on tablet, large on desktop)
- Consider spacing, typography, layout, and visibility across breakpoints
- Run `python -m black .` and `python -m mypy .` in backend/ dir before commiting Python code.