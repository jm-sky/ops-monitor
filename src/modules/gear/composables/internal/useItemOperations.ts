import { useBackend } from '@/shared/composables/useBackend'
import type { ICreateItemDto, IGearItem, IUpdateItemDto } from '../../types/gear.types'
import { gearItemService } from '../../services/gearItemService'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Focused composable for item CRUD operations
 *
 * This composable is part of the refactored useGear.ts mega-composable.
 * It handles only item-related operations (create, read, update, delete).
 *
 * @internal - Use via useGear() facade for backward compatibility
 */
export function useItemOperations() {
  const createItem = async (containerId: TUUID, data: ICreateItemDto): Promise<IGearItem> => {
    return await gearItemService().createItem(containerId, data)
  }

  const updateItem = async (itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem> => {
    const service = gearItemService()
    const { shouldUseAPI } = useBackend()

    // Backend automatically propagates changes to all linked items
    // For API, a single call is sufficient
    if (shouldUseAPI.value) {
      return await service.updateItem(itemId, data)
    }

    // For localStorage, we need to manually update all linked items
    // This logic is now encapsulated in the service layer
    return await service.updateLinkedItems(itemId, data)
  }

  const deleteItem = async (itemId: TUUID): Promise<void> => {
    await gearItemService().deleteItem(itemId)
  }

  const getItemById = async (containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined> => {
    return await gearItemService().getItemFromContainer(containerId, itemId)
  }

  const moveItem = async (itemId: TUUID, targetContainerId: TUUID): Promise<IGearItem> => {
    return await gearItemService().moveItem(itemId, targetContainerId)
  }

  return {
    createItem,
    updateItem,
    deleteItem,
    getItemById,
    moveItem,
  }
}
