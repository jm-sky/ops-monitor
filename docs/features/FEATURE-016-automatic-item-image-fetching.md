# FEATURE-016: Automatic Item Image Fetching

**Status:** 🔄 Planned
**Priority:** Medium
**Complexity:** Large
**Category:** 📷 Media & Resources
**Related Features:** FEATURE-017 (Item Image Gallery Upload - ✅ Completed), FEATURE-013 (Item Descriptions), FEATURE-012 (Add Existing Items)
**Requires:** Backend/DB, Admin Access (isAdmin)

---

## 📋 Overview

Add automatic image fetching functionality for items. Users can search for item images from configured web sources (stores, APIs) when creating or editing items. This feature is **admin-only** and includes configurable image search engines with support for both HTML scraping and API-based sources.

**Note:** Item image gallery already exists (FEATURE-017 ✅ Completed). This feature will integrate with the existing gallery system and add source attribution for images fetched from external sources.

---

## 🎯 Goals

1. **Image Search on Item Creation** - Option to search for images when creating new items
2. **On-Demand Image Search** - Action to search for images for existing items
3. **User Settings** - Default option to auto-search images for new items
4. **Admin-Only Access** - Feature available only for users with `isAdmin` flag
5. **Configurable Search Engines** - Support for multiple image sources (stores, APIs)
6. **Search Engine Configuration** - Server-side storage of search engine configs with relationship to items
7. **Image Selection** - UI to browse and select images from search results
8. **Source Attribution** - Display source information (e.g., "Źródło: militaria.pl") for images fetched from external sources
9. **Caching** - Cache search results to reduce API calls

---

## 📐 Design

### Current State

- ✅ **Item image gallery exists** (FEATURE-017 ✅ Completed)
  - Multi-image gallery support (up to 10 images per item)
  - Image upload, reorder, delete functionality
  - Primary image selection
  - `ItemImageGallery.vue` component
  - `ItemImageCard.vue` component
  - Backend API endpoints for image management
  - Database table `item_images` with fields: `id`, `item_id`, `url`, `fileName`, `isPrimary`, `order`, etc.
- ❌ No image search functionality
- ❌ No image source configuration/attribution
- ❌ No admin-only feature restrictions for image search

### Proposed Changes

#### 1. Database Schema

**New Tables:**

```python
# Image Search Engine Configuration
class ImageSearchEngine(Base):
    __tablename__ = "image_search_engines"
    
    id: UUID
    name: str  # e.g., "Militaria.pl", "Allegro", "Google Images API"
    type: str  # "html_scraper" | "api"
    base_url: str  # e.g., "https://militaria.pl"
    search_template: str  # e.g., "/search?q={query}"
    image_selectors: JSON  # CSS selectors for HTML scraping
    api_endpoint: Optional[str]  # API endpoint if type is "api"
    api_key: Optional[str]  # API key if required
    is_active: bool
    priority: int  # Order of search engines
    created_at: datetime
    updated_at: datetime

# Extend existing ItemImage table (FEATURE-017)
# Add new fields to item_images table:
class ItemImage(Base):
    __tablename__ = "item_images"
    
    # ... existing fields from FEATURE-017 ...
    id: UUID
    item_id: UUID
    url: str
    fileName: str
    isPrimary: bool
    order: int
    # ... other existing fields ...
    
    # NEW FIELDS for FEATURE-016:
    search_engine_id: Optional[UUID]  # FK to image_search_engines (nullable - only for fetched images)
    source_url: Optional[str]  # Original product page URL (nullable - only for fetched images)
    source_name: Optional[str]  # Display name of source (e.g., "militaria.pl") - denormalized for quick access
```

#### 2. User Settings

**Add to User Settings:**

```typescript
interface UserSettings {
  // ... existing settings ...
  autoSearchImagesForNewItems: boolean  // Default: false
}
```

#### 3. Frontend UI Components

**Item Form Page (`ItemFormPage.vue`):**

- Button: "Wyszukaj obrazki w web" (only visible for admins)
- Image search results modal/dialog:
  - Grid of image thumbnails
  - Source indicator badge (which search engine found it, e.g., "militaria.pl")
  - Click to select image
  - Preview larger image on hover/click
  - "Use this image" button (adds image to existing gallery)
