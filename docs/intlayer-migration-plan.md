# Plan migracji z vue-i18n na Intlayer

## Podsumowanie

**Cel:** Pełna migracja z vue-i18n na Intlayer w projekcie Gear Stack

**Podejście:**
- Pełna migracja (całkowite zastąpienie vue-i18n)
- Component-scoped structure (każdy komponent ma własny `.content.ts`)
- Tylko core features (bez Visual Editor, AI translations, VSCode extension)
- Wbudowana pluralizacja Intlayer

**Szacowany czas:** 3.5-5 tygodni (17-26 dni roboczych)

**Rozmiar zadania:**
- 221 komponentów do zmigrowania
- 2401 linii tłumaczeń
- 7 modułów (admin, ai, auth, billing, gear, settings, user)

## 1. Konfiguracja początkowa

### 1.1. Instalacja dependencies

```bash
pnpm add intlayer vue-intlayer
pnpm add -D vite-intlayer
pnpm remove vue-i18n
```

### 1.2. Utworzenie intlayer.config.ts

**Plik:** `/home/madeyskij/projects/gear-stack/intlayer.config.ts`

```typescript
import { type IntlayerConfig } from 'intlayer'

const config: IntlayerConfig = {
  internationalization: {
    locales: ['en', 'pl'],
    defaultLocale: 'en',
  },
  content: {
    typesDir: '.intlayer',
    fileExtensions: ['.content.ts'],
    baseDir: './src',
  },
  editor: {
    enabled: false,
  },
}

export default config
```

### 1.3. Aktualizacja vite.config.ts

**Plik:** `/home/madeyskij/projects/gear-stack/vite.config.ts`

Dodać pluginy Intlayer:

```typescript
import { intlayer, intlayerProxy } from 'vite-intlayer'

export default defineConfig(({ mode }) => {
  return {
    plugins: [
      tailwindcss(),
      vue(),
      intlayer(), // Dodać tutaj
      pwaPlugin,
      // ... rest
    ],
    // intlayerProxy() middleware można dodać opcjonalnie dla URL-based locale detection
  }
})
```

### 1.4. Aktualizacja tsconfig.json

**Plik:** `/home/madeyskij/projects/gear-stack/tsconfig.json`

Dodać w root level:

```json
{
  "include": [".intlayer/**/*.ts"]
}
```

### 1.5. Aktualizacja .gitignore

Dodać:
```
.intlayer
```

## 2. Helper functions

### 2.1. Interpolacja parametrów

**Plik:** `/home/madeyskij/projects/gear-stack/src/shared/i18n/utils/interpolate.ts`

```typescript
/**
 * Interpolate parameters in translation template
 * Example: interpolate("Hello {name}", { name: "John" }) => "Hello John"
 */
export function interpolate(template: string, params: Record<string, string | number>): string {
  return Object.entries(params).reduce(
    (result, [key, value]) => result.replace(`{${key}}`, String(value)),
    template
  )
}
```

### 2.2. Pluralizacja polska (jeśli potrzebna)

**Plik:** `/home/madeyskij/projects/gear-stack/src/shared/i18n/utils/plural.ts`

```typescript
import type { SupportedLocale } from '@/shared/config/config'

type PluralForms = {
  zero?: string
  one: string
  few?: string
  many: string
  other?: string
}

export function getPolishPluralForm(count: number): keyof PluralForms {
  if (count === 0) return 'zero'
  if (count === 1) return 'one'

  const isTeen = count > 10 && count < 20
  const endsWithTwoToFour = count % 10 >= 2 && count % 10 <= 4

  if (!isTeen && endsWithTwoToFour) return 'few'
  return 'many'
}

export function pluralize(
  count: number,
  forms: PluralForms,
  locale: SupportedLocale
): string {
  let form: keyof PluralForms

  if (locale === 'pl') {
    form = getPolishPluralForm(count)
  } else {
    form = count === 0 ? 'zero' : count === 1 ? 'one' : 'many'
  }

  const template = forms[form] ?? forms.many ?? forms.one
  return template.replace('{count}', String(count))
}
```

### 2.3. Page titles helper

**Plik:** `/home/madeyskij/projects/gear-stack/src/router/pageTitles.ts`

