# FEATURE-008: Container Nesting (Parent-Child Relationships)

## 📋 Overview

Implement parent-child relationships between containers, allowing containers to be nested inside other containers. This enables hierarchical organization of gear (e.g., a Pouch inside a Backpack, with a Flashlight inside the Pouch).

## 🎯 Goals

- Allow containers to be added as items in other containers
- Support recursive weight calculation (container weight + nested containers + items)
- Option to hide nested containers from main container list
- Visual indication of nested containers
- Prevent circular references (container cannot be its own parent)

## 📊 Status

- **Status:** 🚧 In Progress
- **Priority:** High
- **Category:** 🔗 Relationships
- **Started:** 2025-11-18

## 🔧 Implementation Plan

### Phase 1: Data Model Updates

1. **Update Type Definitions** (`src/modules/gear/types/gear.types.ts`)
   - Add `parentContainerId?: TUUID` to `IGearContainer`
   - Add `containerId?: TUUID` to `IGearItem` (reference to nested container)
   - Update DTOs accordingly

2. **Update Validation Schemas** (`src/modules/gear/utils/validation.ts`)
   - Add optional `parentContainerId` to container schema
   - Add optional `containerId` to item schema

### Phase 2: Business Logic

3. **Update Service Layer** (`src/modules/gear/services/gearService.ts`)
   - Modify `calculateTotalWeight` to be recursive (include nested containers)
   - Add `getRootContainers()` - returns only containers without parents
   - Add `getNestedContainers(containerId)` - returns all nested containers
   - Add `validateNoCircularReference(containerId, parentId)` - prevents cycles
   - Update `createContainer` to validate parent relationship
   - Update `updateContainer` to validate parent relationship changes

4. **Add Utility Functions** (`src/modules/gear/utils/containerNesting.ts`)
   - `isNestedContainer(container: IGearContainer): boolean`
   - `getContainerDepth(containerId: TUUID): number`
   - `getContainerPath(containerId: TUUID): IGearContainer[]` (breadcrumb path)
   - `getAllNestedContainers(containerId: TUUID): IGearContainer[]` (recursive)

### Phase 3: UI Components

5. **Update Container List** (`src/modules/gear/pages/ContainersPage.vue`)
   - Add filter toggle: "Show only root containers" / "Show all containers"
   - Visual indicator for nested containers (indentation, icon, or badge)

6. **Update Item Form** (`src/modules/gear/components/ItemFormFields.vue`)
   - Add option to select a container as an item
   - Show container selector when creating/editing items
   - Display nested container info in item list

7. **Update Items Table** (`src/modules/gear/components/ItemsTable.vue`)
   - Show special indicator for items that are containers
   - Display nested container details (name, type, item count)
   - Allow navigation to nested container

8. **Update Container Card** (`src/modules/gear/components/ContainerCard.vue`)
   - Show parent container info if nested
   - Visual indicator (badge, icon) for nested status

### Phase 4: Composables & Store

9. **Update Composables**
   - `useGear.ts`: Add `getRootContainers()`, `getNestedContainers()`
   - `useContainer.ts`: Add `parentContainer`, `isNested`, `nestedContainers`

10. **Update Store** (if needed)
    - Ensure store handles parent-child relationships correctly

### Phase 5: Internationalization

11. **Update i18n** (`src/modules/gear/i18n/index.ts`)
    - Add translations for:
      - "Nested container"
      - "Parent container"
      - "Show only root containers"
      - "Show all containers"
      - "Container as item"
      - "View nested container"

## 🧪 Testing Checklist

- [ ] Create a container with a parent
- [ ] Add a container as an item to another container
- [ ] Verify recursive weight calculation works correctly
- [ ] Test circular reference prevention
- [ ] Test filtering (root containers only vs all)
- [ ] Verify nested containers are hidden from main list when filtered
- [ ] Test visual indicators for nested containers
- [ ] Test navigation to nested containers
- [ ] Verify parent-child relationships persist after page reload

## 📝 Notes

- Weight calculation must be recursive: container weight + all items + all nested containers (with their items)
- Consider performance for deeply nested structures
- UI should clearly indicate hierarchy
- Migration: Existing containers will have no parent (root containers)

## 🔗 Related Features

- FEATURE-003: Container Color Coding (visual distinction)
- FEATURE-009: Export to Prompt (should include nested structure)

