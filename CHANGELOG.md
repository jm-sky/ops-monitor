# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- **Agent container hardened by default.** The host's whole `/var/run` is no longer mounted. That mount exposed `docker.sock`, `containerd.sock` and D-Bus, so a compromised agent meant root on the host. Instead, only `/run/ops-monitor-agent/reboot` (copies of `reboot-required*`) is mounted read-only at `/host/reboot`. The container runs as uid/gid 10001 with `read_only`, `tmpfs: /tmp`, `cap_drop: ALL` and `no-new-privileges`. This applies to `agent/docker-compose.yml` and the `agent` profile in the root compose files.
- Root compose files: removed `pid: 'host'` from the `agent` service.
- `scripts/agent-install.sh`: systemd unit sandboxed with `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `PrivateDevices`, an empty `CapabilityBoundingSet` and related settings.

### Added
- `scripts/agent-host-sync-install.sh` (`--uninstall`, `--dest`): installs a systemd `.path` (`PathChanged`) + `.timer` (5 min) + oneshot `.service` and a `tmpfiles.d` entry. Together they copy `/run/reboot-required*` with mtime preserved and remove copies when the originals disappear.
- **Agent 1.3.0**:
  - `AGENT_REBOOT_FLAG_DIR` env. Default chain is `/host/reboot`, then `/host/var/run`, then `/var/run`; an explicit value disables fallback.
  - Startup log of the reboot flag source, with a WARNING when detection is effectively disabled (sync not installed, no directory, container's own `/var/run`).
  - New `/system` fields `reboot_source` and `reboot_flags_synced_at`.
- Opt-out overrides: `agent/docker-compose.legacy-varrun.yml` (⚠️ dangerous) and `agent/docker-compose.legacy-root.yml`.
- Runbook: `docs/runbooks/agent-hardening-migration.md`.

### Fixed
- `scripts/agent-install.sh` now works when run from the repo root, as documented in the README.
- **Agent 1.2.0**: `GET /package-history?since=` parses `/var/log/apt/history.log` and rotated `history.log.N.gz` (also under `/host/var/log/apt`) into install/upgrade/remove/purge events; runs with `unattended-upgrade` or without `Requested-By` are flagged `automatic`. Results cached 5 min. New env: `AGENT_APT_LOG_TZ`, `AGENT_APT_LOG_DIR`; compose files mount `/var/log/apt`
- **Monitor**: `package_update_events` table (migration 069) filled by pulling agent history on the `pollingUpdates` interval and on manual poll, deduplicated on `(site_id, started_at)`
- **Monitor**: read-only service API keys (migration 070) — hashed at rest, scope `read:package-updates`, expiry/revocation; managed via `/api/monitor/api-keys` (admin) and `cli monitor api-keys create|list|revoke`
- **Monitor**: `GET /api/monitor/package-updates` (API key) with `from`, `to`, `site_id`, `include_automatic`, pagination, returning site name and host; `GET /api/monitor/sites/{id}/package-updates` for the UI
- **Frontend**: "Update history" card on the site detail page (events, duration, manual/automatic, packages)

### Notes
- Deploy: run `db migrate`, update agents to 1.2.0 and add the `/var/log/apt` mount; sites keep working with older agents (history simply stays empty)
- Agent 1.3.0 (Docker): run `sudo bash scripts/agent-host-sync-install.sh` on each host **before** redeploying the agent, otherwise reboot detection is disabled (logged as a WARNING). Follow `docs/runbooks/agent-hardening-migration.md`. No backend/frontend changes are needed; the new `/system` fields are stored in `raw_data` as-is
- Known issue (not fixed): in Docker the `apt list --upgradable` fallback (`no_cache=1`, or no `update-notifier` data) mixes host APT lists with the container's dpkg database and reports meaningless counts

---

## [1.0.0] - 2026-07-23

First stable production release of **Ops Monitor** — multi-site health, SSL, system metrics, and alert routing for the VPS fleet.

### Added
- Site monitoring dashboard with filters, dense/live mode, status badges, and route-synced filter state
- Health polling with component-level status (`/api/health/details` bearer-protected for peer checks)
- SSL certificate expiry monitoring, SSL check URL, and configurable polling intervals
- System metrics, reboot/upgrade remote actions, heartbeat, and snapshot history
- Alert channels with type/severity/site/tag filters, quiet hours, and re-alert cooldown
- Security-updates alerts and expected-meta drift detection
- Auth stack: OAuth (Google/GitHub), 2FA (TOTP/WebAuthn), session tracking, CLI user admin
- Deploy via unified `deploy.sh` + Compose auto-detection; agent service on the monitor network

### Security
- Shared-core hardening: OAuth CSRF state store, path-safe storage, rate limiting, admin guards
- CodeQL fixes (TLS, health, storage, OAuth); Dependabot pnpm overrides

---

## [0.5.0] - 2026-07-23

### Added
- **Health**: bearer-protected `GET /api/health/details` for Ops Monitor self/peer checks
- **CLI**: `users change-password`; `users create` with `--role`, name guessing, and TTY guard; soft/hard delete on `users delete`
- **Monitor**: SSL certificate expiry monitoring, SSL check URL + polling interval on sites, degraded health component badges, visual status differentiation, ComponentHealthBadge
- **Monitor**: remote server actions (reboot / upgrade), heartbeat enhancements, route-synced dashboard filters, snapshot/status response improvements
- **Deploy**: unified `deploy.sh` with Compose auto-detection (`compose.yaml` preference)
- **Auth**: token versioning and session tracking (shared-core backport)

### Changed
- Compose cleanup: secrets from `backend/.env` only; footer GitHub URL from app config; root compose DX; agent DNS alias `http://agent:9100`
- Build: vendor manual chunks; silence `@vueuse/core` INVALID_ANNOTATION warnings

