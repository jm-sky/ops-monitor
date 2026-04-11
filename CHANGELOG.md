# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [2.47.1] - 2026-01-21

### Fixed
- **Gear (unified model V2)**: Lint cleanups – remove unused imports (`IGearItemFiltersV2`, `gearQueryKeys`) and variables (`isLoadingAPI` → `_isLoadingAPI`)

---

## [2.47.0] - 2025-12-25

### Security
- **Security Headers Middleware**: Added comprehensive security headers to all HTTP responses
  - Content-Security-Policy (CSP) with support for Google reCaptcha, Sentry, Web Workers, and Vue.js
  - X-Frame-Options: DENY (prevents clickjacking attacks)
  - X-Content-Type-Options: nosniff (prevents MIME type sniffing)
  - X-XSS-Protection: 1; mode=block (enables XSS filter for legacy browsers)
  - Strict-Transport-Security (HSTS): Enabled in production only (max-age=31536000; includeSubDomains; preload)
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy: Disables geolocation, microphone, and camera
  - Headers match Caddyfile configuration for consistency
  - Middleware registered as first in pipeline (before CORS) to ensure headers are applied to all responses

---

## [2.46.0] - 2025-12-23

### Added
- **Premium Feature Lock Button**: New component to manage access to premium features
  - `PremiumFeatureLockButton` component for consistent premium feature gating
  - Enhanced user experience for accessing premium features
  - Integration with billing system for subscription management
- **Stripe Webhook Signature Verification**: Enhanced security for Stripe integration
  - Webhook signature verification for all Stripe webhook events
  - Constants module for webhook paths requiring raw body processing
  - Proper handling of subscription fields in webhook events (both object and string IDs)
  - Improved logging for webhook events

### Changed
- **Billing & Subscription UI**: Enhanced billing navigation and components
  - Reintroduced Billing & Subscription link in AppHeader for improved navigation
  - Updated PlanCard component to display current plan and popular badges more effectively
  - Improved visibility of billing options and premium features
- **Subscription History**: Refactored for dynamic event types
  - Removed restrictive `event_type` constraint from `subscription_history` table
  - Support for dynamic event types (e.g., 'subscription_activated', 'admin_cancel_plan_tier')
  - Enhanced flexibility in subscription event logging
- **Middleware Updates**: Improved Stripe webhook compatibility
  - Updated `ConvertEmptyStringsToNoneMiddleware` to exclude webhook paths
  - Prevents payload modification that could invalidate webhook signatures
  - Ensures compatibility with Stripe's signature verification requirements

### Security
- **Stripe Webhook Security**: Enhanced security for billing system
  - Proper webhook signature verification prevents unauthorized webhook processing
  - Raw body processing for webhook paths ensures signature validity
  - Improved security and reliability of subscription management

---

## [2.45.0] - 2025-01-22

### Added
- **Markdown Link Security (Phase 1)**: Implemented basic link validation and sanitization for markdown content
  - Frontend: Link security utilities with protocol validation and length limits
  - Frontend: Post-processing of rendered markdown HTML to secure links
  - Frontend: Automatic addition of `rel="noopener noreferrer"` to external links
  - Frontend: Blocking of dangerous protocols (`javascript:`, `data:`, `vbscript:`, `file:`, `about:`, etc.)
  - Frontend: Link length validation (max 2048 characters)
  - Backend: Markdown content sanitization before saving to database
  - Backend: Validators for `notes` and `description` fields in containers and items
  - Backend: Automatic removal of dangerous protocol links from markdown content
  - Security: Maximum markdown content length limit (50000 characters)
  - Security: Visual indication of blocked links (disabled styling)

### Security
- **Markdown Link Protection**: Enhanced security for markdown content rendering
  - Prevents XSS attacks through dangerous protocol links
  - Validates link length to prevent DoS attacks
  - Sanitizes markdown content before database storage
  - Blocks external links from executing JavaScript or accessing local files

---

## [2.44.1] - 2025-12-22

### Changed
- **Documentation**: Updated ROADMAP_ONLINE.md with completed features
  - Marked "Global catalogue search improvement" feature as completed
  - Updated "Item and container limits for free/premium accounts" feature to completed status

---

## [2.44.0] - 2025-12-19

### Added
- **Billing & Subscription UI Navigation**: Added billing link to user navigation menu
  - Billing link with CreditCard icon in UserNav dropdown menu
  - Link appears between Settings and Gear settings in user menu
  - Uses i18n translations for both English and Polish

### Changed
- **Billing Pages Layout**: Refactored billing pages to use AuthenticatedLayout
  - BillingPage and BillingSuccessPage now nested in AuthenticatedLayout component
  - Consistent page structure using CommonPageHeader with CreditCard icon
  - Follows same pattern as other authenticated pages (e.g., ContainersListPage)
  - All text content now uses i18n translations

### Fixed
- Fixed billing link visibility in UserNav menu (links are passed via props from AppHeader)

---

## [2.43.0] - 2025-12-18

### Added
- **Polish Pluralization Support**: Enhanced Polish localization with proper pluralization rules
  - New `getPolishPluralizationRule` utility function for vue-i18n
  - Correct handling of plural forms for item counts (0, 1, 2-4, 5+)
  - Improved grammatical accuracy in Polish translations

### Changed
- Updated sidebar button variants styling for better readability and responsiveness
- Improved ShoppingListFilters component lifecycle by changing from `onMounted` to `onBeforeMount` for earlier state initialization

### Fixed
- Fixed sidebar button variants class string formatting for better maintainability

---

## [2.42.0] - 2025-12-18

### Added
- **Content Reporting System**: Community-driven content moderation for public containers
  - New `ContentReportDB` model and database table to track content reports
  - `is_hidden_by_reports` field in containers to manage visibility based on report status
  - API endpoints for reporting public containers (`POST /gear/containers/{id}/report`)
  - Admin API endpoints for reviewing and managing reports (`GET /admin/reports`, `PATCH /admin/reports/{id}`)
  - Automatic container hiding from public views after ≥3 active reports
  - Automatic visibility restoration after admin review (when all reports are dismissed/reviewed)
  - Frontend reporting UI components (`ReportContainerButton`, `ReportContentDialog`)
  - Admin content reports page (`ContentReportsPage`) with filtering and status management
  - Report categories: Spam/Fraud, Violence, Sexual Content, Profanity, Other
  - User can only report a container once (unique constraint)
  - Alert for container owners when their container is hidden due to reports

### Changed
- Public container endpoints now filter out containers hidden by reports
- Enhanced admin dashboard with content reports management

---

## [2.41.0] - 2025-12-17

### Changed
- **Export to Markdown dialog improvements**:
  - Removed redundant "Show notes/descriptions" checkbox - format dropdown now controls visibility
  - Added semantic separators (`---`) in markdown export for better structure and readability
  - Improved clipboard copy to preserve blank lines when pasting into ChatGPT (using non-breaking spaces)
  - Export logic now uses `descriptionFormat` as single source of truth for showing descriptions

### Fixed
- Fixed export dialog confusion where checkbox was checked by default but format was set to 'off', causing nothing to export

---

## [2.40.0] - 2025-12-17

### Added
- **Automatic Image Deletion**: Automatic cleanup of images when associated entities are deleted
  - Images are automatically deleted when user accounts are deleted, ensuring no residual data remains
  - Images are automatically deleted when items are deleted, including graceful error handling
  - Enhanced GearService with methods to delete images from both storage and database
  - Improved data management and compliance with automatic cleanup

### Changed
- Updated roadmap to reflect completion of automatic image deletion features

---

## [2.39.0] - 2025-01-21

### Added
- **Shelf Life (Okres Przydatności) for Items**: New feature to define shelf life period for items before purchase
  - New `shelfLife` field in gear items: `{ value: number, unit: 'days' | 'months' | 'years' }`
  - `ShelfLifeInput` component - unified input for value and unit (similar to weight input)
  - "Set Expiration Date" button to automatically calculate expiration date from shelf life (Today + Shelf Life)
  - Shelf life display on item detail page with quick action button
  - Backend support: `shelf_life` JSONB column in `gear_items` table
  - Database migration `044_add_shelf_life_to_gear_items.py`
  - Default unit: years
  - UI: Expiration date and shelf life displayed side-by-side in form (responsive grid)

### Changed
- Item form layout: Expiration date and shelf life now displayed in a single row (grid layout)
- Improved UX: Shelf life input uses unified component with contextual label

---

## [2.38.0] - 2025-01-21

### Added
- **Item Promotion to Catalogue**: Community-driven promotion system for items to global catalogue
  - New `promote_count` field in gear items to track promotion votes
  - `ItemPromotionDB` model to track which users promoted which items
  - Promotion threshold configuration (default: 10 promotions required)
  - API endpoints:
    - `POST /gear/items/{item_id}/promote` - Promote an item to catalogue
    - `GET /gear/items/{item_id}/promotion-status` - Get promotion status
    - `POST /gear/items/{item_id}/add-to-catalogue` - Admin override to directly add item
  - Promotion requirements:
    - Only registered users with accounts older than 1 month can promote
    - Admin/app owner users can promote regardless of account age
    - Items must be in public containers
    - Users can only promote an item once
  - Automatic addition to catalogue when promotion threshold is reached
  - Frontend promotion UI (`ItemPromotionCard`) with progress bar and promotion button
  - Creator name display in catalogue items (shows name if profile is public, "User" otherwise)

### Changed
- Catalogue items now display creator information based on public profile settings
- Admin promotion actions now correctly set item owner as catalogue item creator (not admin)

---

## [2.37.1] - 2025-12-16

### Fixed
- **Pagination**: Fixed page size not persisting in URL and not applying correctly to DataTable
  - `Pagination` component now uses `computed` for `totalPages` to react to `pageSize` changes
  - `DataTable` no longer allows TanStack Table to reset `pageSize` with stale internal state
  - Added watch with `immediate: true` to sync TanStack Table with external `pageSize` changes (e.g., from URL)
  - Removed redundant `currentPage`/`currentPageSize` computed properties in favor of direct `defineModel` usage

---

## [2.37.0] - 2025-12-16

### Added
- **Automatic Weight Unit Selection**: Added support for automatic weight unit preferences and locale-aware formatting
  - New preferred weight unit options: `auto-g-kg` and `auto-oz-lb`
  - Automatic unit selection based on total weight (< 1 kg → g/oz, ≥ 1 kg → kg/lb)
  - Thousand-separator formatting for all weight displays using user locale
  - Integration with Gear Settings, containers, items, catalogue items, and export-to-prompt flow

### Changed
- Updated weight formatting utilities to support auto modes and locale-aware number formatting
- Updated gear forms and settings to safely map auto units to basic units for validation and backend compatibility

---

## [2.36.0] - 2025-12-15

### Added
- **AI Chat Enhancements**: Extended AI chat functionality with improved history management
  - Added `container_ids` field to AI history model for efficient filtering
  - Database migration to populate `container_ids` from existing history entries
  - Chat from Containers List page with automatic inclusion of filtered containers
  - Resume chat functionality from AI History Page with automatic navigation
  - Chat history sidebar panel using Sheet component (accessible from chat window header)
  - Filter history by `container_ids` and `operationType` in sidebar
  - Automatic navigation logic: single container → Container Detail, multiple/no containers → Containers List
  - Query parameter `restoreHistoryId` support for restoring conversations
- **Unit Tests**: Added comprehensive test coverage for new AI chat features
  - Tests for `useAiHistory` composable with container filtering
  - Tests for history sidebar filtering logic
  - Tests for navigation logic based on container IDs

### Changed
- **AI History**: Enhanced history model to include `container_ids` for better filtering and organization
- **AI Chat Window**: Added history sidebar panel with Sheet component integration
- **AI History Page**: Added "Resume Chat" button with smart navigation based on container context

### Fixed
- Fixed TypeScript type definitions for `IAiHistoryDetail` to include all backend fields
- Fixed undefined `containerIds` handling in history filtering logic

---

## [2.35.0] - 2025-12-12

### Added
- **Catalogue Management Page**: Complete management interface for global catalogue items
  - New DataTable-based management page with filters (search, category, brand, isActive status)
  - Dropdown actions menu in table rows with: Show, Edit, Activate/Deactivate, Delete
  - Admin/owner permission checks and lazy loading for code splitting
  - Integrated with existing catalogue API and composables
- **i18n Translations**: Added missing translations for catalogue management
  - `gear.actions.manage` (EN: "Manage", PL: "Zarządzaj")
  - `gear.fileUpload.imageGallery.previousImage` (EN: "Previous image", PL: "Poprzedni obrazek")
  - `gear.fileUpload.imageGallery.nextImage` (EN: "Next image", PL: "Następny obrazek")

### Changed
- **Catalogue Manage Page**: Replaced card-based view with DataTable for better management experience
  - Consistent with other admin management pages (AdminItemsPage, AdminContainersPage)
  - Better sorting, filtering, and pagination support
  - Improved UX with dropdown actions menu instead of inline buttons

---

## [2.34.0] - 2025-12-11

