# FEATURE-017: Item Image Gallery Upload

**Status:** ✅ Completed | **Version:** v2.10.0
**Priority:** High
**Complexity:** Large
**Category:** 📷 Media & Resources
**Related Features:** FEATURE-016 (Automatic Item Image Fetching)
**Requires:** Backend/DB, Admin Access (isAdmin), S3/Local Storage

---

## 📋 Overview

Enable admins to upload images for gear items with support for multiple images (gallery), reordering, and removal. The system uses a storage adapter pattern to support both local file storage (development/self-hosted) and S3 (cloud/production), configured via environment variables. Includes validation for file size, MIME type, and optional auto-resize/optimization.

---

## 🎯 Goals

1. **Admin-Only Image Upload** - Only users with `isAdmin` flag can upload images
2. **Multi-Image Gallery** - Support multiple images per item with gallery view
3. **Image Order Management** - Drag-and-drop reordering of images
4. **Image Removal** - Ability to delete images from gallery
5. **Storage Adapter Pattern** - Pluggable storage backends (local filesystem, S3)
6. **Validation** - File size limits, MIME type validation, disk space checks
7. **Image Processing** - Auto-resize large images to medium size, format conversion
8. **Primary Image** - Mark one image as primary for item display

---

## 📐 Design

### Current State

- Items have no image upload functionality
- FEATURE-016 planned for automatic image fetching (web search)
- No file upload infrastructure in backend
- No S3 integration

### Proposed Changes

#### 1. Database Schema

**New Tables:**

```python
# Item Images (gallery)
class ItemImage(Base):
    __tablename__ = "item_images"

    id: UUID  # Primary key
    item_id: UUID  # FK to items
    user_id: UUID  # FK to users (uploader)

    # Storage info
    storage_type: str  # "local" | "s3"
    file_path: str  # Relative path for local, S3 key for S3
    file_name: str  # Original filename
    file_size: int  # Size in bytes
    mime_type: str  # image/jpeg, image/png, image/webp

    # Image metadata
    width: Optional[int]  # Image width in pixels
    height: Optional[int]  # Image height in pixels
    is_primary: bool  # Primary image for item
    order: int  # Display order (0-based)

    # Processing flags
    is_processed: bool  # Whether auto-resize/optimization completed
    original_file_size: Optional[int]  # Original size before processing

    created_at: datetime
    updated_at: datetime

    # Relationships
    item: relationship("Item", back_populates="images")
    user: relationship("User")

# Update existing Item model
class Item(Base):
    # ... existing fields ...
    images: relationship("ItemImage", back_populates="item", cascade="all, delete-orphan")
```

#### 2. Storage Adapter Architecture

**Abstract Base Class:**

```python
# backend/app/core/storage/adapter.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional

class StorageAdapter(ABC):
    """Abstract storage adapter for file operations."""

    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        destination_path: str,
        content_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload file to storage.
        Returns: Full path/URL to stored file
        """
        pass

    @abstractmethod
    async def download(self, file_path: str) -> bytes:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get accessible URL for file (signed URL for S3, local path for filesystem)."""
        pass

    @abstractmethod
    async def get_available_space(self) -> Optional[int]:
        """Get available storage space in bytes (None if unlimited/unknown)."""
        pass
```

**Local Filesystem Implementation:**

```python
# backend/app/core/storage/local_adapter.py
import aiofiles
import shutil
from pathlib import Path

class LocalStorageAdapter(StorageAdapter):
    """Local filesystem storage adapter."""

    def __init__(self, base_path: str = "./uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload(
        self,
        file: BinaryIO,
        destination_path: str,
        content_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to local filesystem."""
        full_path = self.base_path / destination_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        return str(destination_path)

    async def download(self, file_path: str) -> bytes:
        """Download file from local filesystem."""
        full_path = self.base_path / file_path
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()

    async def delete(self, file_path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return (self.base_path / file_path).exists()

    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get URL for local file (served via FastAPI static files)."""
        return f"/uploads/{file_path}"

    async def get_available_space(self) -> Optional[int]:
        """Get available disk space."""
        stat = shutil.disk_usage(self.base_path)
        return stat.free
```

