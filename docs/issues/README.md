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