### Fixed
- PWA service worker no longer intercepts `/auth/*` navigations
- Agent cleanup of leftover `reboot-required.pkgs` directory
- Deploy sub-script nested step numbering; CSP allows Google reCAPTCHA origins
- OAuth buttons shown only when provider is configured

### Security
- CodeQL hardening (TLS, health, storage, OAuth)
- Unified OAuth callback `/auth/callback/:provider`; OAuth session tracking, 2FA challenge, CSRF state store
- 2FA: `tv`/`jti` on login/refresh; TOTP `verified`/`method`; SEC-5 backup code hashing
- Rate limiting, admin auth, and WebAuthn login hardening; WebAuthn contract backport from gear-stack
- Frontend and backend vulnerability cleanup; pnpm overrides for Dependabot alerts

## [0.4.1] - 2026-05-08

### Added
- **Security updates alerts** — new `security_updates` alert type for per-channel routing

### Fixed
- Alert channel edit dialog now loads form fields on first open (not only after reopening)

## [0.4.0] - 2026-05-08

### Added
- **Alert channel filters** — per-channel routing by alert type, health severity threshold, site IDs/tags, quiet hours (timezone-aware), and re-alert cooldown
- **Alert channel editing** — edit channel config + filters in the UI; filter summary chips on channel cards
- **DB migration** — `alert_channels.filters` JSONB column for routing rules storage

## [0.3.0] - 2026-04-29