**S3 Implementation:**

```python
# backend/app/core/storage/s3_adapter.py
import aioboto3
from botocore.exceptions import ClientError

class S3StorageAdapter(StorageAdapter):
    """AWS S3 storage adapter."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None  # For S3-compatible services (MinIO, DigitalOcean Spaces)
    ):
        self.bucket_name = bucket_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.session = aioboto3.Session()

    async def upload(
        self,
        file: BinaryIO,
        destination_path: str,
        content_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to S3."""
        async with self.session.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            content = await file.read()
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=destination_path,
                Body=content,
                ContentType=content_type,
                Metadata=metadata or {}
            )
        return destination_path

    async def download(self, file_path: str) -> bytes:
        """Download file from S3."""
        async with self.session.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            response = await s3.get_object(Bucket=self.bucket_name, Key=file_path)
            return await response['Body'].read()

    async def delete(self, file_path: str) -> bool:
        """Delete file from S3."""
        async with self.session.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=file_path)
                return True
            except ClientError:
                return False

    async def exists(self, file_path: str) -> bool:
        """Check if file exists in S3."""
        async with self.session.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.head_object(Bucket=self.bucket_name, Key=file_path)
                return True
            except ClientError:
                return False

    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Generate pre-signed URL for S3 object."""
        async with self.session.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expires_in
            )
            return url

    async def get_available_space(self) -> Optional[int]:
        """S3 has unlimited space (return None)."""
        return None
```

**Storage Factory:**

```python
# backend/app/core/storage/factory.py
from app.core.storage.adapter import StorageAdapter
from app.core.storage.local_adapter import LocalStorageAdapter
from app.core.storage.s3_adapter import S3StorageAdapter
from app.core.config import settings

def get_storage_adapter() -> StorageAdapter:
    """Get storage adapter based on configuration."""
    storage_type = settings.storage.type

    if storage_type == "local":
        return LocalStorageAdapter(
            base_path=settings.storage.local_path
        )
    elif storage_type == "s3":
        return S3StorageAdapter(
            bucket_name=settings.storage.s3_bucket,
            aws_access_key_id=settings.storage.s3_access_key,
            aws_secret_access_key=settings.storage.s3_secret_key,
            region_name=settings.storage.s3_region,
            endpoint_url=settings.storage.s3_endpoint_url
        )
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
```

#### 3. Configuration (Environment Variables)

**Add to `backend/app/core/config.py`:**

```python
class StorageSettings(BaseSettings):
    """Storage configuration for file uploads."""

    model_config = _base_config

    # Storage type
    type: Literal["local", "s3"] = Field(
        default="local",
        validation_alias="STORAGE_TYPE",
        description="Storage backend type (local or s3)"
    )

    # Local storage
    local_path: str = Field(
        default="./uploads",
        validation_alias="STORAGE_LOCAL_PATH",
        description="Local storage base path"
    )

    # S3 storage
    s3_bucket: str = Field(
        default="",
        validation_alias="STORAGE_S3_BUCKET",
        description="S3 bucket name"
    )
    s3_access_key: str = Field(
        default="",
        validation_alias="STORAGE_S3_ACCESS_KEY",
        description="S3 access key ID"
    )
    s3_secret_key: str = Field(
        default="",
        validation_alias="STORAGE_S3_SECRET_KEY",
        description="S3 secret access key"
    )
    s3_region: str = Field(
        default="us-east-1",
        validation_alias="STORAGE_S3_REGION",
        description="S3 region"
    )
    s3_endpoint_url: Optional[str] = Field(
        default=None,
        validation_alias="STORAGE_S3_ENDPOINT_URL",
        description="S3 endpoint URL (for S3-compatible services)"
    )

    # Upload limits
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        validation_alias="STORAGE_MAX_FILE_SIZE",
        description="Maximum file size in bytes"
    )
    max_files_per_item: int = Field(
        default=10,
        validation_alias="STORAGE_MAX_FILES_PER_ITEM",
        description="Maximum number of images per item"
    )
    allowed_mime_types: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp", "image/gif"],
        validation_alias="STORAGE_ALLOWED_MIME_TYPES",
        description="Allowed MIME types for uploads"
    )

    # Image processing
    enable_processing: bool = Field(
        default=True,
        validation_alias="STORAGE_ENABLE_PROCESSING",
        description="Enable auto-resize and optimization"
    )
    max_width: int = Field(
        default=1920,
        validation_alias="STORAGE_MAX_WIDTH",
        description="Maximum image width (auto-resize)"
    )
    max_height: int = Field(
        default=1920,
        validation_alias="STORAGE_MAX_HEIGHT",
        description="Maximum image height (auto-resize)"
    )
    jpeg_quality: int = Field(
        default=85,
        validation_alias="STORAGE_JPEG_QUALITY",
        description="JPEG compression quality (1-100)"
    )
    convert_to_webp: bool = Field(
        default=False,
        validation_alias="STORAGE_CONVERT_TO_WEBP",
        description="Convert images to WebP format"
    )

# Add to main Settings class
class Settings(BaseSettings):
    # ... existing settings ...
    storage: StorageSettings = Field(default_factory=StorageSettings)
```

