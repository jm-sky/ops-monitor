# FEATURE-020: Price Display in Markdown Export (Pokazywanie cen w eksporcie markdown)

**Status:** ✅ Completed
**Priority:** Medium
**Complexity:** Small
**Category:** 🚀 Import/Export
**Related Features:** FEATURE-011 (Markdown Import/Export), FEATURE-017 (Currency Support)

---

## 📋 Overview

Add option to include item and container prices in markdown export. When enabled, prices will be displayed next to items in the exported markdown, and a summary section "To Buy" will be added at the end showing total cost of items marked as "to buy".

This feature enhances the export functionality by allowing users to include financial information when sharing gear lists or working with AI assistants.

---

## 🎯 Goals

1. **Export Option** - Checkbox/toggle in export dialog to enable price display
2. **Price Formatting** - Display prices with currency in export
3. **Item Prices** - Show price next to each item when option enabled
4. **Container Prices** - Show price for containers (if applicable)
5. **Summary Section** - Add "To Buy" summary with total cost at end of export

---

## 📐 Design

### Current State

- ✅ Markdown export exists (`ExportToPromptDialog.vue`)
- ✅ Export options (description format, etc.)
- ✅ Price field exists in items and containers
- ✅ Currency field exists (from FEATURE-017)
- ❌ No option to include prices in export
- ❌ No price summary section

### Proposed Changes

#### 1. Export Option

**Location:** `ExportToPromptDialog.vue`

**UI:**
- Add checkbox: "Show prices" or "Include prices in export"
- Default: unchecked (prices not shown by default)
- When checked: prices included in export

#### 2. Price Display Format

**Item Format:**
```markdown
- **Item Name** x2 (Brand, Color) - 100g - 50.00 PLN
```

**Container Format:**
```markdown
## Container Name [#container-id] - 200.00 PLN
```

**Position:**
- Price shown at the end of item line (after weight)
- Format: `- [price] [currency]`
- Use currency from item/container, or default currency

#### 3. "To Buy" Summary

**Location:** End of exported markdown

**Format:**
```markdown
---

## To Buy

**Total Cost:** 1,234.56 PLN

Items to purchase:
- **Item 1** - 50.00 PLN
- **Item 2** - 100.00 PLN
- **Item 3** - 1,084.56 PLN
```

**Logic:**
- Only include items with `status === 'toBuy'`
- Sum prices: `total = sum(item.price * item.quantity where status === 'toBuy')`
- Group by currency if multiple currencies
- Show list of items with prices

---

## 🛠️ Implementation Plan

### Phase 1: Export Option UI

**Files:**
- `src/modules/gear/components/ExportToPromptDialog.vue`
- `src/modules/gear/i18n/locales/*.ts`

**Changes:**
1. Add checkbox to export options:
   ```vue
   <FormField v-slot="{ componentField }" name="showPrices">
     <FormItem class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
       <FormControl>
         <Checkbox v-bind="componentField" />
       </FormControl>
       <div class="space-y-1 leading-none">
         <FormLabel>
           {{ t('gear.export.showPrices') }}
         </FormLabel>
         <FormDescription>
           {{ t('gear.export.showPricesDescription') }}
         </FormDescription>
       </div>
     </FormItem>
   </FormField>
   ```

2. Add to export options interface:
   ```typescript
   interface ExportOptions {
     // ... existing options
     showPrices?: boolean
   }
   ```

3. Add translations:
   - `gear.export.showPrices`: "Show prices"
   - `gear.export.showPricesDescription`: "Include item and container prices in export"

### Phase 2: Price Formatting in Export

**Files:**
- `src/modules/gear/utils/exportToPrompt.ts`

**Changes:**
1. Import currency formatter (from FEATURE-017):
   ```typescript
   import { formatCurrency } from '@/modules/gear/utils/currencyFormatter'
   import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
   ```

2. Update `formatItem()` function:
   ```typescript
   function formatItem(
     item: IGearItem,
     options: ExportOptions,
     indentLevel: number = 0,
     defaultCurrency: string = 'PLN'
   ): string {
     // ... existing formatting
     
     // Add price if enabled
     if (options.showPrices && item.price) {
       const currency = item.currency || defaultCurrency
       const formattedPrice = formatCurrency(item.price * (item.quantity || 1), currency)
       parts.push(formattedPrice)
     }
     
     return `${indentStr}- ${parts.join(' ')}`
   }
   ```

