# FEATURE-018: Item Ordering (Kolejność przedmiotów w kontenerze)

**Status:** ✅ Completed | **Version:** v2.9.0
**Priority:** Medium
**Complexity:** Medium
**Category:** ✏️ Editing / 🎨 UI/UX
**Related Features:** None

---

## 📋 Overview

Add ability for users to manually order items within containers. Items will have an `order` field that determines their display order, and users can reorder items using drag & drop or up/down buttons.

This feature improves UX by allowing users to organize items in a way that makes sense to them (e.g., by importance, by packing order, by category groups).

---

## 🎯 Goals

1. **Order Field** - Add `order` (or `sortOrder`) field to items
2. **Drag & Drop** - Allow reordering items by dragging (preferred)
3. **Up/Down Buttons** - Alternative: buttons to move items up/down
4. **Persistence** - Save order in localStorage
5. **Sorting Options** - Allow sorting by other criteria with option to return to manual order
6. **Visual Feedback** - Show visual indicators during drag operations

---

## 📐 Design

### Current State

- Items displayed in order they were added
- Can sort by name, weight, category, etc. (but no manual order)
- No way to preserve custom order

### Proposed Changes

#### 1. Order Field

**Data Model:**
- Add `order: number` field to `IGearItem` interface
- Order is a numeric value (0, 1, 2, ...)
- Lower numbers appear first
- Default order = index in array (or timestamp-based)

**Storage:**
- Order saved in localStorage with item
- Order synced to backend when backend enabled

#### 2. Drag & Drop UI

**Location:** `ItemsTable.vue` or `ContainerDetailPage.vue`

**Implementation:**
- Use drag & drop library (e.g., `@dnd-kit/core` or `vue-draggable`)
- Make table rows draggable
- Show visual feedback:
  - Highlight row being dragged
  - Show drop indicator (line between rows)
  - Ghost/preview of dragged item

**Alternative: Up/Down Buttons**
- If drag & drop is too complex, use buttons
- "Move Up" / "Move Down" buttons in item actions menu
- Update order values accordingly

#### 3. Sorting Behavior

**Current Sorting:**
- Users can sort by name, weight, category, priority, etc.
- Sorting temporarily overrides manual order

**New Behavior:**
- Add "Manual Order" option to sort dropdown
- When "Manual Order" selected → use `order` field
- When other sort selected → sort by that criteria, but preserve `order` values
- When returning to "Manual Order" → restore original order

#### 4. Order Management

**Initial Order:**
- New items get `order = max(order) + 1` in container
- Or `order = items.length` (0-indexed)

**Reordering:**
- When item moved up: decrease its order, increase orders of items above
- When item moved down: increase its order, decrease orders of items below
- Or: recalculate all orders based on new position

---

## 🛠️ Implementation Plan

### Phase 1: Data Model & Storage

**Files:**
- `src/modules/gear/types/gear.types.ts`
- `src/modules/gear/services/gearItemService.ts`
- `src/modules/gear/services/gearContainerService.ts`

**Changes:**
1. Add `order?: number` to `IGearItem` interface
2. Add `order` to `ICreateItemDto` and `IUpdateItemDto`
3. Update item creation to assign order:
   ```typescript
   const maxOrder = Math.max(...container.items.map(i => i.order || 0), -1)
   newItem.order = maxOrder + 1
   ```
4. Update item service to handle order in create/update operations

### Phase 2: Display with Order

**Files:**
- `src/modules/gear/utils/getAllItems.ts`
- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/pages/ContainerDetailPage.vue`

**Changes:**
1. Sort items by `order` field when displaying
2. Default to `order` if no other sort selected
3. Add "Manual Order" option to sort dropdown
4. Handle items without order (backward compatibility):
   - Assign order based on current position
   - Or use timestamp/creation order as fallback

### Phase 3: Drag & Drop Implementation

**Option A: Using @dnd-kit/core (Recommended)**

**Files:**
- `src/modules/gear/components/ItemsTable.vue`
- `package.json` (add dependency)

**Changes:**
1. Install `@dnd-kit/core` and `@dnd-kit/sortable`
2. Wrap table in `DndContext`
3. Make rows `SortableContext` items
4. Implement drag handlers:
   - `onDragStart` - highlight dragged row
   - `onDragOver` - show drop indicator
   - `onDragEnd` - update order values
5. Update order values when drop occurs

**Option B: Using vue-draggable**

**Files:**
- `src/modules/gear/components/ItemsTable.vue`
- `package.json` (add dependency)

**Changes:**
1. Install `vuedraggable` or `vue-draggable-plus`
2. Replace table rows with draggable component
3. Handle `@end` event to update orders
4. Update order values based on new array order

**Option C: Up/Down Buttons (Simpler Alternative)**

**Files:**
- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/components/ItemActionsMenu.vue` (if exists)

