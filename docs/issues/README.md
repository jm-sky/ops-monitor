# Issues / zadania

Lokalny rejestr zadań i planów implementacji dla ops-monitor. Pliki w tym katalogu opisują **co** i **jak** zrobić — nie zastępują issue trackera, ale służą jako źródło prawdy w repozytorium.

## Konwencja nazw plików

```
{data}--{task_id}--{tytul-opisowy}.md
```

| Segment | Format | Przykład |
|---|---|---|
| `data` | `YYYY-MM-DD` (data utworzenia zadania) | `2026-07-01` |
| `task_id` | Trzycyfrowy numer rosnący (`001`, `002`, …) | `001` |
| `tytul-opisowy` | Krótki opis kebab-case, bez polskich znaków | `rozroznienie-wizualne-statusow` |

**Przykład:** `2026-07-01--001--rozroznienie-wizualne-statusow.md`

### Statusy zadań

Używaj jednej z wartości w nagłówku pliku (tabela metadanych) i w tabeli poniżej:

| Status | Znaczenie |
|---|---|
| `planned` | Zaplanowane, nie rozpoczęte |
| `in_progress` | W trakcie implementacji |
| `done` | Zakończone i zweryfikowane |
| `cancelled` | Porzucone / nieaktualne |

Po zmianie statusu zaktualizuj zarówno plik zadania, jak i tabelę na tej stronie.

## Lista zadań

| ID | Data | Status | Tytuł | Plik |
|---|---|---|---|---|
| 001 | 2026-07-01 | `done` | Rozróżnienie wizualne statusów monitorowania | [2026-07-01--001--rozroznienie-wizualne-statusow.md](./2026-07-01--001--rozroznienie-wizualne-statusow.md) |
| 002 | 2026-07-01 | `done` | Weryfikacja ważności certyfikatów SSL | [2026-07-01--002--ssl-cert-expiry-monitoring.md](./2026-07-01--002--ssl-cert-expiry-monitoring.md) |
| 003 | 2026-07-01 | `cancelled` | Moduł akcji na monitorowanych serwerach (zbyt duże ryzyko, anulowane 2026-07-24) | [2026-07-01--003--remote-server-actions.md](./2026-07-01--003--remote-server-actions.md) |
| 004 | 2026-07-06 | `done` | CLI `users delete` — soft/hard jak family-recipes | [2026-07-06--004--cli-users-delete-soft-hard.md](./2026-07-06--004--cli-users-delete-soft-hard.md) |
| 005 | 2026-07-07 | `done` | OAuth Facebook — przycisk widoczny tylko przy własnej konfiguracji | [2026-07-07--005--oauth-facebook-button-visibility.md](./2026-07-07--005--oauth-facebook-button-visibility.md) |
| 006 | 2026-07-07 | `done` | OAuth GitHub — logowanie przez GitHub | [2026-07-07--006--oauth-github-login.md](./2026-07-07--006--oauth-github-login.md) |
| 007 | 2026-07-07 | `todo` | GuestLayout — pasek locale/dark mode pod logo (z-index) | [2026-07-07--007--guest-layout-nav-z-index.md](./2026-07-07--007--guest-layout-nav-z-index.md) |
| 008 | 2026-07-20 | `done` | Sekrety monitorowanych serwerów widoczne dla każdego zalogowanego użytkownika (SEC-1) | [2026-07-20--008--monitor-secrets-exposed-to-any-user.md](./2026-07-20--008--monitor-secrets-exposed-to-any-user.md) |
| 009 | 2026-07-20 | `done` | Router `/users/*` omija ochronę Ownera/superadmina (SEC-2) | [2026-07-20--009--users-router-bypasses-owner-protection.md](./2026-07-20--009--users-router-bypasses-owner-protection.md) |
| 010 | 2026-07-20 | `done` | WebAuthn: weryfikacja to zaślepka; logowanie z 2FA zepsute (SEC-3) | [2026-07-20--010--webauthn-stub-and-2fa-login-broken.md](./2026-07-20--010--webauthn-stub-and-2fa-login-broken.md) |
| 011 | 2026-07-20 | `done` | Rate limiting niepodłączony i spoofowalny (SEC-4) | [2026-07-20--011--rate-limiting-not-wired.md](./2026-07-20--011--rate-limiting-not-wired.md) |
| 012 | 2026-07-20 | `done` | Zepsuty endpoint create user + martwy stos wyjątków | [2026-07-20--012--broken-user-create-endpoint-and-dead-exception-stack.md](./2026-07-20--012--broken-user-create-endpoint-and-dead-exception-stack.md) |
| 013 | 2026-07-20 | `done` | Podbić floory pip z aktywnymi CVE (Pillow, jinja2, python-dotenv) | [2026-07-20--013--pip-floor-cve-bump.md](./2026-07-20--013--pip-floor-cve-bump.md) |
| 014 | 2026-07-22 | `done` | OAuth session machinery + server-side state (backport 036+037) | [2026-07-22--014--oauth-session-and-state-backport.md](./2026-07-22--014--oauth-session-and-state-backport.md) |

## Szablon nowego zadania

Skopiuj strukturę z istniejącego pliku. Minimalny nagłówek:

```markdown
# Tytuł zadania

| Pole | Wartość |
|---|---|
| **ID** | `00X` |
| **Data** | YYYY-MM-DD |
| **Status** | `planned` |
| **Moduł** | np. `monitor`, `backend`, `agent` |

## Opis zadania
...

## Plan implementacji
...

## Checklist
- [ ] ...
```

Następnie dodaj wiersz do tabeli **Lista zadań** powyżej.
