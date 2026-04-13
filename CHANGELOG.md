# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

