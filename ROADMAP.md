# ROADMAP

This roadmap groups current work into three priorities.

## P1 - High Priority

- Monitoring "live mode" behavior and docs consistency:
  - Keep default polling at a lower frequency for normal background mode (for example: every 5 minutes). (done)
  - Increase polling frequency when a user is actively viewing the monitoring dashboard (for example: every 2 minutes). (done for monitor list + site detail with visible-tab check)
  - Ensure this behavior is configurable via backend settings and clearly documented. (done via `/api/monitor/config` + env-based monitor runtime settings)

## P2 - Medium Priority

- Monitoring UX and observability improvements:
  - Review monitor dashboard data freshness indicators and alert visibility to improve operator workflow.

## P3 - Low Priority

- Security/auth completeness:
  - Replace placeholder WebAuthn authentication verification with full verification using a proper WebAuthn library.
- OAuth provider expansion:
  - Keep GitHub OAuth support as planned future work.
- Legacy Gear Stack cleanup:
  - Continue removing or rewriting residual Gear Stack-era copy/text/features that do not fit Ops Monitor scope.
  - Keep docs and UI language aligned with the current monitoring-only product direction.

## Completed

- Monitoring reliability and correctness hardening:
  - Completed account deletion side effects in auth service:
    - invalidate all active user sessions/tokens
    - remove related auth data (2FA, passkeys, oauth connections)
  - Implemented real user-token tracking for global token blacklist flows.
