# FEATURE-017: Currency Support (Obsługa waluty)

**Status:** ✅ Completed
**Priority:** Medium
**Complexity:** Medium
**Category:** 📝 Data Model / 💰 Financial
**Related Features:** FEATURE-011 (Markdown Import/Export)

---

## 📋 Overview

Add comprehensive currency support to the application, allowing users to:
- Set default currency in user settings
- Select currency for containers and items in forms
- Display prices with proper currency formatting
- Show currency in tables, statistics, and exports
- Auto-detect currency based on user locale

This feature extends the existing price field (which already exists in the data model) with full UI support and proper formatting.

---

## 🎯 Goals

1. **Default Currency Setting** - User can set default currency in settings (localStorage)
2. **Currency Selection in Forms** - Currency picker in container and item forms
3. **Price Formatting** - Proper currency formatting using `Intl.NumberFormat`
4. **Display in UI** - Show currency in tables, statistics, and container details
5. **Locale Detection** - Auto-detect default currency based on browser locale (PL → PLN, others → EUR)
6. **Export Support** - Include currency in markdown export (already partially implemented)

---

## 📐 Design

### Current State

- ✅ `price` field exists in `IGearItem` and `IGearContainer` types
- ✅ `currency` field exists in types (string | null)
- ✅ Currency parsing in markdown import (PLN, USD, EUR, GBP)
- ❌ No UI for currency selection in forms
- ❌ No currency formatting in display
- ❌ No default currency setting

### Proposed Changes

#### 1. Default Currency Setting

**Location:** Settings page (`PreferencesSettingsCard.vue`)

- Add currency selector dropdown
- Options: PLN, EUR, USD, GBP (and potentially more)
- Store in `IGearSettings` as `defaultCurrency: string`
- Auto-detect based on locale on first use:
  - `pl` → `PLN`
  - `en-US` → `USD`
  - `en-GB` → `GBP`
  - Others → `EUR`

#### 2. Currency Selection in Forms

**Location:** 
- `ItemFormFields.vue` - Extended Fields section
- `ContainerFormFields.vue` - Extended Fields section

**UI:**
- Add currency dropdown next to price input
- Show currency symbol/code (e.g., "PLN" or "zł")
- Default to user's default currency
- Allow changing currency per item/container

**Layout:**
```
Price and Currency (grid 2 columns):
[Price Input] [Currency Select]
```

#### 3. Currency Formatting

**Utility:** `src/modules/gear/utils/currencyFormatter.ts`

- Function: `formatCurrency(amount: number, currency: string): string`
- Uses `Intl.NumberFormat` for proper formatting
- Handles:
  - Decimal places (2 for most currencies)
  - Thousands separators
  - Currency symbol placement
  - Locale-specific formatting

**Examples:**
- `100.50 PLN` → `100,50 PLN` (Polish locale)
- `100.50 USD` → `$100.50` (US locale)
- `100.50 EUR` → `100,50 €` (European locale)

#### 4. Display in UI

**Tables:**
- `ItemsTable.vue` - Show price with currency in price column
- Format: `formatCurrency(item.price, item.currency || defaultCurrency)`

**Statistics:**
- `ContainerHeader.vue` - Show total price with currency
- Handle multiple currencies (show per currency or convert)

**Container Details:**
- Show currency next to price in item cards
- Show currency in extended fields display

#### 5. Markdown Export

**Already implemented:**
- Currency parsing in import ✅
- Currency field in data model ✅

**To add:**
- Option to show prices in export (separate feature: FEATURE-020)
- Format prices with currency in export

---

## 🛠️ Implementation Plan

### Phase 1: Default Currency Setting

**Files:**
- `src/modules/gear/types/gearSettings.types.ts`
- `src/modules/gear/services/gearSettingsService.ts`
- `src/modules/gear/store/useGearSettingsStore.ts`
- `src/modules/settings/components/PreferencesSettingsCard.vue`
- `src/modules/settings/i18n/locales/*.ts`

**Changes:**
1. Add `defaultCurrency: string` to `IGearSettings` interface
2. Add default currency to settings service (load/save)
3. Add currency selector to preferences settings card
4. Auto-detect currency on first load based on locale
5. Add translations for currency labels

**Default Currency Detection:**
```typescript
function detectDefaultCurrency(locale: string): string {
  if (locale.startsWith('pl')) return 'PLN'
  if (locale.startsWith('en-US')) return 'USD'
  if (locale.startsWith('en-GB')) return 'GBP'
  return 'EUR' // Default for other locales
}
```

### Phase 2: Currency Formatter Utility

**Files:**
- `src/modules/gear/utils/currencyFormatter.ts` (new)

**Implementation:**
```typescript
export function formatCurrency(
  amount: number,
  currency: string,
  locale?: string
): string {
  const formatter = new Intl.NumberFormat(locale || 'pl-PL', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return formatter.format(amount)
}

export const SUPPORTED_CURRENCIES = [
  { value: 'PLN', label: 'PLN (zł)', symbol: 'zł' },
  { value: 'EUR', label: 'EUR (€)', symbol: '€' },
  { value: 'USD', label: 'USD ($)', symbol: '$' },
  { value: 'GBP', label: 'GBP (£)', symbol: '£' },
] as const
```

### Phase 3: Currency Selection in Forms

**Files:**
- `src/modules/gear/components/ItemFormFields.vue`
- `src/modules/gear/components/ContainerFormFields.vue`
- `src/modules/gear/composables/useGearSettings.ts`