- Integration with existing `ItemImageGallery.vue` component

**Item Actions (Existing Items):**

- Dropdown action: "Wyszukaj obrazki" (only visible for admins)
- Same image selection modal as above
- Selected images are added to the existing gallery

**Image Source Attribution Display:**

- In `ItemImageCard.vue` component:
  - Display source badge/indicator for images with `source_name` or `source_url`
  - Format: "Źródło: militaria.pl" or "Źródło: allegro.pl"
  - Small, subtle badge (not a full advertisement, just informational)
  - Optional: Clickable link to `source_url` if available
  - Position: Bottom-right corner of image card, or below image
  - Style: Small text, muted color, subtle background

**Settings Page:**

- Section: "Automatyczne wyszukiwanie obrazków" (only visible for admins)
- Checkbox: "Domyślnie wyszukaj obrazków dla nowych przedmiotów"
- Info text: "Funkcjonalność dostępna tylko dla administratorów"

**Admin Panel (Future):**

- Page: "Konfiguracja wyszukiwarek obrazków"
- List of configured search engines
- Add/Edit/Delete search engines
- Test search engine functionality

#### 4. Search Engine Configuration

**Backend Configuration (Python/SQLAlchemy):**

Konfiguracja search engine jest przechowywana w bazie danych (tabela `image_search_engines`) i zarządzana po stronie backendu. Model SQLAlchemy:

```python
class ImageSearchEngine(Base):
    __tablename__ = "image_search_engines"
    
    id: UUID
    name: str  # e.g., "Militaria.pl", "Allegro", "Google Images API"
    type: str  # "html_scraper" | "api"
    base_url: str  # e.g., "https://militaria.pl"
    search_template: Optional[str]  # e.g., "/search?q={query}" (for HTML scrapers)
    image_selectors: Optional[JSON]  # CSS selectors for HTML scraping (JSON field)
    api_endpoint: Optional[str]  # API endpoint if type is "api"
    api_key: Optional[str]  # API key if required (encrypted at rest)
    request_headers: Optional[JSON]  # Custom headers for API requests (JSON field)
    response_mapping: Optional[JSON]  # JSON path mappings for API responses (JSON field)
    is_active: bool
    priority: int  # Order of search engines
    created_at: datetime
    updated_at: datetime
```

**Frontend Type (TypeScript):**

TypeScript interface jest używany tylko do wyświetlania i edycji konfiguracji w admin panelu (future enhancement):

```typescript
// Type for frontend display/editing (matches backend model)
interface ImageSearchEngineConfig {
  id: string
  name: string
  type: 'html_scraper' | 'api'
  baseUrl: string
  
  // For HTML Scrapers
  searchTemplate?: string  // e.g., "/search?q={query}"
  imageSelectors?: {
    container: string  // CSS selector for image container
    image: string  // CSS selector for img tag or data attribute
    thumbnail?: string  // Optional thumbnail selector
    link?: string  // Link to product page
  }
  
  // For API
  apiEndpoint?: string
  apiKey?: string  // Only for display, not sent back to backend
  requestHeaders?: Record<string, string>
  responseMapping?: {
    images: string  // JSON path to images array
    imageUrl: string  // JSON path to image URL
    thumbnailUrl?: string  // JSON path to thumbnail URL
    sourceUrl?: string  // JSON path to source URL
  }
  
  isActive: boolean
  priority: number
}
```

**Note:** Konfiguracja jest zarządzana po stronie backendu (Python). Frontend TypeScript interface służy tylko do wyświetlania i edycji w admin panelu (future enhancement).

**Example Configurations (Python/SQLAlchemy):**

**1. HTML Scraper (Militaria.pl):**
```python
ImageSearchEngine(
    name="Militaria.pl",
    type="html_scraper",
    base_url="https://militaria.pl",
    search_template="/szukaj?fraza={query}",
    image_selectors={
        "container": ".product-item",
        "image": "img.product-image",
        "link": "a.product-link"
    },
    is_active=True,
    priority=1
)
```

