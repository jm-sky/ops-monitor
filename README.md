# Gear Stack

A comprehensive web application for managing survival gear, bug-out bags, and outdoor equipment with multi-user support, cloud synchronization, and advanced organization features.

<img width="1527" height="547" alt="obraz" src="https://github.com/user-attachments/assets/9e71110e-0941-418b-b853-2cd9fe43aa91" />

## Overview

Gear Stack is a full-stack application designed for outdoor enthusiasts, preppers, and survival gear collectors. It combines an intuitive front-end interface with a robust backend to provide secure multi-user gear management with cloud synchronization across devices.

**Key Capabilities:**
- **Multi-User Platform** - Secure user accounts with authentication and authorization
- **Subscription Plans** - Free, Pro, and Pro Plus tiers with Stripe payment integration
- **Hybrid Architecture** - Works offline with localStorage, syncs with cloud when online
- **Advanced Organization** - Hierarchical container system with nested items and weight tracking
- **Rich Metadata** - Track weight, expiration dates, priorities, brands, and custom categories
- **Data Portability** - Import/export functionality with AI-ready markdown format

> 📋 **[Zobacz pełną listę funkcjonalności w języku polskim →](./FEATURES.md)**

---

### Core Features
- Manage multiple gear lists (e.g., Bug-Out Bag, EDC, Get Home Bag, custom).
- Add, edit, and remove items.
- Item fields: name, category, quantity, weight, notes, expiration date (optional), priority.
- Mark items as *owned*, *missing*, or *to buy*.
- Automatic calculation of total pack weight.
- Kit readiness/completeness indicator.

---

### User Experience
- List view and detailed item view.
- Search, filter, and sort by category, weight, priority, or status.
- Highlight expired or soon-to-expire items.
- Quick actions: mark as used, missing, expired.

---

### Data Architecture
- **Hybrid Persistence**:
  - Client-side: `localStorage` for offline-first functionality
  - Server-side: PostgreSQL database for multi-device sync
- **Automatic Synchronization** - Changes sync to cloud when online
- **Conflict Resolution** - Smart merging of offline changes
- **Data Portability** - Import/export in JSON format

---

### Technical Stack

**Frontend:**
- Vue 3.5+ with TypeScript & Composition API
- Pinia for state management
- Vue Router for navigation
- TailwindCSS v4 + shadcn-vue components
- VeeValidate + Zod for form validation
- TanStack Query for server state management
- vue-i18n for internationalization

**Backend:**
- FastAPI (Python) with async/await
- PostgreSQL database
- SQLAlchemy ORM with async support
- JWT authentication with refresh tokens
- Stripe payment integration for subscriptions
- Rate limiting and reCAPTCHA protection
- Modular architecture (auth, billing, two-factor, email)

**Infrastructure:**
- Docker containerization
- Nginx reverse proxy
- Development and production configurations

---

## Business Features

### 🔐 User Management & Security
- **User Registration & Login** - Email/password authentication with secure password hashing
- **OAuth Social Login** - Sign in with Google (GitHub support planned)
- **OAuth Connections Management** - View and manage linked OAuth providers in settings
- **Email Verification** - Confirm email addresses for account security
- **Two-Factor Authentication (2FA)** - TOTP (authenticator apps) and WebAuthn (passkeys/security keys)
- **Password Management** - Reset forgotten passwords, change password for authenticated users
- **reCAPTCHA v3 Protection** - Invisible bot protection on login, registration, and password reset
- **Session Management** - JWT tokens with automatic refresh, secure logout
- **Token Blacklist** - Server-side token invalidation using Redis (prevents token reuse after logout)
- **WebAuthn Challenge Storage** - Server-side challenge storage in Redis for security
- **Account Deletion** - GDPR-compliant soft delete with confirmation
- **Role System** - Owner, Premium, Admin, and User roles with appropriate permissions

