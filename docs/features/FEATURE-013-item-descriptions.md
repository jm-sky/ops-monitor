# FEATURE-013: Item Descriptions in Markdown Import/Export

**Status:** 🔄 Planned
**Priority:** Medium
**Complexity:** Medium
**Category:** 🚀 Import/Export
**Related Features:** FEATURE-011 (Markdown Import/Export)

---

## 📋 Overview

Add support for item descriptions (using existing `notes` field) in markdown import/export functionality. Descriptions will be displayed in italics format and users can choose whether to include them in export and in which format.

This feature extends the existing markdown import/export system to include item notes/descriptions, making it easier to include additional context about items when working with AI or sharing gear lists.

---

## 🎯 Goals

1. **Export Support** - Include item descriptions (`notes` field) in markdown export
2. **Format Options** - Two display formats for descriptions in export
3. **User Control** - Checkbox/toggle to enable/disable descriptions in export
4. **Import Support** - Parse italic text as item descriptions when importing markdown
5. **Consistent Formatting** - Descriptions always displayed in italics (`*text*`)

---

## 📐 Design

### Current State

- Items have optional `notes` field (string)
- Markdown export/import does not include `notes` field
- No UI option to control description export

### Proposed Changes

#### 1. Export Format Options

**Option A: Inline Format (Compact)**
```markdown
- **Nóż** *(mały, składany)* - 100g
- **Latarka** *(LED, wodoodporna)* (Petzl, Black) - 90g
```

**Option B: New Line Format (Detailed)**
```markdown
- **Nóż**
  *Mały, składany* - 100g

- **Latarka** (Petzl, Black)
  *LED, wodoodporna* - 90g
```

#### 2. Export Options UI

Add to `ExportToPromptDialog`:
- Radio buttons or Select dropdown with 3 options:
  - **"OFF"** (default) - descriptions not included in export
  - **"Inline"** - description in parentheses after name: `- **Name** *(description)* ...`
  - **"New Line"** - description on separate line below name with 2-space indent

#### 3. Import Format Support

Parser should recognize both formats:
- Inline: `- **Item** *(description)* - 100g`
- Multi-line: 
  ```markdown
  - **Item** - 100g
    *description*
  ```

### Format Rules

1. **Description Format**
   - Always in italics: `*text*`
   - Can contain any text (commas, parentheses, etc.)
   - Optional field - only exported if item has `notes` and option is enabled

2. **Inline Format (Option A)**
   - Description appears immediately after item name
   - Format: `- **Name** *(description)* [rest of item fields]`
   - Example: `- **Nóż** *(mały, składany)* - 100g`

3. **New Line Format (Option B)**
   - Description appears immediately below item name (before other fields)
   - Indented with 2 spaces
   - Format:
     ```markdown
     - **Name**
       *description* [rest of item fields]
     ```
   - Example:
     ```markdown
     - **Nóż**
       *Mały, składany* - 100g
     ```

4. **Import Parsing**
   - Recognize italic text `*text*` in item lines
   - For inline: extract from `*(description)*` pattern after item name
   - For new line: extract from indented line (2+ spaces) starting with `*` immediately after item name line
   - Descriptions can contain parentheses - parser handles nested parentheses correctly
   - Store in `notes` field

---

## 🛠️ Implementation Plan

### Phase 1: Export Support

**Files:**
- `src/modules/gear/utils/exportToPrompt.ts`
- `src/modules/gear/components/ExportToPromptDialog.vue`

**Changes:**
1. Add to `ExportOptions` interface:
   ```typescript
   descriptionFormat?: 'off' | 'inline' | 'newline' // Description format (default: 'off')
   ```

2. Update `formatItem()` function:
   - Check if `item.notes` exists and `options.descriptionFormat !== 'off'`
   - If inline format: add `*(description)*` immediately after item name (before quantity, brand, etc.)
   - If newline format: split item line - name on first line, description on second line (2-space indent), then rest of fields

3. Update `ExportToPromptDialog`:
   - Add radio buttons or Select dropdown with 3 options: "OFF", "Inline", "New Line"
   - Default: "OFF"
   - Pass `descriptionFormat` option to export functions

### Phase 2: Import Support

**Files:**
- `src/modules/gear/services/markdownImportService.ts`

**Changes:**
1. Update `parseItemLine()` method:
   - Detect inline format: `- **Name** *(description)* ...` (description in parentheses with italics)
   - Detect newline format: check if next line matches indented italic pattern `^\s{2,}\*([^*]+)\*`
   - Extract description and store in `notes` field
   - Handle nested parentheses in descriptions (e.g., `*(tekst z (nawiasami))*`)

2. Parsing logic:
   - **Inline format:** Match pattern `\*\*([^*]+)\*\*\s+\*\(([^)]+)\)\*` (greedy match for parentheses to handle nested)
   - **Newline format:** After parsing item name line, check if next line matches `^\s{2,}\*([^*]+)\*$`
   - Extract text between `*()` for inline or between `*` for newline
   - Store extracted text in `notes` field
   - Remove description from working line after extraction

### Phase 3: Guidelines Update

**Files:**
- `src/modules/gear/services/markdownImportService.ts` (guidelinesTemplate)
- `src/modules/gear/components/GuidelinesDialog.vue`

**Changes:**
1. Update `guidelinesTemplate`:
   - Add section about item descriptions
   - Show both format options with examples
   - Explain when to use each format

2. Add examples:
   ```markdown
   ## Item Descriptions (Optional)
   
   Item descriptions can be included in two formats:
   
   **Inline format:**
   - **Knife** *(small, folding)* - 100g
   
   **New line format:**
   - **Knife**
     *small, folding* - 100g
   
   Descriptions can contain parentheses and other characters.
   ```

