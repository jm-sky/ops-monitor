# Plan implementacji Page Titles

## Format tytułu
Format: `{Page Title} | {App Name}`

Przykład: `Dashboard | Gear Stack`

---

## Routes i proponowane klucze i18n

### App-level routes

| Route Name | Path | i18n Key | EN Title | PL Title | Notes |
|------------|------|----------|----------|----------|-------|
| `landing` | `/` | `common.pages.landing` | `Home` | `Strona główna` | Landing page |
| `Dashboard` | `/dashboard` | `navigation.dashboard` | `Dashboard` | `Panel` | Używa istniejącego klucza |
| `cookies` | `/cookies` | `common.pages.cookies` | `Cookies` | `Cookies` | |
| `privacy` | `/privacy` | `common.pages.privacy` | `Privacy Policy` | `Polityka prywatności` | |
| `contact` | `/contact` | `common.pages.contact` | `Contact` | `Kontakt` | |
| `not-found` | `/:pathMatch(.*)*` | `common.pages.notFound` | `Page Not Found` | `Strona nie znaleziona` | 404 page |

---

### Auth module routes

| Route Name | Path | i18n Key | EN Title | PL Title | Notes |
|------------|------|----------|----------|----------|-------|
| `Login` | `/auth/login` | `auth.pages.login` | `Sign In` | `Logowanie` | |
| `Register` | `/auth/register` | `auth.pages.register` | `Sign Up` | `Rejestracja` | |
| `ForgotPassword` | `/auth/forgot-password` | `auth.forgot_password_page.title` | `Forgot Password?` | `Zapomniałeś hasła?` | Używa istniejącego klucza |
| `ResetPassword` | `/auth/reset-password` | `auth.reset_password_page.title` | `Set New Password` | `Ustaw nowe hasło` | Używa istniejącego klucza |
| `ChangePassword` | `/auth/change-password` | `auth.change_password_page.title` | `Change Password` | `Zmień hasło` | Używa istniejącego klucza |
| `TwoFactorSetup` | `/auth/2fa/setup` | `auth.two_factor.setup.title` | `Two-Factor Authentication Setup` | `Konfiguracja uwierzytelniania dwuskładnikowego` | |
| `TwoFactorVerify` | `/auth/2fa/verify` | `auth.two_factor.verify.title` | `Two-Factor Authentication` | `Uwierzytelnianie dwuskładnikowe` | |
| `VerifyEmail` | `/auth/verify-email` | `auth.pages.verifyEmail` | `Verify Email` | `Weryfikacja email` | |
| `OAuthCallback` | `/auth/callback/:provider` | `auth.pages.oauthCallback` | `OAuth Callback` | `OAuth Callback` | Dynamiczny (provider) |

---

### Gear module routes

