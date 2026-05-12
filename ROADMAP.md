# ROADMAP

This roadmap groups current work into three priorities.

## P1 - High Priority

- Monitoring reliability and correctness hardening:
  - Complete account deletion side effects in auth service:
    - invalidate all active user sessions/tokens
    - remove related auth data (2FA, passkeys, oauth connections)
  - Implement real user-token tracking for global token blacklist flows.
- Monitoring "live mode" behavior and docs consistency:
  - Keep default polling at a lower frequency for normal background mode (for example: every 5 minutes).
  - Increase polling frequency when a user is actively viewing the monitoring dashboard (for example: every 2 minutes).
  - Ensure this behavior is configurable via backend settings and clearly documented.

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
