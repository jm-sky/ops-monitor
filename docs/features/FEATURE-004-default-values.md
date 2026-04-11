# FEATURE-004: Default Values for New Items

**Status:** ✅ Completed  
**Priority:** High  
**Category:** ⚡ Item Addition Improvements  
**Related:** ROADMAP.md - Usprawnienia dodawania przedmiotów

---

## 📋 Overview

Pre-fill new item forms with sensible default values to speed up item creation. Most fields should have defaults, especially required fields.

---

## 🎯 Goals

- Pre-fill form with defaults when creating new item
- Default values: weight (0.1 kg), quantity (1), status (owned), priority (medium)
- Category defaults to "other" or auto-detected (if category detection is implemented)
- Improve UX by reducing form filling time

---

## 🔍 Current State

- Item form exists (`ItemForm.vue` or `ItemFormFields.vue`)
- Form uses DTOs (`ICreateItemDto`)
- Validation schemas exist

**What's missing:**
- Default values in form initialization
- Default values utility/constants

---

## 📝 Implementation Plan

### Step 1: Create Default Values Utility

**File:** `src/modules/gear/utils/defaultValues.ts`

```typescript
import type { ICreateItemDto } from '../types/gear.types'

export const DEFAULT_ITEM_VALUES: Partial<ICreateItemDto> = {
  quantity: 1,
  weight: 0.1,  // 0.1 kg
  weightUnit: 'kg',
  status: 'owned',
  priority: 'medium',
  category: 'other',
}

export function getDefaultItemValues(): Partial<ICreateItemDto> {
  return { ...DEFAULT_ITEM_VALUES }
}
```

### Step 2: Update Item Form Component

**File:** `src/modules/gear/components/ItemForm.vue` or `ItemFormFields.vue`

Initialize form with defaults:

```vue
<script setup lang="ts">
import { getDefaultItemValues } from '../utils/defaultValues'

const formData = reactive<ICreateItemDto>({
  name: '',
  category: 'other',
  quantity: 1,
  weight: 0.1,
  weightUnit: 'kg',
  priority: 'medium',
  status: 'owned',
  ...getDefaultItemValues(),
})
</script>
```

Or if using form library (vee-validate):

```typescript
const initialValues = {
  name: '',
  ...getDefaultItemValues(),
}
```

### Step 3: Update Form Schema (if using Zod)

**File:** `src/modules/gear/utils/validation.ts`

Ensure schema allows defaults:

```typescript
export const itemSchema = z.object({
  name: z.string().min(1),
  category: z.string().default('other'),
  quantity: z.number().int().min(1).default(1),
  weight: z.number().min(0).default(0.1),
  weightUnit: z.enum(['g', 'kg']).default('kg'),
  priority: z.enum(['critical', 'high', 'medium', 'low']).default('medium'),
  status: z.enum(['owned', 'missing', 'toBuy']).default('owned'),
  // ... optional fields
})
```

### Step 4: Consider Auto-focus

**File:** `src/modules/gear/components/ItemForm.vue`

Auto-focus on name field (most important field):

```vue
<script setup lang="ts">
import { useFocus } from '@vueuse/core'

const nameInputRef = ref<HTMLInputElement>()
useFocus(nameInputRef, { initialValue: true })
</script>
```

---

## 📁 Files to Create/Modify

**New Files:**
- `src/modules/gear/utils/defaultValues.ts` - Default values utility

**Files to Modify:**
- `src/modules/gear/components/ItemForm.vue` or `ItemFormFields.vue` - Initialize with defaults
- `src/modules/gear/utils/validation.ts` - Update schema if needed

---

## 🎯 Default Values

| Field | Default Value | Notes |
|-------|--------------|-------|
| `quantity` | `1` | Most items are single |
| `weight` | `0.1` | 0.1 kg (100g) - reasonable default |
| `weightUnit` | `'kg'` | Kilograms |
| `status` | `'owned'` | Most items are already owned |
| `priority` | `'medium'` | Neutral priority |
| `category` | `'other'` | Or auto-detected (see FEATURE-005 |
| `notes` | `''` | Empty |
| `expirationDate` | `undefined` | Optional |

---

## ✅ Acceptance Criteria

- [ ] Form is pre-filled with defaults when creating new item
- [ ] Defaults are sensible and useful
- [ ] User can still change all default values
- [ ] Defaults don't interfere with editing existing items
- [ ] Form validation works with defaults
- [ ] Auto-focus on name field (optional but recommended)

---

## 🔗 Related Features

- Category recognition (FEATURE-005) - can override category default
- Quick edit (FEATURE-007) - different workflow

---

## 💡 Future Enhancements

- User-configurable defaults in settings
- Remember last used values per category
- Smart defaults based on container type