### Added
- **Move Items Between Containers**: Complete functionality for moving items between containers
  - Backend endpoint `PATCH /gear/items/{item_id}/move` for moving items to different containers
  - Repository and service layer implementation with validation
  - Preserves item UUID, linked_item_id relationships, and all item data (images, history)
  - Comprehensive integration tests covering all edge cases
  - Frontend `MoveItemDialog` component with container selection
  - "Move" action in item header actions menu (`ItemHeaderActions.vue`)
  - Full i18n support (PL/EN) for move functionality
  - Toast notifications for success/error feedback
  - Automatic UI refresh after successful move operation

### Changed
- **Gear Item Service**: Added `moveItem` method to `IGearItemService` interface
- **Gear Composables**: Moved `moveItem` from `useContainerCalculations` to `useItemOperations` (proper separation of concerns)
- **Roadmap**: Updated ROADMAP.md and ROADMAP_ONLINE.md to mark move items feature as completed

---

## [2.33.0] - 2025-12-09

### Added
- **AI History Management UI**: Complete user interface for managing AI chat history
  - New `AiHistoryPage` with full history browsing, filtering, and search capabilities
  - `AiHistoryList` component displaying history items with operation type badges
  - `AiHistoryItem` component with restore, delete, and view details actions
  - `AiHistoryFilters` component with search query and operation type filtering
  - `AiHistoryDetailDialog` for viewing complete conversation details
  - Client-side search filtering across prompts, responses, models, and providers
  - Pagination support with URL state persistence
  - Restore conversation functionality to continue previous AI chats
  - Delete individual history items with confirmation dialog
  - Clear all history functionality with bulk delete confirmation
  - Full i18n support (PL/EN) for all history-related features
  - Link to history page from AI Settings card

- **AI Settings Component Refactoring**: Modular architecture for better maintainability
  - Extracted `AiModelSelector` into dedicated settings component
  - New `AiTokenManager` component for API token management
  - New `AiUsageDisplay` component for showing AI usage statistics
  - Improved component organization and separation of concerns
  - Enhanced `AiChatWindowHeader` with better structure and functionality

- **Lazy Loading for Dialogs**: Performance optimization for dialog components
  - Implemented lazy loading for dialog components to reduce initial bundle size
  - Improved application startup time and performance

- **Backend Analysis Documentation**: Comprehensive analysis documentation
  - Complete backend analysis for business modules and API layer
  - Detailed refactoring plans and architectural improvements
  - Security module analysis and fixes documentation

- **Database Migrations**:
  - Migration `037_add_max_tokens_and_temperature_to_ai_settings.py` for AI settings enhancements
  - Migration `038_migrate_ai_history_to_new_schema.py` for AI history schema updates

### Changed
- **AI Chat Window**: Enhanced chat interface with improved header and context configuration
- **Container Styling**: Enhanced container styling and internationalization support
- **Image Management**: Improved image management and item retrieval in gear module
- **Data Table Components**: Minor improvements to DataTable and DataTableToolbar components

### Fixed
- **Gear Module Services**: Applied critical fixes to gear module services for enhanced data consistency
- **Backend Security Modules**: Completed security module fixes and improvements

---

## [2.32.0] - 2025-12-08

### Added
- **Redis Infrastructure**:
  - Redis service added to all Docker Compose configurations (production, development, dev-minio)
  - Redis client configuration with connection pooling and dependency injection
  - Persistent storage with AOF (Append Only File) enabled
  - Health checks and automatic restart policies

- **Token Blacklist Service**:
  - Server-side token invalidation using Redis
  - SHA-256 hashing for secure token storage
  - Automatic expiration using Redis TTL
  - Token blacklisting on logout and account deletion
  - Integration with authentication middleware

- **WebAuthn Challenge Storage**:
  - Server-side challenge storage in Redis (replaces client-side storage)
  - Atomic get-and-delete operations for one-time use
  - 5-minute TTL for challenges
  - Protection against replay attacks
  - Challenge tampering prevention

- **Documentation**:
  - Comprehensive REDIS-TESTING.md guide with testing procedures
  - Troubleshooting guide for Redis issues
  - Production deployment checklist
  - Examples for testing token blacklist and WebAuthn flows

### Changed
- Updated authentication dependencies to include blacklist service
- Refactored WebAuthn service to use server-side challenge storage
- Enhanced logout and account deletion endpoints with token blacklisting
- Improved error handling in optional authentication (gear module)

### Fixed
- Fixed all mypy type checking errors in security modules
- Corrected Redis client method deprecation (close → aclose)
- Fixed type annotations in challenge_store.py
- Resolved AsyncGenerator await issues in two_factor router

### Security
- **CRITICAL**: Implemented token invalidation to prevent reuse after logout
- **CRITICAL**: Server-side WebAuthn challenge storage prevents tampering
- **CRITICAL**: One-time use challenges prevent replay attacks
- Enhanced security posture with Redis-based session management
- Tokens are now properly invalidated on account deletion

---

## [2.31.0] - 2025-12-05

### Added
- **Global Catalogue Enhancements**:
  - Price and currency display for catalogue items
  - URL links to product pages for enhanced product information
  - New items added to global catalogue and example sets
  - Endpoint to fetch images from catalogue items
- **UI/UX Improvements**:
  - Refresh functionality for containers and items
  - Delete functionality for item management
  - Image filter in AllItemsPage with refactored toolbar
  - Search and pagination state now persisted in URL
  - Enhanced item details with catalogue actions

### Changed
- Consolidated filter logic into AllItemsFiltersMenu component
- Refactored pagination component to use computed properties
- Enable conditional fetching of catalogue items in useCatalogue

### Fixed
- Resolved all mypy type checking errors in backend
  - Added type stubs for passlib
  - Fixed Sentry LoggingIntegration type error
  - Added type ignore comments for libraries without stubs
- Improved weight formatting in formatWeight utility
- Corrected import order and v-model bindings in components
- Updated .env.example with improved Sentry and storage configuration

---

## [2.30.0] - 2025-12-04

### Added
- **Feature Limits Management**: Configurable AI and storage limits per user role
  - New `feature_limits` database table storing limits for user, premium, admin, and owner roles
  - Migration `033_add_feature_limits_table` with default limits:
    - User: 0$ AI limit (no access without own token), 20MB storage
    - Premium: 5$ AI limit, 50MB storage
    - Admin: Unlimited AI, 200MB storage
    - Owner: Unlimited AI, 1GB storage
  - Backend CRUD API endpoints (`/feature-limits`) for managing limits (admin/owner only)
  - New admin page (`/admin/limits`) for configuring limits per role
  - Limits are now stored in database instead of hard-coded values
  - `/users/me` endpoint now returns `features` object with AI and storage limits
  - Storage usage endpoint (`/users/me/storage/usage`) uses limits from database
  - Image upload validation uses role-based limits from database

### Changed
- **AI Settings Access**: AI settings are now available for all authenticated users (not just premium)
  - Regular users can use AI only if they have their own API token
  - Premium users can use AI with system token (up to configured limit)
  - `useAi` composable updated to check for own token or premium status
- **User Features Endpoint**: `/users/me` now includes `features` object with:
  - `ai.enabled`: Whether AI is enabled for user
  - `ai.limit`: AI usage limit in USD (null = unlimited)
  - `storage.limit`: Storage limit in bytes
- **Limit Calculation**: All limit calculations now use database values with fallback to config

### Fixed
- Fixed type errors in `users/router.py` - `CurrentUser` from users module uses `role` string instead of boolean flags
- Updated `_map_auth_user` to correctly map all roles (owner, admin, premium, user)

---

## [2.29.0] - 2025-12-03

### Added
- **Weight Breakdown Visualization**: New chart mode showing weight distribution by category (Other / Worn / Consumable)
  - New `calculateWeightBreakdown()` function in `containerCalculations.ts` to categorize items by wearable/consumable flags
  - Extended `CategoryPieChart` component with new `weight-breakdown` mode
  - Visual breakdown showing: Other items (in pack), Worn items (on person), Consumable items
  - Priority logic: consumable > worn > other (if item has both flags, treated as consumable)
  - Color scheme: Other (slate-400), Worn (blue-500), Consumable (green-500)
  - Full i18n support (PL/EN) with descriptive labels

### Changed
- **Chart Component**: Extended `CategoryPieChart` to support weight breakdown mode alongside existing modes (weight, quantity, price, priority)
- **Chart Legend**: Updated `CategoryPieChartLegend` to display weight breakdown categories with proper translations
- **Terminology**: Changed "Base Weight" to "Other" for better clarity (items not worn or consumable)

---

## [2.28.0] - 2025-12-03

### Added
- **Markdown Support in Notes and Descriptions**: Full Markdown formatting support for item notes and container descriptions
  - New `MarkdownRenderer` component for rendering Markdown content with security-focused settings
  - New `TextareaWithMarkdownPreview` component with Edit/Preview toggle for editing Markdown
  - Support for bold, italic, lists (ordered and unordered), links, code blocks, headings, quotes, and more
  - Markdown rendering in all display contexts: item details, container headers, cards, and public views
  - Shared Markdown translations in `common` namespace for use across the entire application

### Changed
- **Form Components**: Updated `ItemFormFields` and `ContainerFormFields` to use `TextareaWithMarkdownPreview` for notes and descriptions
- **Markdown Renderer**: Improved list styling with proper indentation and visible markers (disc, circle, square for nested lists)
- **Translations**: Moved Markdown-related translations from `gear` module to `shared/common` for better reusability

### Fixed
- Fixed CSS syntax errors in `MarkdownRenderer.vue` (missing semicolons)
- Fixed item initialization order issue in `ItemFormPage.vue`

---

## [2.27.1] - 2025-12-02

### Changed
- **Vite Configuration**: Removed commented-out rollupOptions section from `vite.config.ts` for improved readability and maintainability

---

## [2.27.0] - 2025-12-01

### Added
- **OAuth Connections Management**: Settings section for managing linked OAuth providers
  - New `oauth_connections` table and repository methods for multiple OAuth providers per user
  - Backend endpoints: `GET /auth/oauth/connections` and `DELETE /auth/oauth/connections/{provider}`
  - Frontend `OAuthConnectionsCard` in Settings listing linked providers (Google, Facebook) with remove action

### Changed
- **Image Processing Settings**: Enhanced image processing mode settings UI with Premium feature badge and clearer descriptions
- **Container Color Picker**: Added search and improved color class mappings for container colors
- **Layout and Header**: Updated header and layout styles for improved responsiveness and consistency
- **Dependencies**: Updated `reka-ui` to version 2.6.1
- **Documentation**: Added unified model analysis document for containers and items (`UNIFIED_MODEL_ANALYSIS.md`)

---

## [2.26.0] - 2025-01-30

### Added
- **About Page**: New comprehensive About page (`/about`) with full application description and feature list
  - Overview section explaining Gear Stack's purpose and capabilities
  - Detailed core features documentation (containers, items, analytics, search, import/export)
  - Business features documentation (security, user profile, i18n, theming)
  - Technical stack information (frontend and backend technologies)
  - Fully internationalized (EN/PL)

- **AI Context Page**: New AI Context page (`/ai-context`) with Markdown-formatted description for AI assistants
  - Short, concise application description in Markdown format
  - One-click copy to clipboard functionality
  - Designed for quick context sharing with ChatGPT and other AI assistants
  - Includes all key features, capabilities, and technical details
  - Fully internationalized (EN/PL)

- **Public Routes Configuration**: New centralized route configuration system
  - Created `publicRoutes.ts` with `PublicRoutePaths` and `PublicRouteNames` constants
  - Similar pattern to `auth/config/routes.ts` for consistency
  - All public pages now use named routes instead of hardcoded paths
  - Better maintainability and easier route management

### Changed
- **Route Configuration Refactoring**: Replaced all hardcoded route paths with named routes
  - Updated `AppSidebar.vue` to use `PublicRouteNames` instead of hardcoded `/about` and `/ai-context`
  - Updated `AppFooter.vue` to use `PublicRouteNames` for all footer links
  - Updated `LandingPage.vue` to use `PublicRouteNames` for info links
  - Updated `PrivacyPage.vue` to use `PublicRouteNames` for cookies link
  - Updated all layout components (`PublicLayout`, `GuestLayoutCentered`, `GuestLayoutCenteredGlass`, `GuestLayoutTwoColumns`) to use `PublicRouteNames.landing`
  - Improved code consistency and maintainability

- **Routes Structure**: Refactored `routes.ts` to use `publicRoutes` array
  - Cleaner route definitions
  - Better organization of public vs. module routes
  - Consistent route management pattern

### Technical Details
- New pages: `AboutPage.vue` (211 lines), `AiContextPage.vue` (169 lines)
- New route configuration: `publicRoutes.ts` (78 lines)
- Updated translations: Added comprehensive `about` and `aiContext` sections (EN/PL)
- All components now use `:to="{ name: PublicRouteNames.xxx }"` instead of `to="/xxx"`
- Improved type safety with centralized route constants

---

## [2.25.2] - 2025-11-30

### Changed
- **Code Formatting**: Improved code formatting and import organization
  - Fixed import sorting in ProfileEditPage and PrivacyPage for better consistency
  - Enhanced GravatarIcon component formatting for better readability

---

## [2.25.1] - 2025-11-30

### Changed
- **Profile Edit Gravatar Icon**: Updated Gravatar generation button to use custom Gravatar icon instead of generic Sparkles icon
  - New `GravatarIcon.vue` component created with official Gravatar logo design
  - Icon follows Lucide icon styling pattern for consistency
  - Better visual recognition for Gravatar-related functionality

