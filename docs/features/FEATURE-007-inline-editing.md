# FEATURE-007: Inline Editing (Edycja bezpośrednio na liście)

**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Large
**Category:** ✏️ Editing / 🎨 UI/UX
**Related Features:** None

---

## 📋 Overview

Add ability to edit items directly in the table without opening a form. Users can quickly modify item properties inline, similar to LighterPack's approach where all actions are available directly from table rows.

This feature significantly improves UX by reducing friction when making quick edits to items.

---

## 🎯 Goals

1. **Edit Mode Toggle** - Add `editMode` boolean setting (stored in localStorage)
2. **Inline Editing** - Edit basic fields directly in table rows
3. **Quick Actions** - Access common actions directly from row
4. **Add Items Inline** - Add new items directly in table (without form)
5. **LighterPack Pattern** - All actions visible and accessible from row

---

## 📐 Design

### Edit Mode Toggle

**Proposal:**
- Add `editMode: boolean` setting stored in localStorage
- `editMode: true` → Inline editing enabled (cells become editable)
- `editMode: false` → Current behavior (read-only, click to navigate/edit)

**Storage:**
- Key: `gear-stack:items-table-edit-mode` (or similar)
- Default: `false` (backward compatible)
- Toggle location: Container header or table toolbar

**Implementation Approach:**

#### Recommended: Single Component with Separated Edit Logic
- Keep single `ItemsTable.vue` component (clean display logic only)
- Add `editMode` prop/computed from localStorage
- **Editable cells in separate files** - All editing logic isolated
- Conditionally render editable vs read-only cells based on `editMode`
- Pros:
  - **Separation of concerns** - Display logic separate from edit logic
  - Single source of truth for table structure
  - Shared logic (sorting, filtering, etc.) in one place
  - Easy to maintain - edit logic doesn't clutter display component
  - Editable cells can be tested independently
- Structure:
  - `ItemsTable.vue` - Clean display, sorting, filtering, pagination
  - `ItemsTableEditableNameCell.vue` - Edit logic for name
  - `ItemsTableEditableQuantityCell.vue` - Edit logic for quantity
  - `useInlineItemEditing.ts` - Shared composable for edit operations (optional)

**Recommendation:** Single component with editable cells in separate files - Best balance of separation and maintainability.

---

## 🛠️ Implementation Plan

### Phase 1: Edit Mode Toggle

**Files:**
- `src/shared/config/config.ts` - Add storage key constant
- `src/modules/gear/composables/useItemsTableEditMode.ts` - New composable for edit mode state
- `src/modules/gear/components/ItemsTable.vue` - Add edit mode support
- `src/modules/gear/components/ContainerHeader.vue` - Add toggle button

**Steps:**
1. Create storage key constant: `ITEMS_TABLE_EDIT_MODE_KEY`
2. Create `useItemsTableEditMode` composable:
   ```typescript
   export function useItemsTableEditMode() {
     const editMode = ref<boolean>(loadEditMode())
     
     function loadEditMode(): boolean {
       // Load from localStorage, default false
     }
     
     function toggleEditMode() {
       editMode.value = !editMode.value
       // Save to localStorage
     }
     
     return { editMode, toggleEditMode }
   }
   ```
3. Add toggle button in `ContainerHeader` (or table toolbar)
4. Pass `editMode` to `ItemsTable` as prop
5. Conditionally render editable cells based on `editMode`

### Phase 2: Basic Inline Editing

**Fields to Edit Inline:**
- `name` - Text input (click to edit)
- `quantity` - Number input
- `weight` - Number input with unit selector
- `notes` - Textarea (expandable)
- `price` - Number input with currency selector

**Implementation:**
- Create editable cell components in separate files (keeps edit logic isolated):
  - `ItemsTableEditableNameCell.vue` - All name editing logic here
  - `ItemsTableEditableQuantityCell.vue` - All quantity editing logic here
  - `ItemsTableEditableWeightCell.vue` - All weight editing logic here
  - `ItemsTableEditableNotesCell.vue` - All notes editing logic here
  - `ItemsTableEditablePriceCell.vue` - All price editing logic here
- Optional: Create `useInlineItemEditing.ts` composable for shared edit operations:
  - Save/update logic
  - Loading states
  - Error handling
  - Validation
- Each editable cell component:
  - Contains all editing logic (state, handlers, validation)
  - Shows value when not editing
  - Shows input when clicked (or in edit mode)
  - Saves on Enter/Escape/Blur
  - Shows loading state during save
  - Handles validation
  - Emits update event to parent

### Phase 3: Quick Actions

**Actions to Add:**
- Upload photo (inline upload dialog)
- Add link (inline input)
- Mark as worn (toggle)
- Mark as consumable (toggle)
- Star item (toggle)
- Change status (dropdown)
- Change priority (dropdown)

