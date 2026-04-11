# Item Image Gallery Integration Guide

## Overview

The Item Image Gallery feature allows admin users to upload, manage, and reorder images for gear items. It includes:

- 🎨 **Modern drag-and-drop upload** using VueUse's `useDropZone`
- 🖼️ **Multi-image gallery** (max 10 images per item)
- 🌟 **Primary image selection**
- 📐 **Drag-and-drop reordering**
- 🔒 **Admin-only access**
- ✨ **Auto-resize and compression**
- 💾 **Local + S3 storage support**

**Related:** [FEATURE-017: Item Image Gallery Upload](./FEATURE-017-item-image-gallery-upload.md)

---

## Backend Setup

### 1. Dependencies Installed

The following Python packages are required and already installed:

```txt
Pillow>=11.0.0              # Image processing
python-magic>=0.4.27        # MIME type validation
aiofiles>=24.1.0            # Async file operations
aioboto3>=13.3.0            # S3 support (optional)
```

### 2. Configuration

Update your `.env` file with storage settings:

```bash
# Storage type: local or s3
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./uploads

# S3 Settings (if using S3)
# STORAGE_TYPE=s3
# STORAGE_S3_BUCKET=your-bucket-name
# STORAGE_S3_ACCESS_KEY=your-access-key
# STORAGE_S3_SECRET_KEY=your-secret-key
# STORAGE_S3_REGION=us-east-1

# Upload limits
STORAGE_MAX_FILE_SIZE=10485760  # 10 MB
STORAGE_MAX_FILES_PER_ITEM=10

# Image processing
STORAGE_ENABLE_PROCESSING=True
STORAGE_MAX_WIDTH=1920
STORAGE_MAX_HEIGHT=1920
STORAGE_JPEG_QUALITY=85
```

### 3. Database Migration

The migration has been run successfully:

```bash
docker-compose -f docker-compose.dev.yml exec app python migrations/017_add_item_images_table.py upgrade
```

### 4. Restart Backend

Restart the backend to load new dependencies:

```bash
docker-compose -f docker-compose.dev.yml restart app
```

---

## Frontend Integration

### Basic Usage

Add the `ItemImageGallery` component to your item form or detail page:

```vue
<script setup lang="ts">
import { computed } from 'vue'
import ItemImageGallery from '@/modules/gear/components/ItemImageGallery.vue'

// Get current user's admin status
// This depends on your auth implementation
const isAdmin = computed(() => {
  // Option 1: From Pinia store
  // const authStore = useAuthStore()
  // return authStore.user?.isAdmin ?? false

  // Option 2: From composable
  // const { currentUser } = useAuth()
  // return currentUser.value?.isAdmin ?? false

  // Option 3: Hardcoded for testing
  return true
})

// Item ID from route or props
const itemId = 'your-item-id'
</script>

<template>
  <div class="space-y-6">
    <!-- Your existing item form -->
    <div>
      <!-- Item name, category, etc. -->
    </div>

    <!-- Image Gallery -->
    <ItemImageGallery
      v-if="itemId"
      :item-id="itemId"
      :is-admin="isAdmin"
    />
  </div>
</template>
```

### Complete Example (ItemFormPage.vue)

Here's a complete example showing integration into an item edit page:

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

import ItemImageGallery from '@/modules/gear/components/ItemImageGallery.vue'
import { gearItemService } from '@/modules/gear/services/gearItemService'
import type { IGearItem } from '@/modules/gear/types/gear.types'

const route = useRoute()
const router = useRouter()

const itemId = computed(() => route.params.id as string)
const item = ref<IGearItem | null>(null)
const isLoading = ref(false)

// Get admin status - adjust based on your auth implementation
const isAdmin = computed(() => {
  // Replace with your actual auth check
  // Example: return authStore.user?.isAdmin ?? false
  return true
})

async function loadItem() {
  if (!itemId.value) return

  try {
    isLoading.value = true
    item.value = await gearItemService.getItem(itemId.value)
  } catch (error) {
    toast.error('Failed to load item')
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadItem()
})
</script>

<template>
  <div class="container max-w-4xl py-8">
    <div class="space-y-8">
      <!-- Back button -->
      <button
        class="text-sm text-muted-foreground hover:text-foreground"
        @click="router.back()"
      >
        ← Back
      </button>

      <!-- Page title -->
      <div>
        <h1 class="text-3xl font-bold">
          {{ item?.name || 'Loading...' }}
        </h1>
        <p class="text-muted-foreground">
          Edit item details and manage images
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="isLoading" class="py-12 text-center">
        <p class="text-muted-foreground">
          Loading item...
        </p>
      </div>

      <!-- Item form -->
      <div v-else-if="item" class="space-y-8">
        <!-- Your existing item form fields -->
        <div class="rounded-lg border p-6">
          <h2 class="mb-4 text-xl font-semibold">
            Item Details
          </h2>
          <!-- Add your item form fields here -->
        </div>

        <!-- Image Gallery -->
        <div class="rounded-lg border p-6">
          <ItemImageGallery
            :item-id="itemId"
            :is-admin="isAdmin"
          />
        </div>
      </div>

      <!-- Error state -->
      <div v-else class="py-12 text-center">
        <p class="text-destructive">
          Item not found
        </p>
      </div>
    </div>
  </div>
