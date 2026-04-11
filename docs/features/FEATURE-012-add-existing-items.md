# FEATURE-012: Add Existing Items to Container

**Status:** ✅ Completed (v0.22.0)  
**Priority:** High  
**Category:** ⚡ Item Addition Improvements  
**Related:** ROADMAP_OFFLINE.md - Dodawanie istniejących przedmiotów do kontenera, ROADMAP_ONLINE.md - Linkowanie przedmiotów

---

## 📋 Overview

Allow users to add existing items from other containers to the current container without manually re-entering data. Items can be linked between containers, enabling faster container building and avoiding duplicate data entry.

This feature implements the foundation for item linking that will be fully realized with backend support (see Future Enhancements).

---

## 🎯 Goals

- Add existing items to a container from a catalog of all items
- Link items between containers (foundation for backend linking)
- Fuzzy search for finding items by name
- Visual distinction between linked and non-linked items
- Fast container building using existing items
- Future-ready architecture for backend integration

---

## 🔍 Current State

**What exists:**
- Item creation form (`ItemFormPage.vue`, `ItemFormFields.vue`)
- Function to get all items from all containers (`getAllItems()`)
- Navigation to item creation: `/gear/${containerId}/items/new`
- Item data structure (`IGearItem`)

**What's missing:**
- Toggle between "New Item" and "From Catalog" modes in ItemFormPage
- ComboBox/Autocomplete with all existing items
- Item linking mechanism (`linkedItemId` field)
- Visual indicators for linked items
- Filtering logic to exclude items already in current container

---

## 📝 Implementation Plan

### Step 1: Add `linkedItemId` to Item Type

**File:** `src/modules/gear/types/gear.types.ts`

```typescript
export interface IGearItem {
  id: TUUID
  linkedItemId?: TUUID  // Reference to original item when linked
  // ... rest of fields
}
```

**Why:** This field enables item linking. In localStorage, it references the original item. When backend is added, this will map to the global `itemId` from the `gear_items` table.

### Step 2: Add Tabs to ItemFormPage

**File:** `src/modules/gear/pages/ItemFormPage.vue`

- Add Tabs component at the top (before form)
- Two tabs: "New Item" and "From Catalog"
- When switching tabs, reset form
- Default to "New Item" tab

### Step 3: Create ComboBox for Item Selection

**File:** `src/modules/gear/components/ItemFormFields.vue` or new component

- Add ComboBox/Autocomplete for "From Catalog" mode
- Display format: Item name (with category icon) + Container name (in badge on right)
- Show category icon next to item name
- Fuzzy search by item name
- Sort alphabetically
- Exclude items already in current container
- Optionally show preview (weight, brand, color) in tooltip/popover

### Step 4: Create Service Functions for Item Catalog

**File:** `src/modules/gear/services/gearService.ts`

```typescript
/**
 * Get all items from all containers for catalog/autocomplete
 * Excludes items from specified container
 */
getAllItemsForCatalog(excludeContainerId?: TUUID): IGearItemWithContainer[]

/**
 * Get item by ID with container information
 */
getItemWithContainer(itemId: TUUID): IGearItemWithContainer | undefined
```

**File:** `src/modules/gear/utils/getAllItems.ts` (extend existing)

- Add function to format items for ComboBox
- Include container name, category icon info
- Support filtering by container

### Step 5: Handle Item Selection and Linking

**File:** `src/modules/gear/pages/ItemFormPage.vue`

- When item is selected from catalog:
  - Pre-fill form with all fields from selected item
  - Set `linkedItemId` to original item's ID
  - Allow user to edit before saving
  - When saving, create new item with `linkedItemId` reference

### Step 6: Update Item Creation Logic

**File:** `src/modules/gear/services/gearService.ts`

- Update `createItem` to handle `linkedItemId`
- When creating linked item:
  - Generate new `id` (unique in container context)
  - Set `linkedItemId` to reference original
  - Copy all fields from original item (user can modify before save)

### Step 7: Add Visual Indicators for Linked Items

**File:** `src/modules/gear/components/ItemsTable.vue` (or similar)

- Show icon/badge for linked items
- Tooltip showing original container name
- Optionally show link icon next to item name

---

## 🏗️ Technical Architecture

### Item Linking Strategy (Future-Ready)

**Current Implementation (localStorage):**
```typescript
interface IGearItem {
  id: TUUID              // Unique ID in container context
  linkedItemId?: TUUID   // Reference to original item
  // ... other fields
  
  // Quantity/status can differ per container
  // but name, weight, brand, color are shared
}
```

**How it works:**
- User selects existing item → Form is pre-filled
- User can modify fields (quantity, status, etc.) before saving
- On save: New item created with new `id`, but `linkedItemId` points to original
- Each container has its own item instance (quantity/status can differ)
- Other fields (name, weight, brand, color) are copied but can be edited independently

**Future Backend Migration:**
When backend is implemented with full linking:

1. **Backend Structure:**
   ```sql
   -- Global items table
   CREATE TABLE gear_items (
       id VARCHAR(36) PRIMARY KEY,  -- Global item ID
       name VARCHAR(255) NOT NULL,
       category VARCHAR(50) NOT NULL,
       weight FLOAT NOT NULL,
       -- ... shared fields
   );
   
   -- Container-item relationships
   CREATE TABLE container_items (
       container_id VARCHAR(36),
       item_id VARCHAR(36),
       quantity INTEGER,
       status VARCHAR(20),
       -- ... container-specific fields
       PRIMARY KEY (container_id, item_id)
   );
   ```