---

## 📊 Data Flow

### Export Flow

```
Item with notes field
  ↓
ExportOptions { descriptionFormat: 'inline' | 'newline' | 'off' }
  ↓
formatItem() checks if notes exists and descriptionFormat !== 'off'
  ↓
Format description based on descriptionFormat:
  - inline: add *(description)* after name
  - newline: split line, description on separate indented line
  ↓
Markdown with description included
```

### Import Flow

```
Markdown line with italic text
  ↓
parseItemLine() detects description format
  ↓
Extract description text
  ↓
Store in item.notes field
  ↓
Create item with notes
```

---

## 🔍 Technical Details

### Export Implementation

**Inline Format:**
```typescript
if (item.notes && options.descriptionFormat === 'inline') {
  // Insert description immediately after name (before quantity, brand, etc.)
  parts.splice(1, 0, `*(${item.notes})*`) // Insert at position 1 (after name)
}
```

**New Line Format:**
```typescript
if (item.notes && options.descriptionFormat === 'newline') {
  // Split: name on first line, description on second line, then rest of fields
  const namePart = parts[0] // **Name**
  const restParts = parts.slice(1) // quantity, brand, color, etc.
  return `${indentStr}- ${namePart}\n${indentStr}  *${item.notes}*${restParts.length > 0 ? ' ' + restParts.join(' ') : ''}`
}
```

### Import Parsing

**Inline Pattern:**
```typescript
// Match: - **Name** *(description)* rest...
// Use greedy match to handle nested parentheses: *\(([^)]+)\)* or *\((.+?)\)* with balanced parentheses
const inlineDescMatch = line.match(/\*\*([^*]+)\*\*\s+\*\(([^)]+)\)\*/)
if (inlineDescMatch) {
  itemName = inlineDescMatch[1]
  description = inlineDescMatch[2] // Can contain nested parentheses
  // Remove description from working line
  workingLine = workingLine.replace(/\*\*([^*]+)\*\*\s+\*\(([^)]+)\)\*/, '**$1**')
}
```

**New Line Detection:**
```typescript
// After parsing item name line, check next line for indented italic text
if (lines[index + 1]?.match(/^\s{2,}\*([^*]+)\*$/)) {
  const descMatch = lines[index + 1].match(/^\s{2,}\*([^*]+)\*$/)
  if (descMatch) {
    description = descMatch[1]
    index++ // Skip description line
    // Continue parsing rest of item fields from description line or next line
  }
}
```

---

## 🧪 Testing

### Manual Test Cases

1. **Export with inline descriptions**
   - ✅ Item with notes exports with inline format
   - ✅ Description appears in parentheses after name
   - ✅ Other item fields still work correctly

2. **Export with newline descriptions**
   - ✅ Item with notes exports with newline format
   - ✅ Description appears on separate indented line immediately below name
   - ✅ Other item fields appear after description line
   - ✅ Format: `- **Name**\n  *description* - 100g`

3. **Export without descriptions**
   - ✅ When option set to "OFF", descriptions not included
   - ✅ Export format unchanged from current behavior

4. **Import inline format**
   ```markdown
   - **Knife** *(small, folding)* - 100g
   ```
   - ✅ Parses item name correctly
   - ✅ Extracts description to notes field
   - ✅ Parses weight correctly

5. **Import newline format**
   ```markdown
   - **Knife**
     *small, folding* - 100g
   ```
   - ✅ Parses item name correctly
   - ✅ Extracts description from next indented line
   - ✅ Parses weight correctly from description line or next line
   
6. **Import with nested parentheses in description**
   ```markdown
   - **Knife** *(small (folding), lightweight)* - 100g
   ```
   - ✅ Parses item name correctly
   - ✅ Extracts full description including nested parentheses
   - ✅ Stores in notes field correctly

7. **Import without descriptions**
   ```markdown
   - **Knife** - 100g
   ```
   - ✅ Parses correctly (no description)
   - ✅ Notes field remains empty

8. **Mixed format in same export**
   - ✅ Items with notes show descriptions
   - ✅ Items without notes show normally
   - ✅ Format consistent for all items with descriptions

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Item descriptions support in markdown export/import (using `notes` field)
- Export option with 3 choices: OFF, Inline, New Line
- Inline format: description in parentheses after name
- New line format: description on separate indented line below name
- Import parser recognizes both formats automatically
- Support for nested parentheses in descriptions
```

---

## 🚀 Future Enhancements

### Rich Text Descriptions
- Support for markdown formatting in descriptions (bold, links, lists)
- Multi-line descriptions with line breaks
- HTML rendering in UI

### Description Templates
- Pre-defined description templates for common items
- AI-generated descriptions based on item name/category

---

## 📝 Notes

- Uses existing `notes` field - no database schema changes needed
- Descriptions are optional - backward compatible with existing exports
- Format choice is user preference - both formats supported in import
- Italic format (`*text*`) is standard markdown - easy for AI to understand
- Inline format is more compact, newline format is more readable for longer descriptions
- Newline format places description immediately below name (before other fields like weight, brand, etc.)
- Parser handles nested parentheses in descriptions correctly

---

## 🔗 Related Documentation

- [FEATURE-011](./FEATURE-011-markdown-import-export.md) - Markdown Import/Export implementation
- [ROADMAP.md](../ROADMAP.md) - Overall project roadmap
- Export utility: `src/modules/gear/utils/exportToPrompt.ts`
- Import service: `src/modules/gear/services/markdownImportService.ts`
- Export dialog: `src/modules/gear/components/ExportToPromptDialog.vue`

