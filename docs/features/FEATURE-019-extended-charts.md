# FEATURE-019: Extended Charts (Rozszerzenie wykresów)

**Status:** ✅ Completed
**Priority:** Medium
**Complexity:** Medium
**Category:** 📊 Visualizations / Analytics
**Related Features:** None

---

## 📋 Overview

Extend the existing category pie chart on container detail page to support additional chart modes:
- **Price** - Distribution of costs by category
- **Priority** - Distribution of items by priority level

This feature enhances the analytics capabilities by providing more insights into container composition beyond just weight and quantity.

---

## 🎯 Goals

1. **Price Chart** - Pie chart showing cost distribution by category
2. **Priority Chart** - Pie chart showing item distribution by priority
3. **Chart Mode Selector** - Extend existing mode switcher with new options
4. **Data Handling** - Handle missing data gracefully (items without price/priority)
5. **Consistent Styling** - Use same chart library and styling as existing charts

---

## 📐 Design

### Current State

- ✅ Category pie chart exists on container detail page
- ✅ Chart mode switcher with 2 options: "By Weight" and "By Quantity"
- ✅ Uses chart library (likely Chart.js or similar)
- ✅ Chart displays in `ContainerHeader.vue` or similar component

### Proposed Changes

#### 1. Chart Mode Selector

**Current Options:**
- By Weight (existing)
- By Quantity (existing)

**New Options:**
- By Price (new)
- By Priority (new)

**UI:**
- Extend existing radio buttons or select dropdown
- 4 options total: Weight, Quantity, Price, Priority

#### 2. Price Chart

**Data:**
- Group items by category
- Sum prices per category: `totalPrice = sum(item.price * item.quantity)`
- Handle items without price (exclude or show as "No Price")

**Display:**
- Pie chart segments = categories
- Segment size = percentage of total price
- Show category name and total price in legend/tooltip
- Color coding same as existing category chart

**Example:**
```
Tools: 45% (€450.00)
Shelter: 30% (€300.00)
Food: 15% (€150.00)
Other: 10% (€100.00)
```

#### 3. Priority Chart

**Data:**
- Group items by priority level
- Count items per priority: `count = items.filter(i => i.priority === 'critical').length`
- Or sum quantity per priority: `total = sum(item.quantity where priority = 'critical')`

**Display:**
- Pie chart segments = priority levels
- Segment size = percentage of items/quantity
- Show priority name and count in legend/tooltip
- Color coding: Critical (red), High (orange), Medium (yellow), Low (green)

**Example:**
```
Critical: 25% (5 items)
High: 35% (7 items)
Medium: 30% (6 items)
Low: 10% (2 items)
```

#### 4. Missing Data Handling

**Price Chart:**
- Items without price: exclude from chart or show as "No Price" segment
- Containers with no priced items: show message "No price data available"

**Priority Chart:**
- Items without priority: use default priority or exclude
- All items have priority (required field), so this is less likely

---

## 🛠️ Implementation Plan

### Phase 1: Data Calculation Functions

**Files:**
- `src/modules/gear/utils/containerCalculations.ts` (or create new file)

**Functions to Add:**

```typescript
/**
 * Calculate price distribution by category
 */
export function calculatePriceByCategory(
  items: IGearItem[]
): Array<{ category: string; totalPrice: number; percentage: number }> {
  const categoryMap = new Map<string, number>()
  let totalPrice = 0

  items.forEach(item => {
    if (item.price && item.quantity) {
      const itemTotal = item.price * item.quantity
      const current = categoryMap.get(item.category) || 0
      categoryMap.set(item.category, current + itemTotal)
      totalPrice += itemTotal
    }
  })

  return Array.from(categoryMap.entries())
    .map(([category, price]) => ({
      category,
      totalPrice: price,
      percentage: totalPrice > 0 ? (price / totalPrice) * 100 : 0,
    }))
    .sort((a, b) => b.totalPrice - a.totalPrice)
}

/**
 * Calculate item distribution by priority
 */
export function calculateItemsByPriority(
  items: IGearItem[]
): Array<{ priority: TGearItemPriority; count: number; percentage: number }> {
  const priorityMap = new Map<TGearItemPriority, number>()
  const totalItems = items.length

  items.forEach(item => {
    const priority = item.priority || 'medium'
    const current = priorityMap.get(priority) || 0
    priorityMap.set(priority, current + (item.quantity || 1))
  })

  const totalQuantity = Array.from(priorityMap.values()).reduce((a, b) => a + b, 0)

  return Array.from(priorityMap.entries())
    .map(([priority, count]) => ({
      priority,
      count,
      percentage: totalQuantity > 0 ? (count / totalQuantity) * 100 : 0,
    }))
    .sort((a, b) => {
      // Sort by priority order: critical, high, medium, low
      const order: Record<TGearItemPriority, number> = {
        critical: 0,
        high: 1,
        medium: 2,
        low: 3,
      }
      return order[a.priority] - order[b.priority]
    })
}
```

### Phase 2: Chart Mode Selector Update

**Files:**
- `src/modules/gear/components/ContainerHeader.vue` (or wherever chart is)
- `src/modules/gear/i18n/locales/*.ts`

**Changes:**
1. Add new options to chart mode selector:
   - "By Weight" (existing)
   - "By Quantity" (existing)
   - "By Price" (new)
   - "By Priority" (new)

