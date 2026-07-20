# Rate limiting nie działa — spoofowalny klucz i limiter nigdy niepodłączony

| Pole | Wartość |
|---|---|
| **ID** | `011` |
| **Data** | 2026-07-20 |
| **Status** | `done` |
| **Moduł** | `backend/app/core` |
| **Source** | [Security review — backend, SEC-4](../reviews/2026-07-20-security-backend.md) |
| **Severity** | Medium-High |

## Opis zadania

Dwa niezależne problemy powodujące, że limity logowania/rejestracji/resetu hasła (`10/minute`, `5/minute` — komentowane w kodzie jako "CRITICAL") nie chronią w praktyce:

1. `get_client_ip` (`core/limiter.py:15-38`) bierze **pierwszą** wartość nagłówka `X-Forwarded-For`, który jest w pełni kontrolowany przez klienta. Atakujący wysyła świeży fałszywy IP w każdym requeście i każdy trafia do innego bucketu.
2. `setup_limiter(app)` (`core/limiter.py:61-73`) **nigdy nie jest wołany** w `create_app()`/`main.py` (`core/app_factory.py:179-213`) — `app.state.limiter` nigdy nie jest ustawiony, handler `RateLimitExceeded → 429` nigdy nie jest zarejestrowany. Przekroczenie limitu przechodzi przez generyczny handler 500, bez `Retry-After`.

## Checklist

- [ ] Za Caddy: brać IP klienta z najbardziej zaufanego (prawego) hopu proxy albo z `request.client.host`, nie z lewej strony `X-Forwarded-For`
- [ ] Wywołać `setup_limiter(app)` w `create_app()`
- [ ] Test: przekroczenie limitu logowania zwraca 429 z `Retry-After`, nie generyczny 500
- [ ] Test: sfałszowany `X-Forwarded-For` per-request nie omija limitu

## Weryfikacja

`for i in {1..15}; do curl -X POST /api/auth/login ...; done` — po przekroczeniu limitu odpowiedź to 429, niezależnie od podanego `X-Forwarded-For`.