**Changes:**
1. Add "Move Up" and "Move Down" buttons to item actions
2. Implement move functions:
   ```typescript
   function moveItemUp(item: IGearItem) {
     const currentOrder = item.order || 0
     const itemAbove = items.find(i => i.order === currentOrder - 1)
     if (itemAbove) {
       item.order = currentOrder - 1
       itemAbove.order = currentOrder
       // Save both items
     }
   }
   ```
3. Disable buttons when item is first/last

### Phase 4: Order Persistence

**Files:**
- `src/modules/gear/services/gearItemService.ts`
- `src/modules/gear/services/gearItemLocalService.ts`
- `src/modules/gear/services/gearItemApiService.ts`

**Changes:**
1. Ensure order is saved when item is created/updated
2. When reordering, update all affected items
3. Batch update orders for better performance (if multiple items change)

**Optimization:**
- When dragging, update orders only on drop (not during drag)
- Batch update all changed orders in one operation

### Phase 5: Visual Feedback

**Files:**
- `src/modules/gear/components/ItemsTable.vue`
- CSS/styling

**Changes:**
1. Add drag handle icon to rows (e.g., grip icon)
2. Style dragged row (opacity, shadow, etc.)
3. Show drop indicator (line or highlight between rows)
4. Add transition animations for smooth reordering

---

## 📊 Data Flow

### Reordering Flow

```
User drags item to new position
  ↓
onDragEnd event fired
  ↓
Calculate new order values for affected items
  ↓
Update items with new orders
  ↓
Save to localStorage/API
  ↓
Refresh display (items sorted by order)
```

### Initial Order Assignment

```
New item created
  ↓
Get all items in container
  ↓
Find max order value
  ↓
Assign order = maxOrder + 1
  ↓
Save item with order
```

---

## 🔍 Technical Details

### Order Calculation

**Option 1: Sequential (0, 1, 2, ...)**
- Simple, easy to understand
- Requires updating multiple items when reordering
- Gaps can occur if items deleted

**Option 2: Spaced (0, 100, 200, ...)**
- Allows inserting items between without updating others
- More complex calculation
- Can run out of space eventually

**Option 3: Timestamp-based**
- Use creation timestamp as initial order
- Simple, no gaps
- Harder to manually reorder

**Recommendation:** Use sequential (0, 1, 2, ...) with recalculation on reorder.

### Reordering Algorithm

When item moved from position A to position B:

```typescript
function reorderItems(items: IGearItem[], fromIndex: number, toIndex: number) {
  const reordered = [...items]
  const [moved] = reordered.splice(fromIndex, 1)
  reordered.splice(toIndex, 0, moved)
  
  // Recalculate all orders
  reordered.forEach((item, index) => {
    item.order = index
  })
  
  return reordered
}
```

### Backward Compatibility

- Items without `order` field should still work
- Assign order based on current array index on first load
- Or use creation timestamp as fallback order

---

## 🧪 Testing

### Manual Test Cases

1. **Initial Order**
   - ✅ New items get correct order
   - ✅ Items display in order
   - ✅ Items without order get assigned order

2. **Drag & Drop**
   - ✅ Can drag item to new position
   - ✅ Visual feedback during drag
   - ✅ Order updates correctly after drop
   - ✅ Changes persist after reload

3. **Up/Down Buttons** (if implemented)
   - ✅ "Move Up" moves item up
   - ✅ "Move Down" moves item down
   - ✅ Buttons disabled at top/bottom
   - ✅ Order updates correctly

4. **Sorting**
   - ✅ Can sort by other criteria (name, weight, etc.)
   - ✅ Manual order preserved when sorting
   - ✅ "Manual Order" option restores original order
   - ✅ Switching between sorts works correctly

5. **Edge Cases**
   - ✅ Reordering single item container
   - ✅ Reordering with nested containers
   - ✅ Items added after reordering get correct order
   - ✅ Deleted items don't break order

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Manual item ordering within containers
- Drag & drop support for reordering items
- Order field in item data model
- "Manual Order" sorting option
- Visual feedback during drag operations
- Order persistence in localStorage
```

---

## 🚀 Future Enhancements

### Advanced Ordering
- Order items across containers
- Group ordering (order by category, then manual within category)
- Save order presets

### Order Templates
- Pre-defined order templates (by weight, by priority, etc.)
- Apply template to container

### Order Import/Export
- Include order in markdown export
- Preserve order when importing

---

## 📝 Notes

- Order is a numeric field - simple and efficient
- Drag & drop preferred, but buttons are acceptable alternative
- Order stored in localStorage (offline-first)
- Can be synced to backend in future
- Backward compatible with existing items (no order field)

---

## 🔗 Related Documentation

- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Offline Features Roadmap
- Drag & drop library: `@dnd-kit/core` or `vue-draggable`
- Items table: `src/modules/gear/components/ItemsTable.vue`
- Item service: `src/modules/gear/services/gearItemService.ts`

