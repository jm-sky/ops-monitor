# GuestLayout — pasek locale/dark mode pod logo (z-index)

| Pole | Wartość |
|---|---|
| **ID** | `007` |
| **Data** | 2026-07-07 |
| **Status** | `todo` |
| **Moduł** | `layouts` (shared core) |
| **Source** | [gear-stack #015](../../gear-stack/docs/issues/2026-07-07--015--guest-layout-nav-z-index.md) |

## Opis zadania

Na stronie logowania (`GuestLayoutCentered`) pasek z przełącznikiem języka i dark mode renderuje się pod logo. Brakuje `z-10` na `<nav>` — `backdrop-blur` nie działa.

## Checklist

- [ ] `src/layouts/GuestLayoutCentered.vue` — dodać `z-10` do `<nav>` (wzór: `GuestLayoutCenteredGlass.vue`)

**Backport we wszystkich repozytoriach core** — identyczna zmiana w każdym projekcie.

## Weryfikacja

`/auth/login` — kontrolki nad logo, blur widoczny.
