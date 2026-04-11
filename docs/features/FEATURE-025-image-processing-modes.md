# FEATURE-025: Image Processing Modes

**Status:** ✅ Completed  
**Priority:** Medium  
**Complexity:** Medium  
**Version:** v2.16.0

## Overview

User-configurable image processing modes that automatically resize and compress uploaded images based on user preferences. This feature allows users to balance between image quality and storage space usage.

## Requirements

### Functional Requirements

1. **Three Processing Modes:**
   - **High Quality** - Maximum quality, larger file size
   - **Balanced** - Good balance between quality and file size (default)
   - **Storage Saver** - Maximum compression, smaller file size

2. **Access Control:**
   - High Quality mode is **admin-only** (restricted access)
   - Balanced and Storage Saver modes are available to all users
   - Future: Access control based on subscription plan

3. **User Settings:**
   - Setting stored in user profile (`user_settings.image_processing_mode`)
   - Accessible from Gear Settings page (`/gear/settings`)
   - Applied automatically to all new image uploads

4. **Backend Processing:**
   - Automatic resize and compression on upload
   - Processing based on user's selected mode
   - Applies to both item images and container images (when implemented)

## Implementation Details

### Backend

#### Database Schema

**Migration:** `023_add_image_processing_mode_to_user_settings.py`

```sql
ALTER TABLE user_settings
ADD COLUMN image_processing_mode VARCHAR(20) DEFAULT 'balanced' NOT NULL;
```

#### Configuration

**File:** `backend/app/core/config.py`

```python
class StorageSettings(BaseSettings):
    # Image processing mode configurations
    IMAGE_PROCESSING_MODES = {
        "high_quality": {
            "max_width": 2560,
            "max_height": 2560,
            "jpeg_quality": 95,
        },
        "balanced": {
            "max_width": 1200,
            "max_height": 1200,
            "jpeg_quality": 90,
        },
        "storage_saver": {
            "max_width": 800,
            "max_height": 800,
            "jpeg_quality": 80,
        },
    }
```

#### Environment Variables

**File:** `backend/.env.example`

```bash
# Storage Upload Limits
# Maximum file size for regular users (in bytes, default: 20 MB)
STORAGE_MAX_FILE_SIZE=20971520
# Maximum file size for administrators (in bytes, default: 50 MB)
STORAGE_MAX_FILE_SIZE_ADMIN=52428800
```

#### API Endpoints

**Settings Router:** `backend/app/modules/settings/router.py`

- `GET /api/me/settings` - Returns user settings including `imageProcessingMode`
- `PATCH /api/me/settings` - Updates user settings
  - Validates admin access for `high_quality` mode
  - Returns 403 Forbidden if non-admin tries to set `high_quality`

**Image Upload Service:** `backend/app/modules/gear/image_upload_service.py`

- `_get_user_image_processor(user_id)` - Creates `ImageProcessor` with user-specific settings
- `_process_and_store_image()` - Uses user-specific processor for image processing

### Frontend

#### Configuration

**File:** `src/shared/config/config.ts`

```typescript
export const config = {
  storage: {
    // Maximum file size for regular users (20 MB)
    maxFileSize: 20 * 1024 * 1024,
    // Maximum file size for administrators (50 MB)
    maxFileSizeAdmin: 50 * 1024 * 1024,
  },
}
```

#### Components

**Gear Preferences Card:** `src/modules/gear/components/GearPreferencesCard.vue`

- Radio group for selecting image processing mode
- High Quality option only visible to admins (`v-if="isAdmin"`)
- Automatically resets to Balanced if user loses admin privileges

**File Drop Zone:** `src/components/ui/FileDropZone.vue`

- Automatically uses appropriate file size limit based on user permissions
- Displays correct limit in UI (20 MB for regular users, 50 MB for admins)

**Item Image Gallery:** `src/modules/gear/components/ItemImageGallery.vue`

- Uses `FileDropZone` with automatic size limits
- No hardcoded limits - all from config

**Items Table Image Cell:** `src/modules/gear/components/items-table/ItemsTableImageCell.vue`

- Validates file size before upload using config values
- Shows appropriate error message with correct limit

#### Type Definitions

**File:** `src/modules/settings/types/settings.type.ts`

```typescript
export type ImageProcessingMode = 'high_quality' | 'balanced' | 'storage_saver'

export interface Settings {
  // ... other fields
  imageProcessingMode: ImageProcessingMode
}
```

## Processing Modes

### 1. High Quality (Admin Only)

