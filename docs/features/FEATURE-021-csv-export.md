# FEATURE-021: CSV Export (Eksport do CSV)

**Status:** ✅ Completed
**Priority:** Medium
**Complexity:** Medium
**Category:** 🚀 Import/Export
**Related Features:** FEATURE-011 (Markdown Import/Export), FEATURE-020 (Price Display in Export), FEATURE-017 (Currency Support)

---

## 📋 Overview

Add CSV export functionality for containers, allowing users to export gear data to a structured CSV format suitable for spreadsheet applications (Excel, Google Sheets, LibreOffice Calc). The export will support customizable columns, different separators, and UTF-8 encoding with BOM for proper Excel compatibility.

This feature complements the existing markdown export by providing a more structured, data-analysis-friendly format that works seamlessly with spreadsheet software.

---

## 🎯 Goals

1. **CSV Export Dialog** - User-friendly dialog with export options
2. **Column Selection** - Allow users to choose which columns to include
3. **Separator Options** - Support comma and semicolon separators
4. **Excel Compatibility** - UTF-8 with BOM encoding for proper Excel display
5. **Price Support** - Include prices and currencies in export (if available)
6. **Nested Containers** - Export all items including nested containers with container information (optionable, default: `true`, controlled by checkbox)
7. **Comprehensive Data** - Export all relevant item fields (name, category, quantity, weight, price, currency, brand, color, status, priority, URL, notes)

---

## 📐 Design

### UX Analysis

#### Current Export Options
- **JSON Export** (`handleExport`) - Full data export for backup/restore
- **Markdown Export** (`ExportToPromptDialog`) - AI-friendly, human-readable format
- **CSV Export** (new) - Structured data for spreadsheet analysis

#### Use Cases for CSV Export
1. **Financial Analysis** - Calculate total costs, compare prices, budget planning
2. **Weight Analysis** - Analyze weight distribution, optimize packing
3. **Inventory Management** - Track items across containers, generate reports
4. **Shopping Lists** - Export "to buy" items with prices for shopping
5. **Data Migration** - Import into other systems that accept CSV
6. **Sharing with Non-Technical Users** - Easy to open in Excel/Sheets

#### UX Decisions

**1. Location in UI**
- Add "Export to CSV" option in the "More Actions" dropdown menu (same location as JSON export)
- Position: After "Export" (JSON) and before "Import"
- Rationale: Group all export options together, CSV is a common export format

**2. Dialog Design**
- Similar structure to `ExportToPromptDialog` but focused on CSV options
- Sections:
  - Column selection (checkboxes for each available column)
  - Separator selection (radio buttons: comma, semicolon)
  - Encoding option (checkbox: "UTF-8 with BOM for Excel" - checked by default)
  - Preview (optional, can be minimal or just show row count)
  - Action buttons: "Export" and "Cancel"

**3. Column Selection**
- Default: All columns selected
- Grouped by category:
  - **Basic**: Name, Category, Quantity
  - **Physical**: Weight, Weight Unit
  - **Financial**: Price, Currency
  - **Details**: Brand, Color, Status, Priority
  - **Additional**: URL, Notes, Container Name, Container Type
- "Select All" / "Deselect All" buttons for convenience

**4. Separator Selection**
- **Comma (`,`)** - Default for English/US systems
- **Semicolon (`;`)** - Common for European systems (especially Poland, where Excel uses semicolon)
- Default: Based on user locale (semicolon for pl-PL, comma for others)

**5. Nested Containers Handling**
- Export all items from the container and all nested containers
- Include "Container Name" and "Container Type" columns to identify item source
- Flat structure (one row per item) - easier for spreadsheet analysis
- Alternative: Could add option for "Include nested containers" checkbox (default: checked)

**6. File Naming**
- Format: `gear-export-[container-name]-[date].csv`
- Sanitize container name (remove special characters, replace spaces with hyphens)
- Date format: `YYYY-MM-DD`