**2. HTML Scraper (Allegro):**
```python
ImageSearchEngine(
    name="Allegro",
    type="html_scraper",
    base_url="https://allegro.pl",
    search_template="/listing?string={query}",
    image_selectors={
        "container": "article[data-role='offer']",
        "image": "img[data-src]",
        "thumbnail": "img[data-src]",
        "link": "a[data-role='offer-link']"
    },
    is_active=True,
    priority=2
)
```

**3. API (Google Images API):**
```python
ImageSearchEngine(
    name="Google Images API",
    type="api",
    base_url="https://www.googleapis.com",
    api_endpoint="/customsearch/v1",
    api_key=os.getenv("GOOGLE_API_KEY"),  # Encrypted in database
    response_mapping={
        "images": "items",
        "imageUrl": "link",
        "thumbnailUrl": "image.thumbnailLink",
        "sourceUrl": "image.contextLink"
    },
    is_active=True,
    priority=3
)
```

**Note:** Konfiguracje są tworzone przez:
- Database migrations (initial setup)
- Admin API endpoints (runtime configuration)
- Future: Admin UI panel (frontend will use TypeScript interface for editing)

#### 5. Search Query Building

**Query Construction:**

```typescript
interface SearchQuery {
  itemName: string
  brand?: string
  category?: string
  color?: string
}

function buildSearchQuery(item: IGearItem): string {
  const parts: string[] = []
  
  if (item.brand) {
    parts.push(item.brand)
  }
  
  parts.push(item.name)
  
  if (item.color) {
    parts.push(item.color)
  }
  
  return parts.join(' ')
}
```

---

## 🛠️ Implementation Plan

### Phase 1: Backend Infrastructure

**Files:**
- `backend/app/modules/gear/models/image_search.py` - Database models
- `backend/app/modules/gear/schemas/image_search.py` - Pydantic schemas
- `backend/app/modules/gear/repositories/image_search_repository.py` - Repository layer
- `backend/app/modules/gear/services/image_search_service.py` - Business logic
- `backend/app/modules/gear/routers/image_search.py` - API endpoints
- `backend/alembic/versions/XXXX_add_image_search_tables.py` - Database migration

**Changes:**
1. Create database model for `ImageSearchEngine` (new table)
2. **Extend existing `ItemImage` model** (FEATURE-017):
   - Add `search_engine_id` field (nullable UUID, FK to `image_search_engines`)
   - Add `source_url` field (nullable string)
   - Add `source_name` field (nullable string, denormalized for quick display)
3. Create database migration to add new fields to `item_images` table
4. Create Pydantic schemas for API requests/responses
5. Implement repository methods for CRUD operations
6. Create image search service with:
   - HTML scraping logic (using BeautifulSoup or similar)
   - API client logic
   - Query building
   - Image URL extraction and download (store in S3/local storage like existing uploads)
   - Caching mechanism
7. **Extend existing image upload endpoint** (`POST /api/gear/items/{item_id}/images`):
   - Add optional `source_url` and `search_engine_id` parameters
   - When image is fetched from web, download and store it (same as uploaded images)
   - Store source attribution in database
8. Create new API endpoints:
   - `GET /api/image-search/engines` - List all search engines (admin only)
   - `POST /api/image-search/engines` - Create search engine (admin only)
   - `PUT /api/image-search/engines/{id}` - Update search engine (admin only)
   - `DELETE /api/image-search/engines/{id}` - Delete search engine (admin only)
   - `POST /api/image-search/search` - Search for images (admin only)

### Phase 2: Frontend API Integration

**Files:**
- `src/modules/gear/services/imageSearchApiService.ts` - API service
- `src/modules/gear/composables/useImageSearch.ts` - Composable

**Changes:**
1. Create API service for image search endpoints (`imageSearchApiService.ts`)
2. **Extend existing `itemImageApiService.ts`**:
   - Add optional `sourceUrl` and `searchEngineId` parameters to `uploadImage()` method
   - These will be passed when adding images from search results
3. Create composable `useImageSearch.ts` with:
   - `searchImages(query: string, engines?: string[])` - Search for images
   - `addImageFromSearch(itemId: string, imageUrl: string, sourceUrl: string, searchEngineId: string)` - Download and add image to gallery
   - Uses existing `itemImageApiService.uploadImage()` with source attribution
4. Add admin check utility (`useIsAdmin()` composable)

### Phase 3: Frontend UI - Item Form

