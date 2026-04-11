# FEATURE-002: Category Icons

**Status:** ✅ Completed  
**Priority:** High  
**Category:** 🎨 UI/UX Improvements  
**Related:** ROADMAP.md - UI/UX Ulepszenia

---

## 📋 Overview

Add dedicated icons for each item category to improve visual recognition and user experience. Icons will be displayed in item lists, forms, and category selectors.

---

## 🎯 Goals

- Display category-specific icons for all default categories
- Use consistent icon system (Lucide Icons - already in project)
- Show icons in item lists, category selectors, and filters
- Support custom categories (fallback icon)

---

## 🔍 Current State

- Categories are defined in `src/modules/gear/types/gear.types.ts`
- Default categories: `water`, `food`, `shelter`, `fire`, `firstAid`, `tools`, `navigation`, `communication`, `clothing`, `hygiene`, `other`
- Custom categories are supported (string type)
- `lucide-vue-next` is already installed
- Items are displayed in `ItemsTable.vue` component

---

## 📝 Implementation Plan

### Step 1: Create Icon Mapping Utility

**File:** `src/modules/gear/utils/categoryIcons.ts`

Create a utility that maps categories to Lucide icons:

```typescript
import type { Component } from 'vue'
import type { TGearItemCategory } from '../types/gear.types'
import {
  Droplet,        // water
  UtensilsCrossed, // food
  Tent,           // shelter
  Flame,          // fire
  HeartPulse,     // firstAid
  Wrench,         // tools
  Compass,        // navigation
  Radio,          // communication
  Shirt,          // clothing
  Sparkles,       // hygiene
  Package,        // other (default)
} from 'lucide-vue-next'

export const CATEGORY_ICONS: Record<string, Component> = {
  water: Droplet,
  food: UtensilsCrossed,
  shelter: Tent,
  fire: Flame,
  firstAid: HeartPulse,
  tools: Wrench,
  navigation: Compass,
  communication: Radio,
  clothing: Shirt,
  hygiene: Sparkles,
  other: Package,
}

export function getCategoryIcon(category: TGearItemCategory): Component {
  return CATEGORY_ICONS[category] ?? CATEGORY_ICONS.other
}
```

### Step 2: Create CategoryIcon Component

**File:** `src/modules/gear/components/CategoryIcon.vue`

Reusable component for displaying category icons:

```vue
<script setup lang="ts">
import type { TGearItemCategory } from '../types/gear.types'
import { getCategoryIcon } from '../utils/categoryIcons'

interface Props {
  category: TGearItemCategory
  size?: number
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
})

const IconComponent = computed(() => getCategoryIcon(props.category))
</script>

<template>
  <component
    :is="IconComponent"
    :size="size"
    :class="class"
  />
</template>
```

### Step 3: Update ItemsTable Component

**File:** `src/modules/gear/components/ItemsTable.vue`

Add icon column or display icon next to category name:

```vue
<script setup lang="ts">
import CategoryIcon from './CategoryIcon.vue'
// ... existing imports
</script>

<template>
  <!-- In column definition or cell render -->
  <div class="flex items-center gap-2">
    <CategoryIcon :category="item.category" :size="16" />
    <span>{{ $t(`gear.item.categories.${item.category}`) }}</span>
  </div>
</template>
```

### Step 4: Update Category Selector

**File:** `src/modules/gear/components/ItemFormFields.vue` or `ItemForm.vue`

Add icons to category select items:

```vue
<SelectItem value="water">
  <div class="flex items-center gap-2">
    <CategoryIcon category="water" :size="16" />
    <span>{{ $t('gear.item.categories.water') }}</span>
  </div>
</SelectItem>
```

### Step 5: Update Filters (if applicable)

**File:** `src/modules/gear/components/ItemsFilters.vue` (if exists)

Add icons to category filter options.

---

## 📁 Files to Create/Modify

**New Files:**
- `src/modules/gear/utils/categoryIcons.ts` - Icon mapping utility
- `src/modules/gear/components/CategoryIcon.vue` - Icon component

**Files to Modify:**
- `src/modules/gear/components/ItemsTable.vue` - Add icons to table
- `src/modules/gear/components/ItemFormFields.vue` or `ItemForm.vue` - Add icons to selector
- `src/modules/gear/utils/itemsColumns.ts` - Update column definitions if needed

---

## 🎨 Icon Selection

Suggested Lucide icons:
- `water` → `Droplet`
- `food` → `UtensilsCrossed`
- `shelter` → `Tent`
- `fire` → `Flame`
- `firstAid` → `HeartPulse` or `Cross`
- `tools` → `Wrench` or `Tool`
- `navigation` → `Compass`
- `communication` → `Radio` or `MessageSquare`
- `clothing` → `Shirt`
- `hygiene` → `Sparkles` or `Soap`
- `other` → `Package` or `Box`

**Note:** Review and adjust icons based on visual consistency and clarity.

---

## ✅ Acceptance Criteria

- [ ] All default categories have dedicated icons
- [ ] Icons are displayed in item list/table
- [ ] Icons are displayed in category selector
- [ ] Custom categories show fallback icon
- [ ] Icons are consistent in size and style
- [ ] Icons improve visual recognition
- [ ] Icons work with dark/light theme

---

## 🔗 Related Features

- Container color coding (FEATURE-003)
- Quick edit (FEATURE-007)