```typescript
import type { SupportedLocale } from '@/shared/config/config'

export const pageTitles: Record<string, Record<SupportedLocale, string>> = {
  'common.pages.landing': { en: 'Home', pl: 'Strona główna' },
  'common.pages.cookies': { en: 'Cookies', pl: 'Cookies' },
  'common.pages.privacy': { en: 'Privacy Policy', pl: 'Polityka prywatności' },
  'common.pages.terms': { en: 'Terms of Use', pl: 'Regulamin' },
  'common.pages.contact': { en: 'Contact', pl: 'Kontakt' },
  'common.pages.about': { en: 'About', pl: 'O aplikacji' },
  'common.pages.aiContext': { en: 'AI Context', pl: 'Kontekst AI' },
  'common.pages.notFound': { en: 'Page Not Found', pl: 'Strona nie znaleziona' },
  'gear.page.title': { en: 'Gear containers', pl: 'Kontenery sprzętu' },
  // ... dodać resztę tytułów z meta.title w routes
}

export function getPageTitle(key: string, locale: SupportedLocale): string {
  return pageTitles[key]?.[locale] ?? key
}
```

## 3. Shared translations

### 3.1. Struktura katalogów

Utworzyć:
```
src/shared/i18n/content/
├── common.content.ts
├── validation.content.ts
├── errors.content.ts
├── navigation.content.ts
├── footer.content.ts
├── pages.content.ts
├── pwa.content.ts
├── fileUpload.content.ts
├── markdown.content.ts
└── premium.content.ts
```

### 3.2. Przykład: common.content.ts

**Plik:** `/home/madeyskij/projects/gear-stack/src/shared/i18n/content/common.content.ts`

```typescript
import { t, type Dictionary } from 'intlayer'

const commonContent = {
  key: 'common',
  content: {
    welcome: t({ en: 'Welcome', pl: 'Witaj' }),
    loading: t({ en: 'Loading...', pl: 'Ładowanie...' }),
    error: t({ en: 'Error', pl: 'Błąd' }),
    success: t({ en: 'Success', pl: 'Sukces' }),
    cancel: t({ en: 'Cancel', pl: 'Anuluj' }),
    save: t({ en: 'Save', pl: 'Zapisz' }),
    create: t({ en: 'Create', pl: 'Utwórz' }),
    delete: t({ en: 'Delete', pl: 'Usuń' }),
    edit: t({ en: 'Edit', pl: 'Edytuj' }),
    preview: t({ en: 'Preview', pl: 'Podgląd' }),
    close: t({ en: 'Close', pl: 'Zamknij' }),
    confirm: t({ en: 'Confirm', pl: 'Potwierdź' }),
    search: t({ en: 'Search', pl: 'Szukaj' }),
    toggleDarkMode: t({
      en: 'Switch to {mode} mode',
      pl: 'Przełącz na tryb {mode}',
    }),
    toggleLanguage: t({
      en: 'Switch language to {locale}',
      pl: 'Przełącz język na {locale}',
    }),
    copyToClipboard: {
      success: t({ en: 'Copied to clipboard', pl: 'Skopiowano do schowka' }),
      copied: t({ en: 'Copied', pl: 'Skopiowano' }),
      copy: t({ en: 'Copy', pl: 'Skopiuj' }),
    },
    // ... dodać resztę z src/shared/i18n/locales/en.ts common section
  },
} satisfies Dictionary

export default commonContent
```

### 3.3. Przykład: validation.content.ts

**Plik:** `/home/madeyskij/projects/gear-stack/src/shared/i18n/content/validation.content.ts`

```typescript
import { t, type Dictionary } from 'intlayer'

const validationContent = {
  key: 'validation',
  content: {
    required: t({ en: 'This field is required', pl: 'To pole jest wymagane' }),
    email: t({ en: 'Invalid email address', pl: 'Nieprawidłowy adres email' }),
    min: t({
      en: 'Must be at least {min} characters',
      pl: 'Musi mieć co najmniej {min} znaków',
    }),
    minLength: t({
      en: 'Must be at least {min} characters',
      pl: 'Musi mieć co najmniej {min} znaków',
    }),
    max: t({
      en: 'Must be at most {max} characters',
      pl: 'Może mieć maksymalnie {max} znaków',
    }),
    passwordMismatch: t({
      en: 'Passwords do not match',
      pl: 'Hasła nie są identyczne',
    }),
    // ... dodać resztę
  },
} satisfies Dictionary

export default validationContent
```