---

## [2.25.0] - 2025-11-28

### Added
- **Inline Item Name Editing**: Quick edit functionality for item names directly in the items table
  - New `ItemsTableEditModeToggle` component to enable/disable inline editing mode
  - New `ItemsTableEditableNameCell` component for editable name cells
  - Edit mode toggle persists in localStorage
  - Click on item name to edit, save with Enter key or blur, cancel with Escape key or X button
  - Visual feedback with loading states and reset functionality
  - New composables: `useInlineItemEditing` and `useItemsTableEditMode` for shared edit logic
  - Feature flag support via `config.features.inlineEditing.enabled`

- **Switch UI Component**: New Switch component for toggle controls
  - Reusable switch component following design system patterns
  - Used in edit mode toggle and other settings

- **AI Settings Card**: New settings card for AI-related preferences
  - Centralized AI configuration interface
  - Improved organization of AI settings

### Changed
- **Container Color Options**: Refactored container color options in backend and frontend
  - Updated color names for better consistency
  - Refactored `ContainerColorPicker` component to use updated color model
  - Enhanced color utilities in `containerColors.ts`

- **Container Form**: Updated to use new color options
  - Improved color selection UX
  - Better color validation

### Fixed

---

## [2.24.0] - 2025-01-XX

### Added
- **Sidebar Navigation**: New sidebar menu compatible with LighterPack design
  - Collapsible sidebar with container list and navigation links
  - Responsive design with mobile drawer support
  - Sidebar state persisted in cookies
  - New UI components: Sidebar, SidebarProvider, SidebarInset, and related components
  - AppHeader and AppSidebar components for new layout structure
  - Skeleton and Tooltip UI components

- **Import Button in Empty State**: Added "Import from Markdown" button in empty state on Containers List page
  - Quick access to import functionality when no containers exist
  - Improved UX for new users starting with the application

- **Backend Endpoint for Delete All Containers**: New `DELETE /gear/containers` endpoint
  - Atomic deletion of all user containers in single transaction
  - More efficient than deleting containers one by one
  - Ensures data consistency between backend and localStorage

### Changed
- **Layout Refactoring**: Restructured AuthenticatedLayout to use sidebar pattern
  - Moved navigation from top bar to sidebar
  - Header now contains logo, sidebar trigger, and user menu
  - Improved navigation structure and organization

- **Admin Composable Refactoring**: Replaced `useAdmin()` composable with `usePermissions()`
  - Centralized permission logic in shared composable
  - Better code organization and maintainability
  - All admin checks now use `usePermissions()` composable

- **Import Markdown Dialog**: Enhanced preview and import button states
  - Preview button disabled when markdown content is too short
  - Visual feedback for button states (default/outline variants)
  - Improved UX for import workflow

### Fixed
- **Delete All Containers Bug**: Fixed desynchronization between backend and localStorage
  - localStorage now cleared only after successful backend deletion
  - Eliminates issue where containers reappeared after page refresh
  - Uses new dedicated backend endpoint for atomic deletion

---

## [2.23.0] - 2025-11-28

### Added
- **Dynamic Page Titles**: Automatic document title management for all routes
  - Router guard automatically sets page titles based on route metadata
  - Format: `{Page Title} | {App Name}` (e.g., "Dashboard | Gear Stack")
  - Support for static titles via `meta.title` i18n keys
  - Support for dynamic titles with object names (e.g., container/item names)
  - New `usePageTitle()` composable for manual title management in components
  - All routes now have proper i18n translation keys for page titles
  - Dynamic titles update automatically when data loads (containers, items, etc.)

### Changed
- Router now automatically sets document title on navigation
- Page titles are internationalized using existing i18n infrastructure

---

## [2.22.0] - 2025-11-28

### Added
- **Backend Middleware: ConvertEmptyStringsToNone**: Automatic conversion of empty strings to None in request body
  - Processes POST, PUT, PATCH requests with JSON content type
  - Recursively handles nested objects and arrays
  - Ensures consistent handling of optional fields across all API endpoints
  - Similar to Laravel's ConvertEmptyStringsToNull middleware
  - Comprehensive unit tests (266 lines) for middleware functionality

- **Backend Weight Unit Support**: Extended weight unit support to include imperial units
  - Backend now supports `oz` (ounces) and `lb` (pounds) in addition to `g` and `kg`
  - Updated database models, schemas, and service calculations
  - Weight calculations properly convert oz (28.3495g) and lb (453.592g) to grams

- **Inline Item Name Editing**: Quick edit functionality for item names directly on Item Detail page
  - Click on item name or edit icon to start editing
  - Save with Enter key, cancel with Escape key or X button
  - Implemented in dedicated `ItemHeaderName.vue` component
  - Visual feedback with hover states and edit icon

- **Item Header Component**: New reusable `ItemHeader.vue` component
  - Consolidates item header display logic (back button, edit button, badges)
  - Displays category, priority, status, expiration badges
  - Used in ItemDetailPage for consistent header display

- **Expiration Handling Composable**: New `useExpiration` composable for centralized expiration logic
  - Reusable expiration checking across components
  - Provides `isExpired` and `isExpiringSoon` computed properties
  - Replaces duplicate expiration logic in multiple components

- **Expiration Utility Functions**: New utility functions for expiration handling
  - `isExpired()` - Checks if item is expired
  - `isExpiringSoon()` - Checks if item is expiring within warning days
  - Centralized expiration logic for better maintainability

### Changed
- **AI Actions Refactoring**: Refactored AI actions to use centralized services
  - AI actions now use `gearItemService()` and `gearContainerService()` instead of direct local services
  - Ensures consistent handling whether using API or localStorage based on backend status
  - Updated `AiActionType` to reflect new action names (`create_item`, `update_item`, `delete_item`, etc.)
  - Improved structured output types for better type safety

- **API Service Simplification**: Simplified API service methods
  - Removed manual data cleaning logic from `gearItemApiService` and `gearContainerApiService`
  - Services now rely on backend middleware for empty string to null conversion
  - Axios automatically omits undefined values, middleware handles empty strings
  - Removed duplicate `cleanItemUpdateData` and `cleanContainerUpdateData` methods
  - Backend now handles all weight units (g, kg, oz, lb) consistently

- **Expiration Logic Refactoring**: Centralized expiration handling across components
  - Replaced duplicate expiration functions in `ItemDetailPage`, `PublicItemDetailPage`, `ShoppingPlanningPage`
  - All components now use `useExpiration` composable for consistent behavior
  - Improved code maintainability and consistency

- **Container Header Name Editing**: Enhanced inline editing UX
  - Added X button for canceling edit mode
  - Improved keyboard handling (Enter to save, Escape to cancel)
  - Better visual feedback during editing

- **Item Detail Page**: Refactored to use new `ItemHeader` component
  - Simplified component structure
  - Consistent header display across item detail views
  - Better separation of concerns

### Fixed

---

## [2.21.0] - 2025-01-28

### Added
- **Inline Container Name Editing**: Quick edit functionality for container names directly on Container Details page
  - Click on container name or edit icon to start editing
  - Save with Enter key, cancel with Escape key
  - Implemented in dedicated `ContainerHeaderName.vue` component
  - Visual feedback with hover states and edit icon

### Changed
- **Translation Refactoring**: Migrated from `$t` to `t` from `useI18n()` composable
  - Updated `ItemFormFields.vue` (44 occurrences)
  - Updated `ContainerFormFields.vue` (28 occurrences)
  - Updated `ContainerHeader.vue` (3 occurrences)
  - Updated `ColorAutocomplete.vue` (1 occurrence)
  - Improves consistency with Vue 3 Composition API best practices
  - Better TypeScript support and testability

- **Form Labels Standardization**: Replaced manual `<label>` tags with `Label` component
  - Updated `ItemFormPage.vue` to use `Label` component with `required` prop
  - Ensures consistent styling and required field indicators across forms

### Fixed

---

## [2.20.1] - 2025-01-27

### Fixed
- **Public Profile Owner Badge**: Fixed Owner role not displaying correctly on public profiles
  - Backend now uses AuthUser directly in public profile endpoint to access all role fields
  - Previously used adapted User model which lacked `isOwner` and `isPremium` attributes
  - Owner users now correctly show Owner badge instead of Admin badge on public profiles

### Changed
- **Code Refactoring**: Improved code quality and maintainability
  - Added `getPublicUser()` method to `userApiService` for public profile fetching
  - PublicUserProfilePage now uses service layer instead of direct API calls
  - Reused shared `getInitials()` helper from `@/shared/utils/getInitials`
  - Removed duplicate interfaces and mapper functions from component

---

## [2.20.0] - 2025-01-27

### Added
- **UserRoleBadge Component**: Reusable role badge component for consistent role display
  - Single source of truth for role presentation across all pages
  - Color-coded badges: Owner (purple with Crown icon), Premium (yellow with Gem icon), Admin (blue with Shield icon)
  - Configurable icon display via `showIcon` prop
  - Used in ProfileViewPage, PublicUserProfilePage, and AdminUsersPage
  - i18n support for all role labels

### Changed
- **Profile Pages**: Updated to use new UserRoleBadge component
  - ProfileViewPage now shows Owner, Premium, and Admin roles
  - PublicUserProfilePage displays all role types with proper styling
  - AdminUsersPage uses UserRoleBadge without icons for cleaner table view

### Fixed
- **Public Profile API**: Added missing role fields to backend response
  - PublicUserResponse schema now includes `isOwner` and `isPremium` fields
  - Public profile endpoint properly returns all role information
  - Role badges now display correctly on public user profiles

---

## [2.19.0] - 2025-01-27

### Added
- **CLI Command: Toggle Owner Role**: New `toggle-owner` command for managing owner role
  - Interactive mode with user prompts for email/ID
  - Support for `--yes` flag to skip confirmation
  - Displays current and new role information before changes
  - Usage: `python -m cli users toggle-owner <email-or-id> --yes`
- **Owner and Premium Roles**: Full role hierarchy implementation
  - Added `is_owner` and `is_premium` database columns via migration
  - New role badges in admin UI (Owner: purple, Premium: yellow, Admin: blue, User: gray)
  - Role column in admin users table now shows all role types
- **Protected User System**: Comprehensive protection for critical users
  - `SUPERADMIN_EMAIL` environment variable for owner designation
  - `PROTECTED_USER_EMAIL` environment variable to prevent user deletion
  - Admin users can only be deleted by Owners
  - Owner users cannot be deleted or have roles changed by Admins
  - UI disables delete/role change actions for protected users

### Changed
- **Admin Service Protection Logic**: Enhanced user management security
  - Three-tier protection: protected email check, admin protection, owner protection
  - `delete_user` method now checks protected status before deletion
  - `update_user` method prevents unauthorized role changes
- **Admin Users Page UI**: Improved role display and action controls
  - Role badges with color coding for quick identification
  - Disabled actions for Owner and Admin users (delete button)
  - Disabled role toggle for Owner users
  - Updated column header from "Admin" to "Role"

### Fixed
- **AI Item Creation**: Fixed undefined properties for AI-created items
  - All required fields now have proper default values (category: 'other', weight: 0, quantity: 1, weightUnit: 'g', priority: 'medium', status: 'toBuy')
  - Items created through AI actions now properly initialize
- **Admin Guard**: Removed unused `useAuthStore` import to fix linter error

---

## [2.18.0] - 2025-01-28

### Added
- **AI Chat Conversation History**: Added conversation history support for AI chat
  - New `history` field in `AiChatRequest` schema for maintaining conversation context
  - Backend now accepts and processes conversation history in chat requests
  - History messages are included in the prompt sent to AI models
  - Enables multi-turn conversations with context preservation
- **AI Chat Structured Output Debugging**: New component for debugging structured outputs
  - New `AiChatMessageDebugStructuredOutput` component for viewing structured output data
  - Displays structured output in a formatted, readable way
  - Helps developers and users understand AI responses with structured data
- **AI Chat Message Footer**: Enhanced message display with footer component
  - New `AiChatMessageFooter` component for displaying message metadata
  - Shows additional information and actions for chat messages
  - Improved message organization and user experience
- **Button Size Variant**: Added extra-small button size
  - New `xs` size variant for Button component (`h-7 text-xs rounded-md gap-1 px-2`)
  - Provides more compact button option for dense UIs

