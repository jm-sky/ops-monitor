# WebAuthn: weryfikacja podpisu to zaślepka; logowanie z 2FA jest funkcjonalnie zepsute

| Pole | Wartość |
|---|---|
| **ID** | `010` |
| **Data** | 2026-07-20 |
| **Status** | `done` |
| **Moduł** | `backend/app/modules/two_factor` |
| **Source** | [Security review — backend, SEC-3 + discrepancy notes](../reviews/2026-07-20-security-backend.md) |
| **Severity** | High |

## Opis zadania

Dwa powiązane problemy w tym samym obszarze (2FA/passkey login):

**1. WebAuthn authentication nie weryfikuje podpisu (SEC-3).** `complete_authentication` (`two_factor/webauthn_service.py:356-376`) znajduje passkey po `rawId`, potwierdza że należy do usera z challenge, i ma `# TODO: Full WebAuthn verification ... For now, basic check`. Brak weryfikacji podpisu assertion względem zapisanego klucza publicznego, brak sprawdzenia `rpIdHash`/origin, licznik podpisów nadpisywany bez wykrywania klonowania. `.docs/backport-progress.md` oznacza WebAuthn jako ✅ dla ops-monitor — to nieprawda dla ścieżki authentication (rejestracja jest zweryfikowana poprawnie).

**2. Logowanie z włączonym 2FA jest zepsute end-to-end (fail-closed lockout).** Ani `verify_totp_login` (`two_factor/service.py:141-146`, mintuje token bez `tfaVerified`), ani `complete_passkey_authentication` (zwraca `{success, userId, passkeyId}`, nie tokeny) nigdy nie wystawia access tokena z `tfaVerified=True`. `_verify_user_token` (`auth/dependencies.py:168-176`) odrzuca każdy request użytkownika z 2FA z 401 "2FA verification required". **Włączenie TOTP lub passkeya blokuje konto.** To zabezpiecza przed obejściem (fail-closed), ale oznacza, że 2FA nie jest w praktyce używalne, i dlatego SEC-3 nie jest dziś bezpośrednio wykorzystywalny jako bypass logowania.

## Checklist

- [ ] Zaimplementować `verify_authentication_response` (biblioteka `webauthn` już jest zależnością) z pełnym sprawdzeniem: challenge, origin, RP-ID, klucz publiczny, regresja licznika
- [ ] Naprawić `verify_totp_login` / `complete_passkey_authentication`, żeby wystawiały token z `tfaVerified=True` po udanej weryfikacji drugiego czynnika
- [ ] Dodać test end-to-end: użytkownik z włączonym TOTP loguje się i uzyskuje dostęp do chronionego endpointu
- [ ] Dodać test end-to-end: użytkownik z passkeyem loguje się i uzyskuje dostęp
- [ ] Zaktualizować `.docs/backport-progress.md` w meta-repo — WebAuthn dla ops-monitor nie powinno być ✅ bez zastrzeżenia, dopóki authentication nie jest realnie zweryfikowany

## Weryfikacja

Użytkownik z włączonym TOTP/passkeyem może się zalogować i uzyskać dostęp do chronionych endpointów (dziś: nie może). Podrobiona assertion WebAuthn (bez poprawnego podpisu) jest odrzucana.