#### 4. Image Processing Service

**Dependencies:**

```python
# Add to requirements.txt
Pillow>=11.0.0  # Latest stable (2025)
python-magic>=0.4.27  # For MIME type validation
aiofiles>=24.1.0  # Async file operations
aioboto3>=13.3.0  # Async S3 client (optional, only if using S3)
```

**Service Implementation:**

```python
# backend/app/core/storage/image_processor.py
from PIL import Image
import io
from typing import Tuple

class ImageProcessor:
    """Image processing utilities."""

    def __init__(
        self,
        max_width: int = 1920,
        max_height: int = 1920,
        jpeg_quality: int = 85,
        convert_to_webp: bool = False
    ):
        self.max_width = max_width
        self.max_height = max_height
        self.jpeg_quality = jpeg_quality
        self.convert_to_webp = convert_to_webp

    async def process_image(self, image_bytes: bytes, mime_type: str) -> Tuple[bytes, str, int, int]:
        """
        Process image: resize, compress, optionally convert to WebP.
        Returns: (processed_bytes, new_mime_type, width, height)
        """
        # Open image
        img = Image.open(io.BytesIO(image_bytes))

        # Convert RGBA to RGB if saving as JPEG
        if img.mode == 'RGBA' and not self.convert_to_webp:
            img = img.convert('RGB')

        # Get original dimensions
        original_width, original_height = img.size

        # Resize if needed (preserve aspect ratio)
        if original_width > self.max_width or original_height > self.max_height:
            img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)

        width, height = img.size

        # Save processed image
        output = io.BytesIO()

        if self.convert_to_webp:
            img.save(output, format='WEBP', quality=self.jpeg_quality, method=6)
            mime_type = 'image/webp'
        elif mime_type in ['image/jpeg', 'image/jpg']:
            img.save(output, format='JPEG', quality=self.jpeg_quality, optimize=True)
        elif mime_type == 'image/png':
            img.save(output, format='PNG', optimize=True)
        else:
            # Keep original format
            img.save(output, format=img.format, quality=self.jpeg_quality)

        output.seek(0)
        processed_bytes = output.read()

        return processed_bytes, mime_type, width, height

    def validate_image(self, image_bytes: bytes) -> bool:
        """Validate that bytes represent a valid image."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            return True
        except Exception:
            return False
```

#### 5. File Upload Service

