# Router /users/* omija ochronę Ownera/superadmina egzekwowaną w /admin/*

| Pole | Wartość |
|---|---|
| **ID** | `009` |
| **Data** | 2026-07-20 |
| **Status** | `done` |
| **Moduł** | `backend/app/modules/users`, `backend/app/modules/admin` |
| **Source** | [Security review — backend, SEC-2](../reviews/2026-07-20-security-backend.md) |
| **Severity** | High |

## Opis zadania

`AdminService.update_user`/`delete_user` (`modules/admin/service.py:161-191`) poprawnie blokuje admina bez roli Ownera przed: nadaniem/odebraniem roli Owner, usunięciem użytkownika Owner/admin, usunięciem `PROTECTED_USER_EMAIL`.

Równoległe endpointy w module `users` (`PATCH /api/users/{id}`, `DELETE /api/users/{id}`, `DELETE /api/users/{id}/hard` — `modules/users/router.py:177-206,208-225,228-245`) są zabezpieczone tylko przez `AdminUser` i wołają repozytorium bezpośrednio, **bez żadnego** z tych checków.

Zwykły admin (nie-Owner) może więc trwale usunąć (`hard delete`) albo zdegradować konto Ownera/superadmina — dokładnie to, przed czym ma chronić `SUPERADMIN_EMAIL` w `config.py:214-223`.

## Checklist

- [ ] Przekierować mutacje uprzywilejowanych użytkowników przez `AdminService` (albo zreplikować checki owner/protected-user/self w routerze `users`)
- [ ] `DELETE /api/users/{id}/hard` oraz zmiana roli na/z Owner → wymagać `OwnerUser`, nie tylko `AdminUser`
- [ ] Test: admin (nie-Owner) nie może usunąć ani zdegradować konta Ownera przez `/api/users/*`

## Weryfikacja

Próba `DELETE /api/users/{owner_id}` i `PATCH /api/users/{owner_id}` (rola) przez token zwykłego admina zwraca 403, tak jak analogiczna próba przez `/admin/*`.
