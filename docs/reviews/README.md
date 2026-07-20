# Reviews

Pierwszy pełny przegląd projektu (security backend/frontend, code quality, dependency bump) — 2026-07-20.

## Program

| Review | Zakres | Status | Plik |
|--------|--------|--------|------|
| Security | Backend | `done` | [2026-07-20-security-backend.md](2026-07-20-security-backend.md) |
| Security | Frontend | `done` | [2026-07-20-security-frontend.md](2026-07-20-security-frontend.md) |
| Code quality | Backend + Frontend | `done` | [2026-07-20-code-quality.md](2026-07-20-code-quality.md) |
| Dependency bump | Backend (pip) + Frontend (npm) | `done` | [2026-07-20-dependency-bump.md](2026-07-20-dependency-bump.md) |

## Najważniejsze wnioski

- **SEC-1 (High):** sekrety monitorowanych serwerów (token pollingu, Teams webhook URL) widoczne dla każdego zalogowanego użytkownika, nie tylko admina — issue [008](../issues/2026-07-20--008--monitor-secrets-exposed-to-any-user.md)
- **SEC-2 (High):** ochrona Ownera/superadmina egzekwowana w `/admin/*`, ale ominięta w równoległym routerze `/users/*` — issue [009](../issues/2026-07-20--009--users-router-bypasses-owner-protection.md)
- **SEC-3 + 2FA lockout (High):** weryfikacja WebAuthn to zaślepka bez sprawdzenia podpisu; logowanie z 2FA jest funkcjonalnie zepsute (fail-closed lockout) — issue [010](../issues/2026-07-20--010--webauthn-stub-and-2fa-login-broken.md)
- **SEC-4 (Med-High):** rate limiting nie działa (spoofowalny X-Forwarded-For + limiter nigdy niepodłączony do aplikacji) — issue [011](../issues/2026-07-20--011--rate-limiting-not-wired.md)
- **Code quality (High):** `POST /api/users/` zawsze zwraca 500 (NotImplementedError); martwy, równoległy stos obsługi wyjątków w `app/exceptions/` — issue [012](../issues/2026-07-20--012--broken-user-create-endpoint-and-dead-exception-stack.md)
- **Dependency (szybki win):** Pillow/jinja2/python-dotenv mają znane CVE na zadeklarowanym floorze mimo względnie świeżego sweepu z 07-03 — issue [013](../issues/2026-07-20--013--pip-floor-cve-bump.md)

Pozostałe findings (SEC-5…SEC-8, SEC-F2/F4/F5, code-quality mediums/lows, plan bumpów major) — patrz pełne pliki review powyżej; nie mają osobnych issues, traktować jako backlog.

## Postęp napraw

**2026-07-20 — issues 008–013 ukończone.** Wszystkie fixy zaimplementowane najpierw w **gear-stack** (źródło prawdy — 5 z 6 findings okazało się być bugami w samym gear-stack, nie regresją ops-monitor), zweryfikowane tam (pełny test suite + nowe testy + black + mypy), potem backportowane 1:1 do ops-monitor + naprawiony SEC-1 (ops-monitor-only, brak modułu `monitor` w gear-stack). Szczegóły w `.docs/issues/2026-07-20--016--project-review-sweep.md` (meta-repo) i w commitach obu repozytoriów.

Backport do **AI-workspace, zbory-chwz, family-recipes** pozostaje jako osobny follow-up (patrz `.docs/backport-progress.md`).

## Po każdym uruchomieniu

1. Zaktualizuj status w tej tabeli i w pliku review.
2. Dodaj/zaktualizuj wpisy w [issues/](../issues/) dla actionable follow-upów.
3. Rozważ zgłoszenie discrepancy do `.docs/backport-progress.md` w meta-repo, jeśli finding dotyczy zakłamanego stanu backportu (patrz SEC-3/2FA powyżej — WebAuthn ✅ w macierzy jest tylko częściowo prawdziwe).
