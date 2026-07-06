# CLI `users delete` — soft/hard delete (jak family-recipes)

| Pole | Wartość |
|---|---|
| **ID** | `004` |
| **Data** | 2026-07-06 |
| **Status** | `done` |
| **Moduł** | `cli`, `auth` |

**Source:** [family-recipes/backend/cli/commands/users.py](../../../family-recipes/backend/cli/commands/users.py) (`users delete`)  
**Backport:** [backport-progress.md](../../../backport-progress.md)

## Opis zadania

`users list` ma już pełną parametryzację (`--wide`), ale `users delete` zawsze woła `repo.delete_user(..., soft_delete=False)` — brak domyślnego soft delete i flagi `--hard`.

## Oczekiwane zachowanie

| Tryb | Efekt |
|------|--------|
| Domyślny (soft) | `delete_user(soft_delete=True)` — anonimizacja, GDPR cleanup |
| `--hard` | `delete_user(soft_delete=False)` — trwałe usunięcie |

Plus komunikaty ostrzegawcze i sukcesu rozróżniające soft vs hard (jak family-recipes).

## Plan implementacji

1. Dodać `--hard` do `users delete` w `backend/cli/commands/users.py`
2. Przekazać `hard` do `_users_delete_async` i `_delete_user_from_db`
3. Domyślnie `soft_delete=not hard` w repozytorium
4. Zaktualizować docstring i przykłady w helpie

## Checklist

- [x] Flaga `--hard` w CLI
- [x] Komunikaty soft vs hard przy potwierdzeniu
- [x] `_delete_user_from_db(user_id, *, hard=False)` → repository
- [x] Weryfikacja: `./exec.sh users delete …` (soft) i `--hard --yes`