| Route Name | Path | i18n Key | EN Title | PL Title | Notes |
|------------|------|----------|----------|----------|-------|
| `gear-containers` | `/gear` | `gear.page.title` | `Gear containers` | `Kontenery sprzętu` | Używa istniejącego klucza |
| `gear-all-items` | `/gear/items` | `gear.pages.allItems` | `All Items` | `Wszystkie przedmioty` | |
| `gear-shopping-planning` | `/gear/shopping` | `gear.pages.shoppingPlanning` | `Shopping Planning` | `Planowanie zakupów` | |
| `gear-container-new` | `/gear/new` | `gear.container.create.title` | `Create Container` | `Utwórz Kontener` | Używa istniejącego klucza |
| `gear-container-detail` | `/gear/:id` | `gear.pages.containerDetail` | `Container Details` | `Szczegóły kontenera` | **Dynamiczny** - nazwa kontenera |
| `gear-container-edit` | `/gear/:id/edit` | `gear.container.edit.title` | `Edit Container` | `Edytuj Kontener` | Używa istniejącego klucza, **dynamiczny** - nazwa kontenera |
| `gear-item-new` | `/gear/:containerId/items/new` | `gear.item.create` | `Add Item` | `Dodaj Przedmiot` | Używa istniejącego klucza, **dynamiczny** - nazwa kontenera |
| `gear-item-detail` | `/gear/:containerId/items/:itemId` | `gear.pages.itemDetail` | `Item Details` | `Szczegóły przedmiotu` | **Dynamiczny** - nazwa przedmiotu |
| `gear-item-edit` | `/gear/:containerId/items/:itemId/edit` | `gear.item.edit` | `Edit Item` | `Edytuj Przedmiot` | Używa istniejącego klucza, **dynamiczny** - nazwa przedmiotu |
| `gear-public-containers` | `/gear/public` | `gear.pages.publicContainers` | `Public Containers` | `Kontenery publiczne` | |
| `gear-public-container-detail` | `/gear/public/:id` | `gear.pages.publicContainerDetail` | `Public Container` | `Publiczny kontener` | **Dynamiczny** - nazwa kontenera |
| `gear-public-item-detail` | `/gear/public/:containerId/items/:itemId` | `gear.pages.publicItemDetail` | `Public Item` | `Publiczny przedmiot` | **Dynamiczny** - nazwa przedmiotu |
| `gear-shared-container-detail` | `/shared/container/:token` | `gear.pages.sharedContainerDetail` | `Shared Container` | `Udostępniony kontener` | **Dynamiczny** - nazwa kontenera |
| `gear-container-share-tokens` | `/gear/:id/share-tokens` | `gear.shareTokens.title` | `Manage Share Tokens` | `Zarządzaj tokenami udostępniania` | Używa istniejącego klucza, **dynamiczny** - nazwa kontenera |
| `gear-settings` | `/gear/settings` | `gear.settings.page.title` | `Gear Settings` | `Ustawienia sprzętu` | Używa istniejącego klucza |

---

### Admin module routes

| Route Name | Path | i18n Key | EN Title | PL Title | Notes |
|------------|------|----------|----------|----------|-------|
| `admin-dashboard` | `/admin` | `admin.dashboard.title` | `Admin Dashboard` | `Panel administratora` | Używa istniejącego klucza |
| `admin-users` | `/admin/users` | `admin.users.title` | `Users Management` | `Zarządzanie użytkownikami` | Używa istniejącego klucza |
| `admin-containers` | `/admin/containers` | `admin.containers.title` | `Containers Management` | `Zarządzanie kontenerami` | Używa istniejącego klucza |
| `admin-items` | `/admin/items` | `admin.items.title` | `Items Management` | `Zarządzanie przedmiotami` | Używa istniejącego klucza |

---

### User module routes

| Route Name | Path | i18n Key | EN Title | PL Title | Notes |
|------------|------|----------|----------|----------|-------|
| `profile` | `/profile` | `user.profile.title` | `Profile` | `Profil` | Używa istniejącego klucza |
| `profileEdit` | `/profile/edit` | `user.edit.title` | `Edit Profile` | `Edytuj profil` | Używa istniejącego klucza |
| `publicUserProfile` | `/users/:userId/public` | `user.publicProfile.title` | `User Profile` | `Profil użytkownika` | **Dynamiczny** - nazwa użytkownika |

---

### Settings module routes

| Route Name | Path | i18n Key | EN Title | PL Title | Notes |
|------------|------|----------|----------|----------|-------|
| `settings` | `/settings` | `settings.page.title` | `Settings` | `Ustawienia` | Używa istniejącego klucza |

---

## Nowe klucze i18n do dodania

### `src/shared/i18n/locales/en.ts` i `pl.ts`

```typescript
common: {
  // ... istniejące klucze ...
  pages: {
    landing: 'Home',
    cookies: 'Cookies',
    privacy: 'Privacy Policy',
    contact: 'Contact',
    notFound: 'Page Not Found',
  },
}
```

### `src/modules/auth/i18n/locales/en.ts` i `pl.ts`

```typescript
auth: {
  // ... istniejące klucze ...
  pages: {
    login: 'Sign In',
    register: 'Sign Up',
    verifyEmail: 'Verify Email',
    oauthCallback: 'OAuth Callback',
  },
  two_factor: {
    // ... istniejące klucze ...
    setup: {
      // ... istniejące klucze ...
      title: 'Two-Factor Authentication Setup',
    },
    verify: {
      // ... istniejące klucze ...
      title: 'Two-Factor Authentication',
    },
  },
}
```