**7. Price Display**
- Include prices if available (from FEATURE-020 and FEATURE-017)
- Show price per unit (not multiplied by quantity) - users can calculate totals in spreadsheet
- Include currency code in separate column
- Alternative: Option to show "Total Price" (price × quantity) vs "Unit Price"

### Current State

- ✅ Container and item data structures support all required fields
- ✅ Price and currency fields exist (FEATURE-017)
- ✅ Export to JSON exists (`handleExport` in ContainerDetailPage)
- ✅ Export to Markdown exists (`ExportToPromptDialog`)
- ✅ Nested container support exists
- ❌ No CSV export functionality
- ❌ No CSV export dialog
- ❌ No column selection UI
- ❌ No separator/encoding options

### Proposed Changes

#### 1. Export Menu Item

**Location:** `src/modules/gear/components/ContainerHeader.vue`

**Changes:**
- Add "Export to CSV" menu item in dropdown
- Position after "Export" (JSON) menu item
- Icon: Use existing export icon or add CSV-specific icon

#### 2. CSV Export Dialog

**Location:** `src/modules/gear/components/ExportToCSVDialog.vue` (new file)

**UI Structure:**
```vue
<Dialog>
  <DialogHeader>
    <DialogTitle>Export to CSV</DialogTitle>
    <DialogDescription>Configure CSV export options</DialogDescription>
  </DialogHeader>
  
  <DialogContent>
    <!-- Column Selection -->
    <div class="space-y-4">
      <div>
        <Label>Columns to Export</Label>
        <div class="flex gap-2 mb-2">
          <Button @click="selectAllColumns">Select All</Button>
          <Button @click="deselectAllColumns">Deselect All</Button>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <!-- Checkboxes for each column -->
        </div>
      </div>
      
      <!-- Separator Selection -->
      <div>
        <Label>Separator</Label>
        <RadioGroup>
          <RadioGroupItem value="comma">Comma (,)</RadioGroupItem>
          <RadioGroupItem value="semicolon">Semicolon (;)</RadioGroupItem>
        </RadioGroup>
      </div>
      
      <!-- Encoding Option -->
      <div>
        <Checkbox v-model="useBOM">
          UTF-8 with BOM (for Excel compatibility)
        </Checkbox>
      </div>
      
      <!-- Preview Info -->
      <div class="text-sm text-muted-foreground">
        Will export {{ itemCount }} items
      </div>
    </div>
    
    <DialogFooter>
      <Button @click="handleExport">Export</Button>
      <Button variant="outline" @click="handleCancel">Cancel</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

#### 3. CSV Export Utility

**Location:** `src/modules/gear/utils/exportToCSV.ts` (new file)

**Functions:**
- `exportContainerToCSV()` - Main export function
- `generateCSVRow()` - Format single item as CSV row
- `escapeCSVValue()` - Escape special characters in CSV values
- `getDefaultSeparator()` - Get separator based on locale

**CSV Format:**
- Header row with column names
- One row per item
- Proper escaping of commas, quotes, newlines
- UTF-8 encoding with optional BOM

---

## 🛠️ Implementation Plan

### Phase 1: CSV Export Utility

**Files:**
- `src/modules/gear/utils/exportToCSV.ts` (new)

**Changes:**
1. Create `CSVExportOptions` interface:
   ```typescript
   interface CSVExportOptions {
     columns: string[] // Selected column names
     separator: ',' | ';'
     useBOM: boolean
     includeNestedContainers: boolean
   }
   ```

2. Create `exportContainerToCSV()` function:
   ```typescript
   export function exportContainerToCSV(
     container: IGearContainer,
     allContainers: IGearContainer[],
     options: CSVExportOptions
   ): string {
     // Collect all items (including nested)
     // Generate header row
     // Generate data rows
     // Return CSV string
   }
   ```

3. Implement column mapping:
   ```typescript
   const columnMap = {
     name: (item) => item.name,
     category: (item) => item.category,
     quantity: (item) => item.quantity,
     weight: (item) => item.weight,
     weightUnit: (item) => item.weightUnit,
     price: (item) => item.price ?? '',
     currency: (item) => item.currency ?? '',
     brand: (item) => item.brand ?? '',
     color: (item) => item.color ?? '',
     status: (item) => item.status,
     priority: (item) => item.priority,
     url: (item) => item.url ?? '',
     notes: (item) => item.notes ?? '',
     containerName: (item, container) => container.name,
     containerType: (item, container) => container.type,
   }
   ```

4. Implement CSV escaping:
   ```typescript
   function escapeCSVValue(value: string | number | null | undefined): string {
     if (value === null || value === undefined) return ''
     const str = String(value)
     // If contains separator, quote, or newline, wrap in quotes and escape quotes
     if (str.includes(options.separator) || str.includes('"') || str.includes('\n')) {
       return `"${str.replace(/"/g, '""')}"`
     }
     return str
   }
   ```

5. Handle nested containers:
   ```typescript
   function collectAllItems(
     container: IGearContainer,
     allContainers: IGearContainer[]
   ): Array<{ item: IGearItem; container: IGearContainer }> {
     const items: Array<{ item: IGearItem; container: IGearContainer }> = []
     
     // Add items from current container
     container.items.forEach(item => {
       items.push({ item, container })
       
       // If item references nested container, recurse
       if (item.containerId) {
         const nestedContainer = allContainers.find(c => c.id === item.containerId)
         if (nestedContainer) {
           items.push(...collectAllItems(nestedContainer, allContainers))
         }
       }
     })
     
     return items
   }
   ```

6. Add BOM support:
   ```typescript
   function addBOM(csv: string): string {
     return '\uFEFF' + csv // UTF-8 BOM
   }
   ```

### Phase 2: Export Dialog Component

**Files:**
- `src/modules/gear/components/ExportToCSVDialog.vue` (new)
- `src/modules/gear/i18n/locales/*.ts`

**Changes:**
1. Create dialog component with:
   - Column selection checkboxes
   - Separator radio buttons
   - BOM checkbox
   - Preview info (item count)
   - Export and Cancel buttons

2. Define available columns:
   ```typescript
   const availableColumns = [
     { key: 'name', label: 'Name', category: 'basic' },
     { key: 'category', label: 'Category', category: 'basic' },
     { key: 'quantity', label: 'Quantity', category: 'basic' },
     { key: 'weight', label: 'Weight', category: 'physical' },
     { key: 'weightUnit', label: 'Weight Unit', category: 'physical' },
     { key: 'price', label: 'Price', category: 'financial' },
     { key: 'currency', label: 'Currency', category: 'financial' },
     { key: 'brand', label: 'Brand', category: 'details' },
     { key: 'color', label: 'Color', category: 'details' },
     { key: 'status', label: 'Status', category: 'details' },
     { key: 'priority', label: 'Priority', category: 'details' },
     { key: 'url', label: 'URL', category: 'additional' },
     { key: 'notes', label: 'Notes', category: 'additional' },
     { key: 'containerName', label: 'Container Name', category: 'additional' },
     { key: 'containerType', label: 'Container Type', category: 'additional' },
   ]
   ```

3. Default selected columns: All columns selected

4. Default separator: Based on locale (semicolon for pl-PL, comma for others)

5. Default BOM: true (for Excel compatibility)

6. Handle export:
   ```typescript
   const handleExport = () => {
     const csv = exportContainerToCSV(
       props.container,
       store.getAllContainers,
       {
         columns: selectedColumns.value,
         separator: selectedSeparator.value,
         useBOM: useBOM.value,
         includeNestedContainers: true,
       }
     )
     
     // Create blob and download
     const blob = new Blob(
       [csv],
       { type: 'text/csv;charset=utf-8;' }
     )
     const url = URL.createObjectURL(blob)
     const link = document.createElement('a')
     link.href = url
     link.download = generateFileName(props.container.name)
     document.body.appendChild(link)
     link.click()
     document.body.removeChild(link)
     URL.revokeObjectURL(url)
     
     emit('update:open', false)
     toast.success(t('gear.export.csv.success'))
   }
   ```

7. Add translations:
   - `gear.export.csv.title`: "Export to CSV"
   - `gear.export.csv.description`: "Configure CSV export options"
   - `gear.export.csv.columns`: "Columns to Export"
   - `gear.export.csv.selectAll`: "Select All"
   - `gear.export.csv.deselectAll`: "Deselect All"
   - `gear.export.csv.separator`: "Separator"
   - `gear.export.csv.separatorComma`: "Comma (,)"
   - `gear.export.csv.separatorSemicolon`: "Semicolon (;)"
   - `gear.export.csv.useBOM`: "UTF-8 with BOM (for Excel compatibility)"
   - `gear.export.csv.itemsCount`: "Will export {count} items"
   - `gear.export.csv.success`: "CSV exported successfully"

### Phase 3: Integration with Container Header

**Files:**
- `src/modules/gear/components/ContainerHeader.vue`
- `src/modules/gear/pages/ContainerDetailPage.vue`

**Changes:**
1. Add "Export to CSV" menu item in `ContainerHeader.vue`:
   ```vue
   <DropdownMenuItem @click="handleExportToCSV">
     <ExportCSVIcon class="size-4" />
     {{ t('gear.actions.exportToCSV') }}
   </DropdownMenuItem>
   ```

2. Add emit in `ContainerHeader.vue`:
   ```typescript
   const emit = defineEmits<{
     // ... existing emits
     exportToCSV: []
   }>()
   ```

3. Add handler in `ContainerDetailPage.vue`:
   ```typescript
   const isExportToCSVDialogOpen = ref(false)
   
   const handleExportToCSV = () => {
     isExportToCSVDialogOpen.value = true
   }
   ```

4. Add dialog component in `ContainerDetailPage.vue`:
   ```vue
   <ExportToCSVDialog
     v-model:open="isExportToCSVDialogOpen"
     :container="container"
   />
   ```

5. Add translation:
   - `gear.actions.exportToCSV`: "Export to CSV"

### Phase 4: File Name Generation

**Files:**
- `src/modules/gear/utils/exportToCSV.ts`

**Changes:**
1. Create `generateCSVFileName()` function:
   ```typescript
   export function generateCSVFileName(containerName: string): string {
     const sanitized = containerName
       .toLowerCase()
       .normalize('NFD')
       .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
       .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
       .trim()
       .replace(/\s+/g, '-') // Replace spaces with hyphens
       .replace(/-+/g, '-') // Collapse multiple hyphens
     
     const date = new Date().toISOString().split('T')[0] // YYYY-MM-DD
     return `gear-export-${sanitized}-${date}.csv`
   }
   ```

### Phase 5: Testing & Polish

**Files:**
- All files from previous phases

**Changes:**
1. Test with various data:
   - Items with all fields filled
   - Items with missing optional fields
   - Nested containers
   - Items with special characters in names/notes
   - Items with commas/quotes in text fields
   - Items with newlines in notes

2. Test Excel compatibility:
   - Open CSV in Excel (Windows/Mac)
   - Verify Polish characters display correctly
   - Verify proper column separation
   - Verify proper escaping of special characters

3. Test Google Sheets compatibility:
   - Import CSV to Google Sheets
   - Verify proper formatting

4. Test with different separators:
   - Comma separator (English locale)
   - Semicolon separator (Polish locale)

5. Test column selection:
   - Export with all columns
   - Export with subset of columns
   - Export with only required columns

---

## 📊 Data Flow

### CSV Export Flow

```
User clicks "Export to CSV" in menu
  ↓
ExportToCSVDialog opens
  ↓
User selects columns, separator, encoding options
  ↓
User clicks "Export"
  ↓
exportContainerToCSV() called with options
  ↓
Collect all items (including nested containers)
  ↓
Generate CSV header row from selected columns
  ↓
For each item:
  - Map item data to selected columns
  - Escape special characters
  - Format as CSV row
  ↓
Combine header + rows into CSV string
  ↓
Add BOM if option enabled
  ↓
Create Blob and trigger download
  ↓
File saved: gear-export-[name]-[date].csv
```

---

## 🔍 Technical Details

### CSV Format Specification

**Standard:** RFC 4180 (with UTF-8 BOM option for Excel)

**Rules:**
1. Header row with column names
2. One row per item
3. Fields separated by selected separator (`,` or `;`)
4. Fields containing separator, quote, or newline wrapped in double quotes
5. Double quotes in field values escaped as `""`
6. Empty/null values represented as empty string
7. UTF-8 encoding with optional BOM (`\uFEFF`)

### Column Mapping

| Column Key | Source | Format | Notes |
|------------|--------|--------|-------|
| `name` | `item.name` | string | Required field |
| `category` | `item.category` | string | Category name |
| `quantity` | `item.quantity` | number | Default: 1 |
| `weight` | `item.weight` | number | Weight value |
| `weightUnit` | `item.weightUnit` | string | 'g' or 'kg' |
| `price` | `item.price` | number | Empty if null |
| `currency` | `item.currency` | string | Currency code (PLN, USD, etc.) |
| `brand` | `item.brand` | string | Empty if null |
| `color` | `item.color` | string | Empty if null |
| `status` | `item.status` | string | 'owned', 'missing', 'toBuy' |
| `priority` | `item.priority` | string | 'low', 'medium', 'high', 'critical' |
| `url` | `item.url` | string | Empty if null |
| `notes` | `item.notes` | string | Empty if null, may contain newlines |
| `containerName` | `container.name` | string | Container containing the item |
| `containerType` | `container.type` | string | Container type |

### Nested Container Handling

**Strategy:** Flat structure with container identification

- Export all items from main container
- Export all items from nested containers
- Include "Container Name" and "Container Type" columns
- One row per item (no hierarchical structure in CSV)
- Users can filter/group by container in spreadsheet

**Alternative (Future):** Option to export only top-level container items (exclude nested)

### Encoding & BOM

**UTF-8 with BOM:**
- BOM (Byte Order Mark): `\uFEFF`
- Required for Excel to recognize UTF-8 encoding
- Without BOM, Excel may interpret CSV as Windows-1250 (Polish) or other encoding
- Default: Enabled (for better Excel compatibility)

**UTF-8 without BOM:**
- Standard UTF-8 encoding
- Works with Google Sheets, LibreOffice, most modern editors
- Option available for users who don't need Excel compatibility

### Separator Selection

**Comma (`,`):**
- Standard CSV separator
- Default for English/US locales
- Works with most spreadsheet applications

**Semicolon (`;`):**
- Common in European locales (especially Poland)
- Excel in Polish locale uses semicolon by default
- Better compatibility for Polish users

**Auto-detection:**
- Based on user locale (`navigator.language` or i18n locale)
- `pl-PL` → semicolon
- Others → comma

---

## 🧪 Testing

### Manual Test Cases

1. **Basic Export**
   - ✅ Export single container with items
   - ✅ CSV file created with correct name
   - ✅ All columns included (if all selected)
   - ✅ Data matches container items

2. **Column Selection**
   - ✅ Export with all columns selected
   - ✅ Export with subset of columns
   - ✅ Export with only name column
   - ✅ Column order matches selection order

3. **Separator Options**
   - ✅ Comma separator works correctly
   - ✅ Semicolon separator works correctly
   - ✅ Default separator based on locale

4. **Encoding & BOM**
   - ✅ UTF-8 with BOM opens correctly in Excel
   - ✅ Polish characters (ą, ć, ę, ł, ń, ó, ś, ź, ż) display correctly
   - ✅ UTF-8 without BOM works in Google Sheets

5. **Special Characters**
   - ✅ Items with commas in name/notes properly escaped
   - ✅ Items with quotes in name/notes properly escaped
   - ✅ Items with newlines in notes properly escaped
   - ✅ Items with special characters (ą, ć, etc.) display correctly

6. **Nested Containers**
   - ✅ Items from main container included
   - ✅ Items from nested containers included
   - ✅ Container name/type columns identify item source
   - ✅ No duplicate items

7. **Empty/Null Values**
   - ✅ Empty fields exported as empty string
   - ✅ Null values exported as empty string
   - ✅ Items without optional fields (price, brand, etc.) export correctly

8. **Price & Currency**
   - ✅ Items with prices export correctly
   - ✅ Items without prices export with empty price/currency
   - ✅ Multiple currencies handled correctly

9. **File Naming**
   - ✅ File name includes container name (sanitized)
   - ✅ File name includes date (YYYY-MM-DD)
   - ✅ Special characters in container name removed/replaced

10. **Excel Compatibility**
    - ✅ CSV opens in Excel (Windows)
    - ✅ CSV opens in Excel (Mac)
    - ✅ Columns properly separated
    - ✅ Polish characters display correctly
    - ✅ No encoding issues

11. **Google Sheets Compatibility**
    - ✅ CSV imports to Google Sheets correctly
    - ✅ Columns properly separated
    - ✅ Data formatted correctly

12. **Edge Cases**
    - ✅ Container with no items (empty CSV with header only)
    - ✅ Container with only nested containers (no direct items)
    - ✅ Very long item names/notes
    - ✅ Items with all fields filled
    - ✅ Items with no optional fields

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- CSV export functionality for containers
- Export dialog with column selection, separator options, and encoding settings
- Support for comma and semicolon separators
- UTF-8 with BOM encoding option for Excel compatibility
- Export of nested containers with container identification columns
- Comprehensive column support (name, category, quantity, weight, price, currency, brand, color, status, priority, URL, notes, container info)
```

---

## 🚀 Future Enhancements

### Advanced Export Options
- Export multiple containers at once
- Filter items by status (e.g., only "to buy" items)
- Filter items by category
- Export date range (items created/updated in date range)
- Custom column order (drag & drop)

### Export Formats
- Excel format (.xlsx) export (native Excel, not CSV)
- JSON export enhancement (already exists, but could add CSV-like column selection)
- PDF export with formatted table

### Import from CSV
- Import items from CSV back into containers
- Column mapping UI
- Validation and error handling
- Preview before import

### Analytics Integration
- Pre-calculated totals (total weight, total price) in separate rows
- Summary statistics at end of CSV
- Category breakdowns

---

## 📝 Notes

- CSV export complements existing markdown export - different use cases
- Markdown export: AI-friendly, human-readable, flexible format
- CSV export: Structured data, spreadsheet analysis, data migration
- UTF-8 BOM is essential for Excel compatibility with non-ASCII characters
- Semicolon separator is important for Polish users (Excel default)
- Flat structure (one row per item) is easier for spreadsheet analysis than hierarchical
- Container identification columns allow filtering/grouping in spreadsheet
- All optional fields should gracefully handle null/undefined values

---

## 🔗 Related Documentation

- [FEATURE-011](./FEATURE-011-markdown-import-export.md) - Markdown Import/Export
- [FEATURE-020](./FEATURE-020-price-display-in-export.md) - Price Display in Export
- [FEATURE-017](./FEATURE-017-currency-support.md) - Currency Support
- [ROADMAP_OFFLINE.md](../ROADMAP_OFFLINE.md) - Offline Features Roadmap
- Export utility: `src/modules/gear/utils/exportToCSV.ts` (to be created)
- Export dialog: `src/modules/gear/components/ExportToCSVDialog.vue` (to be created)
- Container header: `src/modules/gear/components/ContainerHeader.vue`