### 👤 User Profile
- **Profile Management** - Update name, email, and preferences
- **Avatar Support** - OAuth providers automatically provide profile pictures (Gravatar fallback)
- **Public Profile** - Option to share profile publicly with user information and public containers
- **Role Badges** - Visual role indicators (Owner, Premium, Admin) with icons and colors
- **Preferred Settings** - Weight units (including auto modes), language, theme preferences
- **Security Settings** - Manage 2FA methods, view security status

### 🌐 Multi-Language Support
- English and Polish fully supported
- Automatic locale detection from browser
- Manual language switching in settings
- All UI text, validation messages, and emails localized

### 🎨 Theming
- **Dark Mode** - Full dark theme support with system preference detection
- **Theme Persistence** - Settings saved per user account

---

## 💳 Subscription Plans

Gear Stack offers flexible subscription plans powered by **Stripe** for secure payment processing:

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0/month | Basic gear management, data export, BYOK AI (bring your own OpenRouter key), 100MB storage, 2,000 items limit |
| **Pro** | $5/month or $50/year | Everything in Free + AI-powered recommendations, ~$1 AI tokens/month, advanced features, 5GB storage, 10,000 items limit |
| **Pro Plus** | $15/month or $150/year | Everything in Pro + priority AI processing, ~$10 AI tokens/month, premium support, 50GB storage, 50,000 items limit |

**Payment Features:**
- Secure checkout powered by Stripe
- Monthly and annual billing (save 17% with annual)
- Customer self-service portal for subscription management
- Automatic subscription renewal
- Easy plan switching and cancellation

**Grandfathered Users:**
Early supporters with existing premium access retain lifetime Pro benefits at no cost. 👑

---

## Gear Management Features

### 📦 Container System
- **Multiple Container Types** - Bug-out bags, EDC kits, get-home bags, medical kits, camping gear, and custom types
- **Hierarchical Organization** - Containers can contain other containers (nested packs, pouches in bags)
- **Visual Distinction** - Assign colors to containers for quick identification (10+ colors)
- **Container Metadata** - Type, description, base weight, color coding
- **Cycle Detection** - Prevents circular references in nested containers

### 🎒 Item Management
- **Rich Item Data**:
  - Basic: Name, quantity, weight (with unit selection: g, kg, oz, lb)
  - Organization: Category, priority, status (owned/missing/to buy)
  - Metadata: Brand, notes, expiration date, shelf life
  - Advanced: Consumable flag, worn flag, custom categories
- **Smart Categorization** - Automatic category recognition based on item name (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)
- **Status Tracking** - Mark items as owned, missing, or to buy
- **Priority Levels** - Low, medium, high, critical
- **Expiration Tracking** - Monitor consumables and replace before they expire
- **Shelf Life Tracking** - Define shelf life period (days/months/years) with automatic expiration date calculation
- **Inline Name Editing** - Quick edit item names directly on detail pages
- **Item Linking** - Link items across containers with automatic change propagation
- **Move Items** - Move items between containers while preserving all data

### 📊 Analytics & Insights
- **Weight Calculations**:
  - Total pack weight with recursive calculation for nested containers
  - Category-based weight distribution
  - Base weight vs. consumables tracking
  - Weight breakdown by type (Other/Worn/Consumable)
- **Readiness Indicators** - Kit completeness percentage based on owned vs. missing items
- **Donut Charts** - Visual breakdown of weight, quantity, price, or priority by category
- **Item Statistics** - Count items by status, category, or priority
- **Automatic Weight Unit Selection** - Auto modes (auto-g-kg, auto-oz-lb) with locale-aware formatting

### 🔍 Search & Filtering
- **Smart Search** - Find items by name, brand, or notes across all containers
- **Multi-Criteria Filtering** - Filter by category, status, priority, or container
- **Sorting Options** - Sort by name, weight, expiration date, or priority
- **Highlight Expired Items** - Visual warnings for expired or soon-to-expire items

### 🚀 Import/Export
- **JSON Export/Import** - Full data backup and restore
- **AI-Ready Markdown Export** - Export containers to markdown format for AI processing
  - Structured format with metadata (weight, brand, color, status)
  - Nested container support with calculated weights
  - Legend explaining data structure
  - One-click copy to clipboard
  - Export options: description format, semantic separators, UUID support