**Implementation:**
- Extend `ItemsTableRowActions.vue` or create new component
- Show actions as icons/buttons in row
- Handle actions inline (no navigation)

### Phase 4: Add Items Inline

**Implementation:**
- Add "Add Item" row at top/bottom of table
- Inline form with required fields
- Save creates new item
- Cancel removes row

---

## 🔧 Technical Details

### Debounce Strategy

**Pattern:** Like LighterPack - debounced auto-save with immediate save option

**Implementation:**
- Use `useDebounceFn` from `@vueuse/core` (already used in project, e.g., `ContainerFormPage.vue`)
- Debounce delay: **500ms** (configurable)
- Two save modes:
  1. **Debounced auto-save** - After 500ms of no changes
  2. **Immediate save** - On Enter key (bypasses debounce)

**Benefits:**
- Reduces API calls when editing multiple fields
- Better UX (no flickering from multiple saves)
- User can force immediate save with Enter
- Pending changes indicator shows unsaved state

**Example Flow:**
1. User edits name → debounce timer starts (500ms)
2. User edits quantity → timer resets, starts again (500ms)
3. User edits weight → timer resets, starts again (500ms)
4. User stops editing → after 500ms → single save with all 3 changes
5. OR: User presses Enter → immediate save (cancels debounce)

### Edit Mode State Management

**Storage Key:**
```typescript
export const ITEMS_TABLE_EDIT_MODE_KEY = `${config.app.id}:items-table-edit-mode`
```

**Composable:**
```typescript
// src/modules/gear/composables/useItemsTableEditMode.ts
export function useItemsTableEditMode() {
  const editMode = ref<boolean>(loadEditMode())
  
  function loadEditMode(): boolean {
    try {
      const stored = localStorage.getItem(ITEMS_TABLE_EDIT_MODE_KEY)
      return stored === 'true'
    } catch {
      return false
    }
  }
  
  function toggleEditMode() {
    editMode.value = !editMode.value
    try {
      localStorage.setItem(ITEMS_TABLE_EDIT_MODE_KEY, String(editMode.value))
    } catch (error) {
      console.error('Error saving edit mode to storage:', error)
    }
  }
  
  watch(editMode, (newValue) => {
    try {
      localStorage.setItem(ITEMS_TABLE_EDIT_MODE_KEY, String(newValue))
    } catch (error) {
      console.error('Error saving edit mode to storage:', error)
    }
  })
  
  return { editMode, toggleEditMode }
}
```

### Component Structure

**ItemsTable.vue (Clean Display Logic):**
```vue
<script setup lang="ts">
import ItemsTableNameCell from './items-table/ItemsTableNameCell.vue'
import ItemsTableEditableNameCell from './items-table/ItemsTableEditableNameCell.vue'
// ... other cells

const { editMode } = useItemsTableEditMode()

// Clean separation - ItemsTable only handles display and routing
// All edit logic is in editable cell components
</script>

<template>
  <DataTable>
    <template #name="{ row }">
      <!-- Conditional rendering - edit logic is in separate components -->
      <ItemsTableEditableNameCell
        v-if="editMode"
        :item="row.original"
        @update="handleItemUpdate"
      />
      <ItemsTableNameCell
        v-else
        :item="row.original"
        @navigate="navigateToItem"
      />
    </template>
    <!-- Similar pattern for other columns -->
  </DataTable>
</template>
```

**File Structure:**
```
src/modules/gear/components/
├── ItemsTable.vue                    # Clean display, sorting, filtering
├── items-table/
│   ├── ItemsTableNameCell.vue         # Read-only name cell
│   ├── ItemsTableEditableNameCell.vue # Editable name cell (all edit logic here)
│   ├── ItemsTableQuantityCell.vue     # Read-only quantity
│   ├── ItemsTableEditableQuantityCell.vue # Editable quantity (all edit logic here)
│   └── ... (other cells)
└── composables/
    └── useInlineItemEditing.ts        # Optional: shared edit operations
```

### Editable Cell Pattern

**All edit logic isolated in editable cell component:**

