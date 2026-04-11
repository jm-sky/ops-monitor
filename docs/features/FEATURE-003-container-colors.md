# FEATURE-003: Container Color Coding

**Status:** ✅ Completed  
**Priority:** Medium  
**Category:** 🎨 UI/UX Improvements  
**Related:** ROADMAP.md - UI/UX Ulepszenia

---

## 📋 Overview

Allow users to assign colors to containers for visual distinction. Containers can be colored with predefined color options, making it easier to identify and organize different containers at a glance.

---

## 🎯 Goals

- Add color field to container model
- Provide predefined color palette
- Display container color in list view
- Allow color selection in container form
- Visual distinction improves UX

---

## 🔍 Current State

- Container type is defined in `IGearContainer` interface
- Container form exists for create/edit
- Container list displays containers

**What's missing:**
- Color field in container model
- Color picker/selector in form
- Visual color display in list

---

## 📝 Implementation Plan

### Step 1: Update Types

**File:** `src/modules/gear/types/gear.types.ts`

Add color type and field:

```typescript
// Container color options
export type TContainerColor =
  | 'default'  // No color (gray/neutral)
  | 'blue'
  | 'green'
  | 'red'
  | 'yellow'
  | 'purple'
  | 'orange'
  | 'pink'
  | 'teal'
  | 'indigo'

// Update IGearContainer interface
export interface IGearContainer {
  id: TUUID
  name: string
  description?: string
  type: TGearContainerType
  color?: TContainerColor  // Optional, defaults to 'default'
  items: IGearItem[]
  createdAt: TDateTime
  updatedAt: TDateTime
}

// Update DTOs
export interface ICreateContainerDto {
  name: string
  description?: string
  type: TGearContainerType
  color?: TContainerColor
}

export interface IUpdateContainerDto {
  name?: string
  description?: string
  type?: TGearContainerType
  color?: TContainerColor
}
```

### Step 2: Create Color Utilities

**File:** `src/modules/gear/utils/containerColors.ts`

```typescript
import type { TContainerColor } from '../types/gear.types'

export const CONTAINER_COLORS: TContainerColor[] = [
  'default',
  'blue',
  'green',
  'red',
  'yellow',
  'purple',
  'orange',
  'pink',
  'teal',
  'indigo',
]

export const COLOR_CLASSES: Record<TContainerColor, string> = {
  default: 'bg-gray-100 border-gray-300 text-gray-800',
  blue: 'bg-blue-100 border-blue-300 text-blue-800',
  green: 'bg-green-100 border-green-300 text-green-800',
  red: 'bg-red-100 border-red-300 text-red-800',
  yellow: 'bg-yellow-100 border-yellow-300 text-yellow-800',
  purple: 'bg-purple-100 border-purple-300 text-purple-800',
  orange: 'bg-orange-100 border-orange-300 text-orange-800',
  pink: 'bg-pink-100 border-pink-300 text-pink-800',
  teal: 'bg-teal-100 border-teal-300 text-teal-800',
  indigo: 'bg-indigo-100 border-indigo-300 text-indigo-800',
}

export const COLOR_DOT_CLASSES: Record<TContainerColor, string> = {
  default: 'bg-gray-400',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  red: 'bg-red-500',
  yellow: 'bg-yellow-500',
  purple: 'bg-purple-500',
  orange: 'bg-orange-500',
  pink: 'bg-pink-500',
  teal: 'bg-teal-500',
  indigo: 'bg-indigo-500',
}
```

### Step 3: Update Container Form

**File:** `src/modules/gear/components/ContainerForm.vue` or `ContainerFormFields.vue`

Add color selector:

```vue
<FormField v-slot="{ value, handleChange }" name="color">
  <FormItem>
    <FormLabel :label="$t('gear.container.color')" />
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="color in CONTAINER_COLORS"
        :key="color"
        type="button"
        :class="[
          'size-10 rounded-full border-2 transition-all',
          COLOR_DOT_CLASSES[color],
          value === color ? 'ring-2 ring-offset-2 ring-gray-400' : 'opacity-50 hover:opacity-75'
        ]"
        @click="handleChange(color)"
        :aria-label="color"
      />
    </div>
  </FormItem>
</FormField>
```

### Step 4: Update Container Card/List

**File:** `src/modules/gear/components/ContainerCard.vue` or list component

Display color:

```vue
<div
  :class="[
    'border-l-4 rounded-lg p-4',
    COLOR_CLASSES[container.color ?? 'default']
  ]"
>
  <!-- Container content -->
</div>
```

Or use color dot:

```vue
<div class="flex items-center gap-2">
  <div
    :class="[
      'size-3 rounded-full',
      COLOR_DOT_CLASSES[container.color ?? 'default']
    ]"
  />
  <span>{{ container.name }}</span>
</div>
```

### Step 5: Update Validation Schema

**File:** `src/modules/gear/utils/validation.ts`

Add color to schema if using Zod:

```typescript
containerSchema = z.object({
  // ... existing fields
  color: z.enum(['default', 'blue', 'green', ...]).optional(),
})
```

### Step 6: Migration (if needed)

If containers already exist, default color to 'default' or handle migration.

---

## 📁 Files to Create/Modify

**New Files:**
- `src/modules/gear/utils/containerColors.ts` - Color utilities

**Files to Modify:**
- `src/modules/gear/types/gear.types.ts` - Add color type and field
- `src/modules/gear/components/ContainerForm.vue` - Add color selector
- `src/modules/gear/components/ContainerCard.vue` - Display color
- `src/modules/gear/utils/validation.ts` - Add color validation
- `src/modules/gear/i18n/` - Add translations for color labels

---

## 🎨 Color Palette

Predefined colors (Tailwind CSS classes):
- Default (gray) - neutral/no color
- Blue - calm, reliable
- Green - nature, ready
- Red - urgent, important
- Yellow - warning, attention
- Purple - premium, special
- Orange - energetic, active
- Pink - personal, custom
- Teal - organized, clean
- Indigo - professional, structured

---

## ✅ Acceptance Criteria

- [ ] Color field added to container model
- [ ] Color selector in container form
- [ ] Colors displayed in container list
- [ ] Default color works for existing containers
- [ ] Color persists correctly
- [ ] Colors are visually distinct
- [ ] Works with dark/light theme
- [ ] Translations for color labels

---

## 🔗 Related Features

- Category icons (FEATURE-002)
- Container nesting (FEATURE-004)

---


### Updated Color Utilities (summary)

- `CONTAINER_COLORS` – lista powyższych kolorów.
- `COLOR_DOT_CLASSES` – używa HEX (np. `coyote: #8B6F47`, `olive: #556B2F`, `black: #111111`) dobranych tak, żeby przypominały realne materiały (cordura, plecaki, odzież).
- `COLOR_TEXT_CLASSES`, `COLOR_BORDER_CLASSES` – używają klas Tailwind możliwie zbliżonych do powyższych HEX, ale z priorytetem na kontrast i czytelność w light/dark theme.

### Why These Colors?

- Paleta jest inspirowana realnym gear’em: coyote/khaki/olive/tan/brown dla sprzętu taktycznego, forestGreen/navy/jeans/gray/black/orange dla typowych kolorów ubrań i ekwipunku.
- Kropka pokazuje **„realny” kolor kontenera**, a tekst i ramka są spójne z kropką, ale pozostają w granicach bezpiecznego UI (Tailwind).

### UX Guidelines

- Kolory mają być:
  - łatwo odróżnialne na liście kontenerów,
  - semantycznie sensowne dla outdoor/tactical,
  - działające poprawnie w trybie jasnym i ciemnym.
  