**Uwaga:** Wszystkie pozostałe shared content files (errors, navigation, footer, pages, pwa, fileUpload, markdown, premium) należy utworzyć analogicznie na podstawie `/home/madeyskij/projects/gear-stack/src/shared/i18n/locales/{en,pl}.ts`

## 4. Core composables

### 4.1. useLocale - migracja

**Plik:** `/home/madeyskij/projects/gear-stack/src/shared/i18n/composables/useLocale.ts`

Przepisać całkowicie:

```typescript
import { computed } from 'vue'
import { useLocale as useIntlayerLocale } from 'vue-intlayer'
import { LOCALE_STORAGE_KEY, type SupportedLocale } from '@/shared/config/config'

export interface ILocale {
  code: SupportedLocale
  label: string
}

const SUPPORTED_LOCALES: SupportedLocale[] = ['en', 'pl']
const LOCALE_LABELS: Record<SupportedLocale, string> = {
  en: 'English',
  pl: 'Polski',
}

export function useLocale() {
  const { locale, setLocale: setIntlayerLocale } = useIntlayerLocale()

  const currentLocale = computed<SupportedLocale>({
    get: () => locale.value as SupportedLocale,
    set: (newLocale: SupportedLocale) => {
      if (SUPPORTED_LOCALES.includes(newLocale)) {
        setIntlayerLocale(newLocale)
        localStorage.setItem(LOCALE_STORAGE_KEY, newLocale)
        document.documentElement.setAttribute('lang', newLocale)
      }
    },
  })

  const availableLocales = computed<ILocale[]>(() =>
    SUPPORTED_LOCALES.map((locale: SupportedLocale) => ({
      code: locale,
      label: LOCALE_LABELS[locale],
    }))
  )

  const nextLocale = computed<ILocale>(() => {
    const currentIndex = SUPPORTED_LOCALES.indexOf(currentLocale.value)
    const nextIndex = (currentIndex + 1) % SUPPORTED_LOCALES.length
    return availableLocales.value[nextIndex] ?? availableLocales.value[0]!
  })

  const setLocale = (newLocale: SupportedLocale) => {
    currentLocale.value = newLocale
  }

  const toggleLocale = () => {
    const currentIndex = SUPPORTED_LOCALES.indexOf(currentLocale.value)
    const nextIndex = (currentIndex + 1) % SUPPORTED_LOCALES.length
    const nextLocale = SUPPORTED_LOCALES[nextIndex]
    if (nextLocale) {
      currentLocale.value = nextLocale
    }
  }

  return {
    currentLocale,
    availableLocales,
    nextLocale,
    setLocale,
    toggleLocale,
  }
}
```

### 4.2. main.ts - integracja Intlayer

**Plik:** `/home/madeyskij/projects/gear-stack/src/main.ts`

Zmiany:

```typescript
// USUNĄĆ:
// import { i18n } from '@/i18n'

// DODAĆ:
import { installIntlayer } from 'vue-intlayer'

// USUNĄĆ:
// app.use(i18n)

// DODAĆ:
installIntlayer(app)

// Pozostałe integracje bez zmian (setHtmlLangAttribute można usunąć - Intlayer robi to automatycznie)
```

### 4.3. Router integration - page titles

**Plik:** `/home/madeyskij/projects/gear-stack/src/router/index.ts`

```typescript
import { getPageTitle } from './pageTitles'
import { LOCALE_STORAGE_KEY, type SupportedLocale } from '@/shared/config/config'

// USUNĄĆ:
// import { i18n } from '@/i18n'

router.afterEach((to) => {
  const metaTitle = to.meta.title as string | undefined
  if (metaTitle) {
    const currentLocale = (localStorage.getItem(LOCALE_STORAGE_KEY) as SupportedLocale) ?? 'en'
    const title = getPageTitle(metaTitle, currentLocale)
    document.title = `${title} | ${config.app.name}`
  } else {
    document.title = config.app.name
  }
})
```

## 5. Gear module (największy moduł)

### 5.1. Domain content files

**Plik:** `/home/madeyskij/projects/gear-stack/src/modules/gear/content/categories.content.ts`