**Example: ItemsTableEditableNameCell.vue (All edit logic here with debounce):**
```vue
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useInlineItemEditing } from '@/modules/gear/composables/useInlineItemEditing'

const props = defineProps<{ item: IGearItem }>()
const emit = defineEmits<{ update: [item: IGearItem] }>()

// Use shared composable with debounce support
const { isLoading, hasPendingChanges, saveImmediately, queueUpdate, cancelPending } = 
  useInlineItemEditing(props.item)

// All editing state and logic contained in this component
const isEditing = ref(false)
const editedName = ref(props.item.name)

// Watch for changes and queue for debounced save
watch(editedName, (newValue) => {
  if (isEditing.value && newValue !== props.item.name) {
    // Queue update for debounced save (500ms after last change)
    queueUpdate({ name: newValue.trim() })
  }
})

// Immediate save on Enter (bypasses debounce)
async function handleEnter() {
  if (editedName.value.trim() === '') {
    // Validation
    return
  }
  
  const updated = await saveImmediately({ name: editedName.value.trim() })
  if (updated) {
    emit('update', updated)
    isEditing.value = false
  }
}

// Cancel edit mode
function handleCancel() {
  cancelPending() // Cancel any pending debounced saves
  editedName.value = props.item.name
  isEditing.value = false
}

// Watch for external changes to item
watch(() => props.item.name, (newName) => {
  if (!isEditing.value) {
    editedName.value = newName
  }
})
</script>

<template>
  <div v-if="isEditing" class="flex items-center gap-2">
    <div class="relative flex-1">
      <Input 
        v-model="editedName" 
        @keyup.enter="handleEnter" 
        @keyup.esc="handleCancel"
        :disabled="isLoading"
        class="pr-8"
      />
      <!-- Pending changes indicator -->
      <span 
        v-if="hasPendingChanges && !isLoading"
        class="absolute right-2 top-1/2 -translate-y-1/2 size-2 bg-yellow-500 rounded-full"
        title="Unsaved changes"
      />
    </div>
    <Button size="sm" @click="handleEnter" :loading="isLoading">Save</Button>
    <Button size="sm" variant="ghost" @click="handleCancel" :disabled="isLoading">Cancel</Button>
  </div>
  <div 
    v-else 
    @click="isEditing = true" 
    class="cursor-pointer hover:underline hover:bg-muted/50 px-2 py-1 rounded"
  >
    {{ item.name }}
  </div>
</template>
```

**Alternative: Simpler approach without shared composable (each cell manages its own debounce):**
```vue
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useGearStore } from '@/modules/gear/store/useGearStore'

const props = defineProps<{ item: IGearItem }>()
const emit = defineEmits<{ update: [item: IGearItem] }>()

const store = useGearStore()
const isEditing = ref(false)
const editedName = ref(props.item.name)
const isLoading = ref(false)

// Debounced save (500ms)
const debouncedSave = useDebounceFn(async () => {
  if (editedName.value.trim() === props.item.name) return
  
  isLoading.value = true
  try {
    const updated = await store.updateItem(props.item.id, { name: editedName.value.trim() })
    emit('update', updated)
  } catch (error) {
    console.error('Failed to update item name:', error)
  } finally {
    isLoading.value = false
  }
}, 500)

// Watch for changes and trigger debounced save
watch(editedName, () => {
  if (isEditing.value) {
    debouncedSave()
  }
})

// Immediate save on Enter
async function handleEnter() {
  debouncedSave.cancel() // Cancel pending debounced save
  if (editedName.value.trim() === '') return
  
  isLoading.value = true
  try {
    const updated = await store.updateItem(props.item.id, { name: editedName.value.trim() })
    emit('update', updated)
    isEditing.value = false
  } catch (error) {
    console.error('Failed to update item name:', error)
  } finally {
    isLoading.value = false
  }
}

function handleCancel() {
  debouncedSave.cancel()
  editedName.value = props.item.name
  isEditing.value = false
}
</script>
```

**Optional: Shared Composable for Common Edit Operations with Debounce**

**useInlineItemEditing.ts:**
```typescript
import { ref } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import type { IGearItem, IUpdateItemDto } from '@/modules/gear/types/gear.types'

export function useInlineItemEditing(item: IGearItem) {
  const store = useGearStore()
  const isLoading = ref(false)
  const error = ref<Error | null>(null)
  const pendingUpdates = ref<IUpdateItemDto>({})
  const hasPendingChanges = ref(false)

  // Debounced save function (500ms delay)
  const debouncedSave = useDebounceFn(async () => {
    if (Object.keys(pendingUpdates.value).length === 0) {
      return
    }

    isLoading.value = true
    error.value = null
    
    try {
      const updates = { ...pendingUpdates.value }
      pendingUpdates.value = {} // Clear pending
      hasPendingChanges.value = false
      
      const updated = await store.updateItem(item.id, updates)
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to update item')
      // Keep pending updates on error (user can retry)
      return null
    } finally {
      isLoading.value = false
    }
  }, 500)

  // Immediate save (bypasses debounce, e.g., on Enter key)
  async function saveImmediately(updates: IUpdateItemDto): Promise<IGearItem | null> {
    // Cancel pending debounced save
    debouncedSave.cancel()
    
    isLoading.value = true
    error.value = null
    
    try {
      // Merge with any pending updates
      const allUpdates = { ...pendingUpdates.value, ...updates }
      pendingUpdates.value = {}
      hasPendingChanges.value = false
      
      const updated = await store.updateItem(item.id, allUpdates)
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to update item')
      return null
    } finally {
      isLoading.value = false
    }
  }

  // Queue update for debounced save
  function queueUpdate(updates: IUpdateItemDto) {
    pendingUpdates.value = { ...pendingUpdates.value, ...updates }
    hasPendingChanges.value = true
    debouncedSave() // Trigger debounced save
  }

  // Cancel pending changes
  function cancelPending() {
    debouncedSave.cancel()
    pendingUpdates.value = {}
    hasPendingChanges.value = false
  }

  return {
    isLoading,
    error,
    hasPendingChanges,
    saveImmediately, // For Enter key or explicit save
    queueUpdate,     // For auto-save with debounce
    cancelPending,   // For Escape key
  }
}
```

