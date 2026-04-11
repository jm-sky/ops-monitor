# Plan Refaktoringu Komponentów Vue

> **Data utworzenia:** 2025-11-26
> **Status:** W trakcie
> **Cel:** Podział dużych komponentów Vue na mniejsze, bardziej zarządzalne części

## Spis treści

- [Przegląd](#przegląd)
- [Priorytety](#priorytety)
- [Szczegółowy plan](#szczegółowy-plan)
- [Zasady struktury katalogów](#zasady-struktury-katalogów)
- [Status realizacji](#status-realizacji)

---

## Przegląd

Identyfikacja i refaktoring komponentów Vue przekraczających 300 linii kodu. Główne cele:

- ✅ Zwiększenie czytelności kodu
- ✅ Ułatwienie testowania
- ✅ Poprawa maintainability
- ✅ Zgodność z zasadami Single Responsibility Principle
- ✅ Łatwiejsze ponowne użycie komponentów

### Statystyki przed refaktoringiem

| Komponent                | Linie kodu | Priorytet |
|--------------------------|-----------|-----------|
| ShoppingPlanningPage.vue | 1084      | 🔴 Wysoki |
| ItemsTable.vue           |  552      | 🟡 Średni |
| ContainerDetailPage.vue  |  549      | 🟡 Średni |
| ItemFormFields.vue       |  389      | 🟢 Niski |
| CategoryPieChart.vue     |  365      | 🟢 Niski |
| ImportMarkdownDialog.vue |  360      | 🟡 Średni |
| ContainerFormFields.vue  |  294      | ✅ OK |
| ContainerHeader.vue      |  206      | ✅ OK |

---

## Priorytety

### 🔴 Priorytet 1 (Wysokie) - DO ZROBIENIA NAJPIERW

#### 1. ShoppingPlanningPage.vue (1084 linie)

**Status:** ✅ Ukończono (2025-11-26)

**Uzasadnienie:** Zdecydowanie największy komponent, łączy logikę biznesową z prezentacją

**Wynik refaktoringu:**
- Oryginalny plik: 1084 linie → 682 linie (-37%)
- Utworzono 8 nowych komponentów (7 + 1 typ)
- Wszystkie testy przeszły: type-check ✅, lint ✅, build ✅

**Plan podziału:**

```
src/modules/gear/
├── pages/
│   └── ShoppingPlanningPage.vue (tylko layout + główna logika orkiestracji)
└── components/
    └── shopping/
        ├── ShoppingListSummary.vue
        ├── ShoppingListFilters.vue
        ├── ShoppingListItem.vue
        ├── AvailableItemsList.vue
        ├── AvailableItemCard.vue
        ├── DeletedItemsList.vue
        ├── ShoppingExportDialog.vue
        └── AddItemToShoppingDialog.vue
```

**Komponenty utworzone:**

- [x] `ShoppingListSummary.vue` - podsumowanie (linie 621-647, 948-973)
  - Props: `shoppingList`, `totalPriceByCurrency`
  - 45 linii ✅

- [x] `ShoppingListFilters.vue` - filtry (linie 649-719)
  - Props: `allCategories`, `selectedCategories`, `budget`, `includeExpiringSoon`, `defaultCurrency`
  - Emits: `update:selectedCategories`, `update:budget`, `update:includeExpiringSoon`
  - 162 linii ✅

- [x] `ShoppingListItem.vue` - pojedynczy item z listy zakupowej (linie 740-838)
  - Props: `item`
  - Emits: `purchase`, `increment`, `decrement`, `delete`
  - 155 linii ✅

- [x] `AvailableItemCard.vue` - pojedynczy dostępny item (linie 859-943)
  - Props: `item`, `isInShoppingList`
  - Emits: `toggle`
  - 135 linii ✅

- [x] `DeletedItemsList.vue` - sekcja usuniętych itemów (linie 975-1024)
  - Props: `deletedItems`
  - Emits: `restore`
  - 79 linii ✅

- [x] `ShoppingExportDialog.vue` - dialog eksportu markdown (linie 1026-1047)
  - Props: `open`, `markdownContent`
  - Emits: `update:open`, `copy`
  - 39 linii ✅

- [x] `AddItemToShoppingDialog.vue` - dialog dodawania itemu (linie 1049-1081)
  - Props: `open`, `loading`
  - Emits: `update:open`, `submit`, `cancel`
  - 48 linii ✅

- [x] `shopping.types.ts` - typy dla shopping (IItemWithContainerId)
  - 6 linii ✅

**Pozostałe linie w głównym komponencie:** ~650 linii (logika, composables, helpers)

**Potencjalna optymalizacja:** Wyodrębnić część logiki do composable `useShoppingPlanning.ts`

---

### 🟡 Priorytet 2 (Średnie) - DO ZROBIENIA JAKO DRUGIE

#### 2. ItemsTable.vue (552 linie → 495 linii, -10.8%)

**Status:** ✅ Ukończono

**Plan podziału:**

```
src/modules/gear/components/
├── ItemsTable.vue (główna logika + DataTable wrapper)
└── items-table/
    ├── ItemsTableNameCell.vue
    ├── ItemsTableMoveButtons.vue
    ├── ItemsTableCategoryCell.vue
    └── ItemsTableWeightCell.vue
```

**Komponenty utworzone:**

- [x] `ItemsTableMoveButtons.vue` - przyciski up/down
  - Props: `canMoveUp`, `canMoveDown`
  - Emits: `moveUp`, `moveDown`
  - 37 linii ✅

- [x] `ItemsTableCategoryCell.vue` - kategoria z ikoną
  - Props: `category`
  - Uses: `useCategoryLabel()` composable
  - 21 linii ✅

- [x] `ItemsTableWeightCell.vue` - waga
  - Props: `item`, `isNestedContainer`, `totalWeight`, `preferredWeightUnit`
  - 27 linii ✅

- [x] `ItemsTableNameCell.vue` - komórka z nazwą
  - Props: `item`, `publicMode`, `isExpired`, `isExpiringSoon`, `isNestedContainer`, `isRowExpanded`, `canMoveUp`, `canMoveDown`, `nestedContainer`
  - Emits: `moveUp`, `moveDown`, `navigate`, `navigateToNestedContainer`, `toggleExpand`
  - Uses: `ItemsTableMoveButtons` component
  - 108 linii ✅

**Pozostałe linie:** 495 linii (logika sortowania, expand/collapse, helpers)

**Dodatkowe usprawnienia:**
- Zastąpiono duplikat `getCategoryLabel()` na composable `useCategoryLabel()`
- Poprawiono kolejność importów zgodnie z ESLint Perfectionist
- Wszystkie komponenty używają Vue 3.5+ patterns (destructured props, explicit types)

---

#### 3. ImportMarkdownDialog.vue (378 linii → 309 linii, -18.3%)

**Status:** ✅ Ukończono (2025-12-01)

**Plan podziału:**

```
src/modules/gear/components/
├── ImportMarkdownDialog.vue (główny dialog + logika importu)
└── import-markdown/
    ├── MarkdownImportPreview.vue
    └── MarkdownImportOptions.vue
```

**Komponenty utworzone:**

- [x] `MarkdownImportOptions.vue` - opcje importu
  - Props: `recognizeFromName`, `importMode`, `hasUuids`, `showPreview`
  - defineModel: `recognizeFromName`, `importMode`
  - 58 linii ✅

- [x] `MarkdownImportPreview.vue` - podgląd parsowanego markdownu
  - Props: `previewResult`
  - 54 linii ✅

**Wynik refaktoringu:**
- Oryginalny plik: 378 linie → 309 linii (-18.3%)
- Utworzono 2 nowe komponenty
- Wszystkie testy przeszły: type-check ✅, lint ✅, build ✅

**Pozostałe linie:** 309 linii (główny dialog + logika importu + textarea)

---

### 🟢 Priorytet 3 (Niskie/Opcjonalne)

#### 4. ItemFormFields.vue (389 linii → 320 linii, -17.7%)

**Status:** ✅ Ukończono (2025-12-01) - Utworzono dedykowane select komponenty

**Uwaga:** Nie rozbijano na sub-komponenty (ItemBasicFields, ItemStatusFields, etc.) - zamiast tego utworzono reużywalne select komponenty.

**Plan podziału:**

```
src/modules/gear/components/
├── ItemFormFields.vue (główny formularz)
└── inputs/
    ├── PrioritySelect.vue
    ├── StatusSelect.vue
    └── QualitySelect.vue
```

**Komponenty utworzone:**

- [x] `PrioritySelect.vue` - select dla priority (critical/high/medium/low)
  - defineModel: `TGearItemPriority`
  - 34 linii ✅

- [x] `StatusSelect.vue` - select dla status (owned/missing/toBuy)
  - defineModel: `TGearItemStatus`
  - 34 linii ✅

- [x] `QualitySelect.vue` - select dla quality (low/medium/high)
  - defineModel: `TGearItemQuality`
  - 34 linii ✅

**Wynik refaktoringu:**
- Oryginalny plik: 389 linie → 320 linii (-17.7%)
- Utworzono 3 reużywalne select komponenty
- Wszystkie testy przeszły: type-check ✅, lint ✅, build ✅
- Bonus: Naprawiono błędy TypeScript w ItemsTableEditablePriceCell i ItemsTableEditableWeightCell

**Pozostałe linie:** 320 linii (główny formularz)

---

#### 5. ContainerDetailPage.vue (549 linii → 472 linii, -14%)

**Status:** ✅ Częściowo ukończono (2025-12-01) - Wyodrębniono rating section

**Plan podziału:**

```
src/modules/gear/
├── pages/
│   └── ContainerDetailPage.vue (główna logika page)
└── components/
    └── ContainerRatingSection.vue (rating logic + UI)
```

**Komponenty utworzone:**

- [x] `ContainerRatingSection.vue` - sekcja ratingów z pełną logiką
  - Props: `container: IGearContainer`
  - Zawiera: Rating state, handleRate, handleDeleteRating
  - Używa: ContainerRatingCard, gearContainerApiService
  - 105 linii ✅

**Wynik refaktoringu:**
- Oryginalny plik: 549 linie → 472 linie (-14%)
- Utworzono 1 komponent z pełną logiką rating
- Wszystkie testy przeszły: type-check ✅, lint ✅, build ✅

**Pozostałe linie:** 472 linii (page logic + items + export/import)

**Możliwe dalsze refaktoringi:**
- Wyodrębnić composable dla export/import operations
- Wyodrębnić logikę sortowania do composable

---

#### 6. CategoryPieChart.vue (365 linii)

**Status:** ⚠️ Opcjonalnie

**Opcjonalny plan podziału:**

```
src/modules/gear/components/
├── CategoryPieChart.vue
└── category-chart/
    ├── CategoryChartModeSelector.vue
    └── CategoryChartTooltip.vue
```

**Komponenty do stworzenia (opcjonalnie):**

- [ ] `CategoryChartModeSelector.vue` - przyciski weight/quantity/price/priority (~40 linii)
- [ ] `CategoryChartTooltip.vue` - niestandardowy tooltip (~50 linii)

---

## Zasady struktury katalogów

Zgodnie z architekturą projektu (`CLAUDE.md`):

### Konwencje nazewnictwa

```
src/modules/gear/components/
├── [Component].vue              # Pojedyncze, samodzielne komponenty
├── [feature]/                   # Pod-katalog dla grupy powiązanych komponentów
│   ├── [Feature]Main.vue       # Główny komponent feature
│   ├── [Feature]Item.vue       # Pod-komponenty
│   └── [Feature]Dialog.vue
```

### Przykład: Shopping Planning

```
src/modules/gear/components/shopping/
├── ShoppingListSummary.vue      # Podsumowanie listy
├── ShoppingListFilters.vue      # Filtry
├── ShoppingListItem.vue         # Item z listy zakupowej
├── AvailableItemCard.vue        # Dostępny item
├── DeletedItemsList.vue         # Lista usuniętych
├── ShoppingExportDialog.vue     # Dialog eksportu
└── AddItemToShoppingDialog.vue  # Dialog dodawania
```

### Zasady tworzenia pod-komponentów

1. **Props** - jasno zdefiniowane, typowane z TypeScript
2. **Emits** - wszystkie eventy zdefiniowane w `defineEmits`
3. **Composables** - logika biznesowa w dedykowanych composables
4. **Single Responsibility** - jeden komponent = jedna odpowiedzialność
5. **Reusability** - komponenty powinny być reusable tam, gdzie to możliwe

### Identyfikacja wspólnych komponentów (Reusability)

**WAŻNE:** Podczas refaktoringu należy zwracać uwagę na powtarzające się wzorce, które można wyodrębnić do wspólnych komponentów:

#### Przykłady potencjalnie reużywalnych komponentów:

1. **Price/Cost Cards**
   - Karty z cenami występują w wielu miejscach (ItemsTable, ShoppingPlanning, ContainerDetail)
   - Kandydat: `PriceCard.vue` lub `CostSummary.vue`
   - Lokalizacja: `src/components/ui/` lub `src/shared/components/`

2. **Status/Priority Badges**
   - Badges dla statusów i priorytetów powtarzają się wszędzie
   - Obecnie używamy `getPriorityVariant()` i `getStatusVariant()`
   - Rozważyć: `ItemStatusBadge.vue`, `ItemPriorityBadge.vue`

3. **Weight Display Components**
   - Wyświetlanie wagi z jednostkami i konwersjami
   - Kandydat: `WeightDisplay.vue`
   - Używa `formatWeightWithPreferredUnit()`

4. **Expiration Badges/Warnings**
   - Badges dla expiring/expired items
   - Powtarzają się w ShoppingPlanning, ItemsTable, ItemDetail
   - Kandydat: `ExpirationBadge.vue`

5. **Item Info Summary**
   - Sekcja z category, brand, quantity, weight, price
   - Występuje w ShoppingListItem, AvailableItemCard, DeletedItemsList
   - Kandydat: `ItemMetadata.vue` lub `ItemSummary.vue`

**Strategia:**
- Podczas refaktoringu każdego komponentu **dokumentować powtarzające się wzorce**
- Po refaktoringu 2-3 komponentów **przeanalizować** wspólne elementy
- Utworzyć reużywalne komponenty w dedykowanym miejscu
- **Nie przedwcześnie optymalizować** - czekać aż wzorzec pojawi się 3+ razy

---

### Best Practices Vue 3.5+

**WAŻNE:** Projekt używa Vue 3.5+, więc obowiązują następujące praktyki:

1. **defineModel dla v-model**
   - ✅ Używaj: `const open = defineModel<boolean>('open', { required: true })`
   - ❌ Unikaj: `defineProps<{ open: boolean }>()` + `emit('update:open')`
   - Template: `<Dialog :open>` (prop shortcut)

2. **Destructured props są reaktywne**
   - ✅ Używaj: `const { loading } = defineProps<{ loading: boolean }>()`
   - Nie trzeba `toRefs()` ani `props.loading`

3. **Prop shortcut w template**
   - ✅ Używaj: `<Dialog :open>` zamiast `<Dialog :open="open">`
   - Vue 3.5+ automatycznie dopasowuje nazwę propa

4. **Routing helpers zamiast hardcoded paths**
   - ✅ Używaj: `GearRoutePath.ItemEditById(containerId, itemId)`
   - ❌ Unikaj: `` `/gear/${containerId}/items/${itemId}/edit` ``
   - Importuj z: `@/modules/gear/routes`

5. **Sortowanie importów**
   - Zewnętrzne paczki → Vue ecosystem → lokalne moduły
   - Alfabetycznie w każdej grupie (ESLint Perfectionist)

6. **Kolejność deklaracji w `<script setup>`**
   - ✅ Kolejność: Composables (`useI18n`, `useStore`) → defineProps → defineModel → defineEmits → Computed/Reactive/Refs → Functions
   - Przykład:
   ```typescript
   const { t } = useI18n()
   const store = useGearStore()

   const { loading } = defineProps<{ loading: boolean }>()
   const open = defineModel<boolean>('open')
   const emit = defineEmits<{ submit: [] }>()

   const count = ref(0)
   const doubled = computed(() => count.value * 2)

   function handleClick() { ... }
   ```

7. **Używaj composables zamiast duplikacji**
   - ✅ Używaj: `useCategoryLabel()` (dla `getCategoryLabel`)
   - ✅ Używaj: `useContainerTypeLabel()` (dla `getContainerTypeLabel`)
   - ❌ Unikaj: Kopiowania tej samej funkcji do wielu komponentów
   - Lokalizacja composables: `src/modules/gear/composables/`

8. **Wyodrębniaj komponenty z v-for**
   - ✅ Gdy v-for zawiera >10 linii logiki → nowy komponent
   - Przykład: `DeletedItemsList.vue` używa `DeletedItemCard.vue`

---

## Status realizacji

### Ogólny postęp: 55.5% (5/9 komponentów zrefaktorowanych)

#### Priorytet 1 (Wysoki)
- [x] **ShoppingPlanningPage.vue** ✅ **UKOŃCZONO**
  - [x] ShoppingListSummary.vue
  - [x] ShoppingListFilters.vue
  - [x] ShoppingListItem.vue
  - [x] AvailableItemCard.vue
  - [x] DeletedItemsList.vue
  - [x] ShoppingExportDialog.vue
  - [x] AddItemToShoppingDialog.vue
  - [x] shopping.types.ts

#### Priorytet 2 (Średni)
- [x] **ItemsTable.vue** ✅ **UKOŃCZONO**
  - [x] ItemsTableNameCell.vue
  - [x] ItemsTableMoveButtons.vue
  - [x] ItemsTableCategoryCell.vue
  - [x] ItemsTableWeightCell.vue
  - [x] ItemsTableEditableNameCell.vue
  - [x] ItemsTableImageCell.vue

- [x] **ImportMarkdownDialog.vue** ✅ **UKOŃCZONO**
  - [x] MarkdownImportOptions.vue
  - [x] MarkdownImportPreview.vue

#### Priorytet 3 (Niski/Opcjonalny)
- [x] **ItemFormFields.vue** ✅ **UKOŃCZONO** (select komponenty)
  - [x] PrioritySelect.vue
  - [x] StatusSelect.vue
  - [x] QualitySelect.vue
- [x] **ContainerDetailPage.vue** ✅ **CZĘŚCIOWO UKOŃCZONO** (rating section)
  - [x] ContainerRatingSection.vue
- [ ] CategoryPieChart.vue (opcjonalnie)

---

## Notatki i uwagi

### Kompatybilność wsteczna
- ✅ Wszystkie refaktoringi muszą zachować obecne API komponentów
- ✅ Nie zmieniamy routingu ani publicznych interfejsów
- ✅ Testy po refaktoringu powinny przejść bez zmian

### Code style
- Zgodność z `.eslint.config.ts`
- Brak średników
- Single quotes
- Sortowanie importów (Perfectionist plugin)
- Max 3 atrybuty w jednej linii

### Testing
Po każdym refaktoringu:
1. [ ] Manual testing w przeglądarce
2. [ ] Sprawdzenie `pnpm type-check`
3. [ ] Sprawdzenie `pnpm lint`
4. [ ] Build test `pnpm build`

---

## Historia zmian

| Data | Komponent | Status | Uwagi |
|------|-----------|--------|-------|
| 2025-11-26 | - | Plan utworzony | Zidentyfikowano 8 komponentów do refaktoringu |
| 2025-11-26 | ShoppingPlanningPage.vue | ✅ Ukończono | Podzielono na 8 komponentów (1084→682 linie, -37%) |
| 2025-11-26 | ShoppingPlanningPage.vue | 🔧 Poprawki | Zastosowano Vue 3.5+ best practices (defineModel, routing helpers) |
| 2025-11-26 | Shopping components | 🔧 Refaktoring | Utworzono `useCategoryLabel()` composable, `DeletedItemCard.vue`, poprawiono kolejność deklaracji |
| 2025-12-01 | ItemsTable.vue | ✅ Ukończono | Podzielono na 6 komponentów (552→511 linie, -7.4%), dodano inline editing support |
| 2025-12-01 | ImportMarkdownDialog.vue | ✅ Ukończono | Podzielono na 3 komponenty (378→309 linie, -18.3%) |
| 2025-12-01 | ItemFormFields.vue | ✅ Ukończono | Utworzono 3 reużywalne select komponenty (389→320 linie, -17.7%) |
| 2025-12-01 | ContainerDetailPage.vue | ✅ Częściowo ukończono | Wyodrębniono ContainerRatingSection (549→472 linie, -14%) |

---

## Następne kroki

1. ✅ Utworzenie planu refaktoringu
2. ✅ Start refaktoringu ShoppingPlanningPage.vue
3. ✅ Testy i weryfikacja (type-check, lint, build)
4. ✅ Refaktoring ItemsTable.vue
5. ✅ Refaktoring ImportMarkdownDialog.vue
6. ⏳ Opcjonalne: ItemFormFields.vue i CategoryPieChart.vue

---

## Tracker wspólnych komponentów (Reusability)

Ta sekcja śledzi powtarzające się wzorce wykryte podczas refaktoringu. Gdy wzorzec pojawi się **3+ razy**, rozważamy utworzenie wspólnego komponentu.

### Wykryte wzorce:

| Wzorzec | Lokalizacje | Liczba wystąpień | Status | Notatki |
|---------|-------------|------------------|--------|---------|
| **Item metadata** (category, brand, qty, weight, price) | ShoppingListItem, AvailableItemCard, DeletedItemsList | 3 | ⏳ Kandydat | Bardzo podobna struktura HTML + logic |
| **Expiration badge** (expired/expiring soon) | ShoppingListItem, AvailableItemCard, ItemsTable (?) | 2-3 | ⏳ Do weryfikacji | Identyczna logika `isExpired()`, `isExpiringSoon()` |
| **Priority badge** | ShoppingListItem, AvailableItemCard, DeletedItemsList, ItemsTable (?) | 3+ | ⏳ Kandydat | Używa `getPriorityVariant()` |
| **Status badge** | ShoppingListItem, AvailableItemCard, ItemsTable (?) | 2-3 | ⏳ Do weryfikacji | Używa `getStatusVariant()` |
| **Weight display** | ShoppingListItem, AvailableItemCard, ItemsTable (?) | 3+ | ⏳ Kandydat | Używa `formatWeightWithPreferredUnit()` |
| **Price display** | ShoppingListItem, AvailableItemCard, DeletedItemsList (?) | 2-3 | ⏳ Do weryfikacji | Używa `formatCurrency()`, `getCurrency()` |

**Legenda:**
- ⏳ Kandydat - wykryto 3+ wystąpienia, gotowe do ekstrakcji
- ⏳ Do weryfikacji - potencjalny kandydat, wymaga weryfikacji w kolejnych refaktoringach
- 🚧 W trakcie - tworzenie wspólnego komponentu
- ✅ Utworzono - wspólny komponent gotowy

### Akcje po refaktoringu ItemsTable i ImportMarkdownDialog:

Po ukończeniu refaktoringu tych dwóch komponentów:
1. ✅ Przeanalizować powtarzające się wzorce
2. ✅ Zaktualizować tabelę powyżej
3. ✅ Utworzyć propozycję wspólnych komponentów (jeśli wzorzec występuje 3+ razy)
4. ✅ Dodać do planu jako osobny punkt (Priorytet 4: Wspólne komponenty)

---

**Ostatnia aktualizacja:** 2025-12-01