</template>
```

---

## Component Features

### FileDropZone Component

The gallery uses a reusable `FileDropZone` component that can be used anywhere:

```vue
<script setup lang="ts">
import FileDropZone from '@/components/ui/FileDropZone.vue'

function handleFilesSelected(files: File[]) {
  console.log('Files selected:', files)
  // Handle file upload
}

function handleError(message: string) {
  console.error('Error:', message)
}
</script>

<template>
  <FileDropZone
    accept="image/jpeg,image/png,image/webp,image/gif"
    :max-size="10 * 1024 * 1024"
    :max-files="5"
    @files-selected="handleFilesSelected"
    @error="handleError"
  >
    <!-- Optional custom slot -->
    <div>
      <p>Custom drop zone content</p>
    </div>
  </FileDropZone>
</template>
```

#### Props:

- `accept` (string): Allowed file types (default: `'image/*'`)
- `maxSize` (number): Max file size in bytes (default: 10 MB)
- `maxFiles` (number): Max number of files (default: 1)
- `disabled` (boolean): Disable the drop zone (default: false)
- `class` (string): Additional CSS classes

#### Events:

- `@filesSelected` (File[]): Emitted when valid files are selected
- `@error` (string): Emitted when validation fails

---

## API Endpoints

### Upload Image

```http
POST /api/gear/items/{item_id}/images
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (binary)
is_primary: false
```

**Response:**
```json
{
  "id": "uuid",
  "url": "/uploads/items/{item_id}/filename.jpg",
  "fileName": "filename.jpg",
  "fileSize": 123456,
  "mimeType": "image/jpeg",
  "width": 1920,
  "height": 1080,
  "isPrimary": false,
  "order": 0
}
```

### Get Images

```http
GET /api/gear/items/{item_id}/images
```

### Delete Image

```http
DELETE /api/gear/items/images/{image_id}
Authorization: Bearer {token}
```

### Reorder Images

```http
PUT /api/gear/items/{item_id}/images/reorder
Authorization: Bearer {token}
Content-Type: application/json

{
  "imageOrders": [
    {"id": "uuid-1", "order": 0},
    {"id": "uuid-2", "order": 1}
  ]
}
```

### Set Primary Image

```http
PUT /api/gear/items/{item_id}/images/{image_id}/primary
Authorization: Bearer {token}
```

---

## Security

- ✅ **Admin-only uploads**: Only users with `isAdmin=true` can upload images
- ✅ **MIME validation**: Uses `python-magic` for magic number validation
- ✅ **File size limits**: Default 10 MB (configurable)
- ✅ **Allowed types**: JPEG, PNG, WebP, GIF
- ✅ **Transaction safety**: Automatic rollback on failure
- ✅ **Input sanitization**: Filename sanitization and path validation

---

## Troubleshooting

### Images not appearing

1. Check if backend is serving static files:
   ```bash
   curl http://localhost:8000/uploads/items/test/image.jpg
   ```

2. Verify Docker volume is mounted:
   ```bash
   docker volume inspect gear_stack_uploads
   ```

3. Check file permissions in container:
   ```bash
   docker-compose -f docker-compose.dev.yml exec app ls -la /app/uploads
   ```

### Upload fails with 403

- Ensure user has `isAdmin=true` in database:
  ```sql
  UPDATE users SET is_admin = true WHERE email = 'your-email@example.com';
  ```

### Images disappear after container restart

- Ensure Docker volume is properly configured in `docker-compose.dev.yml`:
  ```yaml
  volumes:
    - gear_stack_uploads:/app/uploads
  ```

---

## Performance Tips

1. **Image processing**: The backend automatically resizes images to 1920x1920 with 85% JPEG quality
2. **Lazy loading**: Consider implementing lazy loading for image grids
3. **CDN**: For production, use S3 with CloudFront or similar CDN
4. **Caching**: Browser caching is automatic via static file serving

---

## Next Steps

- [ ] Implement user storage quotas
- [ ] Add image cropping UI
- [ ] Implement image search/filter
- [ ] Add bulk upload support
- [ ] Integrate with FEATURE-016 (automatic image fetching)

---

**Last Updated:** 2025-01-25
**Status:** 🚧 In Progress (backend complete, frontend integration manual)