```typescript
import { t, type Dictionary } from 'intlayer'

const categoriesContent = {
  key: 'gearCategories',
  content: {
    water: t({ en: 'Water', pl: 'Woda' }),
    food: t({ en: 'Food', pl: 'Jedzenie' }),
    shelter: t({ en: 'Shelter', pl: 'Schronienie' }),
    fire: t({ en: 'Fire', pl: 'Ogień' }),
    firstAid: t({ en: 'First Aid', pl: 'Pierwsza Pomoc' }),
    blades: t({ en: 'Blades', pl: 'Ostrza' }),
    tool: t({ en: 'Tools', pl: 'Narzędzia' }),
    tools: t({ en: 'Tools', pl: 'Narzędzia' }),
    light: t({ en: 'Light', pl: 'Światło' }),
    navigation: t({ en: 'Navigation', pl: 'Nawigacja' }),
    communication: t({ en: 'Communication', pl: 'Komunikacja' }),
    clothing: t({ en: 'Clothing', pl: 'Odzież' }),
    hygiene: t({ en: 'Hygiene', pl: 'Higiena' }),
    container: t({ en: 'Container', pl: 'Kontener' }),
    other: t({ en: 'Other', pl: 'Inne' }),
  },
} satisfies Dictionary

export default categoriesContent
```

**Podobnie utworzyć:**
- `containerTypes.content.ts`
- `itemStatuses.content.ts`
- `itemPriorities.content.ts`

### 5.2. Refactor composables

**Plik:** `/home/madeyskij/projects/gear-stack/src/modules/gear/composables/useCategoryLabel.ts`

```typescript
import { computed, type Reactive, type Ref, toRef } from 'vue'
import { useIntlayer } from 'vue-intlayer'
import { useGearSettings } from './useGearSettings'

export const useCategoryLabel = (categoryValue?: Ref<string> | Reactive<string> | string) => {
  const categories = useIntlayer('gearCategories')
  const { customCategories } = useGearSettings()

  const getCategoryLabel = (categoryValue: string): string => {
    const customCategory = customCategories.value.find(c => c.value === categoryValue)
    if (customCategory) return customCategory.value

    const normalizedCategory = categoryValue === 'tool' ? 'tools' : categoryValue
    return categories[normalizedCategory as keyof typeof categories] ?? categoryValue
  }

  const categoryLabel = computed<string | undefined>(() => {
    if (!categoryValue) return undefined
    return getCategoryLabel(toRef(categoryValue).value)
  })

  return { categoryLabel, getCategoryLabel }
}
```

**Podobnie zrefaktorować:**
- `useContainerTypeLabel.ts`
- Inne domain composables

### 5.3. Component-scoped content (przykłady)

Dla każdego komponentu i strony utworzyć `.content.ts` obok pliku `.vue`:

```
src/modules/gear/
├── pages/
│   ├── ContainersListPage.vue
│   ├── ContainersListPage.content.ts
│   ├── ContainerDetailPage.vue
│   ├── ContainerDetailPage.content.ts
│   └── ...
└── components/
    ├── ContainerCard.vue
    ├── ContainerCard.content.ts
    └── ...
```

**Przykład content file:**

```typescript
// ContainersListPage.content.ts
import { t, type Dictionary } from 'intlayer'

const containersListPageContent = {
  key: 'containersListPage',
  content: {
    title: t({ en: 'Gear Containers', pl: 'Kontenery sprzętu' }),
    createButton: t({ en: 'Create Container', pl: 'Utwórz kontener' }),
    emptyState: t({
      en: 'No containers yet. Create your first one!',
      pl: 'Brak kontenerów. Utwórz pierwszy!'
    }),
    // ... reszta tłumaczeń dla tej strony
  },
} satisfies Dictionary

export default containersListPageContent
```

### 5.4. Refactor komponentu (przykład)

**Przed:**
```vue
<!-- ContainersListPage.vue -->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div>
    <h1>{{ t('gear.page.title') }}</h1>
    <Button>{{ t('gear.container.create.button') }}</Button>
  </div>
</template>
```

**Po:**
```vue
<!-- ContainersListPage.vue -->
<script setup lang="ts">
import { useIntlayer } from 'vue-intlayer'

const content = useIntlayer('containersListPage')
</script>

<template>
  <div>
    <h1>{{ content.title }}</h1>
    <Button>{{ content.createButton }}</Button>
  </div>
</template>
```

## 6. Pozostałe moduły

Analogicznie jak Gear module:

### Auth module
- Utworzyć content files dla pages (LoginPage, RegisterPage, etc.)
- Refaktorować komponenty używające `useI18n()`

### Admin module
- Utworzyć content files
- Refaktorować admin dashboard components

### AI, Settings, User, Billing modules
- Każdy moduł analogicznie

