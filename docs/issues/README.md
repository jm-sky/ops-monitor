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
| 003 | 2026-07-01 | `planned` | Moduł akcji na monitorowanych serwerach | [2026-07-01--003--remote-server-actions.md](./2026-07-01--003--remote-server-actions.md) |
| 004 | 2026-07-06 | `done` | CLI `users delete` — soft/hard jak family-recipes | [2026-07-06--004--cli-users-delete-soft-hard.md](./2026-07-06--004--cli-users-delete-soft-hard.md) |
| 005 | 2026-07-07 | `done` | OAuth Facebook — przycisk widoczny tylko przy własnej konfiguracji | [2026-07-07--005--oauth-facebook-button-visibility.md](./2026-07-07--005--oauth-facebook-button-visibility.md) |
| 006 | 2026-07-07 | `done` | OAuth GitHub — logowanie przez GitHub | [2026-07-07--006--oauth-github-login.md](./2026-07-07--006--oauth-github-login.md) |
| 007 | 2026-07-07 | `todo` | GuestLayout — pasek locale/dark mode pod logo (z-index) | [2026-07-07--007--guest-layout-nav-z-index.md](./2026-07-07--007--guest-layout-nav-z-index.md) |

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