```python
# backend/app/modules/gear/services/image_upload_service.py
import uuid
import magic
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.core.config import settings
from app.modules.gear.repositories.item_image_repository import ItemImageRepository

class ImageUploadService:
    """Service for handling image uploads."""

    def __init__(self):
        self.storage = get_storage_adapter()
        self.processor = ImageProcessor(
            max_width=settings.storage.max_width,
            max_height=settings.storage.max_height,
            jpeg_quality=settings.storage.jpeg_quality,
            convert_to_webp=settings.storage.convert_to_webp
        )
        self.max_file_size = settings.storage.max_file_size
        self.allowed_mime_types = settings.storage.allowed_mime_types

    async def validate_upload(self, file: UploadFile, item_id: str, user_id: str) -> None:
        """Validate file upload constraints."""
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size / 1024 / 1024:.1f} MB"
            )

        # Check MIME type (preliminary check)
        if file.content_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(self.allowed_mime_types)}"
            )

        # Check number of existing images for item
        repo = ItemImageRepository()
        existing_count = await repo.count_by_item(item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item"
            )

        # Check available storage space (for local storage)
        if settings.storage.type == "local":
            available_space = await self.storage.get_available_space()
            if available_space and available_space < file_size:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail="Insufficient storage space"
                )

    async def upload_image(
        self,
        file: UploadFile,
        item_id: str,
        user_id: str,
        is_primary: bool = False
    ) -> dict:
        """
        Upload and process image.
        Returns: Image metadata
        """
        # Read file content
        content = await file.read()

        # Validate MIME type using python-magic (magic numbers)
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(content)

        if detected_mime not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid file type. Detected: {detected_mime}"
            )

        # Validate image integrity
        if not self.processor.validate_image(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file"
            )

        original_size = len(content)

        # Process image if enabled
        if settings.storage.enable_processing:
            content, detected_mime, width, height = await self.processor.process_image(
                content, detected_mime
            )
            processed_size = len(content)
        else:
            # Get dimensions without processing
            img = Image.open(io.BytesIO(content))
            width, height = img.size
            processed_size = original_size

        # Generate unique filename
        file_ext = self._get_extension(detected_mime)
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        destination_path = f"items/{item_id}/{unique_filename}"

        # Upload to storage
        file_io = io.BytesIO(content)
        stored_path = await self.storage.upload(
            file_io,
            destination_path,
            detected_mime,
            metadata={
                "item_id": item_id,
                "user_id": user_id,
                "original_filename": file.filename
            }
        )

        # Create database record
        repo = ItemImageRepository()
        image_record = await repo.create({
            "item_id": item_id,
            "user_id": user_id,
            "storage_type": settings.storage.type,
            "file_path": stored_path,
            "file_name": file.filename,
            "file_size": processed_size,
            "mime_type": detected_mime,
            "width": width,
            "height": height,
            "is_primary": is_primary,
            "order": await repo.get_next_order(item_id),
            "is_processed": settings.storage.enable_processing,
            "original_file_size": original_size if settings.storage.enable_processing else None
        })

        # Get accessible URL
        url = await self.storage.get_url(stored_path)

        return {
            "id": image_record.id,
            "url": url,
            "file_name": file.filename,
            "file_size": processed_size,
            "mime_type": detected_mime,
            "width": width,
            "height": height,
            "is_primary": is_primary,
            "order": image_record.order
        }

    def _get_extension(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif"
        }
        return mime_map.get(mime_type, ".jpg")

    async def delete_image(self, image_id: str, user_id: str) -> bool:
        """Delete image by ID."""
        repo = ItemImageRepository()
        image = await repo.get_by_id(image_id)

        if not image:
            return False

        # Delete from storage
        await self.storage.delete(image.file_path)

        # Delete from database
        await repo.delete(image_id)

        return True

    async def reorder_images(self, item_id: str, image_orders: list[dict]) -> bool:
        """
        Reorder images for an item.
        image_orders: [{"id": "uuid", "order": 0}, ...]
        """
        repo = ItemImageRepository()
        for item in image_orders:
            await repo.update(item["id"], {"order": item["order"]})
        return True

    async def set_primary_image(self, item_id: str, image_id: str) -> bool:
        """Set image as primary for item."""
        repo = ItemImageRepository()

        # Unset current primary
        await repo.unset_primary_for_item(item_id)

        # Set new primary
        await repo.update(image_id, {"is_primary": True})

        return True
```

#### 6. API Endpoints