**Files:**
- `src/modules/gear/pages/ItemFormPage.vue`
- `src/modules/gear/components/ImageSearchDialog.vue` - New component
- `src/modules/gear/components/ImageSearchResults.vue` - New component

**Changes:**
1. Add "Wyszukaj obrazki w web" button to item form (admin only, next to existing image upload)
2. Create `ImageSearchDialog.vue` component:
   - Search input (pre-filled with item name + brand)
   - Loading state during search
   - `ImageSearchResults` component for displaying results
   - Image selection handler
3. Create `ImageSearchResults.vue` component:
   - Grid layout for image thumbnails (similar to `ItemImageGallery`)
   - Image preview on hover/click
   - Source indicator badge (e.g., "militaria.pl")
   - "Dodaj do galerii" button for each image
4. Handle image selection:
   - Download image from URL (backend handles this)
   - Call existing `itemImageApiService.uploadImage()` with `sourceUrl` and `searchEngineId`
   - Image is added to existing gallery (same as manual upload)
   - Refresh `ItemImageGallery` to show new image
   - Show success toast

### Phase 4: Frontend UI - Existing Items

**Files:**
- `src/modules/gear/components/ItemsTableRowActions.vue`
- `src/modules/gear/pages/ContainerDetailPage.vue`

**Changes:**
1. Add "Wyszukaj obrazki" action to item row actions dropdown (admin only)
2. Open same `ImageSearchDialog` with pre-filled query (item name + brand)
3. Handle image selection:
   - Download and add image to gallery (same as in Phase 3)
   - Image appears in existing `ItemImageGallery` component

### Phase 5: User Settings

**Files:**
- `src/modules/settings/pages/SettingsPage.vue`
- `src/modules/settings/store/useSettingsStore.ts`
- `src/modules/settings/types/settings.types.ts`

**Changes:**
1. Add `autoSearchImagesForNewItems` to settings type
2. Add settings section "Automatyczne wyszukiwanie obrazków" (admin only)
3. Add checkbox for default auto-search
4. Update item form to check this setting and auto-trigger search if enabled

### Phase 6: Image Display

**Files:**
- `src/modules/gear/components/ItemImage.vue` - New component
- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/components/ContainerCard.vue`

**Changes:**
1. **Update existing `ItemImageCard.vue` component**:
   - Add source attribution display for images with `source_name` or `source_url`
   - Display small badge: "Źródło: militaria.pl" (or source name)
   - Position: Bottom-right corner or below image
   - Style: Small text, muted color, subtle background (informational, not advertisement)
   - Optional: Make source clickable link to `source_url` if available
   - Only show if `image.sourceName` or `image.sourceUrl` exists
2. **Update `IItemImage` TypeScript type**:
   - Add optional `sourceUrl?: string`
   - Add optional `sourceName?: string`
   - Add optional `searchEngineId?: TUUID`
3. Image display already exists in:
   - `ItemImageGallery.vue` (item detail page)
   - `ContainerItemImagesGallery.vue` (container view)
   - Items table (if implemented)
4. Source attribution will automatically appear in all these places

### Phase 7: Admin Panel (Future)

**Files:**
- `src/modules/admin/pages/ImageSearchEnginesPage.vue` - New page
- `src/modules/admin/components/ImageSearchEngineForm.vue` - New component

**Changes:**
1. Create admin page for managing search engines
2. Create form for adding/editing search engines
3. List existing search engines with edit/delete actions
4. Test search engine functionality

---

## 📊 Data Flow

### Image Search Flow

```
User clicks "Wyszukaj obrazki" (admin only)
  ↓
Frontend builds search query (item name + brand + color)
  ↓
API call: POST /api/image-search/search
  {
    query: "Petzl Headlamp Black",
    engines: ["engine-1", "engine-2"] // Optional, or use all active
  }
  ↓
Backend service:
  - Iterates through active search engines (by priority)
  - For HTML scrapers: fetches HTML, parses with selectors
  - For API: makes API call with query
  - Extracts image URLs, thumbnails, source URLs
  - Caches results
  ↓
Returns array of image results:
  [
    {
      imageUrl: "https://...",
      thumbnailUrl: "https://...",
      sourceUrl: "https://...",
      searchEngine: "Militaria.pl"
    },
    ...
  ]
  ↓
