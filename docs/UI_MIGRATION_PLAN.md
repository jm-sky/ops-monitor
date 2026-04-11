# UI Migration Plan - V1 to V2

**Created:** 2025-12-25
**Updated:** 2025-12-25
**Status:** Components Complete ✅ | Pages In Progress 🔄
**Goal:** Migrate all components and remaining pages from V1 to V2 unified model

---

## 📊 Current Status

**Components:**
- ✅ Using V2: 20/20 (100%) ✅ **COMPLETE**
- Initial estimate was inflated - only 20 components needed migration

**Pages:**
- ✅ Using V2: 6/13 (46%)
- ❌ Remaining: 7/13 (54%)

---

## 🎯 Migration Strategy

### Phase 1: Critical Path Components (High Priority)
**Target:** Core components used across multiple pages
**Estimated:** ~20-30 components

1. **Forms & Inputs:**
   - ContainerFormFields.vue
   - ItemFormFields.vue
   - Item form components

2. **Cards & Lists:**
   - ContainerCard.vue
   - ItemCard.vue (if exists)
   - ContainerCardActions.vue
   - ContainerCardBadges.vue

3. **Headers:**
   - ContainerHeader.vue
   - ItemHeader.vue
   - ContainerHeaderName.vue
   - ContainerHeaderStats.vue

4. **Dialogs:**
   - ExportToCSVDialog.vue
   - ExportToPromptDialog.vue
   - ImportMarkdownDialog.vue
   - CloneContainerDialog.vue

### Phase 2: Remaining Pages
**Target:** 9 pages
**Priority:**
1. ItemDetailPage.vue
2. ItemFormPage.vue
3. AllItemsPage.vue
4. ShoppingPlanningPage.vue
5. PublicItemDetailPage.vue
6. CatalogueBrowserPage.vue
7. Other pages...

### Phase 3: Supporting Components (Medium Priority)
**Target:** ~40-50 components

- Tables: ItemsTable*, data-table/*
- Filters: ContainersFilters, ItemsFilters
- Stats: CategoryPieChart, ReadinessProgress
- Images: ItemImage*, ContainerItemImages*

### Phase 4: UI Elements (Low Priority)
**Target:** ~30-40 components

- Badges (some already done)
- Buttons
- Icons
- Small utility components

---

## 🔄 Migration Pattern

For each component:

```vue
<!-- BEFORE (V1) -->
<script setup lang="ts">
import type { IGearContainer, IGearItem } from '@/modules/gear/types/gear.types'
import { useGearStore } from '@/modules/gear/store/useGearStore'

const props = defineProps<{
  container: IGearContainer
}>()

const store = useGearStore()
</script>

<!-- AFTER (V2) -->
<script setup lang="ts">
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { isContainer } from '@/modules/gear/types/gear.types.v2'

const props = defineProps<{
  item: IGearItemV2
}>()

const store = useGearStoreV2()

// Type guard if needed
if (isContainer(props.item)) {
  // Container-specific logic
}
</script>
```

---

## ✅ Completed Components (20/20) ✅

**Commit `cea5f2f` - 13 components:**
1. ItemFormFields.vue ✅
2. ItemHeader.vue ✅
3. ItemHeaderName.vue ✅
4. ItemHeaderActions.vue ✅
5. ItemsTableEditableNameCell.vue ✅
6. ItemsTableEditableQuantityCell.vue ✅
7. ItemsTableEditablePriceCell.vue ✅
8. ItemsTableEditableCategoryCell.vue ✅
9. ItemsTableEditableWeightCell.vue ✅
10. ItemsTableEditablePriorityCell.vue ✅
11. ItemsTableEditableStatusCell.vue ✅
12. ItemsTableEditableNotesCell.vue ✅
13. ItemsTableWeightCell.vue ✅

**Commit `229ad0b` - 7 components:**
14. ContainerItemImagesGallery.vue ✅
15. ContainerItemImageCard.vue ✅
16. SortConfirmationAlert.vue ✅
17. ItemsTableRowActions.vue ✅
18. UpdateFromCatalogueDialog.vue ✅
19. MatchWithCatalogueDialog.vue ✅
20. ItemsTable.vue ✅

**Detailed Summary:** See [UNIFIED_MODEL_V2_UI_MIGRATION_SUMMARY.md](./UNIFIED_MODEL_V2_UI_MIGRATION_SUMMARY.md)

---

## 📝 Notes

- Many components may work with both V1 and V2 with minimal changes
- Focus on type imports and store usage
- Test each migrated component
- Commit in batches of 10-15 components
- Update this document as progress is made

---

## 🎯 Success Criteria

- [ ] All 119 components using V2 types
- [ ] All 15 pages migrated
- [ ] No V1 imports remaining in /gear module
- [ ] All tests passing
- [ ] TypeScript compiles without errors