```python
# backend/app/modules/gear/routers/item_images.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.modules.auth.decorators import admin_required
from app.modules.auth.dependencies import get_current_user
from app.modules.gear.services.image_upload_service import ImageUploadService

router = APIRouter(prefix="/items", tags=["item-images"])

@router.post("/{item_id}/images", dependencies=[Depends(admin_required)])
async def upload_item_image(
    item_id: str,
    file: UploadFile = File(...),
    is_primary: bool = False,
    current_user = Depends(get_current_user)
):
    """Upload image for item (admin only)."""
    service = ImageUploadService()

    # Validate upload
    await service.validate_upload(file, item_id, current_user.id)

    # Upload and process
    result = await service.upload_image(file, item_id, current_user.id, is_primary)

    return result

@router.get("/{item_id}/images")
async def get_item_images(item_id: str):
    """Get all images for an item."""
    repo = ItemImageRepository()
    images = await repo.get_by_item(item_id)

    # Generate URLs for each image
    storage = get_storage_adapter()
    for img in images:
        img.url = await storage.get_url(img.file_path)

    return images

@router.delete("/images/{image_id}", dependencies=[Depends(admin_required)])
async def delete_item_image(
    image_id: str,
    current_user = Depends(get_current_user)
):
    """Delete item image (admin only)."""
    service = ImageUploadService()
    success = await service.delete_image(image_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Image not found")

    return {"message": "Image deleted successfully"}

@router.put("/{item_id}/images/reorder", dependencies=[Depends(admin_required)])
async def reorder_item_images(
    item_id: str,
    image_orders: list[dict],
    current_user = Depends(get_current_user)
):
    """Reorder images for item (admin only)."""
    service = ImageUploadService()
    await service.reorder_images(item_id, image_orders)
    return {"message": "Images reordered successfully"}

@router.put("/{item_id}/images/{image_id}/primary", dependencies=[Depends(admin_required)])
async def set_primary_image(
    item_id: str,
    image_id: str,
    current_user = Depends(get_current_user)
):
    """Set image as primary for item (admin only)."""
    service = ImageUploadService()
    await service.set_primary_image(item_id, image_id)
    return {"message": "Primary image set successfully"}
```

#### 7. Frontend Implementation

**API Service:**

```typescript
// src/modules/gear/services/itemImageApiService.ts
import { apiClient } from '@/shared/services/apiClient'
import type { TUUID } from '@/shared/types/base.type'

export interface IItemImage {
  id: TUUID
  itemId: TUUID
  userId: TUUID
  storageType: 'local' | 's3'
  filePath: string
  fileName: string
  fileSize: number
  mimeType: string
  width: number
  height: number
  isPrimary: boolean
  order: number
  url: string
  createdAt: string
  updatedAt: string
}

export const itemImageApiService = {
  async uploadImage(
    itemId: TUUID,
    file: File,
    isPrimary: boolean = false
  ): Promise<IItemImage> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_primary', isPrimary.toString())

    const response = await apiClient.post<IItemImage>(
      `/items/${itemId}/images`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  },

  async getImages(itemId: TUUID): Promise<IItemImage[]> {
    const response = await apiClient.get<IItemImage[]>(`/items/${itemId}/images`)
    return response.data
  },

  async deleteImage(imageId: TUUID): Promise<void> {
    await apiClient.delete(`/items/images/${imageId}`)
  },

  async reorderImages(
    itemId: TUUID,
    imageOrders: Array<{ id: TUUID; order: number }>
  ): Promise<void> {
    await apiClient.put(`/items/${itemId}/images/reorder`, imageOrders)
  },

  async setPrimaryImage(itemId: TUUID, imageId: TUUID): Promise<void> {
    await apiClient.put(`/items/${itemId}/images/${imageId}/primary`)
  }
}
```

**Image Gallery Component:**