### `src/modules/gear/i18n/index.ts` (en.ts i pl.ts)

```typescript
gear: {
  // ... istniejące klucze ...
  pages: {
    allItems: 'All Items',
    shoppingPlanning: 'Shopping Planning',
    containerDetail: 'Container Details',
    itemDetail: 'Item Details',
    publicContainers: 'Public Containers',
    publicContainerDetail: 'Public Container',
    publicItemDetail: 'Public Item',
    sharedContainerDetail: 'Shared Container',
  },
}
```

---

## Dynamiczne tytuły

Następujące strony wymagają dynamicznych tytułów (z nazwą obiektu):

1. **Container Detail** - `{Container Name} | Gear Stack`
2. **Container Edit** - `Edit {Container Name} | Gear Stack`
3. **Item Detail** - `{Item Name} | Gear Stack`
4. **Item Edit** - `Edit {Item Name} | Gear Stack`
5. **Item New** (w kontekście kontenera) - `Add Item to {Container Name} | Gear Stack`
6. **Public Container Detail** - `{Container Name} | Gear Stack`
7. **Public Item Detail** - `{Item Name} | Gear Stack`
8. **Shared Container Detail** - `{Container Name} | Gear Stack`
9. **Container Share Tokens** - `Share {Container Name} | Gear Stack`
10. **Public User Profile** - `{User Name} | Gear Stack`
11. **OAuth Callback** - `OAuth Callback ({Provider}) | Gear Stack`

Dla tych stron tytuł będzie ustawiany w komponencie za pomocą composable `usePageTitle()`.

---

## Implementacja

### 1. Router guard (`src/router/index.ts`)
- `router.afterEach()` - ustawia tytuł na podstawie `meta.title`
- Format: `t(meta.title) + ' | ' + config.app.name`
- Fallback: `config.app.name` jeśli brak `meta.title`

### 2. Meta fields w routes
- Dodaj `meta.title` do każdej route z kluczem i18n
- Dla dynamicznych stron: `meta.title` jako fallback, tytuł ustawiany w komponencie

### 3. Composable `usePageTitle()` (`src/shared/composables/usePageTitle.ts`)
- Funkcja `setTitle(key: string, params?: Record<string, string>)` - ustawia dynamiczny tytuł
- Funkcja `resetTitle()` - resetuje do tytułu z route meta
- Używa `useI18n()` i `config.app.name`

### 4. Klucze i18n
- Dodaj nowe klucze do odpowiednich plików i18n
- Użyj istniejących kluczy gdzie to możliwe

---

## Przykłady użycia

### Statyczny tytuł (w route)
```typescript
{
  path: '/gear',
  name: 'gear-containers',
  meta: { 
    layout: 'authenticated',
    title: 'gear.page.title'
  }
}
```

### Dynamiczny tytuł (w komponencie)
```vue
<script setup>
import { usePageTitle } from '@/shared/composables/usePageTitle'
import { useRoute } from 'vue-router'
import { useGearStore } from '@/modules/gear/store'

const route = useRoute()
const gearStore = useGearStore()
const { setTitle } = usePageTitle()

const container = computed(() => 
  gearStore.getContainerById(route.params.id as string)
)

watchEffect(() => {
  if (container.value) {
    setTitle('gear.pages.containerDetail', { name: container.value.name })
  }
})
</script>
```

---

## Checklist implementacji

- [ ] Dodać nowe klucze i18n do wszystkich modułów
- [ ] Dodać `meta.title` do wszystkich routes
- [ ] Utworzyć composable `usePageTitle()`
- [ ] Dodać router guard `afterEach` w `src/router/index.ts`
- [ ] Zaimplementować dynamiczne tytuły w komponentach (ContainerDetail, ItemDetail, etc.)
- [ ] Przetestować wszystkie routes
- [ ] Sprawdzić format tytułu w przeglądarce