### Added
- **Site metadata fields** — `server_label`, `environment`, `tags`, `ip` on site model, forms, and UI cards
- **Expected meta drift detection** — `expected_meta` + `meta_mismatches` columns on `sites` and `site_snapshots`; UI surfaces mismatches in forms and detail components
- **Security updates indicator** — `SecurityUpdatesCountBadge` component, count surfaced on `SiteStatusCard`; ESM/Pro updates excluded from count
- **Snapshot history** — paginated snapshot history retrieval and `SiteDetailSnapshotHistoryCard`; raw response viewing for health/system payloads
- **Dense + live mode** — compact layout toggle on monitor dashboard; live mode with alert event logging
- **Filters bar** — `MonitorFiltersBar` for filtering sites on the dashboard
- **Self-monitoring** — ops-monitor server polls its own health/system endpoints
- **System metrics detail** — `SystemMetricsChart`, `SystemStateBadge`, reboot information on `SiteDetailSystemCard`
- **Site not found state** — dedicated `SiteNotFoundState` component on `SiteDetailPage`
- **Health schema spec** — `docs/health-schema.md` with component icons and status normalization rules
- **Agent enhancements** — `security_packages` list in system metrics, agent versioning, improved update info retrieval
- **CLI** — `monitor` command group with detailed status reporting, `--wide` flag for `monitor sites` / `users list`, interactive prompts for flags, Back option in interactive menu, UUID generator helper, fix-reboot script
- **Docker Compose** — dev and prod compose files for app, database, Redis, and agent services; bind mounts for reboot-required file access; seeds directory bundled in image
- **Clipboard** — `ToClipboard` component (with legacy fallback)
- **PasswordInput integration** — adopted in `LoginForm` and `SiteFormFields`

### Changed
- Robust health status parsing across heterogeneous app responses
- `overallStatus` typed as dedicated `MonitorOverallStatus` union
- Sentry ingest allowed in CSP `connect-src`

### Fixed
- `is_file()` instead of `exists()` for reboot-required detection
- `SiteDetailSystemCard` button visibility logic
- `SiteStatusCard` styling and visibility tweaks for dense mode

### Tests
- Unit tests for monitor router and formatters

## [0.2.0] - 2026-04-13

### Added
- **Monitor module** — pull-only site health and system polling
- `sites` table with configurable polling intervals (health, system, updates, reboot)
- `site_snapshots` table — JSONB raw data, per-type status history, 1000-snapshot retention
- Background `PollerScheduler` (asyncio, 10 s check interval) started on app lifespan
- REST API: `/monitor/sites` CRUD + per-site snapshot history + manual poll trigger
- Monitor dashboard (`/monitor`) — site grid cards with status badges
- Site detail page — health components, system metrics (CPU / RAM / disk / uptime), config panel
- `SiteStatusBadge` component mapping status strings to badge variants
- **Alert channels** — configurable per-channel alert dispatch (Teams Adaptive Cards, Email, Telegram Bot)
- Alert deduplication via `alert_events` table — fires only on status change, not on every poll
- `backend/migrations/057_create_alert_channels.py` — `alert_channels` + `alert_events` tables
- Alert Channels admin page (`/monitor/alerts`) with enable/disable toggle, test button, delete
- `AddChannelDialog` with type-specific config fields (webhook URL, SMTP credentials, Telegram bot token + chat ID)
- CLI `monitor seed-sites` command — upserts sites from a YAML file, supports `--dry-run`
- `backend/seeds/sites.example.yml` — committed template for seeding monitored sites
- `backend/seeds/sites.yml` — gitignored file for real production sites
- Sidebar links for Monitor and Alert Channels

### Security
- Pinned transitive vulnerable dependencies via `pnpm.overrides`:
  - `minimatch` → 3.1.4 / 9.0.7
  - `flatted` → 3.4.2
  - `ajv` → 6.14.0
  - `picomatch` → 2.3.2 / 4.0.4
  - `brace-expansion` → 1.1.13
- Upgraded `vite` to ^7.3.2, `happy-dom` to ^20.8.9, `markdown-it` to ^14.1.1, `vitest` to ^4.1.4

## [0.1.0] - 2026-04-13

### Added
- Initial rebooted baseline created as a clone/fork of the previous Gear Stack codebase.
- Authentication and user management flows are implemented and operational.

### Changed
- Application identity updated toward Ops Monitor branding.
- UI colors and visual styling refreshed from the original Gear Stack theme.