```vue
<!-- src/modules/gear/components/ItemImageGallery.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import { Upload, X, Star, GripVertical } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { itemImageApiService, type IItemImage } from '@/modules/gear/services/itemImageApiService'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { TUUID } from '@/shared/types/base.type'

const props = defineProps<{
  itemId: TUUID
}>()

const { isAdmin } = useAuth()
const images = ref<IItemImage[]>([])
const isLoading = ref(false)
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const sortedImages = computed(() => {
  return [...images.value].sort((a, b) => a.order - b.order)
})

const primaryImage = computed(() => {
  return images.value.find(img => img.isPrimary)
})

async function loadImages() {
  try {
    isLoading.value = true
    images.value = await itemImageApiService.getImages(props.itemId)
  } catch (error) {
    toast.error('Failed to load images')
  } finally {
    isLoading.value = false
  }
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (!files || files.length === 0) return

  const file = files[0]

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    toast.error('Invalid file type. Allowed: JPEG, PNG, WebP, GIF')
    return
  }

  // Validate file size (10 MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    toast.error('File size exceeds 10 MB')
    return
  }

  await uploadImage(file)
}

async function uploadImage(file: File) {
  try {
    isLoading.value = true
    const isPrimary = images.value.length === 0 // First image is primary
    const newImage = await itemImageApiService.uploadImage(props.itemId, file, isPrimary)
    images.value.push(newImage)
    toast.success('Image uploaded successfully')
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to upload image'
    toast.error(message)
  } finally {
    isLoading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

async function deleteImage(imageId: TUUID) {
  if (!confirm('Are you sure you want to delete this image?')) return

  try {
    await itemImageApiService.deleteImage(imageId)
    images.value = images.value.filter(img => img.id !== imageId)
    toast.success('Image deleted successfully')
  } catch (error) {
    toast.error('Failed to delete image')
  }
}

async function setPrimary(imageId: TUUID) {
  try {
    await itemImageApiService.setPrimaryImage(props.itemId, imageId)
    images.value = images.value.map(img => ({
      ...img,
      isPrimary: img.id === imageId
    }))
    toast.success('Primary image updated')
  } catch (error) {
    toast.error('Failed to set primary image')
  }
}

// Drag and drop reordering
let draggedIndex = -1

function handleDragStart(index: number) {
  draggedIndex = index
  isDragging.value = true
}

function handleDragOver(event: DragEvent, index: number) {
  event.preventDefault()
  if (draggedIndex === index) return

  const sorted = sortedImages.value
  const draggedItem = sorted[draggedIndex]
  sorted.splice(draggedIndex, 1)
  sorted.splice(index, 0, draggedItem)

  draggedIndex = index
}

async function handleDragEnd() {
  isDragging.value = false

  // Update order on backend
  const imageOrders = sortedImages.value.map((img, index) => ({
    id: img.id,
    order: index
  }))

  try {
    await itemImageApiService.reorderImages(props.itemId, imageOrders)
    toast.success('Images reordered')
  } catch (error) {
    toast.error('Failed to reorder images')
    await loadImages() // Reload to reset
  }
}

onMounted(() => {
  loadImages()
})
</script>

<template>
  <div class="space-y-4">
    <div v-if="isAdmin" class="flex items-center justify-between">
      <h3 class="text-lg font-semibold">Images</h3>
      <Button @click="fileInput?.click()" :disabled="isLoading">
        <Upload class="size-4" />
        Upload Image
      </Button>
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>

    <div v-if="images.length === 0" class="text-center text-muted-foreground py-8">
      No images uploaded yet
    </div>

    <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      <div
        v-for="(image, index) in sortedImages"
        :key="image.id"
        class="relative group"
        :draggable="isAdmin"
        @dragstart="handleDragStart(index)"
        @dragover="handleDragOver($event, index)"
        @dragend="handleDragEnd"
      >
        <img
          :src="image.url"
          :alt="image.fileName"
          class="w-full h-48 object-cover rounded-lg"
        />

        <!-- Overlay controls (admin only) -->
        <div
          v-if="isAdmin"
          class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-2"
        >
          <Button
            size="icon"
            variant="ghost"
            class="text-white"
            @click="setPrimary(image.id)"
            v-tooltip="'Set as primary'"
          >
            <Star :class="{ 'fill-yellow-400': image.isPrimary }" class="size-4" />
          </Button>

          <Button
            size="icon"
            variant="ghost"
            class="text-white cursor-move"
            v-tooltip="'Drag to reorder'"
          >
            <GripVertical class="size-4" />
          </Button>

          <Button
            size="icon"
            variant="ghost"
            class="text-white"
            @click="deleteImage(image.id)"
            v-tooltip="'Delete image'"
          >
            <X class="size-4" />
          </Button>
        </div>

        <!-- Primary indicator -->
        <div
          v-if="image.isPrimary"
          class="absolute top-2 left-2 bg-yellow-400 text-black px-2 py-1 rounded text-xs font-semibold"
        >
          Primary
        </div>
      </div>
    </div>
  </div>
</template>
```