- **CSV Export** - Export containers to CSV format with column selection, separators, and UTF-8 BOM encoding
- **UUID Import/Export** - UUID-based update workflow for containers and items
- **Cross-Device Transfer** - Export from one device, import on another

### ⚡ Productivity Features
- **Quick Item Entry** - Smart defaults and keyboard shortcuts
- **Inline Name Editing** - Edit item and container names directly on detail pages
- **Item Ordering** - Manual item ordering within containers with batch save confirmation
- **Dynamic Page Titles** - Automatic document title management with container/item names
- **Sidebar Navigation** - Collapsible sidebar with container list and navigation links
- **Markdown Support** - Full Markdown formatting in notes and descriptions with preview
- **Drag & Drop Reordering** - Visual drag & drop interface (planned)
- **Bulk Actions** - Mark multiple items as owned/missing (planned)
- **Templates** - Save and reuse common gear configurations (planned)

---

## Features

### ✅ Implemented Features

#### 🌐 Internationalization
- **Locale Detection** - Automatic language detection from browser settings with fallback to Polish
- Manual language switching in settings (English/Polish)
- HTML lang attribute automatically set based on detected language
- **Polish Pluralization** - Proper pluralization rules for Polish language (0, 1, 2-4, 5+)

#### 🎨 UI/UX
- **Category Icons** - Dedicated icons for each item category (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)
- **Container Colors** - Assign colors to containers for visual distinction (10+ colors available)
- **Donut Chart Analytics** - Pie chart showing category distribution by weight, quantity, price, or priority in containers
- **Weight Breakdown Visualization** - Visual breakdown by type (Other/Worn/Consumable)
- **Sidebar Navigation** - Collapsible sidebar with container list and navigation links (LighterPack-compatible design)
- **Dynamic Page Titles** - Automatic document title management for all routes with container/item names
- **Markdown Support** - Full Markdown formatting support for item notes and container descriptions with preview

#### 🔗 Container Nesting
- **Parent-Children Relationship** - Containers can contain other containers as items
- Hide nested containers from main container list
- Expandable rows in item tables to view nested container contents
- Recursive weight calculation (container + contents)
- Cycle detection to prevent infinite loops
- Separate "Add Item" and "Add Container" actions

#### ⚡ Quick Item Entry
- **Default Values** - New items have sensible defaults (0.1 kg weight, quantity 1, status "owned", priority "medium")
- **Category Recognition** - Automatic category detection based on item name keywords (supports English and Polish)
- Recognition triggered on blur event for immediate feedback
- **Inline Name Editing** - Quick edit functionality for item and container names directly on detail pages
- **Item Ordering** - Manual item ordering within containers with batch save confirmation

#### 🚀 Export Features
- **Export to AI Prompt** - Export container with all contents as markdown for AI processing
- Compact format with metadata (weight, brand, color, status, expiration)
- Support for nested containers with calculated weights
- Legend explaining data structure for AI
- One-click copy to clipboard
- **CSV Export** - Export containers to CSV format with column selection, separators, and UTF-8 BOM encoding
- **UUID Support** - UUID-based update workflow for containers and items in markdown import/export

### ✅ Recently Completed Features

#### High Priority
- ✅ **All Items List Page** - Dedicated page showing all items from all containers with filtering and sorting
- ✅ **Shopping Planning Page** - Page for managing items to buy and expiring soon, with shopping list functionality
- ✅ **Container Cloning** - Duplicate containers with all items and nested containers
- ✅ **Add Existing Items** - Add items from other containers using catalog selector
- ✅ **Inline Name Editing** - Quick edit for item and container names directly on detail pages
- ✅ **Item Ordering** - Manual item ordering within containers with batch save confirmation
- ✅ **Move Items Between Containers** - Complete functionality for moving items between containers
- ✅ **Content Reporting System** - Community-driven content moderation for public containers
- ✅ **Item Promotion to Catalogue** - Community-driven promotion system for items to global catalogue
- ✅ **Shelf Life Tracking** - Define shelf life period for items before purchase with automatic expiration date calculation