### Changed
- **AI Chat Backend**: Enhanced message processing and JSON cleaning
  - Improved JSON block removal in chat responses (handles both ````json` and plain ```` blocks)
  - Better whitespace cleanup for cleaner AI responses
  - Enhanced message building to include conversation history
- **AI Chat Frontend**: Improved message display and debugging
  - Enhanced `AiChatMessage` component with structured output debugging support
  - Better integration of debug components for prompt and structured output inspection
  - Improved message footer integration

### Fixed
- **AI Chat JSON Cleaning**: Fixed JSON block removal to handle various formats
  - Now correctly removes both ````json { ... } ``` and ```` { ... } ``` patterns
  - Improved regex patterns for better code block detection
  - Better handling of nested JSON structures in AI responses

---

## [2.17.3] - 2025-11-27

### Added
- **AI Chat Module Enhancements**: Enhanced AI chat interface with new components and improved formatting
  - New `AiChatMessage` component for displaying chat messages with proper formatting
  - New `AiChatMessageDebugPrompt` component for debugging full prompts sent to AI
  - New `AiChatTemplateMsgButton` component for quick template message buttons
  - New formatting utilities: `useFormattedItemPrice` and `useFormattedItemWeight` for consistent display
  - New `CurrencySelect` and `WeightUnitSelect` components for better form UX
  - New `ImageProcessingModeRadioGroup` component for user preferences
  - Comprehensive i18n structure for AI-related translations (`src/modules/ai/i18n/index.ts`)
  - New `weightUnits.ts` utility for weight unit management

### Changed
- **AI Chat API Schema**: Synchronized frontend-backend API schema for AI chat
  - Changed `IAiChatRequest.prompt` to `.message` to match backend schema
  - Updated `IAiChatResponse` to match backend `AiChatResponse` structure
  - Replaced `structured_data` with `structured_output` (backend naming)
  - Updated token fields: `prompt/completion/total` (backend format)
  - Simplified context to `Record<string, unknown>` for flexibility
- **AI Chat Components**: Improved chat interface and user experience
  - Enhanced `AiChatDialog` with descriptions and improved accessibility
  - Updated `AiChatWindow` to send correct request format
  - Refactored components to utilize new formatting functions
- **Gear Components**: Improved form components and display consistency
  - Updated `ItemFormFields` and `ContainerFormFields` to use new select components
  - Enhanced price and weight display across all pages using new formatting utilities
  - Improved `GearPreferencesCard` with better structure
- **Backend AI Service**: Enhanced chat service with improved system prompt and model configuration
- **2FA Module**: Added preferred 2FA method to user settings (database migration)

### Fixed
- **AI Chat API Synchronization**: Fixed 422 validation error when sending chat requests
  - Frontend now correctly matches backend API schema
  - Proper field mapping between frontend and backend
- **Linting**: Fixed unused variable in `AiChatWindow.vue` (`selectedFields`)

---

## [2.17.2] - 2025-11-27

### Fixed
- **Item Edit Currency Field**: Fixed currency field not being loaded when editing items
  - Currency value now properly initialized in `ItemFormPage.vue` from existing item data
  - Currency field now correctly populated in both `getInitialValues()` and `loadItem()` functions
  - Previously currency was lost when editing items, now it's preserved correctly

### Changed
- **Item Detail URL Display**: Improved URL link display in item detail page
  - Desktop view: Shows domain name (e.g., "example.com") instead of generic "Open Link" text
  - Mobile view: Shows "Open Link" text for better touch target clarity
  - Responsive design: Uses `sm:hidden` and `hidden sm:inline` classes for appropriate display per screen size
  - Better user experience: Users can see the destination domain before clicking on desktop

---

## [2.17.1] - 2025-11-26

### Fixed
- **Share Token Deletion**: Fixed critical bug where share tokens were not actually deleted from database
  - Added missing `await` to `self.db.delete()` call in `backend/app/modules/gear/repository.py:576`
  - SQLAlchemy 2.0+ async sessions require `await` on delete operations
  - Previous behavior: API returned 204 No Content but token remained in database
  - Tokens now properly delete and disappear from the table immediately

---

## [2.17.0] - 2025-11-26

### Added
- **DataTable Loading State**: Comprehensive loading state support for DataTable component
  - New `loading` prop for DataTable component
  - `TableLoadingSkeleton` component with animated spinner
  - Customizable loading state via `#loading` slot
  - Loading state takes priority over empty state display
  - Applied to all admin pages (Containers, Users, Items)
  - Improved user feedback during data fetching operations

- **Translations**: Added `create` translation to common translations
  - Polish: `common.create: 'Utwórz'`
  - English: `common.create: 'Create'`

- **ROADMAP**: Added Container View Statistics feature to roadmap
  - View count tracking (total and unique visitors)
  - Dashboard for container owners with analytics
  - Privacy-first design (stats visible only to owner)
  - Planned for future implementation

### Changed
- **Share Token Management UI**: Improved responsive design for header
  - Header buttons stack vertically on mobile, horizontal on desktop
  - Equal-width buttons on mobile for better touch targets
  - Better spacing and layout on small screens
  - Empty state with full-width button on mobile

### Fixed
- **Share Token Page**: Removed complex table RWD that degraded mobile experience
- **Translation**: Fixed missing Polish translation for create button

---

## [2.16.1] - 2025-11-26

### Fixed
- **Admin Repository SQL Error**: Fixed PostgreSQL GROUP BY error in `get_all_containers` query
  - Changed `joinedload(GearContainerDB.user)` to `selectinload(GearContainerDB.user)` in `backend/app/modules/admin/repository.py:88`
  - `joinedload` was adding user table columns to SELECT list without including them in GROUP BY clause
  - `selectinload` issues a separate query for the relationship, avoiding GROUP BY conflicts
  - Error: `column "users_1.id" must appear in the GROUP BY clause or be used in an aggregate function`

---

## [2.16.0] - 2025-01-28

### Added
- **Item Linking**: Link items across containers with automatic change propagation
  - Items can be linked when adding from catalog (autocomplete selection)
  - Changes to one linked item automatically propagate to all linked instances
  - Visual indication of linked items (violet ring + chain icon in table)
  - Backend automatically handles propagation for API mode
  - Frontend handles propagation for localStorage mode

### Changed
- **Item Update Logic**: Enhanced `useGear.updateItem` to support linked items
  - Single API call for backend (automatic propagation)
  - Multiple updates for localStorage (manual propagation)
  - Master item detection based on `linkedItemId` or `id`

---

## [2.15.0] - 2025-11-26

### Added
- **PWA Configuration**: Comprehensive Progressive Web App configuration
  - Dedicated `pwa.config.ts` file for centralized PWA settings
  - Manifest properties: app name, description, theme color, icons
  - Runtime caching strategies for Google Fonts and API requests
  - Enhanced build process for PWA capabilities

- **Image Management Enhancements**:
  - **Upload Images from URL**: New functionality to add images from external URLs
    - `ItemImageGalleryUrlForm` component for URL-based image uploads
    - URL validation and error handling
    - Support for fetching and processing images from external sources
    - Alternative to file upload, especially useful for admins
  - **Primary Image in Table Rows**: Optional display of primary image thumbnails in items table
    - `ItemsTableImageCell` component for displaying image thumbnails
    - Primary image shown in table rows for quick visual identification
    - Lazy loading for performance optimization
    - Clickable thumbnails navigate to item details
    - Available in both `ItemsTable` and `AllItemsPage`
  - **Image Preview Overlay**: Full-screen image preview functionality
    - `ItemImagePreviewOverlay` component with overlay display
    - `ItemImagePreviewOverlayButton` for triggering preview
    - Enhanced image viewing experience in gallery

- **Backend Image Management API**:
  - Enhanced image upload service with URL support
  - New API endpoints and schemas for URL-based image operations
  - Improved image deletion, reordering, and primary image setting methods

### Changed
- **PWA Configuration**: Refactored PWA settings from `vite.config.ts` to dedicated `pwa.config.ts` for better maintainability
- **Image Gallery**: Enhanced `ItemImageGallery` component with URL upload form integration
- **Items Table**: Added optional image column support in `ItemsTable` and `AllItemsPage`
- **i18n Translations**: Added new translations for image-related messages and tooltips

---

## [2.14.0] - 2025-11-26

### Added
- **UUID Import/Export Update Workflow**: UUID-based update flow for containers and items in markdown import/export
  - Export can include stable UUID identifiers in the format `[uuid:xxx]` (optional, via `showUuid`)
  - Import parses UUIDs from markdown and uses them to identify existing containers/items
  - When UUID exists in the system, import updates the existing container/item instead of creating a duplicate
  - When UUID does not exist, import creates a new container/item reusing the UUID from export (keeps references stable)
  - Import dialog now exposes an explicit option: **“Aktualizuj istniejące (po UUID)” vs “Twórz nowe”**
  - UUID support is wired through frontend DTOs (`ICreateContainerDto`, `ICreateItemDto`), local services, API services, and backend schemas/repository

- **Batch Sorting with Confirmation Alert (ItemsTable)**: Batch-based item ordering with explicit save in Container Detail page
  - Reordering items via column sorting or Up/Down buttons no longer saves immediately
  - New `SortConfirmationAlert` is shown whenever there are pending sorting changes
  - **Save** button persists the new order using `batchUpdateOrder` for both backend API and localStorage
  - **Cancel** button clears pending changes and restores original order (reloads container from API when backend is enabled)
  - Works consistently for both inline sorting and manual Up/Down moves

### Changed
- **Markdown Import Containers**: `ICreateContainerDto` now supports `currency` to keep container price data consistent with items
- **Gear Services**: Updated gear container/item API and local services to:
  - Accept optional UUID when creating containers/items
  - Use `batchUpdateOrder` as the single path for saving reordered items, both for backend and localStorage

---

## [2.13.0] - 2025-01-27

### Added
- **CSV Export Functionality** (FEATURE-021): Complete CSV export feature for containers
  - Export dialog with column selection (Basic and Additional columns)
  - Support for comma and semicolon separators (auto-detected based on locale)
  - UTF-8 with BOM encoding option for Excel compatibility (enabled by default)
  - Export of nested containers with container identification columns
  - Export single container from ContainerHeader menu
  - Export all containers from ContainersListPage (button and dropdown menu)
  - Comprehensive column support: name, category, quantity, weight, weight unit, price, currency, brand, color, status, priority, URL, notes, container name, container type
  - Default selection: only basic columns (name, category, quantity, weight, weight unit, status, priority)
  - Proper CSV escaping according to RFC 4180
  - File naming: `gear-export-[container-name]-[date].csv` for single container, `gear-export-all-[date].csv` for all containers

### Changed
- Updated cursor rules to clarify Checkbox component usage (`model-value` / `v-model` instead of `checked`)
- Export menu item label changed from "Export Data" to "Export to JSON" for clarity

---

## [2.12.0] - 2025-11-25

### Added
- **S3 Storage Support**: Scaleway Object Storage integration for backend
  - Storage CLI command for testing S3 connectivity (`storage info`, `storage test`)
  - S3 environment variables in production docker-compose.yml
  - Support for Scaleway Object Storage (Warsaw region: pl-waw)
  - Automatic storage adapter switching between local and S3 based on configuration

### Changed
- Image uploads now use configured storage backend (local or S3)
- Backend storage adapter automatically selects S3 when `STORAGE_TYPE=s3` is set

---

## [2.11.1] - 2025-01-24

### Fixed
- **Duplicate Containers/Items Bug**: Fixed critical bug causing duplicate containers and items when using "Generate Sample Set" feature
  - Removed redundant localStorage backup calls in `gearContainerService` and `gearItemService`
  - Store already automatically saves to localStorage via `saveToStorage()` method
  - Local service methods were creating new objects with new IDs, causing duplicates
  - Affected operations: `createContainer`, `updateContainer`, `createItem`, `updateItem`, `batchUpdateOrder`
  - Now containers and items are created only once (via API) and properly synced to store/localStorage

### Technical Details
- Removed unnecessary `gearContainerLocalService.createContainer()` backup call
- Removed unnecessary `gearContainerLocalService.updateContainer()` backup call
- Removed unnecessary `gearItemLocalService.createItem()` backup call
- Removed unnecessary `gearItemLocalService.updateItem()` backup call
- Removed unnecessary `gearItemLocalService.batchUpdateOrder()` backup call
- Store's `addContainer()` and `updateContainer()` methods already handle localStorage persistence automatically

---

## [2.11.0] - 2025-01-24

### Added
- **Item Image Gallery Upload (FEATURE-017)**: Complete image upload system for gear items
  - **Admin-Only Upload**: Only users with admin privileges can upload images
  - **Multi-Image Gallery**: Support for up to 10 images per item with gallery view
  - **Drag-and-Drop Upload**: Modern drag-and-drop interface using VueUse
  - **Image Management**:
    - Primary image selection (first image auto-set as primary)
    - Drag-and-drop reordering of images
    - Image deletion with confirmation
    - Visual feedback during drag operations
  - **Image Processing**:
    - Automatic resize to max 1920x1920px (preserves aspect ratio)
    - JPEG compression (quality 85%)
    - RGBA to RGB conversion for JPEG (white background)
    - Optional WebP conversion support
  - **Storage Adapter Pattern**: Pluggable storage backends
    - Local filesystem storage (development)
    - S3-compatible storage (production ready)
    - Factory pattern for dynamic adapter selection
  - **Validation & Security**:
    - File size limits (10 MB default, configurable)
    - MIME type validation (JPG, PNG, WebP, GIF)
    - Double MIME detection (content-type header + magic numbers/Pillow)
    - Transaction safety with rollback on database failure
    - File deletion from storage if database insert fails
  - **Frontend Components**:
    - `ItemImageGallery.vue` - Main gallery component with upload, display, reorder, delete
    - `ItemImageCard.vue` - Individual image card with controls
    - `ItemImageCardControls.vue` - Image controls (primary, delete)
    - `ContainerItemImagesGallery.vue` - Gallery view for container items (shows primary images)
    - `FileDropZone.vue` - Reusable drag-and-drop file upload component
    - `ItemImageGalleryEmptyState.vue` - Empty state component
  - **Item Detail Page**: New dedicated page for viewing item details
    - Complete item information display
    - Integrated image gallery
    - Edit button navigation
    - Proper loading states and error handling
  - **Backend Services**:
    - `ImageUploadService` - Complete upload service with validation and processing
    - `ItemImageRepository` - Database repository for image operations
    - `ImageProcessor` - Async image processing with Pillow
    - `StorageAdapter` - Abstract storage interface
    - `LocalStorageAdapter` - Filesystem storage implementation
    - `S3StorageAdapter` - S3-compatible storage implementation
  - **API Endpoints** (admin-only):
    - `POST /api/gear/items/{item_id}/images` - Upload image
    - `GET /api/gear/items/{item_id}/images` - Get all images for item
    - `DELETE /api/gear/items/images/{image_id}` - Delete image
    - `PUT /api/gear/items/{item_id}/images/reorder` - Reorder images
    - `PUT /api/gear/items/{item_id}/images/{image_id}/primary` - Set primary image
  - **Database Schema**:
    - New `item_images` table with proper indexes
    - Foreign keys with CASCADE delete
    - Migration: `017_add_item_images_table.py`
  - **Container Image Display**: Option to show item images in container view
    - `showItemImages` field in container settings
    - Displays primary images for items in container
    - Limited to 12 items for performance

### Changed
- **ItemFormPage**: Fixed type-check error (`item` prop type: `IGearItem | null` → `IGearItem | undefined`)
- **ROADMAP**: Marked FEATURE-017 (Item Image Gallery Upload) as completed

### Technical Details
- **Backend**:
  - Storage adapter pattern for flexible storage backends
  - Async image processing with `asyncio.to_thread()` (non-blocking)
  - Proper error handling with HTTPException and detailed error messages
  - Transaction safety: rollback file upload if database insert fails
  - Configurable via environment variables (storage type, paths, limits)
- **Frontend**:
  - TypeScript types: `IItemImage`, `IImageOrderUpdate`
  - API service: `itemImageApiService` with all CRUD operations
  - Proper loading states, error handling, and user feedback
  - Responsive grid layout for image gallery
  - Admin-only access control (checks both `isAdmin` and container ownership)
- **Storage**:
  - Local storage: files served via FastAPI static files (`/uploads/...`)
  - Docker volume persistence for local storage
  - S3 support with configurable endpoint (compatible with S3-compatible services)
- **Dependencies**:
  - Backend: Pillow, python-magic, aiofiles, aioboto3
  - Frontend: No new dependencies (uses existing VueUse for drag-and-drop)
- **Documentation**:
  - `ITEM_IMAGE_GALLERY_INTEGRATION.md` - Integration guide
  - `ITEM_DETAIL_PAGE_IMPLEMENTATION.md` - Item detail page documentation
  - `CODE_REVIEW_v2.10.0.md` - Comprehensive code review
- All type checking and linting passes successfully

---

## [2.10.0] - 2025-01-24

### Added
- **Admin Badge Display**: Admin users now have a visual badge with Shield icon displayed on profile pages
- **Admin Avatar Ring**: Admin users' avatars display a primary-colored ring with offset for easy identification
- **isAdmin Field in Auth Responses**: Login and authentication responses now include isAdmin flag for frontend use

### Changed
- **Backend Refactoring - Admin Module**: Complete architectural refactoring following Repository→Service→Router pattern
  - Created `AdminRepository` class for database queries (211 lines)
  - Created `AdminService` class for business logic (331 lines)
  - Created proper Pydantic response schemas (`AdminUserResponse`, `AdminContainerResponse`, `AdminItemResponse`)
  - Refactored `admin/router.py` from 406 to 224 lines (45% reduction)
  - Eliminated code duplication (consolidated user serialization)
  - Improved type safety and maintainability
- **Public Profile API**: Now includes `isAdmin` field in public user profile responses
- **User Type Definitions**: Added optional `isAdmin` field to `IUser` interface

### Technical Details
- Frontend: Added Shield icon and Badge components to profile pages
- Frontend: Added admin ring styling to UserNav avatar component
- Backend: Admin module now follows same clean architecture as Gear module
- Backend: All admin endpoints use proper dependency injection and type-safe responses
- Translations: Added admin badge translations (EN: "Admin", PL: "Administrator")
- All type checking and linting passes successfully

---

## [2.9.0] - 2025-01-21

### Added
- **Item Ordering (FEATURE-018)**: Manual item ordering within containers
  - Added `order` field to items for custom sorting
  - Up/Down buttons in items table to change item order
  - Items automatically sorted by order (nulls last)
  - New items automatically get `order = max(order) + 1`
  - Order persisted in localStorage and database
  - Backend support: `order` field in database schema, API, and repository
  - Database migration: `015_add_order_field.py` for adding order column
  - Toast success notification only shown when using API/backend (not for localStorage)
  - Translations for order feature (PL/EN)

### Changed
- **ItemsTable**: Default sorting now uses `order` field instead of creation date
- **Backend Repository**: `get_items()` now sorts by `order` (ascending, nulls last), then by `created_at`
- **Backend Create Item**: Automatically assigns order if not provided (max + 1)
- **ROADMAP**: Marked FEATURE-018 (Item Ordering) as completed

### Technical Details
- Frontend: `order` field added to `IGearItem`, `ICreateItemDto`, `IUpdateItemDto`
- Backend: `order` field added to `GearItemDB` model, `ItemCreate`/`ItemUpdate` schemas
- Services: Both `gearItemLocalService` and `gearItemApiService` handle order field
- UI: Up/Down buttons disabled at top/bottom of list for better UX

---

## [2.8.0] - 2025-01-21

### Added
- **Extended Charts (FEATURE-019)**: Enhanced category pie chart with additional visualization modes
  - **Price Mode**: Pie chart showing cost distribution by category
    - Sums prices per category (price × quantity)
    - Percentage distribution of total cost
    - Displays only items with price data
    - Currency formatting using `formatCurrency()` utility
  - **Priority Mode**: Pie chart showing item distribution by priority level
    - Counts items per priority (critical, high, medium, low)
    - Percentage distribution of total items
    - Color-coded segments: Critical (red), High (orange), Medium (yellow), Low (green)
  - **Chart Mode Selector**: Extended with 4 options (Weight, Quantity, Price, Priority)
  - **New Utilities**:
    - `calculatePriceByCategory()` - Calculates price distribution by category
    - `calculateItemsByPriority()` - Calculates item distribution by priority
  - **i18n Translations**: Added `gear.chart.byPrice` and `gear.chart.byPriority` (EN/PL)

### Changed
- **CategoryPieChart**: Extended to support 4 chart modes (weight, quantity, price, priority)
- **CategoryPieChartLegend**: Updated to display data for all chart modes with proper formatting
- **usePieChartGeometry**: Enhanced to handle price and priority modes
- **Chart Types**: Updated `CategoryData` and `ChartDataPoint` interfaces to support optional `price` and `priority` fields
- **ROADMAP**: Marked currency support (FEATURE-017) and extended charts (FEATURE-019) as completed

---

## [2.7.0] - 2025-01-21

### Added
- **Public Item Detail Page**: Added read-only public item detail page (`PublicItemDetailPage.vue`)
  - Public route `/gear/public/:containerId/items/:itemId` for viewing public items
  - Displays all item information including category, priority, status, weight, price, and extended fields
  - Visual indicators for expired and expiring items
  - Empty state placeholder when no additional details are available
- **ItemsTable Public Mode**: Enhanced `ItemsTable` component with public mode support
  - New `publicMode` prop to enable public viewing mode
  - New `containerId` prop for navigation in public mode
  - Clicking items in public mode navigates to public item detail page instead of edit page
  - Actions column hidden in public mode (read-only)
  - Navigation to nested containers uses public routes in public mode
- **i18n Translations**: Added translations for public item detail page (EN/PL)
  - `gear.item.details` - Details section title
  - `gear.item.openLink` - Open link button text
  - `gear.item.noDetails` - Empty state message

### Changed
- **PublicContainerDetailPage**: Updated to pass `publicMode` and `containerId` props to `ItemsTable`
- **Routes**: Added `PublicItemDetail` route and helper function `PublicItemDetailById()`

---

## [2.6.0] - 2025-01-21

### Added
- **Currency Support (FEATURE-017)**: Comprehensive currency support throughout the application
  - Default currency setting in user preferences with auto-detection based on browser locale
  - Currency selector in item and container forms (8 supported currencies: PLN, EUR, USD, GBP, JPY, CHF, CAD, AUD)
  - Proper currency formatting using `Intl.NumberFormat` for locale-aware display
  - Currency display in tables, statistics, and container details
  - Multi-currency support in statistics (totals grouped by currency)
  - Helper function `getCurrency()` for consistent currency handling
  - Currency field added to `IGearItem` and `IGearContainer` types
  - Currency validation in form schemas
- **New Utilities**:
  - `currencyFormatter.ts` - Currency formatting utilities with `formatCurrency()`, `getCurrency()`, and `detectDefaultCurrency()`
  - Enhanced `containerCalculations.ts` with `calculateTotalPriceSync()` for multi-currency price calculations
- **i18n Translations**: Added currency-related translations (EN/PL) and date format `short` for both locales
- **Settings**: Added default currency selector to `GearPreferencesCard.vue`

### Changed
- **Forms**: Updated `ItemFormFields.vue` and `ContainerFormFields.vue` to include currency selection next to price input
- **Tables**: Added price column to `ItemsTable.vue` with formatted currency display
- **Statistics**: Enhanced `ContainerHeader.vue` to show total prices grouped by currency
- **Shopping Planning**: Updated `ShoppingPlanningPage.vue` to use currency formatting throughout
- **Settings**: Extended `IGearSettings` interface with `defaultCurrency` field

---

## [2.5.1] - 2025-11-24

### Added
- **Date Handling**: Added `date-fns` library for better date/time manipulation
- **New Components**:
  - `ContainerCardBadges` - Reusable component for displaying container badges
  - `ContainerCardCreatedDate` - Component showing creation date with time-ago format
  - `ContainerCardStats` - Component for displaying container statistics
  - `PublicContainerCard` - Card component for public container browser
  - `PublicContainerAuthorBadge` - Badge showing container author information
  - `LandingPageContainerCard` - Card component for landing page statistics
- **Composables**: New `useContainerTypeLabel` composable for centralized container type label management
- **Services**: Added `publicContainersService` for public container operations
- **Utils**: Added `dateTime.ts` and `smallDateTime.ts` utility functions

### Changed
- **Component Refactoring**: Refactored `ContainerCard` to use smaller, modular sub-components for better maintainability
- **Component Enhancements**:
  - Enhanced `Card` component with `as` prop for polymorphic rendering
  - Updated `ContainerFormFields` to use `getContainerTypeLabel` from composable
  - Refactored `ContainerHeader` to use `useContainerTypeLabel` composable
  - Updated `ExportToPromptDialog` to use `getContainerTypeLabel` function
- **Pages**:
  - Renamed `HomePage.vue` to `DashboardPage.vue` for clarity
  - Enhanced `LandingPage` with improved statistics display
  - Improved `PublicContainersBrowserPage` with better responsive design
  - Enhanced `PublicContainerDetailPage` with author information
  - Updated `PublicUserProfilePage` to show user's public containers
  - Refactored `ShoppingPlanningPage` UI improvements
- **Routing**: Added new routes for public user profiles and container details
- **Internationalization**: Updated Polish translations for better consistency (auth, gear, user modules)
- **Filters**: Enhanced `ContainersFilters` component with better UX

### Fixed
- Fixed incorrect display of custom container types in `ContainerFormFields` dropdown
- Fixed type label passing in export functionality (was passing computed value instead of function)

---

## [2.5.0] - 2025-11-24

### Release: Testing Infrastructure, UI/UX Enhancements & Deployment Automation

This release focuses on improving code quality with comprehensive unit tests, enhancing user experience with app versioning and authentication improvements, and streamlining deployment workflows.

### Added
- **Testing Infrastructure**:
  - Added 1348 lines of unit tests for utility functions (#114315c)
  - Tests for: `cn` function, `valueUpdater`, category recognition, container calculations, weight formatting, item retrieval, parameter recognition, suggested values, and type guards
  - Backend unit tests for auth service and utilities (#cc93948)
  - Enhanced test environment setup with proper database engine configuration

- **App Version & Build Information**:
  - App version and build date now displayed in footer (#35, #8b2f483)
  - Created `useAppVersion` composable for centralized version management (#78f52b6)
  - Dynamic company information from environment variables
  - Build date automatically injected via Vite during build process

- **Authentication & User Experience**:
  - New `AuthenticationRequiredAlert` component for profile pages (#ab3f991)
  - `DropdownMenuItemLink` component for better navigation in UserNav
  - OAuth button added to RegisterForm (#97caa9d)
  - Improved user authentication flow with conditional rendering

- **Deployment Automation**:
  - GitHub Actions workflow for automated deployment (#ce6d3cc)
  - Backend restart and migration script (`backend_restart_migrate.sh`) (#48fcb62)
  - Frontend build and deploy script (`frontend_build_deploy.sh`)
  - Comprehensive deployment documentation in `DEPLOYMENT.md`

- **Developer Experience**:
  - VSCode settings and Pyright configuration for backend development (#f9c3452)
  - Example environment variables for backend configuration (#3126fe6)
  - `pnpm-workspace.yaml` for monorepo support

- **UI Components**:
  - `GuestLayoutFooter` component for consistent footer across guest layouts (#78f52b6)

### Changed
- **Documentation Improvements**:
  - Added comprehensive `TODO_FEATURES.md` file consolidating features from both offline and online roadmaps (#b1792d3)
  - Updated `README.md` with link to TODO features list and completed features (#7bacf27)
  - Restructured roadmap: split into `ROADMAP_OFFLINE.md` and `ROADMAP_ONLINE.md`
  - Moved analysis docs to `docs/analysis/` directory
  - Moved archived docs to `docs/archive/` directory
  - Updated cursor rules with Question vs. Action Protocol and TailwindCSS best practices

- **User Authentication Refactoring**:
  - Refactored user profile handling with consistent `avatarUrl` usage (#ab3f991)
  - UserNav now conditionally shows login/register options based on auth status
  - Improved profile page with authentication-aware components
  - Enhanced route handling with constants for user profile paths

- **Footer Component Refactoring**:
  - Replaced hardcoded footer content with reusable `GuestLayoutFooter` component
  - Centralized footer logic in `AppFooter.vue` with dynamic configuration
  - Consistent footer across `GuestLayoutCentered`, `GuestLayoutCenteredGlass`, and `GuestLayoutTwoColumns`

- **Configuration Updates**:
  - Updated `.env.example` to use array syntax for CORS settings (#6c716ac)
  - Enhanced `.gitignore` for better environment file handling
  - Removed draft deployment configurations for cleaner repo

- **Public Containers UI**:
  - Improved responsive design for public containers browser (#752e210)
  - Enhanced mobile layout for public container detail pages

- **Deployment Scripts**:
  - Refactored `deploy.sh` for better maintainability (#48fcb62)
  - Separated frontend build logic into dedicated script
  - Improved CI/CD environment variable handling

### Fixed
- **OAuth Internationalization**:
  - Fixed OAuth callback i18n interpolation syntax (#e0d2499)
  - Removed debug log from reCAPTCHA utility

- **Deployment**:
  - Fixed CI environment variable handling in deployment script
  - Removed pnpm version specification from deploy workflow (#36)
  - Updated deployment branch configuration

- **Code Quality**:
  - Automatic formatting with Black for Python backend code (#80a9012)
  - Fixed various TypeScript and ESLint issues

### Security
- Enhanced backend test coverage for authentication and authorization flows
- Improved environment variable handling and validation

### Development
- Backend restart and migration workflow streamlined
- Improved local development setup with proper configuration examples
- Better separation of concerns between frontend and backend deployment

---

## [2.4.0] - 2025-11-23

### Added
- **Shopping List Features**:
  - Shopping list persistence functionality (#24)
  - "Add All" functionality for shopping lists (#24)
  - Shopping planning page functionality (#21)
  - Enhanced shopping list functionality and item editing (#23)

- **Progressive Web App (PWA)**:
  - PWA support with Vue and Vite (#19)
  - Installable web application support
  - Offline capabilities

- **Internationalization**:
  - Email internationalization and translations (#15)

- **Documentation**:
  - AI plan documentation

### Changed
- **Data Structure**:
  - Unified brand, category, and type fields (#20)
  - Refactored to use 'value' instead of 'key' and 'label' for custom items
  - Simplified settings card components for brands, categories, and container types

- **OAuth Integration**:
  - Implemented internationalization for OAuth login
  - Improved OAuth callback page with better error handling

### Fixed
- Shopping list and item page issues (#22)
- Removed unnecessary v-if from create container button
- Improved OAuth error message display

---

## [2.3.0] - 2025-11-22

### Added
- **Testing Infrastructure**: Set up Vitest testing framework
  - Installed Vitest, @vitest/ui, and happy-dom
  - Created `vitest.config.ts` configuration
  - Added test scripts: `test`, `test:ui`, `test:run`, `test:coverage`
  - **57 unit tests** for markdown import service with 100% pass rate

- **Markdown Import Enhancements**:
  - **Container Descriptions**: Support for parsing container descriptions from markdown
    - Extracts text between container header and first item
    - Supports multi-line descriptions with empty lines
  - **Price Parsing**: Comprehensive price and currency support
    - PLN formats: `100PLN`, `10 PLN`, `10,00 PLN`, `1 000,00 PLN`, `10zł`
    - USD formats: `$50`, `50$`, `50 USD`
    - EUR formats: `€100`, `100€`, `100 EUR`
    - GBP formats: `£75`, `75£`, `75 GBP`
  - Added `price` and `currency` fields to `ICreateItemDto` type
  - Added `description`, `price`, and `currency` fields to `IMarkdownImportResult`

- **Error Handling**:
  - Global chunk loading error handler for post-deployment errors
  - User-friendly dialog with i18n support (PL/EN)
  - Automatic detection of ChunkLoadError and related failures
  - Graceful page reload option

- **404 Page**:
  - New NotFoundPage component with proper UI
  - Wildcard route `/:pathMatch(.*)*` for catching all unmatched routes
  - Helpful navigation links to Containers, Dashboard, and Settings
  - Full i18n support (PL/EN)

- **Translations**:
  - Added `errors.chunkLoadError` translations (PL/EN)
  - Added `notFound` page translations (PL/EN)

### Fixed
- **Profile Page Mobile**: Fixed email overflow on mobile devices
  - Added `break-all` class to email display
  - Added `flex-shrink-0` to Mail icon to prevent crushing

- **Markdown Export**: Fixed description format in newline mode
  - Descriptions now appear alone on second line
  - Metadata (UUID, quantity, brand, weight) stays on first line
  - No more mixing of description with other fields

### Changed
- Updated ROADMAP.md with completed features and new planned tasks
- Enhanced markdown import parser with better field extraction
- Improved type safety with currency field additions

---

## [2.2.1] - 2025-11-22

### Fixed
- **reCAPTCHA Configuration**: Fixed environment variable naming issues
  - Changed `GOOGLE_RECAPTCHA_SITE_KEY` → `RECAPTCHA_SITE_KEY` in backend
  - Changed `GOOGLE_RECAPTCHA_SECRET_KEY` → `RECAPTCHA_SECRET_KEY` in backend
  - Enabled reCAPTCHA in both frontend and backend configurations
  - Added reCAPTCHA variables to docker-compose.yml and docker-compose.dev.yml
  - Created diagnostic script `backend/scripts/check_env.py` for environment verification

- **reCAPTCHA Logging**: Enhanced debugging capabilities
  - Added detailed logging in `backend/app/core/recaptcha.py`
  - Added logging in `backend/app/modules/auth/decorators.py`
  - Logs now show configuration, request/response details, and error codes

- **OAuth Authentication**: Fixed critical bugs preventing OAuth login
  - Fixed `login_with_oauth` to support both camelCase and snake_case field names
  - Fixed missing `logger` import in `backend/app/modules/auth/router.py`
  - Fixed incorrect settings path: `settings.jwt` → `settings.security`
  - Added detailed OAuth callback logging for debugging

- **Frontend OAuth Error Handling**: Improved user experience
  - Replaced hardcoded paths with `AuthRoutePaths` variables in OAuthCallbackPage
  - Enhanced error message extraction from API responses
  - Increased error display timeout from 2s to 3s

### Security
- **reCAPTCHA v3**: Now fully operational with score-based bot detection (min score: 0.5)
- **OAuth**: Google OAuth authentication now functional end-to-end

---

## [2.2.0] - 2025-01-21

### Release: Security Enhancements - reCAPTCHA & OAuth Integration

This release introduces major security features including Google reCAPTCHA v3 protection and OAuth authentication infrastructure.

### Added
- **reCAPTCHA v3 Integration (Frontend)**: Invisible bot protection on all authentication forms
  - Auto-loads reCAPTCHA script on app startup
  - Integrated into LoginForm, RegisterForm, and ForgotPasswordPage
  - Sends reCAPTCHA tokens to backend for verification
  - Zero friction for legitimate users (invisible verification)
  - Added `useRecaptcha` composable and utility functions
  - Backend already supported reCAPTCHA, now enabled with frontend integration

- **OAuth Infrastructure (Backend - 90% Complete)**: Foundation for social login
  - Complete OAuth service with Google provider implementation (`app/core/oauth.py`)
  - OAuth configuration in settings (`OAuthSettings`)
  - Database migration for OAuth fields (provider, provider_id, avatar_url)
  - Repository methods: `create_oauth_user()`, `get_user_by_oauth_provider()`
  - OAuth schemas: `OAuthAuthUrlRequest/Response`, `OAuthCallbackRequest/Response`
  - User model updated to support nullable passwords (OAuth users)
  - OAuth fields added to UserDB model

- **2FA Settings Visibility Fix**: Security settings card now visible on Settings page
  - Shows TOTP (Authenticator App) status
  - Shows WebAuthn/Passkeys status
  - Displays preferred 2FA method selector
  - Previously existed but wasn't shown due to missing import

- **Documentation**: Comprehensive implementation guides
  - `FEATURE-014-oauth-authentication.md` - Complete OAuth implementation plan
  - `FEATURE-015-recaptcha-integration.md` - Complete reCAPTCHA implementation plan
  - `IMPLEMENTATION_STATUS.md` - Current status and remaining work tracker
  - `IMPLEMENTATION_COMPLETE.md` - Detailed progress report

### Changed
- User model `hashedPassword` field is now nullable (supports OAuth users without passwords)
- Repository `_map_user` method updated to handle OAuth fields
- Auth types updated to include `recaptchaToken` field in login/register/forgot-password requests
- Config updated with reCAPTCHA and OAuth settings

### Security
- ✅ **reCAPTCHA Protection Active**: Login, register, and forgot-password endpoints now protected against bots
- ✅ **OAuth CSRF Protection**: State parameter generation for preventing CSRF attacks
- ✅ **Score-based Verification**: reCAPTCHA uses score threshold (0.5) to detect suspicious activity
- ✅ **Action Verification**: Backend verifies reCAPTCHA action matches expected endpoint

### Technical Details

**Environment Variables**:
- Backend: `RECAPTCHA_ENABLED=true`, `GOOGLE_RECAPTCHA_SITE_KEY`, `GOOGLE_RECAPTCHA_SECRET_KEY`
- Frontend: `VITE_GOOGLE_RECAPTCHA_SITE_KEY`, `VITE_GOOGLE_OAUTH_CLIENT_ID`
- Backend OAuth: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`

**Database Changes**:
- New migration: `011_add_oauth_fields.py`
- Added columns: `oauth_provider`, `oauth_provider_id`, `avatar_url`
- Made `hashed_password` nullable for OAuth users
- Index created on `(oauth_provider, oauth_provider_id)` for efficient lookups

**Remaining Work** (OAuth Frontend - ~6-8 hours):
- OAuth login/callback composable (`useOAuth`)
- OAuth button component
- OAuth callback page
- Integration into login/register pages
- OAuth endpoints in auth router (backend)
- OAuth service method in auth service (backend)

---

## [2.1.1] - 2025-01-27

### Added
- **Landing Page Local Data Detection**: Landing page now detects when user is not logged in but has containers stored in localStorage
  - Shows container summary statistics (containers count, items count, ready containers count)
  - Displays login/register call-to-action buttons prominently
  - Encourages users to log in or register to synchronize their local data
  - Summary section only appears when local containers exist and user is not authenticated

### Changed
- Landing page now conditionally shows features section or local data summary based on authentication and localStorage state
- Improved user experience for users with local data who haven't logged in yet

---

## [2.1.0] - 2025-01-27

### Release: Hybrid Mode & Offline-First Architecture

This release introduces a hybrid mode that allows the application to work seamlessly both with and without user authentication. Users can now use the app immediately without creating an account, with all data stored locally. After logging in, the app automatically switches to API mode while maintaining localStorage as a backup.

**Key highlights:**
- **Hybrid Mode**: Automatic switching between localStorage (offline) and API (online) based on authentication status
- **Zero-Friction Onboarding**: Users can start using the app immediately without registration
- **Data Migration**: Optional migration dialog to transfer local data to API after first login
- **Offline-First**: All pages and features accessible without login
- **Smart Fallback**: Automatic fallback to localStorage on API errors
- **Settings Translations**: Fixed missing translations for settings page and delete account feature

**New Features:**
- **Hybrid Services**: All services (Gear, Settings, User) now support both localStorage and API modes
- **Data Migration Dialog**: User-friendly dialog to migrate local data to API after login
- **Landing Page Enhancement**: Added "Add Container" button for immediate access
- **Route Accessibility**: All gear pages accessible without authentication
- **Conditional Features**: Delete Account only visible when authenticated

**Technical improvements:**
- Extended `useBackend` composable with `isAuthenticated` and `shouldUseAPI` helpers
- Unified conditional logic across all services (Gear, Settings, User)
- Enhanced error handling with automatic localStorage fallback
- Improved service architecture with hybrid implementations
- Fixed translation structure for settings page sections

**Breaking Changes:**
- None - fully backward compatible

This release maintains full backward compatibility while adding powerful new capabilities for both offline and online usage.

---

## [2.0.0] - 2025-11-21

### Release: Backend Integration & Authentication

This is the second major release (2.0.0) of Gear Stack, introducing backend integration and full authentication system. The application now supports user accounts, authentication, and backend API integration while maintaining backward compatibility with local storage.

**Key highlights:**
- **Backend Integration**: Full API integration with backend services
- **Authentication Module**: Complete user authentication system with email verification
- **Two-Factor Authentication (2FA)**: Enhanced security with WebAuthn support
- **User Management**: User accounts, profiles, and session management
- **Logout Functionality**: Proper session cleanup and logout flow
- **Enhanced Services**: Refactored gear services with container/item API services
- **Improved Error Handling**: Enhanced Vite configuration and interceptor error handling
- **Routing Updates**: Updated routing and layout for landing and home pages
- **Container Data Handling**: Enhanced container data handling with missing fields support

**Technical improvements:**
- Service layer refactoring for better separation of concerns
- Enhanced API interceptors with improved error handling
- Updated application settings and user authentication flow
- Workflow permissions fixes for code scanning alerts

This release marks the transition from a pure local storage application to a full-stack application with backend support, while maintaining all existing features and data compatibility.

---

## [1.0.0] - 2025-11-21

### Release: Full local storage

This is the first major release (1.0.0) of Gear Stack, marking the completion of the full local storage implementation. All core features are now functional and working entirely with localStorage, without requiring a backend, database, or authentication.

**Key highlights:**
- Complete gear management system with containers and items
- Full import/export functionality (JSON and Markdown formats)
- Container nesting and relationships
- Extended fields (brand, color, price, URL, quality)
- Weight management with multiple unit support (g, kg, oz, lb)
- Category recognition and parameter recognition
- Container cloning and catalog-based item addition
- Comprehensive settings system (core and gear-specific)
- Full internationalization (PL/EN)
- Responsive design with mobile support

All features documented in the ROADMAP are now implemented and working with localStorage. Future versions may include backend integration for multi-device synchronization and collaboration features.

---

## [0.22.0] - 2025-01-21

### Added
- **Feature: Add Existing Items to Container** - Users can now add existing items from other containers to the current container using a catalog selector
  - New tabs in ItemFormPage: "New Item" and "From Catalog"
  - ItemCatalogSelector component with fuzzy search, category icons, and container badges
  - Item linking support with `linkedItemId` field (future-ready for backend integration)
  - Items already in current container are automatically excluded from catalog
  - Form resets when switching between tabs
  - Alphabetical sorting of catalog items
  - Translations for catalog mode (PL/EN)

### Changed
- Extended `IGearItem` interface with `linkedItemId?: TUUID` field for item linking
- Added `getAllItemsForCatalog()` and `getItemWithContainer()` methods to gear service
- Extended `getAllItems()` utility to support filtering by container ID

### Fixed
- Fixed TypeScript type errors in ItemCatalogSelector component

---

## [0.21.0] - 2025-01-21

### Added
- **Container Cloning Feature**:
  - Added "Duplicate Container" action in container dropdown menu
  - CloneContainerDialog with options:
    - Editable new container name (default: "[Copy] Original Name")
    - Checkbox: "Include nested containers"
    - Checkbox: "Include item prices"
  - Deep cloning with new UUIDs for all entities
  - Preserves all container metadata (type, color, brand, description, etc.)
  - Toast notification with success message
  - Translations for cloning feature (PL/EN)

- **TableEmptyDecorated Component**:
  - New reusable component for decorated empty states in tables
  - Supports custom icon, title, description
  - Optional action button support
  - Consistent styling across all empty states

- **HomePage Empty State Options**:
  - Added "Import from Markdown" option in empty state
  - Added "Generate Sample Set" option in empty state
  - Options displayed after "or" separator below main action

- **Query Parameter Support for Import**:
  - ContainersListPage now opens import dialog automatically when URL contains `?import=true`
  - Allows direct navigation to import from HomePage

### Changed
- **UI/UX Improvements**:
  - Improved empty states with decorated component (TableEmptyDecorated)
    - AllItemsPage, ItemsTable now use TableEmptyDecorated
    - DataTableEmpty refactored to use TableEmptyDecorated internally
    - Consistent styling with icon in circular background
  - Footer mobile layout improved (flex-col sm:flex-row with better gap spacing)
  - Color grid in ContainerFormPage now uses responsive grid (5 columns on mobile, 10 on desktop)
  - Horizontal scroll indicator added to DataTable (gradient hint on mobile)
  - Search placeholder in ContainersListPage changed from "Search items..." to "Search containers..."

- **Button Visibility Logic**:
  - Header buttons on ContainersListPage and HomePage now hidden when containers list is empty
  - Prevents duplicate "Create Container" buttons
  - Dropdown menu always visible on ContainersListPage (contains import option)

- **Accessibility**:
  - Added aria-labels to all icon-only buttons:
    - ContainerCardActions dropdown trigger
    - ContainerHeader actions (SparklesIcon, MoreVertical)
    - ContainersListPage actions (Sparkles)
    - ContainersListPageDropdown trigger
  - Added translations for "more actions" (PL/EN)

### Fixed
- **Critical Mobile UX Issues**:
  - Fixed color grid layout on mobile (ContainerFormPage) - now displays 5 columns instead of 10 in single row
  - Fixed footer mobile layout - better spacing and responsive columns
  - Fixed duplicate "Create Container" buttons on ContainersListPage and HomePage
  - Fixed placeholder text inconsistency ("Search items..." → "Search containers...")

- **Component Issues**:
  - Fixed TableEmptyDecorated component - proper icon component handling with computed
  - Fixed empty states across application - consistent styling and layout
  - Fixed horizontal scroll indicator positioning in DataTable

---

## [0.20.0] - 2025-01-20

### Added
- **maxWeight Feature** (Container Weight Limits):
  - Added `maxWeight` and `maxWeightUnit` fields to containers
  - Weight limit input in container form (Extended Fields section)
  - Automatic weight calculation including container's own weight
  - Visual indicators in ContainerHeader:
    - Warning badge when weight exceeds 90% of limit (orange)
    - Exceeded badge when weight exceeds 100% (red)
    - Color-coded weight display (green/yellow/orange/red)
    - Progress bar showing weight usage percentage
  - Stats card displays "currentWeight / maxWeight" with visual progress bar
  - Weight limit calculations: `calculateWeightLimitPercentage()` and `isWeightLimitExceeded()`
  - Translations for maxWeight feature (PL/EN)

- **hideWhenNested Feature** (Smart Container Filtering):
  - Added `hideWhenNested` boolean field to containers
  - Checkbox in container form: "Hide on list when nested"
  - Automatic filtering in ContainersListPage - containers with `hideWhenNested=true` and `parentContainerId` are hidden from main list
  - Filter respects "Show only root containers" toggle
  - Helps organize nested containers without cluttering main list

- **Parameter Recognition in ContainerForm**:
  - Added "Recognize Parameters" button to container form
  - Recognizes brand from container name using fuzzy matching
  - Same functionality as ItemForm parameter recognition
  - Toast notifications for recognition results

- **UI/UX Improvements**:
  - Container name is now a clickable link in ItemFormPage (navigates to container details)
  - Added `flex-1` to form buttons for better mobile layout:
    - ItemFormFields: Cancel and Save buttons have equal width
    - ContainerHeader: Add Item button expands on mobile (`flex-1 sm:flex-none`)
  - Build script now includes deployment to `/var/www/gear-stack`

### Fixed
- Fixed brand and color displaying as lowercase in UI
  - Changed `getBrandOptions()` to use original case instead of `toLowerCase()`
  - Changed `getColorOptions()` to use original case instead of `toLowerCase()`
  - Brand badge now displays with normal-case (e.g., "Maxpedition" instead of "maxpedition")
- Fixed missing Checkbox import in ContainerFormFields
- Fixed weight calculation to include container's own weight in total

### Changed
- Updated ROADMAP with new features:
  - Added maxWeight feature documentation with use cases
  - Added container/item management features (cloning, existing items catalog)

---

## [0.19.0] - 2025-01-22

### Added
- **Parameter Recognition Feature**:
  - Added automatic recognition of brand and color from item names
  - New utility: `parameterRecognition.ts` with fuzzy matching against `SUGGESTED_BRANDS` and `SUGGESTED_COLORS`
  - "Recognize Parameters" action in item row actions menu
  - "Recognize Parameters" button in item form (fills brand/color fields)
  - Bulk action "Recognize Parameters for All Items" in container header dropdown menu
  - Recognition only fills empty fields (doesn't overwrite existing values)
  - Integration with existing suggested values dictionaries

### Changed
- **UI Improvements**:
  - Added visual separator in item form between fields and actions
  - Improved parameter recognition UX with proper toast notifications
  - Badge component now properly imported from registry in `PageListHeader.vue`

### Fixed
- Fixed TypeScript error in parameter recognition (handling undefined first word)
- Improved nested container display - nested containers now have bold font and clickable links to container detail page

---

## [0.18.0] - 2025-01-21

### Added
- **Modular Settings Architecture**:
  - Separated core settings (locale, dark mode, preferred weight unit) from gear-specific settings (custom categories, container types)
  - Created dedicated services: `CoreSettingsService` and `GearSettingsService`
  - Created separate Pinia stores: `useSettingsStore` and `useGearSettingsStore`
  - Created separate composables: `useSettings()` and `useGearSettings()`
  - Modular SettingsPage component with slot-based architecture for extensibility
  - Settings page now supports adding module-specific settings via slots

### Changed
- **Settings Architecture Refactoring**:
  - Split monolithic settings into core and gear modules
  - Core settings stored in `core-settings` localStorage key
  - Gear settings stored in `gear-settings` localStorage key
  - Automatic migration from old unified settings storage
  - Settings page structure: core settings in module, gear settings added via slot in `/src/pages/settings/`
  - All components updated to use appropriate settings composables

### Fixed
- Improved code organization and maintainability through modular architecture
- Better separation of concerns between core application settings and module-specific settings

---

## [0.17.0] - 2025-01-21

### Added
- **Imperial Weight Units Support**:
  - Added support for ounces (oz) and pounds (lb) as weight units
  - Users can now select oz and lb in item and container forms
  - Preferred weight unit setting now includes oz and lb options
  - All weight conversion functions updated to support imperial units
  - Conversion rates: 1 oz = 28.3495 g, 1 lb = 453.592 g

### Changed
- **Weight Unit Type**: Extended `TGearWeightUnit` type from `'g' | 'kg'` to `'g' | 'kg' | 'oz' | 'lb'`
- **Weight Conversion Functions**: Updated all conversion functions in `formatWeight.ts` to handle oz and lb
- **Form Validation**: Updated zod schemas to accept oz and lb as valid weight units
- **Markdown Import/Export**: Parser now recognizes and handles oz and lb in markdown format
- **Translations**: Added translations for oz and lb in both English and Polish

### Technical Details
- Added constants: `GRAMS_PER_OUNCE = 28.3495` and `GRAMS_PER_POUND = 453.592`
- Updated all weight-related interfaces and types to support imperial units
- All weight displays automatically convert to preferred unit (including oz/lb)

---

## [0.16.0] - 2025-01-21

### Added
- **Guidelines Dialog Component**:
  - Created dedicated `GuidelinesDialog` component for displaying formatting guidelines
  - Reusable component used in both Export and Import dialogs
  - Guidelines are now shown in a modal dialog instead of being copied directly
  - Users can view guidelines and copy them manually when needed

### Changed
- **Guidelines Display**:
  - Guidelines button now opens a dialog instead of copying to clipboard immediately
  - Guidelines template has been shortened while keeping essential information
  - Reduced number of examples to make guidelines more concise
  - Dialog is smaller than parent dialogs for better UX

- **Code Refactoring**:
  - Extracted Guidelines functionality into reusable component
  - Removed code duplication between Export and Import dialogs
  - Improved maintainability and consistency

---

## [0.15.0] - 2025-01-21

### Added
- **Preferred Weight Unit Setting**:
  - Users can now set their preferred weight unit (g or kg) in settings
  - All displayed weights across the application (tables, cards, headers) are automatically converted to the preferred unit
  - Forms can still use different units, but display is consistent
  - Setting is saved in localStorage and synchronized throughout the application
  - UI option added to Preferences settings page

- **Export Configuration Options**:
  - Added export options dialog with checkboxes to control markdown export content:
    - Show UUID in export
    - Show weight
    - Show color
    - Show brand
    - Show nested container reference (e.g., `[#bagaznik]`)
    - Show legend
  - All options are reactive - markdown updates in real-time when toggling options
  - Options are saved per export session

### Changed
- **Export Dialog**: Refactored to accept container/containers directly instead of pre-generated markdown, allowing real-time updates based on options
- **Weight Display**: All weight displays now use preferred unit from settings instead of automatic unit selection
- **Export Format**: Container ID references (`[#id]`) in headers and items are now controlled by export options

### Fixed
- Fixed legend duplication when exporting multiple containers - legend now appears only once at the end
- Fixed Checkbox component usage - now uses standard `v-model` instead of deprecated `v-model:checked` for regular refs

### Documentation
- Added `.cursorrules` file with Reka-ui Checkbox usage guidelines
- Updated `CLAUDE.md` with UI component notes about Checkbox usage
- Split ROADMAP into front-end only (`ROADMAP.md`) and backend-required (`ROADMAP_V2.md`) features

---

## [0.14.0] - 2025-01-20

### Added
- **Container Weight and URL Fields**:
  - Containers can now have weight and weight unit (g/kg) fields
  - Containers can now have URL field for linking to product pages or resources
  - Weight and URL fields added to container form
  - Container header displays weight and URL (if provided)
  - Weight displayed as badge in container header
  - URL displayed as clickable link in container header

- **Enhanced Export/Import**:
  - Export now includes container weight in format: `## Container Name [#id] (Type) <URL> - [weight]g`
  - Import parser now extracts container weight and URL from markdown headers
  - Guidelines template updated to document container weight and URL format

### Changed
- **Guidelines Template**: Moved from `ExportToPromptDialog.vue` to `markdownImportService.ts` for better code organization and reusability
- **Container Form**: Added weight, weightUnit, and URL input fields with proper validation

### Fixed
- Fixed TypeScript errors in markdown import service (containerUrl undefined check, container type definition)

---

## [0.13.1] - 2025-01-19

### Fixed
- **Nested Container Import**: Fixed issue where nested containers were not properly linked during markdown import
  - Import now correctly resolves `nestedContainerId` (slug) to actual container UUID
  - Two-phase import process: containers created first, then items with nested container relationships resolved
  - Nested containers (e.g., "Bagażnik" inside "Samochód Opel Zafira") now properly create parent-child relationships

---

## [0.13.0] - 2025-01-19

### Added
- **UUID Support for Import/Export Workflow**:
  - Export now includes `[uuid:xxx]` for both containers and items
  - Import parser extracts UUIDs from markdown format
  - Import mode selection: "Update Existing (by UUID)" vs "Create New"
  - Update workflow: items/containers with matching UUIDs are updated instead of created
  - Radio Group UI component for import mode selection
  - Success message differentiates between created and updated items

- **Enhanced Guidelines Template**:
  - Added UUID documentation to formatting guidelines
  - Updated examples to show UUID format in all samples
  - Documented update vs create workflow in guidelines

### Changed
- **Export Format**: All items and containers now include `[uuid:xxx]` after name/header
  - Container format: `## Name [#slug-id] [uuid:xxx] (Type)`
  - Item format: `- **Name** [uuid:xxx] x2 (Brand, Color) ...`
- **Import Dialog**: Shows mode selection only when UUIDs are detected in markdown
- **Import Logic**: Automatically detects UUIDs and enables update workflow

### Fixed
- Import now properly handles UUID-based updates for existing items and containers

---

## [0.12.0] - 2025-01-19

### Added
- **AI Prompt Export Enhancements**:
  - "Export to Prompt (AI)" button for all containers on ContainersListPage
  - "Guidelines" button in ExportToPromptDialog with comprehensive markdown formatting template
  - URL support in items (auto-detected from `http://`, `https://`, `www.`)
  - Nested container support with ID references using `[#slug-id]` format
  - Container IDs auto-generated as slugs from container names

- **Enhanced Markdown Import/Export**:
  - Unified format for import and export with flexible parsing
  - Parser recognizes URLs in angle brackets or plain format
  - Parser extracts `[#id]` from container headers and items
  - Support for nested container relationships via ID references
  - Weight is now optional (defaults to 100g if not specified)
  - Quantity can appear anywhere in the line (flexible regex matching)

- **Mobile/RWD Improvements**:
  - Click-based dropdown menu for UserNav (replaces hover-only)
  - Proper overflow handling for tables on mobile devices
  - Added `min-width: 640px` to tables with horizontal scroll
  - Responsive dialogs with `w-[95vw]` on mobile
  - Gap between search and column visibility in DataTable toolbar
  - Increased card padding on mobile (p-4 instead of p-2)

### Changed
- **Table Overflow Chain**: Fixed multi-layer overflow issues by adding `max-w-full overflow-hidden` to all page wrappers and DataTable root
- **AuthenticatedLayout**: Reduced padding on mobile (px-2) for more content space
- **Global CSS**: Added `overflow-x-hidden` to html, body, and #app to prevent horizontal scroll
- **UserNav**: Migrated from CSS hover to DropdownMenu component for better mobile support
- **Export Format**: All container headers now include `[#id]` for identification
- **Guidelines Template**: Updated with complete formatting rules, examples, and nested container documentation

### Fixed
- Tables exceeding viewport width on mobile devices
- Dropdown menus not opening on touch devices
- Multiple overflow wrappers causing scroll issues
- Missing gap between DataTable toolbar elements
- Dialog max-width issues on small screens

---

## [0.11.1] - 2025-01-19

### Added
- "Delete All Containers" button in containers page dropdown menu
- Confirmation dialog for deleting all containers with warning message
- `deleteAllContainers()` method in store, service, and composable
- Success toast notification after deleting all containers
- Translations for delete all feature (English and Polish)

---

## [0.11.0] - 2025-01-19

### Added
- Markdown import feature - import containers and items from markdown files
- `ImportMarkdownDialog` component with preview and error handling
- `markdownImportService` with intelligent parsing:
  - Parses `## Container` headers as containers
  - Parses `- Item` lines as items
  - Extracts brands from bold text (`**Brand**`)
  - Parses parameters from parentheses `(color, x5, 500g)`
  - Detects quantity from `x5` or `×5` patterns
  - Auto-categorizes items based on keywords
  - Matches colors and brands against predefined lists
  - Sets default weight (100g) for items without specified weight
- Import button in containers page dropdown menu
- Translations for import feature (English and Polish)
- `.claude/commands/release-version.md` - slash command for Claude Code

### Fixed
- Mobile responsiveness - tables now have horizontal scroll on mobile devices
- Mobile navigation - nav links now available in user dropdown menu on mobile
- All data table components updated with `overflow-x-auto` for better mobile UX

---

## [0.10.0] - 2025-01-20

### Added
- All Items page - view and manage all items from all containers in one unified table
- `AllItemsPage` component with full item listing across all containers
- `getAllItems` utility function to aggregate items from all containers
- `allItemsColumns` utility for All Items table column definitions
- Navigation link to All Items page in main navigation
- Container information column in All Items table (shows container name and color)
- Translations for All Items page (English and Polish)
- `ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY` for storing All Items table column visibility preferences

### Fixed
- Nested container weight now displays sum of all items in container instead of 0g
- Weight column alignment improved with right-aligned text in items table

---

## [0.9.0] - 2025-01-19

### Added
- Export to Prompt (AI) feature - export container data to markdown format for AI prompts
- `ExportToPromptDialog` component with markdown preview and copy functionality
- `exportToPrompt` utility function for generating markdown exports
- Support for nested containers in export with calculated total weight
- Compact export format: `x4 **Name** (Brand, Color) (Expiration: date, Status) - weight`
- AI legend explaining data structure for better AI understanding
- Translations for all export texts (title, description, legend)
- Export button in container header dropdown menu

### Changed
- Export format now shows quantity as `x4` before item name instead of `(4x)` in parentheses
- Container headers in export no longer include color suffix
- Nested containers now display calculated total weight instead of 0g
- Export format optimized for AI consumption with compact structure

### Fixed
- Removed empty line after main title in export
- Fixed nested container weight calculation in export

---

## [0.8.0] - 2025-01-19

### Added
- Extended fields for gear items and containers (brand, color, price, URL, quality)
- ComboBox component with creatable options for brand and color fields
- Suggested values for colors (Olive, Coyote, Black, Tan, etc.) and brands (Helicon, Maxpedition, Mil-Tec, etc.)
- Column visibility management in items table with localStorage persistence
- Color visualization in items table - colored circle with color name
- Command and Popover UI components (shadcn-vue based)
- `getColorHex()` utility function for mapping color names to hex values
- `ITEMS_TABLE_COLUMN_VISIBILITY_KEY` for storing column visibility preferences

### Changed
- Brand and Color fields now use ComboBox component instead of plain Input
- Items table columns (brand, color) are hidden by default
- All table columns can now be shown/hidden via column visibility dropdown
- Color column displays colored circle next to color name
- Improved DataTable column visibility synchronization with v-model
- Enhanced DataTableToolbar to properly handle column visibility toggling

### Fixed
- Column visibility state now properly syncs between table and parent component
- Fixed issue where columns could be shown but not hidden
- Improved ComboBox filtering and creatable option display

---

## [0.7.0] - 2025-11-19

### Added
- Category pie chart visualization on container detail page
- Interactive donut chart showing category distribution by weight or quantity
- Chart legend with category breakdown and totals
- Percentage labels on chart segments
- Chart tooltips with formatted values (weight in grams, quantity with units)
- `CategoryPieChart` component with mode switching (weight/quantity)
- `CategoryPieChartLabels` component for segment percentage labels
- `CategoryPieChartLegend` component for category breakdown
- Chart UI components (`ChartContainer`, `ChartTooltip`, `ChartTooltipContent`, `ChartLegendContent`)
- `usePieChartGeometry` composable for chart geometry calculations
- Footer component with links to privacy, cookies, contact pages
- Privacy policy page
- Cookies information page
- Contact page
- GitHub icon component
- Container filters component for filtering containers list
- Color dot visualization component for containers

### Changed
- Enhanced container detail page with category visualization
- Improved container header with chart toggle
- Updated container card layout
- Enhanced i18n translations for chart-related labels

### Fixed
- TypeScript type errors in pie chart geometry composable

---

## [0.6.0] - 2025-11-19

### Added
- Container nesting functionality (FEATURE-008)
- Support for nested containers - containers can be added as items to other containers
- `parentContainerId` field in container model for direct parent-child relationships
- `containerId` field in item model for referencing nested containers
- Circular reference validation to prevent infinite nesting loops
- Recursive weight calculation for nested containers
- `AddNestedContainerDialog` component for selecting containers to nest
- Expandable rows in items table - click to expand and view nested container contents
- `ItemsTableNestedContainerRow` component for displaying nested container items
- Container color visualization in expanded nested container rows
- Filter to show only root containers (containers without parents and not used as items)
- Enhanced container actions menu - different actions for nested containers vs regular items
- "View Container" action in dropdown menu for nested containers
- Visual indicators for nested containers (icon, badge, clickable name)
- Container nesting utilities (`containerNesting.ts`) with functions for:
  - Circular reference detection
  - Root container filtering
  - Nested container retrieval
  - Container path calculation

### Changed
- Separated "Add Item" and "Add Container" actions in container detail page
- Container list page now filters out containers used as items when "Show only root containers" is enabled
- Improved `getRootContainers()` to check both `parentContainerId` and usage as items
- Container color now affects the border color of expanded nested container rows
- Nested container names are now clickable and styled with container color

### Fixed
- Root container filter now correctly excludes containers used as items in other containers

---

## [0.5.0] - 2025-11-18

### Added
- Category recognition system for items based on name keywords
- Container type recognition system based on name keywords
- Keyword dictionaries supporting both Polish and English
- Automatic category/type detection on name field blur
- Recognition utilities (`categoryRecognition.ts`, `containerTypeRecognition.ts`)

### Changed
- Category/type recognition now triggers on blur event (when user leaves name field) instead of during typing
- Recognition logic prioritizes longer keywords to avoid false matches (e.g., "bagażnik" matches "bagażnik" not "bag")
- Improved UX - users can type full names without premature category changes

---

## [0.4.0] - 2025-11-18

### Added
- Container color coding system
- Color picker in container form with 10 predefined colors (default, blue, green, red, yellow, purple, orange, pink, teal, indigo)
- Color dot indicator in container cards
- Color utilities (`containerColors.ts`) with Tailwind CSS classes
- Translations for all color names (English and Polish)

### Changed
- Container model now includes optional `color` field
- Container cards display color dot for visual distinction
- Improved visual organization of containers with color coding

---

## [0.3.0] - 2025-11-18

### Added
- Default values utility for new items (`defaultValues.ts`)
- Automatic browser locale detection on first visit
- HTML lang attribute automatically set based on detected locale

### Changed
- New item forms now pre-filled with sensible defaults:
  - Weight: 0.1 kg (instead of 0)
  - Weight unit: kg (instead of g)
  - Status: owned (instead of toBuy)
  - Quantity: 1
  - Priority: medium
  - Category: other
- Browser language is automatically detected and saved to localStorage
- Improved form initialization using `toTypedSchema` for better type safety

### Fixed
- TypeScript type issues in form initialization

---

## [0.2.0] - 2025-11-18

### Added
- Category icons for all item categories (water, food, shelter, fire, first aid, tools, navigation, communication, clothing, hygiene, other)
- CategoryIcon component for displaying category icons
- Icons displayed in items table and category selectors
- Feature implementation plans structure in `docs/features/`
- Roadmap updates including brand color selection planning

### Changed
- Enhanced visual recognition of categories with dedicated icons
- Improved UX in category selection with icon indicators

---

## [0.1.0] - 2025-11-18

### Added
- Basic project structure
- Gear management module
- Container and item system
- CRUD operations for containers and items
- Data persistence in localStorage
- Import/Export data in JSON format

