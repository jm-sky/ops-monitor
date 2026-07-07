# OAuth Facebook — widoczność przycisku niezależnie od Google

| Pole | Wartość |
|---|---|
| **ID** | `005` |
| **Data** | 2026-07-07 |
| **Status** | `done` |
| **Moduł** | `auth` (shared core) |

## Opis zadania

Przycisk „Continue with Facebook” jest renderowany wewnątrz bloku `v-if="config.oauth.google.enabled"`, więc pojawia się gdy skonfigurowany jest tylko Google — nawet bez `VITE_FACEBOOK_OAUTH_CLIENT_ID`.

Pliki:

- `src/modules/auth/components/LoginForm.vue`
- `src/modules/auth/components/RegisterForm.vue`

## Plan implementacji

Backport z [gear-stack #013](../../gear-stack/docs/issues/2026-07-07--013--oauth-facebook-button-visibility.md):

1. Sekcja OAuth: `v-if="config.oauth.google.enabled || config.oauth.facebook.enabled"`
2. `OAuthGoogleButton v-if="config.oauth.google.enabled"`
3. `OAuthFacebookButton v-if="config.oauth.facebook.enabled"`

## Checklist

- [ ] `LoginForm.vue`
- [ ] `RegisterForm.vue`
- [ ] Weryfikacja: 4 scenariusze konfiguracji env (tylko Google / tylko Facebook / oba / żaden)