Frontend displays results in ImageSearchDialog
  ↓
User selects image
  ↓
API call: POST /api/image-search/download-and-add
  {
    itemId: "...",
    imageUrl: "https://...",
    sourceUrl: "https://militaria.pl/product/123",
    searchEngineId: "..."
  }
  ↓
Backend:
  - Downloads image from imageUrl
  - Stores in S3/local storage (same as upload)
  - Creates ItemImage record with:
    - url: (stored image URL)
    - sourceUrl: (original product page)
    - sourceName: (denormalized from search engine name)
    - searchEngineId: (FK to search engine)
  ↓
API call: POST /api/gear/items/{itemId}/images
  (existing endpoint, extended with source fields)
  ↓
Backend creates ItemImage record with source attribution
  ↓
Frontend refreshes ItemImageGallery to show new image
  ↓
ItemImageCard displays source badge: "Źródło: militaria.pl"
```

### Auto-Search Flow (Settings Enabled)

```
User creates new item (admin only)
  ↓
Check user settings: autoSearchImagesForNewItems === true
  ↓
Auto-trigger image search after item name/brand entered
  ↓
Show ImageSearchDialog with results
  ↓
User can select image or dismiss
```

---

## 🔍 Technical Details

### HTML Scraping Implementation

**Backend Service:**

```python
async def scrape_html_images(
    engine: ImageSearchEngine,
    query: str
) -> List[ImageSearchResult]:
    """Scrape images from HTML source."""
    import httpx
    from bs4 import BeautifulSoup
    
    # Build search URL
    search_url = f"{engine.base_url}{engine.search_template.format(query=query)}"
    
    # Fetch HTML
    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, timeout=10.0)
        response.raise_for_status()
        html = response.text
    
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find image containers
    containers = soup.select(engine.image_selectors['container'])
    
    results = []
    for container in containers[:20]:  # Limit to 20 results
        img_tag = container.select_one(engine.image_selectors['image'])
        if not img_tag:
            continue
        
        image_url = img_tag.get('src') or img_tag.get('data-src')
        if not image_url:
            continue
        
        # Make absolute URL
        if image_url.startswith('/'):
            image_url = f"{engine.base_url}{image_url}"
        
        # Get source URL
        link_tag = container.select_one(engine.image_selectors.get('link', 'a'))
        source_url = link_tag.get('href') if link_tag else None
        
        results.append(ImageSearchResult(
            image_url=image_url,
            thumbnail_url=image_url,  # Use same URL if no thumbnail selector
            source_url=source_url or search_url,
            search_engine_id=engine.id
        ))
    
    return results
```

### API-Based Search Implementation

**Backend Service:**

```python
async def search_api_images(
    engine: ImageSearchEngine,
    query: str
) -> List[ImageSearchResult]:
    """Search images via API."""
    import httpx
    
    # Build API request
    url = f"{engine.base_url}{engine.api_endpoint}"
    params = {
        'q': query,
        'key': engine.api_key,
        # ... other API-specific params
    }
    
    headers = engine.request_headers or {}
    
    # Make API call
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
    
    # Extract images using response mapping
    images = get_nested_value(data, engine.response_mapping['images'])
    
    results = []
    for img_data in images[:20]:  # Limit to 20 results
        image_url = get_nested_value(img_data, engine.response_mapping['imageUrl'])
        thumbnail_url = get_nested_value(
            img_data, 
            engine.response_mapping.get('thumbnailUrl', 'imageUrl')
        )
        source_url = get_nested_value(
            img_data,
            engine.response_mapping.get('sourceUrl', 'link')
        )
        
        results.append(ImageSearchResult(
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            source_url=source_url,
            search_engine_id=engine.id
        ))
    
    return results
```

### Caching Strategy

**Cache Key:**
```
image_search:{engine_id}:{query_hash}
```

**Cache Duration:**
- 24 hours for successful searches
- 1 hour for failed searches (to avoid repeated failures)

**Cache Storage:**
- Redis (if available) or in-memory cache
- Store: `List[ImageSearchResult]`

### Admin Check

**Backend Middleware/Decorator:**

```python
from functools import wraps
from fastapi import HTTPException, status