2. Update mode type:
   ```typescript
   type ChartMode = 'weight' | 'quantity' | 'price' | 'priority'
   ```

3. Add translations for new modes

### Phase 3: Chart Data Provider

**Files:**
- `src/modules/gear/components/ContainerHeader.vue` (or chart component)

**Changes:**
1. Create computed property that returns chart data based on mode:
   ```typescript
   const chartData = computed(() => {
     switch (chartMode.value) {
       case 'weight':
         return calculateWeightByCategory(container.items)
       case 'quantity':
         return calculateQuantityByCategory(container.items)
       case 'price':
         return calculatePriceByCategory(container.items)
       case 'priority':
         return calculateItemsByPriority(container.items)
       default:
         return []
     }
   })
   ```

2. Handle empty data:
   - Show message if no data available
   - Hide chart if no data

### Phase 4: Chart Rendering

**Files:**
- Chart component (wherever pie chart is rendered)

**Changes:**
1. Update chart configuration based on mode:
   - **Price mode:** Use price data, format labels with currency
   - **Priority mode:** Use priority data, use priority colors

2. Update chart colors:
   - **Price/Quantity/Weight:** Use category colors (existing)
   - **Priority:** Use priority colors (red, orange, yellow, green)

3. Update tooltips/legends:
   - Show appropriate labels and values
   - Format currency for price mode
   - Show counts/percentages for priority mode

### Phase 5: Missing Data Handling

**Files:**
- Chart component
- `src/modules/gear/components/ContainerHeader.vue`

**Changes:**
1. Check if data available before rendering chart
2. Show message if no data:
   - Price mode: "No items with price data"
   - Priority mode: "No items available" (shouldn't happen)
3. Handle partial data:
   - Price mode: Show "No Price" segment if some items lack price
   - Or exclude items without price (preferred)

---

## 📊 Data Flow

### Chart Rendering Flow

```
User selects chart mode
  ↓
chartMode changes (weight/quantity/price/priority)
  ↓
chartData computed recalculates
  ↓
Chart component receives new data
  ↓
Chart re-renders with new data and colors
```

### Price Calculation Flow

```
Container items
  ↓
Filter items with price
  ↓
Group by category
  ↓
Sum price * quantity per category
  ↓
Calculate percentages
  ↓
Format for chart display
```

---

## 🔍 Technical Details

### Chart Library

Use existing chart library (likely Chart.js or similar). Ensure:
- Same library for all chart modes
- Consistent styling and colors
- Responsive design

### Color Schemes

**Category Colors (existing):**
- Use existing category color mapping
- Same colors for weight/quantity/price modes

**Priority Colors (new):**
- Critical: Red (`#ef4444`)
- High: Orange (`#f97316`)
- Medium: Yellow (`#eab308`)
- Low: Green (`#22c55e`)

### Data Formatting

**Price Mode:**
- Format currency using `formatCurrency()` (from FEATURE-017)
- Show both amount and percentage in tooltip

**Priority Mode:**
- Show priority name and count
- Show percentage of total items

### Performance

- Calculate chart data only when mode changes
- Use computed properties for reactivity
- Cache calculations if needed

---

## 🧪 Testing

### Manual Test Cases

1. **Price Chart**
   - ✅ Chart displays when items have prices
   - ✅ Categories grouped correctly
   - ✅ Percentages calculated correctly
   - ✅ Currency formatted correctly
   - ✅ Handles items without price (excludes or shows "No Price")
   - ✅ Shows message when no items have price

2. **Priority Chart**
   - ✅ Chart displays with all priority levels
   - ✅ Items counted correctly per priority
   - ✅ Percentages calculated correctly
   - ✅ Priority colors applied correctly
   - ✅ Sorted by priority order (critical → low)

3. **Mode Switching**
   - ✅ Can switch between all 4 modes
   - ✅ Chart updates correctly when mode changes
   - ✅ Data recalculates correctly
   - ✅ Colors change appropriately

4. **Edge Cases**
   - ✅ Container with no items
   - ✅ Container with items but no prices (price mode)
   - ✅ Container with single category/priority
   - ✅ Container with many categories/priorities

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Price distribution chart by category
- Priority distribution chart
- Extended chart mode selector with 4 options (Weight, Quantity, Price, Priority)
- Price calculation utilities for chart data
- Priority calculation utilities for chart data
- Missing data handling for price chart
```

---

## 🚀 Future Enhancements

### Additional Chart Modes
- By Brand
- By Status (owned/missing/toBuy)
- By Expiration Date

### Chart Types
- Bar charts for comparison
- Stacked charts for multi-dimensional analysis
- Time-series charts for historical data

### Interactive Charts
- Click to filter items by category/priority
- Drill-down to item list
- Export chart as image

---

## 📝 Notes

- Extends existing chart functionality - no new chart library needed
- Uses same styling and colors as existing charts
- Price chart requires FEATURE-017 (Currency Support) for proper formatting
- Priority is a required field, so priority chart should always have data
- Price is optional, so price chart needs graceful handling of missing data

---

## 🔗 Related Documentation

- [FEATURE-017](./FEATURE-017-currency-support.md) - Currency Support (for price formatting)
- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Offline Features Roadmap
- Chart component: `src/modules/gear/components/ContainerHeader.vue` (or similar)
- Calculations: `src/modules/gear/utils/containerCalculations.ts`