**Changes:**
1. Import currency formatter and supported currencies
2. Add currency field to form (next to price field)
3. Use `Select` component for currency dropdown
4. Default to `item.currency || container.currency || defaultCurrency`
5. Update form validation if needed

**Layout Example:**
```vue
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
  <FormField v-slot="{ componentField }" name="price">
    <FormItem>
      <FormLabel :label="$t('gear.item.price')" />
      <Input
        v-bind="componentField"
        type="number"
        min="0"
        step="0.01"
      />
    </FormItem>
  </FormField>
  
  <FormField v-slot="{ value, handleChange }" name="currency">
    <FormItem>
      <FormLabel :label="$t('gear.item.currency')" />
      <Select :value="value || defaultCurrency" @update:value="handleChange">
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem
            v-for="curr in SUPPORTED_CURRENCIES"
            :key="curr.value"
            :value="curr.value"
          >
            {{ curr.label }}
          </SelectItem>
        </SelectContent>
      </Select>
    </FormItem>
  </FormField>
</div>
```

### Phase 4: Display Currency in UI

**Files:**
- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/components/ContainerHeader.vue`
- `src/modules/gear/pages/ContainerDetailPage.vue`
- `src/modules/gear/pages/ShoppingPlanningPage.vue` (already uses currency)

**Changes:**
1. Import `formatCurrency` utility
2. Import `useGearSettings` for default currency
3. Format prices using `formatCurrency(price, currency || defaultCurrency)`
4. Update all price displays to include currency

**Example:**
```vue
<template>
  <span>{{ formatCurrency(item.price, item.currency || defaultCurrency) }}</span>
</template>

<script setup>
import { formatCurrency } from '@/modules/gear/utils/currencyFormatter'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'

const { defaultCurrency } = useGearSettings()
</script>
```

### Phase 5: Statistics with Multiple Currencies

**Files:**
- `src/modules/gear/utils/containerCalculations.ts`
- `src/modules/gear/components/ContainerHeader.vue`

**Changes:**
1. Calculate total price per currency
2. Display totals grouped by currency
3. Or show primary currency total with note about other currencies

**Example Display:**
```
Total Price: 1,234.56 PLN
Other currencies: 50.00 USD, 100.00 EUR
```

---

## 📊 Data Flow

### Currency Selection Flow

```
User opens form
  ↓
Form loads defaultCurrency from settings
  ↓
If item/container has currency → use it
Else → use defaultCurrency
  ↓
User can change currency in dropdown
  ↓
Save currency with price
```

### Display Flow

```
Item/Container with price and currency
  ↓
formatCurrency(price, currency || defaultCurrency)
  ↓
Formatted string displayed in UI
```

---

## 🔍 Technical Details

### Currency Storage

- Currency stored as ISO 4217 code (string): `PLN`, `EUR`, `USD`, `GBP`
- Nullable field (can be null if price not set)
- Default currency stored in user settings (localStorage)

### Formatting Rules

- Use `Intl.NumberFormat` for locale-aware formatting
- Always show 2 decimal places for currency
- Currency symbol placement depends on locale:
  - Polish: `100,50 PLN`
  - US: `$100.50`
  - European: `100,50 €`

### Supported Currencies

Initially: PLN, EUR, USD, GBP
Can be extended later with more currencies.

---

## 🧪 Testing

### Manual Test Cases

1. **Default Currency Setting**
   - ✅ Set default currency in settings
   - ✅ Default currency persists after reload
   - ✅ Auto-detection works for different locales

2. **Currency in Forms**
   - ✅ Currency dropdown appears next to price
   - ✅ Default currency is pre-selected
   - ✅ Can change currency per item/container
   - ✅ Currency saved correctly

3. **Price Formatting**
   - ✅ Prices formatted correctly for each currency
   - ✅ Decimal places correct (2 for all currencies)
   - ✅ Thousands separators correct
   - ✅ Currency symbol in correct position

4. **Display in UI**
   - ✅ Prices show with currency in tables
   - ✅ Prices show with currency in statistics
   - ✅ Prices show with currency in container details
   - ✅ Default currency used when item currency is null

5. **Multiple Currencies**
   - ✅ Items with different currencies display correctly
   - ✅ Statistics handle multiple currencies
   - ✅ Export includes currency (FEATURE-020)

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Currency support for items and containers
- Default currency setting in user preferences
- Currency selector in item and container forms
- Proper currency formatting using Intl.NumberFormat
- Auto-detection of default currency based on browser locale
- Currency display in tables, statistics, and container details
- Support for PLN, EUR, USD, GBP currencies
```

---

## 🚀 Future Enhancements

### Currency Conversion
- Real-time currency conversion
- Show prices in multiple currencies
- Historical exchange rates

### More Currencies
- Add more supported currencies
- User-defined currency list

### Currency Statistics
- Total value per currency
- Currency distribution charts
- Cost analysis by currency

---

## 📝 Notes

- Uses existing `currency` field in data model - no schema changes needed
- Currency is optional - backward compatible
- Default currency stored in localStorage (offline-first)
- Can be extended to sync with backend in future
- Currency formatting respects user's locale
- Markdown import already supports currency parsing ✅

---

## 🔗 Related Documentation

- [FEATURE-011](./FEATURE-011-markdown-import-export.md) - Markdown Import/Export
- [FEATURE-020](./FEATURE-020-price-display-in-export.md) - Price Display in Export
- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Offline Features Roadmap
- Currency formatter: `src/modules/gear/utils/currencyFormatter.ts` (new)
- Settings: `src/modules/gear/types/gearSettings.types.ts`