**Restrictions:**
- Only available to users with `isAdmin = true`
- Backend validates admin status before allowing this mode
- Frontend hides option for non-admin users

**Parameters:**
- Maximum size: **2560x2560px**
- JPEG quality: **95%**
- Use case: Best quality for detailed images, professional use
- File size: Larger (typically 2-5 MB per image)

**Access Control:**
- Frontend: Option hidden for non-admins
- Backend: Returns 403 Forbidden if non-admin tries to set this mode
- Automatic fallback: If admin loses privileges, setting resets to Balanced

### 2. Balanced (Default)

**Parameters:**
- Maximum size: **1200x1200px**
- JPEG quality: **90%**
- Use case: Optimal for most users, good balance for thumbnails and gallery views
- File size: Medium (typically 500 KB - 1.5 MB per image)

**Availability:**
- Available to all users
- Default mode for new users

### 3. Storage Saver

**Parameters:**
- Maximum size: **800x800px**
- JPEG quality: **80%**
- Use case: Maximum storage efficiency, suitable for thumbnails
- File size: Small (typically 200-500 KB per image)

**Availability:**
- Available to all users

## File Size Limits

### Regular Users
- Maximum upload size: **20 MB** (configurable via `STORAGE_MAX_FILE_SIZE`)
- Images are automatically processed and compressed after upload
- Final file size depends on selected processing mode

### Administrators
- Maximum upload size: **50 MB** (configurable via `STORAGE_MAX_FILE_SIZE_ADMIN`)
- Can upload larger original files
- Still processed according to selected mode

**Note:** Even though admins can upload larger files, the final processed image size is determined by the selected processing mode, not the original file size.

## User Interface

### Settings Page

**Location:** `/gear/settings`

**Component:** `GearPreferencesCard.vue`

**UI Elements:**
- Radio group with three options
- Each option shows:
  - Mode name
  - Description with parameters
  - File size impact information
- High Quality option only visible to admins
- Save button to persist selection

**Translations:**
- `settings.preferences.imageProcessingMode.label`
- `settings.preferences.imageProcessingMode.subtitle`
- `settings.preferences.imageProcessingMode.options.highQuality`
- `settings.preferences.imageProcessingMode.options.balanced`
- `settings.preferences.imageProcessingMode.options.storageSaver`

## Future Enhancements

### Subscription-Based Access Control

**Planned:** Access to High Quality mode based on subscription plan

**Implementation Plan:**
1. Add `subscription_plan` field to user model
2. Update access control logic:
   - Free plan: Balanced and Storage Saver only
   - Premium plan: All modes including High Quality
   - Admin: Always has access to all modes
3. Update UI to show subscription-based restrictions
4. Add upgrade prompts for free users trying to access High Quality

### Thumbnail Generation

**Planned:** Automatic thumbnail generation for faster loading

**Details:**
- Generate multiple thumbnail sizes (150x150px, 300x300px, 600x600px)
- Lazy loading with full image on demand
- Reduce bandwidth and improve page load times
- See ROADMAP for more details

### Separate Settings for Items vs Containers

**Planned:** Different processing modes for item images and container images

**Use Case:**
- Container images might need higher quality (displayed larger)
- Item images might prioritize storage efficiency (displayed as thumbnails)

## Testing

### Test Cases

1. **Mode Selection:**
   - Regular user can select Balanced or Storage Saver
   - Regular user cannot select High Quality (option hidden)
   - Admin can select all three modes
   - Setting persists after page reload

2. **Access Control:**
   - Non-admin cannot set High Quality via API (403 Forbidden)
   - Admin loses privileges → setting resets to Balanced
   - Frontend validation matches backend validation

3. **Image Processing:**
   - Uploaded images are processed according to selected mode
   - File sizes match expected ranges for each mode
   - Image quality is appropriate for selected mode

4. **File Size Limits:**
   - Regular user cannot upload files > 20 MB
   - Admin cannot upload files > 50 MB
   - Error messages show correct limits

## Related Features

- [FEATURE-017: Item Image Gallery Upload](./FEATURE-017-item-image-gallery-upload.md) - Base image upload functionality
- [FEATURE-024: Container Images and Unification](./FEATURE-024-container-images-and-unification.md) - Container images (planned)

## Changelog

### v2.16.0
- ✅ Added image processing mode selection in Gear Settings
- ✅ Implemented three processing modes (High Quality, Balanced, Storage Saver)
- ✅ Added admin-only restriction for High Quality mode
- ✅ Implemented file size limits (20 MB regular, 50 MB admin)
- ✅ Automatic image processing based on user settings
- ✅ Frontend validation matches backend limits