---

## 🛠️ Implementation Plan

### Phase 1: Backend Infrastructure

**Files:**
- `backend/app/core/storage/adapter.py` - Abstract storage adapter
- `backend/app/core/storage/local_adapter.py` - Local filesystem implementation
- `backend/app/core/storage/s3_adapter.py` - S3 implementation
- `backend/app/core/storage/factory.py` - Storage factory
- `backend/app/core/storage/image_processor.py` - Image processing service
- `backend/app/core/config.py` - Add StorageSettings
- `backend/requirements.txt` - Add dependencies

**Changes:**
1. Create storage adapter pattern with abstract base class
2. Implement local filesystem adapter
3. Implement S3 adapter (with support for S3-compatible services)
4. Add storage configuration to settings
5. Create image processor with Pillow
6. Add dependencies: Pillow, python-magic, aiofiles, aioboto3

### Phase 2: Database Schema

**Files:**
- `backend/migrations/XXX_add_item_images_table.py` - Database migration
- `backend/app/modules/gear/db_models.py` - Add ItemImage model

**Changes:**
1. Create item_images table
2. Add relationship to items
3. Add indexes for item_id, user_id, order

### Phase 3: Backend Service & API

**Files:**
- `backend/app/modules/gear/repositories/item_image_repository.py` - Repository
- `backend/app/modules/gear/services/image_upload_service.py` - Upload service
- `backend/app/modules/gear/routers/item_images.py` - API endpoints
- `backend/app/modules/gear/schemas/item_image.py` - Pydantic schemas

**Changes:**
1. Create ItemImageRepository for CRUD operations
2. Create ImageUploadService with validation and processing
3. Create API endpoints for upload, list, delete, reorder, set primary
4. Add admin-only decorators to endpoints

### Phase 4: Static File Serving (Local Storage)

**Files:**
- `backend/app/core/static.py` - Static file configuration
- `backend/main.py` - Mount static files

**Changes:**
1. Configure FastAPI to serve uploaded files from /uploads path
2. Add security headers for static files

### Phase 5: Frontend API Integration

**Files:**
- `src/modules/gear/services/itemImageApiService.ts` - API service
- `src/modules/gear/types/itemImage.types.ts` - TypeScript types

**Changes:**
1. Create API service for image operations
2. Define TypeScript types for ItemImage

### Phase 6: Frontend UI Components

**Files:**
- `src/modules/gear/components/ItemImageGallery.vue` - Gallery component
- `src/modules/gear/pages/ItemFormPage.vue` - Integrate gallery into form

**Changes:**
1. Create ItemImageGallery component with upload, display, reorder, delete
2. Integrate gallery into item form page
3. Add drag-and-drop reordering
4. Add primary image indicator

### Phase 7: Testing & Documentation

**Files:**
- `backend/tests/test_image_upload_service.py` - Unit tests
- `backend/tests/test_storage_adapters.py` - Storage adapter tests
- `.env.example` - Add storage configuration examples
- `README.md` - Update with storage setup instructions

**Changes:**
1. Write unit tests for upload service
2. Write tests for storage adapters
3. Document configuration options
4. Add setup instructions for S3

---

## 📊 Configuration Examples

### Local Storage (Development)

```bash
# .env
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./uploads
STORAGE_MAX_FILE_SIZE=10485760  # 10 MB
STORAGE_MAX_FILES_PER_ITEM=10
STORAGE_ENABLE_PROCESSING=true
STORAGE_MAX_WIDTH=1920
STORAGE_MAX_HEIGHT=1920
STORAGE_JPEG_QUALITY=85
STORAGE_CONVERT_TO_WEBP=false
```

### S3 Storage (Production)