#### Medium Priority
- ✅ **Preferred Weight Unit** - User setting with auto modes (auto-g-kg, auto-oz-lb) and locale-aware formatting
- ✅ **Extended Fields** - Additional fields for items (price, URL, quality tier, brand, color)
- ✅ **Extended Container Fields** - Brand and price fields for containers
- ✅ **Max Weight Limit** - Set maximum weight for containers with visual warnings
- ✅ **Parameter Recognition** - Automatic recognition of brand and color from item names
- ✅ **404 Page** - User-friendly not found page with navigation suggestions
- ✅ **Markdown Support** - Full Markdown formatting support for notes and descriptions
- ✅ **CSV Export** - Export containers to CSV format with column selection
- ✅ **UUID Import/Export** - UUID-based update workflow for containers and items

#### Low Priority
- ⏸️ **Brand Color Selection** - Choose primary brand color (on hold - current color is satisfactory)
- ✅ **Footer & Legal Pages** - Cookie information, RODO compliance, privacy policy
- ✅ **About Page** - Comprehensive About page with full application description
- ✅ **AI Context Page** - Markdown-formatted description for AI assistants

### 🔄 Planned Features

#### High Priority
- 🔄 **Full Inline Editing** - Quick edit all item fields directly in the list without opening forms
- 🔄 **Drag & Drop Reordering** - Visual drag & drop interface for item ordering

#### Backend Features
- 🚧 **AI Features** - Chat interface, history management (partially completed)
- 🚧 **Multi-Device Sync** - Automatic synchronization between devices (partially completed)
- ✅ **Global Item Catalog** - Shared item database (completed)
- ✅ **Public Container Sharing** - Public containers and token sharing (completed)

### 🔮 Future Roadmap

**Frontend Features (see [ROADMAP.md](./docs/ROADMAP.md)):**
- Inline editing of items directly in lists
- Drag & drop item ordering
- Custom brand management
- Currency support
- Markdown support in notes
- Integrated weight input with unit picker

**Backend Features (see [ROADMAP_ONLINE.md](./docs/ROADMAP_ONLINE.md)):**
- ✅ User authentication (OAuth, 2FA, reCAPTCHA) - Completed
- ✅ Token blacklist and WebAuthn challenge storage (Redis) - Completed
- ✅ Role system (Owner, Premium, Admin, User) - Completed
- ✅ **Subscription billing (Stripe integration)** - Completed
- 🚧 Multi-device synchronization - Partially completed
- ✅ Container sharing (public containers, token sharing) - Completed
- ✅ Public container gallery - Completed
- ✅ Global item catalog with promotion system - Completed
- ✅ Progressive Web App (PWA) - Completed
- 🚧 AI-powered features (chat, history) - Partially completed
- ✅ Item photo uploads (S3 storage) - Completed
- ✅ Content reporting system - Completed
- ✅ Feature limits management - Completed

> 📋 **See also:**
> - [ROADMAP.md](./docs/ROADMAP.md) - 📍 Roadmap index (start here)
> - [ROADMAP_OFFLINE.md](./docs/ROADMAP_OFFLINE.md) - Offline features (localStorage)
> - [ROADMAP_ONLINE.md](./docs/ROADMAP_ONLINE.md) - Online features (backend/DB/auth)
> - [Features Documentation](./docs/features/) - Detailed implementation plans

---

## Development

### Prerequisites
- Node.js ^20.19.0 or >=22.12.0
- pnpm 10.18.3+
- Python 3.12+
- PostgreSQL 15+
- Docker & Docker Compose (for containerized development)

### Quick Start

**Frontend Development:**
```bash
pnpm install
pnpm dev              # Start dev server (http://localhost:5176)
pnpm build            # Build for production
pnpm type-check       # Run TypeScript checks
pnpm lint             # Run ESLint with auto-fix
```