**Benefits of this approach:**
- ✅ **Clean separation** - ItemsTable.vue stays focused on display
- ✅ **Isolated edit logic** - Each editable cell is self-contained
- ✅ **Easy to test** - Editable cells can be tested independently
- ✅ **Easy to maintain** - Edit logic doesn't clutter display component
- ✅ **Reusable** - Shared composable for common operations (optional)

---

## 🎨 UI/UX Considerations

### Edit Mode Toggle

**Location Options:**
1. Container header (next to other actions)
2. Table toolbar (above table)
3. Settings menu

**Recommendation:** Container header, as toggle button with icon (Edit icon / Pencil icon)

**Visual:**
- Toggle button with icon
- Active state: highlighted/filled icon
- Tooltip: "Enable inline editing" / "Disable inline editing"

### Inline Editing UX

**Interaction:**
- Click cell → enter edit mode
- **Enter → save immediately** (bypasses debounce)
- **Auto-save after 500ms** of inactivity (debounce) - like LighterPack
- Escape → cancel
- Click outside → save (or cancel, depending on preference)

**Save Strategy (Debounce Pattern):**
- User edits multiple fields in sequence (e.g., name, quantity, weight, price)
- Each field change triggers debounce timer (500ms)
- If user continues editing → timer resets
- After 500ms of no changes → auto-save all pending changes
- **Enter key** → immediate save (bypasses debounce, cancels pending timer)
- Benefits:
  - Reduces API calls (one save instead of 4)
  - Better UX (no flickering from multiple saves)
  - Faster editing experience

**Visual Feedback:**
- Highlight editable cells (subtle border or background)
- Show edit icon on hover
- Loading spinner during save
- Pending changes indicator (optional: subtle dot or "unsaved" badge)
- Success/error toast notifications

**Mobile:**
- Touch-friendly inputs
- Larger tap targets
- Consider modal for complex fields (e.g., weight with unit selector)

---

## 📝 Notes

### Why This Approach?

1. **Separation of Concerns** - Display logic (ItemsTable.vue) separate from edit logic (editable cells)
2. **DRY Principle** - No code duplication for sorting, filtering, pagination (all in ItemsTable)
3. **Maintainability** - Edit logic isolated in separate files, easy to find and modify
4. **Clean Code** - ItemsTable.vue stays focused on display, not cluttered with edit logic
5. **Testability** - Editable cells can be tested independently
6. **Consistency** - Same table structure regardless of edit mode

### File Organization

```
ItemsTable.vue (Display only)
├── Sorting logic
├── Filtering logic
├── Pagination logic
└── Conditional rendering of cells

ItemsTableEditableNameCell.vue (Edit logic only)
├── Edit state management
├── Save/cancel handlers
├── Validation
└── Loading/error states

ItemsTableNameCell.vue (Read-only display)
└── Simple display + navigation
```

### Benefits Over Alternatives

**vs. Two Separate Table Components:**
- ✅ No duplication of sorting/filtering/pagination logic
- ✅ Single source of truth for table structure

**vs. All Logic in ItemsTable:**
- ✅ Clean separation - edit logic doesn't clutter display component
- ✅ Easier to understand and maintain
- ✅ Better testability

---

## ✅ Acceptance Criteria

- [ ] Edit mode toggle persists in localStorage
- [ ] Toggle button visible in container header
- [ ] When `editMode: false`, table behaves as currently
- [ ] When `editMode: true`, cells become editable
- [ ] Inline editing works for: name, quantity, weight, notes, price
- [ ] Changes save automatically (or on Enter)
- [ ] Escape cancels edit
- [ ] Loading states during save
- [ ] Error handling for failed saves
- [ ] Mobile-friendly editing
- [ ] Quick actions available in edit mode
- [ ] Add items inline works

---

## 🔗 Related

- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Main roadmap
- FEATURE-018 - Item ordering (similar complexity pattern)