2. **Migration Path:**
   - `linkedItemId` in localStorage → `itemId` in backend's `container_items`
   - Local `id` is removed (only used during localStorage phase)
   - Changes to linked item in one container update all references (via backend)

3. **Benefits:**
   - No structural changes needed to `IGearItem` type
   - Easy migration: `linkedItemId` maps directly to `itemId` in backend
   - Forward compatible: works now and later
   - Backward compatible: can add linking gradually

---

## 📁 Files to Create/Modify

**New Files:**
- `src/modules/gear/components/ItemCatalogComboBox.vue` - ComboBox for selecting existing items (optional, can be in ItemFormFields)
- `src/modules/gear/utils/itemCatalog.ts` - Utilities for item catalog operations

**Files to Modify:**
- `src/modules/gear/types/gear.types.ts` - Add `linkedItemId?: TUUID` to `IGearItem`
- `src/modules/gear/pages/ItemFormPage.vue` - Add tabs, handle mode switching, handle item selection
- `src/modules/gear/components/ItemFormFields.vue` - Add ComboBox for catalog mode
- `src/modules/gear/services/gearService.ts` - Add catalog functions, handle `linkedItemId` in createItem
- `src/modules/gear/composables/useGear.ts` - Expose catalog functions
- `src/modules/gear/utils/getAllItems.ts` - Add formatting functions for catalog
- `src/modules/gear/components/ItemsTable.vue` - Add visual indicator for linked items
- `src/modules/gear/i18n/index.ts` - Add translations for catalog mode

---

## 🎨 UI/UX Details

### Tabs in ItemFormPage

```
┌─────────────────────────────────┐
│ [New Item] [From Catalog]       │  ← Tabs at top
├─────────────────────────────────┤
│                                 │
│  Form fields here...            │
│                                 │
└─────────────────────────────────┘
```

### ComboBox Format

**Display:**
```
[📦] Latarka              [Plecak główny]
     ^icon  ^name             ^container badge
```

**Details:**
- Category icon on left
- Item name in middle
- Container name in badge on right
- Fuzzy search by name
- Tooltip shows: weight, brand, color (optional)

### Form Behavior

- **New Item tab:** Normal form (current behavior)
- **From Catalog tab:**
  - ComboBox at top (replaces name field initially)
  - When item selected: Form pre-filled, ComboBox hidden, normal form shown
  - User can edit any fields before saving
  - Switch back to "New Item": Form resets

---

## 📊 Data Flow

### Adding Linked Item

1. User opens `/gear/${containerId}/items/new`
2. Switches to "From Catalog" tab
3. Types in ComboBox → Fuzzy search shows matching items
4. Selects item → Form pre-fills with item data, `linkedItemId` set
5. User can edit fields (e.g., change quantity or status)
6. Clicks Save → `createItem` called with:
   - New `id` (generated)
   - `linkedItemId` (original item's ID)
   - All other fields (from form)

### Item Structure Example

**Original Item (in Container A):**
```typescript
{
  id: "item-1",
  name: "Latarka",
  quantity: 1,
  status: "owned",
  // ... no linkedItemId
}
```

**Linked Item (in Container B):**
```typescript
{
  id: "item-2",              // New unique ID
  linkedItemId: "item-1",    // Reference to original
  name: "Latarka",           // Copied from original
  quantity: 2,               // User changed this
  status: "toBuy",           // User changed this
  // ... other fields copied but can be different
}
```

---

## ✅ Acceptance Criteria

- [ ] Tabs "New Item" and "From Catalog" are visible at top of ItemFormPage
- [ ] Switching tabs resets the form
- [ ] "From Catalog" tab shows ComboBox with all existing items
- [ ] ComboBox displays: category icon + item name + container badge
- [ ] Fuzzy search works by item name
- [ ] Items already in current container are excluded from list
- [ ] List is sorted alphabetically
- [ ] Selecting item pre-fills form with all fields
- [ ] User can edit pre-filled fields before saving
- [ ] Saving creates new item with `linkedItemId` reference
- [ ] Linked items show visual indicator in item list
- [ ] Tooltip shows original container name for linked items
- [ ] Works correctly with existing item creation flow

---

## 🔗 Related Features

- **Default values (FEATURE-004)** - Pre-filled form uses defaults when creating from catalog
- **Category recognition (FEATURE-005)** - Category icons shown in ComboBox
- **Quick edit (FEATURE-007)** - Different workflow for inline editing
- **Item linking (ROADMAP_ONLINE)** - Full linking implementation with backend

---

## 🚀 Future Enhancements

### Backend Integration (ROADMAP_ONLINE)

When backend is implemented:

1. **Structure Changes:**
   - Items stored in global `gear_items` table
   - `container_items` table for relationships
   - `linkedItemId` becomes `itemId` in backend

2. **Full Linking:**
   - Changes to linked item in one container update all references
   - Backend handles synchronization
   - Visual indicators show live links

3. **Migration:**
   - Existing `linkedItemId` references migrate to `container_items`
   - No data loss
   - Seamless transition

### Additional Features

- Filter by container source in ComboBox
- Filter by category in ComboBox
- Group items by container in ComboBox
- Bulk add multiple items at once
- "Unlink" item (convert linked item to independent copy)
- Show all containers containing a specific item
- Visual graph of item relationships

---

## 📝 Notes

- **Why `linkedItemId` now?** Prepares for backend linking without requiring structural changes later
- **Why not full linking now?** localStorage limitations - true linking requires backend/DB
- **Quantity/Status differences:** Allowed per container even when linked
- **Future compatibility:** Design allows easy migration to backend structure

