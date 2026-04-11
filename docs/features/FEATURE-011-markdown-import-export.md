# FEATURE-011: Markdown Import/Export (AI-Friendly Format)

**Status:** ✅ Completed
**Priority:** High
**Complexity:** Large
**Category:** 🚀 Import/Export
**Related Features:** FEATURE-009 (Export to Prompt)

---

## 📋 Overview

Comprehensive markdown-based import/export system that allows bidirectional conversion between app data and a human/AI-friendly markdown format. The system enables users to:
- Export gear lists to markdown for AI processing (ChatGPT, Claude, etc.)
- Edit gear lists in plain text using AI assistance
- Import markdown back into the app with flexible parsing
- Maintain relationships between nested containers using slug-based IDs

This feature bridges the gap between structured data storage and natural language processing, making it easy to leverage AI for gear list management, optimization, and planning.

---

## 🎯 Goals

1. **Unified Format** - Single markdown format for both import and export
2. **AI-Friendly** - Easy for AI to understand and generate
3. **Flexible Parsing** - Import parser can handle fields in any order and guess missing data
4. **Nested Container Support** - Proper handling of container hierarchies using `[#slug-id]` references
5. **URL Support** - Auto-detection and parsing of URLs from items
6. **Optional Fields** - Only item name is required, everything else is optional with sensible defaults
7. **Guidelines Template** - Comprehensive formatting guide for AI models

---

## 📐 Design

### Markdown Format

```markdown
## [Container Name] [#container-id] ([Container Type])
- **[Item Name]** x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
```

### Format Rules

1. **Container Header**
   - Level 2 heading (`##`)
   - Container name (required)
   - `[#slug-id]` - slug-based ID generated from name (required)
   - `(Type)` in parentheses - container type (optional)
   - Example: `## Bug-Out Bag [#bug-out-bag] (Backpack)`

2. **Item Line**
   - Starts with `- ` (list item)
   - `**Name**` - bold text is item name (required)
   - `x[number]` - quantity, can appear anywhere (optional, default: 1)
   - `([Brand], [Color])` - first parentheses for brand/color (optional)
   - `([Status])` or `(Expiration: DD.MM.YYYY)` - second parentheses for status/expiration (optional)
   - `[#nested-id]` - reference to nested container (optional)
   - `<URL>` or plain URL - link to product/info (optional)
   - `- [weight]g` or `- [weight]kg` - weight at the end (optional, default: 100g)

### Example

```markdown
## Bug-Out Bag [#bug-out-bag] (Backpack)
- **Water Bottle** x2 (Nalgene) - 300g
- **Emergency Food** x5 (Expiration: 31.12.2025) - 1000g
- **Tactical Knife** (Victorinox, Black) <https://victorinox.com> - 200g
- **First Aid Pouch** (Pouch) [#first-aid-pouch] - 350g

## First Aid Pouch [#first-aid-pouch] (Pouch)
- **Bandages** x5 - 100g
- **Pain Pills** (Expiration: 31.12.2025) - 50g
```

---

## 🛠️ Implementation

### Phase 1: Slug-based ID System ✅

**Files:**
- `src/modules/gear/utils/exportToPrompt.ts`

**Changes:**
1. Added `slugify()` function:
   - Converts text to lowercase
   - Normalizes unicode characters (NFD)
   - Removes diacritics
   - Removes special characters
   - Replaces spaces with hyphens
   - Example: "First Aid Pouch" → "first-aid-pouch"

2. Added `generateContainerId()` function:
   - Wraps slug with `#` prefix
   - Example: "Bug-Out Bag" → "#bug-out-bag"

3. Updated export functions to include `[#id]` in container headers and nested item references

### Phase 2: Export Enhancements ✅

**Files:**
- `src/modules/gear/utils/exportToPrompt.ts`
- `src/modules/gear/components/ExportToPromptDialog.vue`
- `src/modules/gear/pages/ContainersListPage.vue`

**Changes:**
1. Added URL export: `<URL>` format in item lines
2. Added container ID in headers: `[#slug-id]`
3. Added nested container ID references: `[#nested-id]` in item lines
4. Added "Export All" button to ContainersListPage
5. Added "Guidelines" button to ExportToPromptDialog with comprehensive template
6. Updated format to make weight optional

### Phase 3: Flexible Import Parser ✅

**Files:**
- `src/modules/gear/services/markdownImportService.ts`

**Changes:**
1. Updated `IMarkdownImportResult` interface:
   - Added `id?: string` to container
   - Added `nestedContainerId?: string` to item

