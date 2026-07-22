# OAuth session machinery + server-side state (backport 036+037)

| Pole | Wartość |
|---|---|
| **ID** | `014` |
| **Data** | 2026-07-22 |
| **Status** | `done` |
| **Moduł** | `auth` (backend — OAuth) |
| **Source** | gear-stack issues [036](../../../gear-stack/docs/issues/2026-07-21--036--oauth-login-bypasses-session-machinery.md) + [037](../../../gear-stack/docs/issues/2026-07-21--037--oauth-callback-state-not-verified.md) |
| **Severity** | Medium |

## Opis zadania

Backport security fixes from gear-stack:

1. **036 — OAuth login session machinery:** ensure OAuth goes through `_issue_login_tokens` (jti/tv/session tracking) and that `AuthServiceWith2FA` honors 2FA on OAuth the same way as password login.
2. **037 — OAuth CSRF `state`:** persist `state` server-side (Redis, single-use, TTL, provider-bound) and consume it in the callback before exchanging the authorization code.

ops-monitor specifics preserved:

- `_issue_login_tokens` still returns `tuple[str, str]` (access, refresh), not `LoginResponse`.
- `login_with_oauth` builds `LoginResponse` manually after issuing tokens.
- Inactive-user rejection (`if not user.isActive`) kept inside `_resolve_oauth_user`.
- Existing auth_integration DI style for `token_blacklist_service` unchanged.

## Checklist

- [x] `backend/app/core/oauth_state_store.py` (copy from gear-stack)
- [x] `backend/app/modules/auth/service.py` — `_resolve_oauth_user` + `login_with_oauth`
- [x] `backend/app/modules/two_factor/auth_integration.py` — `_build_two_factor_challenge` + `login_with_oauth`
- [x] `backend/app/modules/auth/router.py` — `store_state` / `consume_state`
- [x] `backend/tests/test_oauth_state_store.py`
- [x] `backend/tests/test_oauth_2fa_login.py`
- [x] `backend/tests/test_auth_service.py` — `TestLoginWithOAuth`

## Weryfikacja

```bash
docker exec ops-monitor-app python -m pytest \
  tests/test_oauth_state_store.py \
  tests/test_oauth_2fa_login.py \
  tests/test_auth_service.py::TestLoginWithOAuth \
  tests/test_auth_service.py::TestDeleteAndOAuthHardening \
  -v
```
