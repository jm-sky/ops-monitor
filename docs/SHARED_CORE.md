# Shared Core — ops-monitor ↔ gear-stack

> Last reviewed: 2026-07-03
> Companion document: full findings live in
> [`gear-stack/docs/REVIEW_AND_REFACTOR_PLAN.md`](../../gear-stack/docs/REVIEW_AND_REFACTOR_PLAN.md).

## Why this document exists

`ops-monitor` and `gear-stack` were built from the **same core skeleton**. That
core was **copied**, not shared as a versioned dependency. As a result the two
repos share a large surface of near-identical infrastructure code — and that
surface has already **drifted**. A change (including a security fix) made in one
repo does **not** automatically reach the other.

This file inventories the shared areas, records the current drift, and defines the
rules for keeping them in sync until a proper shared package exists.

---

## 1. Shared areas

### Backend (`backend/app/core/*`, `backend/app/common/*`, `backend/cli/*`)
- **Config** — `app/core/config.py` (Pydantic-settings; nested App/Server/Database/
  Security/RateLimit/Recaptcha/OAuth/Email/Storage/Sentry/Redis/WebAuthn settings).
- **Security & middleware** — `security_headers.py`, `middleware.py`,
  `convert_empty_strings_middleware.py`, `limiter.py`, `recaptcha.py`, `oauth.py`.
- **Auth core** — `app/core/auth/*` (token blacklist, dependencies).
- **Email** — `app/core/email/*` (service, i18n, `file`/`smtp`/`audit`/`retry` adapters).
- **Storage** — `app/core/storage/*` (adapter + factory, `local`/`s3`, image processor).
- **Infra** — `redis.py`, `database.py`, `logging_config.py`, `static.py`,
  `migrations.py` (migration runner + `schema_migrations` table convention).
- **Common** — `app/common/*` (pagination, search, id/repository utils, email audit
  model + repository).
- **CLI** — `backend/cli/*` (Django-style `db` / `users` / `test` command groups).
- **Exceptions** — `app/exceptions/*` (handlers + custom exceptions).

### Frontend (`src/shared/*`, `src/components/ui/*`, tooling)
- **API layer** — `src/shared/services/*` (apiClient, auth & error interceptors, sentry).
- **Auth/token** — `src/modules/auth/store/useAuthStore.ts`, token-refresh store.
- **i18n infra** — `src/shared/i18n/*` + registry pattern.
- **UI kit** — `src/components/ui/*` (shadcn-vue component set).
- **Tooling** — `eslint.config.ts`, `pwa.config.ts`, `vite.config.ts`, `tsconfig*.json`,
  `playwright.config.ts`, `vitest.config.ts`, `env.d.ts`.

---

## 2. Current drift (as of 2026-07-03)

`diff -rq` between the two `backend/app/core` trees — these files **differ**:

| File | Nature of drift |
|------|-----------------|
| `config.py` | Brand defaults (APP name, WebAuthn RP), domain-specific settings |
| `security_headers.py` | CSP `connect-src` domain (`gear-stack.ovh` vs none) |
| `app_factory.py` | Sentry / router wiring |
| `auth/token_blacklist.py` | Behavioural drift (same size, different content) |
| `convert_empty_strings_middleware.py` | — |
| `email/service.py`, `email/audit_adapter.py` | — |
| `storage/local_adapter.py`, `storage/s3_adapter.py` | — |
| `migrations.py` | Migration runner drift |
| `static.py` | — |
| `common/pagination.py`, `common/repositories/email_audit_repository.py` | — |

Frontend shared drift includes: `shared/config/config.ts`,
`shared/composables/useAppInitialization.ts`, `useHandleError.ts`,
`shared/services/error.interceptor.ts`, `shared/utils/appInit.ts`, i18n locales,
and several `components/ui/*` widgets (each repo also has app-specific widgets:
gear-stack has `weight-input`/`shelf-life-input`; ops-monitor has `to-clipboard`).

**Legitimate drift** = branding, domains, app-specific settings/widgets → these
belong in **config/env**, not forked code.
**Accidental drift** = security/infra logic that diverged unintentionally → this is
the risk to close.

---

## 3. Findings that apply to BOTH repos

Because the core is shared, these `gear-stack` review findings are **also true for
ops-monitor** and should be fixed in both:

- 🔴 **Auth tokens in `localStorage`** (`useAuthStore.ts` stores access + refresh +
  2FA tokens) → XSS-exfiltration risk. Confirmed identical in ops-monitor.
- 🔴 **CSP allows `script-src 'unsafe-inline'`** in `security_headers.py` → weakens
  XSS defense. Confirmed identical in ops-monitor.
- 🟡 **Duplicated boolean parsing** and **duplicated JWT builders** in the config /
  auth core.
- 🟢 **No production-invariant startup assertion** (non-default secret, no `*` CORS,
  non-empty `ALLOWED_HOSTS`, `DEBUG=false`).

See the gear-stack plan for the full detail and fix approach.

---

## 4. Sync rules (until a shared package exists)

1. **Treat shared-core paths as shared.** Any change to a file listed in
   [section 1](#1-shared-areas) must be mirrored to the sibling repo in the same
   change set (or a linked follow-up), unless the change is purely brand/domain.
2. **Push brand/domain values into config/env**, never hard-code them in core files.
   This shrinks legitimate drift to zero and makes files byte-identical.
3. **Security fixes are non-negotiable to mirror.** CSP, auth, token handling,
   middleware, and secret validation must never diverge silently.
4. **Record intentional divergence here** with a one-line reason, so the next `diff`
   doesn't look alarming.

## 5. Target end state

Extract the stable core out of both apps into versioned internal dependencies:

- **Backend:** a `pip`-installable package (e.g. `app-core`) containing
  `app/core` + `app/common` + `cli`, consumed by both services.
- **Frontend:** a private npm package containing `src/shared` + `src/components/ui`.

Then "remember to copy the fix" becomes "bump the dependency version", and drift
becomes an explicit, reviewable choice instead of an accident.

See the phased plan (Phase 2) in
[`gear-stack/docs/REVIEW_AND_REFACTOR_PLAN.md`](../../gear-stack/docs/REVIEW_AND_REFACTOR_PLAN.md).