2. Complete rewrite of `parseItemLine()` method:
   - Sequential extraction with working line approach
   - Extract bold text as item name
   - Extract weight at the end (`- 500g` or `- 2.5kg`)
   - Extract container ID `[#id]` for nested references
   - Extract URL (angle brackets, plain http://, https://, www.)
   - Extract quantity anywhere in line (`x2`, `×5`)
   - Parse multiple parentheses groups for brand/color/status/expiration
   - Flexible field recognition - any order, all optional except name
   - Default values: weight=100g, quantity=1, status=owned

3. Added URL auto-detection:
   - Recognizes URLs in angle brackets: `<https://example.com>`
   - Recognizes plain URLs: `https://example.com`, `http://example.com`
   - Recognizes www URLs: `www.example.com`
   - Auto-adds `https://` to www URLs

4. Container ID extraction from headers:
   - Regex: `/\[#([^\]]+)\]/`
   - Extracts ID from `## Container Name [#container-id] (Type)`
   - Stores in container object for relationship building

### Phase 4: Guidelines Template ✅

**Files:**
- `src/modules/gear/components/ExportToPromptDialog.vue`

**Changes:**
1. Added comprehensive markdown template (`guidelinesTemplate`)
2. Sections:
   - Standard format definition
   - Format rules for each field
   - Examples (minimal, with quantity, with brand/color, with status, with URL, complete)
   - Container examples with nesting
   - Nested container documentation
   - Container types list
   - Important notes
3. Added "Guidelines" button with copy functionality
4. Added translation for guidelines copied toast

### Phase 5: UI/UX Improvements ✅

**Files:**
- `src/modules/gear/pages/ContainersListPage.vue`
- `src/modules/gear/components/ExportToPromptDialog.vue`
- `src/modules/gear/i18n/index.ts`

**Changes:**
1. Added "Export All" menu item to ContainersListPage dropdown
2. Updated dialog to `w-[95vw]` for mobile responsiveness
3. Added translations:
   - `gear.export.allToPrompt`
   - `gear.export.noContainers`
   - `gear.export.guidelines`
   - `gear.export.guidelinesCopied`

---

## 📊 Data Flow

### Export Flow

```
Container Data (App)
  ↓
exportContainerToPrompt() / exportContainersToPrompt()
  ↓
Generate slug-based IDs from container names
  ↓
Format items with all fields (brand, color, URL, status, expiration, weight)
  ↓
Add [#id] to container headers and nested references
  ↓
Markdown String
  ↓
ExportToPromptDialog (with Guidelines button)
  ↓
User copies to clipboard
```

### Import Flow

```
Markdown String (from AI or manual edit)
  ↓
markdownImportService.parseMarkdown()
  ↓
Extract container headers with [#id]
  ↓
Extract item lines with flexible parser
  ↓
Recognize fields in any order (name, qty, brand, color, status, URL, weight, nested ID)
  ↓
Apply defaults for missing fields
  ↓
Match brands/colors against suggested values
  ↓
Auto-categorize items by keywords
  ↓
IMarkdownImportResult { containers, errors }
  ↓
ImportMarkdownDialog (preview & import)
  ↓
Create containers and items in app
  ↓
Build nested container relationships using [#id] references
```

---

## 🔍 Technical Details

### Slug Generation Algorithm

```typescript
function slugify(text: string): string {
  return text
    .toLowerCase()                      // "Bug-Out Bag" → "bug-out bag"
    .normalize('NFD')                   // Normalize unicode
    .replace(/[\u0300-\u036f]/g, '')   // Remove diacritics (ą→a, ć→c)
    .replace(/[^a-z0-9\s-]/g, '')      // Remove special chars
    .trim()                             // Trim whitespace
    .replace(/\s+/g, '-')              // "bug-out bag" → "bug-out-bag"
    .replace(/-+/g, '-')               // Collapse multiple hyphens
}
```

### Parser Strategy

The parser uses a "working line" approach:
1. Start with full item line
2. Extract each field type with regex
3. Remove matched text from working line
4. Continue with remaining text
5. Final remaining text is fallback for name if bold match failed

This makes the parser resilient to field order and missing fields.

### URL Recognition

```typescript
// Matches three patterns:
const urlMatch = workingLine.match(/<([^>]+)>|(\bhttps?:\/\/[^\s]+)|(\bwww\.[^\s]+)/)

// Pattern 1: <https://example.com>
// Pattern 2: https://example.com or http://example.com
// Pattern 3: www.example.com
```

### Nested Container Relationships

**Export side:**
- Generate slug ID from container name
- Add `[#id]` to container header
- Add `[#id]` to item line if item references nested container

**Import side:**
- Extract `[#id]` from container header → store as `container.id`
- Extract `[#id]` from item line → store as `item.nestedContainerId`
- Import dialog builds relationships by matching IDs

---

## 🧪 Testing

### Manual Test Cases

1. **Export single container**
   - ✅ Container with items exports correctly
   - ✅ Nested containers included with full content
   - ✅ All fields present in output (name, qty, brand, color, status, URL, weight)
   - ✅ Slug IDs generated correctly

2. **Export all containers**
   - ✅ Multiple containers export with proper separation
   - ✅ Each container has unique slug ID
   - ✅ Nested containers not duplicated

3. **Import markdown - minimal format**
   ```markdown
   ## Test Container [#test-container] (Backpack)
   - **Flashlight** - 150g
   ```
   - ✅ Parses container name
   - ✅ Parses container ID
   - ✅ Parses item name
   - ✅ Parses weight
   - ✅ Applies defaults (qty=1, status=owned)

4. **Import markdown - full format**
   ```markdown
   - **Knife** x2 (Victorinox, Black) (Missing) <https://example.com> - 200g
   ```
   - ✅ Parses all fields correctly
   - ✅ Quantity extracted
   - ✅ Brand and color extracted
   - ✅ Status extracted
   - ✅ URL extracted
   - ✅ Weight extracted

5. **Import markdown - flexible order**
   ```markdown
   - **Item** (Brand) x5 - 500g (Color)
   ```
   - ✅ Parses despite unusual order
   - ✅ All fields extracted correctly

6. **Import markdown - nested containers**
   ```markdown
   ## Main Bag [#main] (Backpack)
   - **EDC Pouch** [#edc] - 500g

   ## EDC Pouch [#edc] (Pouch)
   - **Multi-tool** - 250g
   ```
   - ✅ Parser extracts both container IDs
   - ✅ Parser extracts nested reference from item
   - ✅ Import dialog can build relationship

7. **Import markdown - URL variations**
   - ✅ `<https://example.com>` → parsed correctly
   - ✅ `https://example.com` → parsed correctly
   - ✅ `www.example.com` → parsed and prefixed with https://

8. **Guidelines button**
   - ✅ Button visible in export dialog
   - ✅ Clicking copies template to clipboard
   - ✅ Toast shows success message
   - ✅ Template contains all formatting rules

---

## 📦 Release

**Version:** 0.12.0
**Release Date:** 2025-01-19
**Branch:** develop → main

### CHANGELOG Entry

Added comprehensive section in CHANGELOG.md covering:
- AI Prompt Export Enhancements (export all, guidelines button)
- Enhanced Markdown Import/Export (unified format, flexible parsing)
- URL support in items
- Nested container support with ID references
- Container IDs as slugs
- Mobile/RWD improvements (separate but related)

---

## 🚀 Future Enhancements

### UUID Support for Update Workflow 🔄

**Problem:**
Current slug-based IDs work well for initial import but have limitations:
- IDs change when container names change
- No way to update existing containers during import
- Import can only create new containers, not update existing ones

**Solution:**
Add UUID support for stable references across import/export cycles.

**Implementation Plan:**

1. **Data Model Changes**
   - Add `uuid` field to `IGearContainer` and `IGearItem`
   - Generate UUIDs on container/item creation
   - Store UUIDs in localStorage

2. **Export Format**
   ```markdown
   ## Container Name [#slug-id] [uuid:abc-123-def] (Type)
   - **Item** [uuid:item-456] - 100g
   ```

3. **Import Parser**
   - Extract UUIDs from headers and items
   - Match against existing containers/items by UUID
   - Update existing if UUID found, create new if not

4. **Import Dialog Options**
   - Radio buttons: "Create new" vs "Update existing"
   - "Update existing" mode:
     - Matches by UUID
     - Updates all fields
     - Preserves relationships
     - Shows diff preview
   - "Create new" mode:
     - Ignores UUIDs
     - Creates everything fresh
     - Current behavior

5. **Use Cases**
   - Export → Edit in AI → Import → Updates existing containers
   - Rename containers without breaking relationships
   - Sync between devices (future cloud storage)
   - Version control for gear lists

**Priority:** Medium
**Complexity:** Medium
**Estimated Effort:** 2-3 days

### Export Configuration Options 🔄

**Features:**
- Show/hide URLs in export
- Show/hide prices in export
- Include "To Buy" summary section at the end
- Export format options (compact vs detailed)
- Custom metadata fields

**Priority:** Low
**Complexity:** Small
**Estimated Effort:** 1 day

---

## 📝 Notes

- The markdown format is designed to be both human-readable and AI-parseable
- Slug-based IDs provide human-readable references but need UUID supplement for update workflow
- Parser flexibility is intentional - AI models may generate slightly different formats
- Guidelines template is comprehensive to reduce back-and-forth with AI
- The format supports all current data fields (brand, color, status, expiration, URL, weight)
- Future fields can be added without breaking existing parsers (backward compatible)

---

## 🔗 Related Documentation

- [ROADMAP.md](../ROADMAP.md) - Overall project roadmap
- [FEATURE-008](./FEATURE-008-container-nesting.md) - Container nesting implementation
- [CHANGELOG.md](../../CHANGELOG.md) - v0.12.0 release notes
- Export utility: `src/modules/gear/utils/exportToPrompt.ts`
- Import service: `src/modules/gear/services/markdownImportService.ts`
- Export dialog: `src/modules/gear/components/ExportToPromptDialog.vue`
- Import dialog: `src/modules/gear/components/ImportMarkdownDialog.vue`