## 7. Cleanup - usunięcie starych plików

Po pełnej migracji usunąć:

```
src/i18n/index.ts
src/shared/i18n/config/i18n.ts
src/shared/i18n/config/getPolishPluralizationRule.ts
src/shared/i18n/locales/en.ts
src/shared/i18n/locales/pl.ts
src/modules/admin/i18n/
src/modules/ai/i18n/
src/modules/auth/i18n/
src/modules/billing/i18n/
src/modules/gear/i18n/
src/modules/settings/i18n/
src/modules/user/i18n/
```

## 8. Etapy implementacji (chronologicznie)

### Faza 0: Przygotowanie (1-2 dni)
- [ ] Instalacja dependencies
- [ ] Konfiguracja (intlayer.config.ts, vite.config.ts, tsconfig.json)
- [ ] Helper functions (interpolate, plural, pageTitles)

### Faza 1: Shared translations (2-3 dni)
- [ ] Utworzenie struktury src/shared/i18n/content/
- [ ] Konwersja wszystkich shared content files

### Faza 2: Core integration (1-2 dni)
- [ ] useLocale refactor
- [ ] main.ts integration
- [ ] Router integration
- [ ] Testowanie localStorage/backend sync

### Faza 3: Gear module (3-5 dni)
- [ ] Domain content files
- [ ] Composables refactor
- [ ] Pages migration
- [ ] Components migration
- [ ] Testing

### Faza 4: Auth module (1-2 dni)
- [ ] Content files
- [ ] Components migration
- [ ] Testing flow

### Faza 5: Admin module (1-2 dni)
- [ ] Content files
- [ ] Components migration

### Faza 6: Pozostałe moduły (2-3 dni)
- [ ] AI module
- [ ] Settings module
- [ ] User module
- [ ] Billing module

### Faza 7: Cleanup (1 dzień)
- [ ] Usunięcie starych plików vue-i18n
- [ ] Weryfikacja brak referencji do vue-i18n

### Faza 8: Testing & QA (2-3 dni)
- [ ] E2E tests
- [ ] Locale switching tests
- [ ] Pluralizacja tests
- [ ] Performance testing
- [ ] Manual QA

### Faza 9: Production (1 dzień)
- [ ] Code review
- [ ] Dokumentacja update (CLAUDE.md)
- [ ] Deploy staging → production

## 9. Potencjalne problemy i rozwiązania

### Problem: Dynamiczne klucze translation
**Rozwiązanie:** Użyć bracket notation lub composables z mapowaniem

### Problem: Pluralizacja polska (4 formy)
**Rozwiązanie:** Custom helper function `pluralize()` jeśli Intlayer nie wspiera

### Problem: Global $t() w szablonach
**Rozwiązanie:** Dodać `useIntlayer()` w script setup

### Problem: 221 komponentów do migracji
**Rozwiązanie:** Priorytet: shared → pages → components; automatyzacja gdzie możliwe

## 10. Rollback plan

**W razie critical issues:**
1. Git revert commit(s) migracji
2. Deploy poprzedniej wersji
3. Tag working commit przed migracją jako backup

## 11. Success metrics

**Must have:**
- ✅ Wszystkie komponenty zmigrowane
- ✅ Obie locale (en, pl) działają
- ✅ Runtime locale switching działa
- ✅ localStorage + backend sync działa
- ✅ Zero błędów konsoli/TypeScript
- ✅ Wszystkie testy przechodzą

**Nice to have:**
- Bundle size reduction
- Improved load time
- Better DX (type safety, autocomplete)

## 12. Krytyczne pliki do implementacji

**Najwyższy priorytet:**
1. `intlayer.config.ts`
2. `vite.config.ts`
3. `src/main.ts`
4. `src/shared/i18n/composables/useLocale.ts`
5. `src/shared/i18n/content/common.content.ts`
6. `src/router/index.ts`
7. `src/router/pageTitles.ts`

---

## Źródła dokumentacji

- [Intlayer Vite+Vue Guide](https://intlayer.org/doc/environment/vite-and-vue)
- [vue-i18n vs Intlayer](https://intlayer.org/blog/vue-i18n-vs-intlayer)
- [Intlayer with vue-i18n](https://intlayer.org/blog/intlayer-with-vue-i18n)
- [Best i18n Tools for Vue](https://intlayer.org/blog/i18n-technologies/frameworks/vue)