```bash
# .env
STORAGE_TYPE=s3
STORAGE_S3_BUCKET=gear-stack-uploads
STORAGE_S3_ACCESS_KEY=your-access-key
STORAGE_S3_SECRET_KEY=your-secret-key
STORAGE_S3_REGION=us-east-1
# For S3-compatible services (MinIO, DigitalOcean Spaces)
STORAGE_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
```

---

## 🧪 Testing

### Manual Test Cases

1. **Upload Image (Admin)**
   - ✅ Admin can upload image
   - ✅ Non-admin cannot upload (403 error)
   - ✅ Image is validated (size, MIME type)
   - ✅ Image is processed (resize, compress)
   - ✅ First image becomes primary automatically

2. **Delete Image (Admin)**
   - ✅ Admin can delete image
   - ✅ Image removed from storage
   - ✅ Database record deleted

3. **Reorder Images (Admin)**
   - ✅ Drag-and-drop reordering works
   - ✅ Order persisted to database
   - ✅ Order reflected in gallery

4. **Set Primary Image (Admin)**
   - ✅ Can set any image as primary
   - ✅ Only one image marked as primary
   - ✅ Primary indicator displayed

5. **Storage Adapters**
   - ✅ Local storage works
   - ✅ S3 storage works
   - ✅ Switch between adapters via config

6. **Validation**
   - ✅ File size limit enforced
   - ✅ MIME type validation works
   - ✅ Max files per item enforced
   - ✅ Disk space check (local storage)

7. **Image Processing**
   - ✅ Large images resized
   - ✅ JPEG compression works
   - ✅ WebP conversion works (if enabled)
   - ✅ Aspect ratio preserved

---

## 📦 Dependencies

### Backend

```python
# requirements.txt additions
Pillow>=11.0.0              # Image processing (2025 stable)
python-magic>=0.4.27        # MIME type validation
aiofiles>=24.1.0            # Async file operations
aioboto3>=13.3.0            # Async S3 client (optional)
```

### Frontend

No additional dependencies needed (uses existing libraries)

---

## 📝 Notes

- **Admin-Only**: Feature restricted to users with `isAdmin` flag
- **Storage Flexibility**: Supports both local filesystem and S3 via adapter pattern
- **Image Processing**: Auto-resize large images to reduce storage and bandwidth
- **Security**: Validates MIME types using magic numbers, not just file extensions
- **Validation**: Enforces file size limits, file count limits, and disk space checks
- **Performance**: Async operations throughout for better performance
- **S3-Compatible**: Works with AWS S3, MinIO, DigitalOcean Spaces, etc.

---

## 🔗 Related Documentation

- [ROADMAP_ONLINE.md](../ROADMAP_ONLINE.md) - Online features roadmap
- [FEATURE-016](./FEATURE-016-automatic-item-image-fetching.md) - Automatic image fetching

---

## 📚 Research Sources

### Image Processing Libraries (2025)
- [Python libraries to compress & resize images fast | Uploadcare](https://uploadcare.com/blog/image-optimization-python/)
- [Image module - Pillow (PIL Fork) 12.0.0 documentation](https://pillow.readthedocs.io/en/stable/reference/Image.html)
- [Python Image Resize With Pillow and OpenCV](https://cloudinary.com/guides/bulk-image-resize/python-image-resize-with-pillow-and-opencv)
- [Image Processing in Python with Pillow](https://auth0.com/blog/image-processing-in-python-with-pillow/)

### FastAPI File Upload Validation (2025)
- [validate file type and extention with fastapi UploadFile - Stack Overflow](https://stackoverflow.com/questions/69192379/validate-file-type-and-extention-with-fastapi-uploadfile)
- [How to Handle File Uploads in FastAPI](https://davidmuraya.com/blog/fastapi-file-uploads/)
- [Upload files in FastAPI with file validation | Medium](https://medium.com/@jayhawk24/upload-files-in-fastapi-with-file-validation-787bd1a57658)
- [Handling File Uploads in FastAPI: From Basics to S3 Integration | Medium (Nov 2025)](https://mahdijafaridev.medium.com/handling-file-uploads-in-fastapi-from-basics-to-s3-integration-fc7e64f87d65)
- [Uploading Files Using FastAPI: A Complete Guide | Better Stack Community](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)