def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This feature is available only for administrators"
            )
        return await func(*args, **kwargs)
    return wrapper
```

**Frontend Composable:**

```typescript
export function useIsAdmin() {
  const userStore = useUserStore()
  
  const isAdmin = computed(() => {
    return userStore.user?.isAdmin === true
  })
  
  return { isAdmin }
}
```

### Source Attribution Display

**Frontend Component (`ItemImageCard.vue`):**

```vue
<template>
  <div class="relative">
    <!-- Image -->
    <img :src="image.url" :alt="image.fileName" />
    
    <!-- Source Attribution Badge -->
    <div
      v-if="image.sourceName || image.sourceUrl"
      class="absolute bottom-2 right-2 rounded bg-black/60 px-2 py-1 text-xs text-white backdrop-blur-sm"
    >
      <a
        v-if="image.sourceUrl"
        :href="image.sourceUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="hover:underline"
      >
        Źródło: {{ image.sourceName || extractDomain(image.sourceUrl) }}
      </a>
      <span v-else>
        Źródło: {{ image.sourceName }}
      </span>
    </div>
  </div>
</template>
```

**Design Guidelines:**
- **Position**: Bottom-right corner of image card (absolute positioning)
- **Style**: Small text (text-xs), semi-transparent dark background (bg-black/60), white text
- **Purpose**: Informational only, not advertisement
- **Clickable**: If `sourceUrl` exists, make it a clickable link (opens in new tab)
- **Visibility**: Only show if `sourceName` or `sourceUrl` exists
- **Text Format**: "Źródło: [source_name]" (e.g., "Źródło: militaria.pl")
- **Fallback**: If `sourceName` is missing, extract domain from `sourceUrl`

**TypeScript Type Update:**

```typescript
export interface IItemImage {
  // ... existing fields from FEATURE-017 ...
  id: TUUID
  itemId: TUUID
  url: string
  fileName: string
  isPrimary: boolean
  order: number
  // ... other existing fields ...
  
  // NEW FIELDS for FEATURE-016:
  sourceUrl?: string  // Optional: Original product page URL
  sourceName?: string  // Optional: Display name of source (e.g., "militaria.pl")
  searchEngineId?: TUUID  // Optional: FK to image_search_engines
}
```

---

## 🧪 Testing

### Manual Test Cases

1. **Admin Access Check**
   - ✅ Non-admin users don't see "Wyszukaj obrazki" button
   - ✅ Non-admin users get 403 error if they try to call API directly
   - ✅ Admin users see button and can use feature

2. **Image Search on Item Creation**
   - ✅ Admin creates new item
   - ✅ Clicks "Wyszukaj obrazki" button
   - ✅ Dialog opens with search results
   - ✅ Can select image
   - ✅ Image is attached to item

3. **Image Search for Existing Item**
   - ✅ Admin opens existing item
   - ✅ Clicks "Wyszukaj obrazki" from actions menu
   - ✅ Dialog opens with search results
   - ✅ Can select image
   - ✅ Image is attached to item

4. **Auto-Search Setting**
   - ✅ Admin enables "Domyślnie wyszukaj obrazków dla nowych przedmiotów"
   - ✅ Creates new item
   - ✅ Search dialog auto-opens after entering name/brand
   - ✅ Non-admin setting has no effect

5. **Multiple Search Engines**
   - ✅ Multiple engines configured
   - ✅ Search queries all active engines
   - ✅ Results show source engine
   - ✅ Results are combined and deduplicated

6. **HTML Scraper**
   - ✅ Configure HTML scraper for test site
   - ✅ Search returns images from HTML
   - ✅ Image URLs are absolute
   - ✅ Source URLs are correct

7. **API Scraper**
   - ✅ Configure API scraper (e.g., Google Images)
   - ✅ Search returns images from API
   - ✅ Response mapping works correctly

8. **Image Display**
   - ✅ Selected images display in items table
   - ✅ Images display in container cards
   - ✅ Fallback to category icon if image fails to load

9. **Caching**
   - ✅ Same query returns cached results
   - ✅ Cache expires after 24 hours
   - ✅ Failed searches cached for 1 hour

### Unit Tests

1. **Backend:**
   - `test_image_search_service.py` - Test HTML scraping, API calls, query building
   - `test_image_search_repository.py` - Test CRUD operations
   - `test_image_search_router.py` - Test API endpoints, admin checks

2. **Frontend:**
   - `imageSearchApiService.spec.ts` - Test API service methods
   - `useImageSearch.spec.ts` - Test composable logic
   - `ImageSearchDialog.spec.ts` - Test component rendering and interactions

---

## 📦 Release

**Version:** TBD
**Release Date:** TBD
**Branch:** develop → main

### CHANGELOG Entry

```
### Added
- Automatic image search for items (admin-only feature)
- Image search on item creation and for existing items
- User setting: "Domyślnie wyszukaj obrazków dla nowych przedmiotów" (admin only)
- Configurable image search engines (HTML scrapers and API-based)
- Image selection UI with preview
- Image display in items table and container cards
- Caching for search results (24h for success, 1h for failures)