**Backend Development:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
python migrations/047_add_billing_tables.py upgrade  # Run billing migration
uvicorn app.main:app --reload
```

**Docker (Full Stack):**
```bash
docker-compose up -d
```

### Environment Variables

**Frontend (.env):**
```env
VITE_API_PROXY_URL=http://localhost:8000
VITE_GOOGLE_RECAPTCHA_SITE_KEY=your_recaptcha_site_key
VITE_GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
# Stripe (optional - for subscription features)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

**Backend (backend/.env):**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gearstack
JWT_SECRET_KEY=your-secret-key
RECAPTCHA_ENABLED=true
RECAPTCHA_SECRET_KEY=your_recaptcha_secret
GOOGLE_OAUTH_CLIENT_ID=your_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_oauth_client_secret
# Stripe (optional - for subscription features)
STRIPE_ENABLED=true
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

See `.env.example` and `backend/.env.example` for complete configuration options.

---

## Project Structure

```
gear-stack/
├── src/                      # Frontend source code
│   ├── modules/              # Feature modules
│   │   ├── auth/             # Authentication module
│   │   ├── gear/             # Gear management module
│   │   ├── settings/         # Settings module
│   │   └── user/             # User profile module
│   ├── components/           # Shared components
│   │   └── ui/               # shadcn-vue components
│   ├── layouts/              # Layout wrappers
│   ├── router/               # Vue Router config
│   ├── shared/               # Shared utilities
│   └── i18n/                 # Internationalization
├── backend/                  # Backend source code
│   ├── app/
│   │   ├── core/             # Core functionality (config, DB, email)
│   │   ├── modules/          # Feature modules
│   │   │   ├── auth/         # Auth module
│   │   │   ├── billing/      # Stripe subscription module
│   │   │   └── two_factor/   # 2FA module
│   │   └── main.py           # FastAPI app entry
│   └── migrations/           # Database migrations
├── docs/                     # Documentation
│   ├── features/             # Feature implementation plans
│   ├── ROADMAP.md            # Roadmap index (entry point)
│   ├── ROADMAP_OFFLINE.md    # Offline features (localStorage)
│   └── ROADMAP_ONLINE.md     # Online features (backend/DB/auth)
└── docker-compose.yml        # Docker configuration
```

---

## Architecture

### Module-Based Frontend

Each feature is self-contained in `src/modules/`:
- `pages/` - Vue page components
- `components/` - Module-specific components
- `store/` - Pinia stores for state
- `services/` - Business logic layer
- `composables/` - Reusable composition functions
- `types/` - TypeScript definitions
- `routes.ts` - Module routes
- `i18n/` - Module translations

### Backend Modules

Backend follows FastAPI modular pattern:
- `router.py` - API endpoints with rate limiting
- `service.py` - Business logic
- `repositories.py` - Database access
- `models.py` - Domain models
- `schemas.py` - Request/response schemas
- `db_models.py` - SQLAlchemy models

### State Management Pattern

**Frontend:**
- Pinia stores handle state persistence
- Service classes contain business logic
- Stores expose simple CRUD + localStorage sync
- Services handle validation, calculations

**Backend:**
- Repository pattern for data access
- Service layer for business rules
- Clean separation of concerns

---

## Security Features

- ✅ **JWT Authentication** - Secure token-based auth with refresh tokens
- ✅ **Password Hashing** - bcrypt with configurable rounds
- ✅ **Rate Limiting** - Protection against brute force attacks
- ✅ **reCAPTCHA v3** - Bot protection (score-based, invisible)
- ✅ **OAuth 2.0** - CSRF protection via state parameter
- ✅ **Two-Factor Authentication** - TOTP and WebAuthn support
- ✅ **Email Verification** - Confirm user email addresses
- ✅ **CORS Configuration** - Secure cross-origin requests
- ✅ **SQL Injection Prevention** - Parameterized queries via SQLAlchemy
- ✅ **XSS Protection** - Input validation and sanitization

---

## Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct before submitting pull requests.

---

## License

[To be determined]

---

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