3. Update `formatContainer()` function:
   ```typescript
   function formatContainer(
     container: IGearContainer,
     options: ExportOptions,
     defaultCurrency: string = 'PLN'
   ): string {
     // ... existing formatting
     
     // Add price to header if enabled
     if (options.showPrices && container.price) {
       const currency = container.currency || defaultCurrency
       const formattedPrice = formatCurrency(container.price, currency)
       headerParts.push(formattedPrice)
     }
     
     return `## ${headerParts.join(' ')}`
   }
   ```

### Phase 3: "To Buy" Summary

**Files:**
- `src/modules/gear/utils/exportToPrompt.ts`

**Changes:**
1. Add function to calculate "To Buy" summary:
   ```typescript
   function generateToBuySummary(
     containers: IGearContainer[],
     defaultCurrency: string = 'PLN'
   ): string {
     const toBuyItems: Array<{
       name: string
       price: number
       quantity: number
       currency: string
     }> = []
     
     containers.forEach(container => {
       container.items
         .filter(item => item.status === 'toBuy' && item.price)
         .forEach(item => {
           toBuyItems.push({
             name: item.name,
             price: item.price!,
             quantity: item.quantity || 1,
             currency: item.currency || container.currency || defaultCurrency,
           })
         })
     })
     
     if (toBuyItems.length === 0) {
       return ''
     }
     
     // Group by currency
     const byCurrency = new Map<string, typeof toBuyItems>()
     toBuyItems.forEach(item => {
       const existing = byCurrency.get(item.currency) || []
       existing.push(item)
       byCurrency.set(item.currency, existing)
     })
     
     // Generate summary
     let summary = '\n---\n\n## To Buy\n\n'
     
     byCurrency.forEach((items, currency) => {
       const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
       const formattedTotal = formatCurrency(total, currency)
       
       summary += `**Total Cost (${currency}):** ${formattedTotal}\n\n`
       summary += 'Items to purchase:\n'
       items.forEach(item => {
         const itemTotal = item.price * item.quantity
         const formattedPrice = formatCurrency(itemTotal, currency)
         summary += `- **${item.name}**${item.quantity > 1 ? ` x${item.quantity}` : ''} - ${formattedPrice}\n`
       })
       summary += '\n'
     })
     
     return summary
   }
   ```

2. Update main export function to include summary:
   ```typescript
   export function exportToPrompt(
     containers: IGearContainer[],
     options: ExportOptions
   ): string {
     // ... existing export logic
     
     let markdown = // ... existing markdown
     
     // Add "To Buy" summary if prices enabled
     if (options.showPrices) {
       const defaultCurrency = // ... get from settings
       const summary = generateToBuySummary(containers, defaultCurrency)
       markdown += summary
     }
     
     return markdown
   }
   ```

### Phase 4: Integration

**Files:**
- `src/modules/gear/components/ExportToPromptDialog.vue`
- `src/modules/gear/utils/exportToPrompt.ts`

**Changes:**
1. Pass `showPrices` option to export function
2. Get default currency from settings
3. Update preview to show prices when option enabled
4. Test with various currency combinations

---

## 📊 Data Flow

### Export Flow with Prices

```
User enables "Show prices" option
  ↓
Export function receives showPrices: true
  ↓
formatItem() checks showPrices option
  ↓
If item has price → format with currency
  ↓
Add price to item line
  ↓
After all containers exported
  ↓
If showPrices enabled → generate "To Buy" summary
  ↓
Append summary to markdown
  ↓
Return complete markdown with prices
```

---

## 🔍 Technical Details

### Price Display Format

**Item:**
- Format: `- **Name** ... - [weight] - [price] [currency]`
- Price = `item.price * item.quantity` (total cost for item)
- Currency from item, container, or default

**Container:**
- Format: `## Name [#id] - [price] [currency]`
- Price = `container.price`
- Currency from container or default

### Currency Handling

- Use item currency if available
- Fall back to container currency
- Fall back to default currency from settings
- Group "To Buy" summary by currency if multiple currencies

### "To Buy" Summary Logic

- Only include items with `status === 'toBuy'`
- Only include items with price
- Calculate total: `price * quantity`
- Group by currency
- Show per-currency totals and item lists

---

## 🧪 Testing

### Manual Test Cases

1. **Export with Prices Enabled**
   - ✅ Prices shown next to items
   - ✅ Prices shown for containers
   - ✅ Currency displayed correctly
   - ✅ Price formatting correct (currency formatter)

2. **Export with Prices Disabled**
   - ✅ Prices not shown (default behavior)
   - ✅ Export format unchanged

3. **"To Buy" Summary**
   - ✅ Summary appears at end when prices enabled
   - ✅ Only "toBuy" items included
   - ✅ Totals calculated correctly
   - ✅ Multiple currencies handled correctly
   - ✅ Summary not shown if no "toBuy" items

4. **Edge Cases**
   - ✅ Items without price (not shown in export)
   - ✅ Items without currency (use default)
   - ✅ Multiple currencies in one export
   - ✅ Container with no items
   - ✅ All items have prices
   - ✅ No items have prices

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Option to show prices in markdown export
- Price display next to items and containers in export
- "To Buy" summary section with total cost at end of export
- Currency formatting in export (requires FEATURE-017)
- Support for multiple currencies in "To Buy" summary
```

---

## 🚀 Future Enhancements

### Advanced Price Options
- Show prices only for "toBuy" items
- Show price per unit vs total price
- Include price history/trends

### Price Analysis
- Price comparison between containers
- Average price per category
- Price distribution charts

### Export Formats
- CSV export with prices
- Excel export with price breakdown
- PDF export with formatted prices

---

## 📝 Notes

- Requires FEATURE-017 (Currency Support) for proper currency formatting
- Price is optional field - gracefully handle missing prices
- "To Buy" summary only shown if there are items with status "toBuy" and price
- Currency formatting uses `Intl.NumberFormat` for locale-aware display
- Backward compatible - prices not shown by default

---

## 🔗 Related Documentation

- [FEATURE-011](./FEATURE-011-markdown-import-export.md) - Markdown Import/Export
- [FEATURE-017](./FEATURE-017-currency-support.md) - Currency Support
- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Offline Features Roadmap
- Export utility: `src/modules/gear/utils/exportToPrompt.ts`
- Export dialog: `src/modules/gear/components/ExportToPromptDialog.vue`