### Changed
- Extended `ItemImage` model with source attribution fields (`source_url`, `source_name`, `search_engine_id`)
- Extended `itemImageApiService.uploadImage()` to accept optional source attribution parameters
- Updated `ItemImageCard.vue` to display source attribution badge
- Updated `IItemImage` TypeScript type with source fields
- Admin-only access control for image search features

### Database
- New table: `image_search_engines` - Configuration for search engines
- Extended `item_images` table (FEATURE-017):
  - Added `search_engine_id` field (nullable UUID, FK to `image_search_engines`)
  - Added `source_url` field (nullable string)
  - Added `source_name` field (nullable string, denormalized for quick display)
```

---

## 🚀 Future Enhancements

### Image Upload
- Allow users to upload their own images (requires S3 storage)
- Combine uploaded images with searched images

### Image Optimization
- Automatic image resizing and compression
- WebP conversion
- CDN integration

### Advanced Search
- Search by image (reverse image search)
- AI-powered image matching
- Image quality scoring

### Search Engine Management UI
- Admin panel for managing search engines
- Test search engine functionality
- Analytics for search engine performance

### Multi-Image Support
- Support for multiple images per item (gallery)
- Image reordering
- Image deletion

---

## 📝 Notes

- **Admin-Only Feature**: This feature is restricted to administrators only. Non-admin users will not see any UI elements related to image search.
- **Search Engine Configuration**: Search engines are configured and stored in the database (Python/SQLAlchemy model). Initially, they will be configured via database migrations or admin API endpoints. Future enhancement will add admin UI panel where frontend (TypeScript) will display and edit configurations, but the actual storage and logic remains on the backend (Python).
- **HTML Scraping Limitations**: HTML scraping may break if websites change their structure. API-based sources are more reliable but require API keys.
- **Rate Limiting**: Consider implementing rate limiting for search requests to avoid overwhelming external APIs.
- **Legal Considerations**: Ensure compliance with website terms of service when scraping HTML. Prefer API-based sources when available.
- **Image Storage**: Images fetched from web sources are downloaded and stored in S3/local storage (same as uploaded images), not just stored as external URLs. This ensures images remain available even if the source website changes or removes them.
- **Source Attribution**: Source information (e.g., "Źródło: militaria.pl") is displayed as informational badge, not as advertisement. It helps users know where the image came from.
- **Caching**: Cache is important to reduce API calls and improve performance. Consider Redis for production.
- **Error Handling**: Gracefully handle failures (network errors, parsing errors, API errors) and show user-friendly messages.

---

## 🔗 Related Documentation

- [ROADMAP_ONLINE.md](../ROADMAP_ONLINE.md) - Online/backend features roadmap
- [FEATURE-017](./FEATURE-017-item-image-gallery-upload.md) - Item Image Gallery Upload (✅ Completed - existing gallery system)
- [FEATURE-012](./FEATURE-012-add-existing-items.md) - Add existing items (similar UI patterns)
- [FEATURE-013](./FEATURE-013-item-descriptions.md) - Item descriptions (form enhancements)
- Backend auth module: `backend/app/modules/auth/`
- Frontend auth module: `src/modules/auth/`
- Existing image gallery components:
  - `src/modules/gear/components/ItemImageGallery.vue`
  - `src/modules/gear/components/ItemImageCard.vue`
  - `src/modules/gear/services/itemImageApiService.ts`
