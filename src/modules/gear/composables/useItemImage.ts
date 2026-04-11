import type { IItemImage } from '../types/itemImage.types'
import { itemImageApiService } from '../services/itemImageApiService'
import { useGear } from './useGear'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Composable for managing item images with automatic store updates
 *
 * This composable provides methods to manage item images (upload, delete, set primary)
 * and automatically updates the item's primaryImageUrl in the Pinia store.
 */
export function useItemImage() {
  const { updateItem } = useGear()

  /**
   * Upload image for an item and update primaryImageUrl if needed
   *
   * @param itemId - Item ID
   * @param file - Image file to upload
   * @param isPrimary - Whether this should be the primary image
   * @returns Uploaded image metadata
   */
  async function uploadImage(itemId: TUUID, file: File, isPrimary: boolean = false): Promise<IItemImage> {
    const image = await itemImageApiService.uploadImage(itemId, file, isPrimary)

    // Update item's primaryImageUrl if this is the primary image
    if (isPrimary) {
      await updateItem(itemId, { primaryImageUrl: image.url })
    }

    return image
  }

  /**
   * Upload image from URL and update primaryImageUrl if needed
   *
   * @param itemId - Item ID
   * @param url - External image URL
   * @param isPrimary - Whether this should be the primary image
   * @param hostLocally - If true, download and store image. If false, only save external URL.
   * @returns Created image metadata
   */
  async function uploadImageFromUrl(
    itemId: TUUID,
    url: string,
    isPrimary: boolean = false,
    hostLocally: boolean = true,
  ): Promise<IItemImage> {
    const image = await itemImageApiService.uploadImageFromUrl(itemId, url, isPrimary, hostLocally)

    // Update item's primaryImageUrl if this is the primary image
    if (isPrimary) {
      await updateItem(itemId, { primaryImageUrl: image.url })
    }

    return image
  }

  /**
   * Delete an image and update primaryImageUrl if needed
   *
   * @param itemId - Item ID
   * @param imageId - Image ID to delete
   * @returns void
   */
  async function deleteImage(itemId: TUUID, imageId: TUUID): Promise<void> {
    // Get current images before deletion
    const images = await itemImageApiService.getImages(itemId)
    const imageToDelete = images.find(img => img.id === imageId)

    // Delete the image
    await itemImageApiService.deleteImage(imageId)

    // If we deleted the primary image, update the item
    if (imageToDelete?.isPrimary) {
      // Get remaining images after deletion
      const remainingImages = images.filter(img => img.id !== imageId)

      // Find the next primary image (if any)
      const nextPrimary = remainingImages.find(img => img.isPrimary)

      // Update item with new primaryImageUrl (null if no images left)
      await updateItem(itemId, { primaryImageUrl: nextPrimary?.url ?? null })
    }
  }

  /**
   * Toggle primary status for image and update primaryImageUrl
   *
   * @param itemId - Item ID
   * @param imageId - Image ID to toggle primary status
   * @returns True if image is now primary, False if it was unset
   */
  async function togglePrimaryImage(itemId: TUUID, imageId: TUUID): Promise<boolean> {
    // Get the image details before toggling
    const images = await itemImageApiService.getImages(itemId)
    const image = images.find(img => img.id === imageId)

    if (!image) {
      throw new Error('Image not found')
    }

    // Toggle primary status on backend
    const isPrimary = await itemImageApiService.togglePrimaryImage(itemId, imageId)

    // Update item's primaryImageUrl (null if unset, image.url if set)
    await updateItem(itemId, { primaryImageUrl: isPrimary ? image.url : null })

    return isPrimary
  }

  /**
   * Reorder images for an item
   *
   * @param itemId - Item ID
   * @param imageOrders - Array of {id, order} objects
   * @returns void
   */
  async function reorderImages(itemId: TUUID, imageOrders: Array<{ id: TUUID; order: number }>): Promise<void> {
    await itemImageApiService.reorderImages(itemId, imageOrders)
  }

  return {
    uploadImage,
    uploadImageFromUrl,
    deleteImage,
    togglePrimaryImage,
    reorderImages,
  }
}
