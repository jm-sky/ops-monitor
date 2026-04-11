import { logger } from '@/shared/utils/logger'
import type { ICreateItemDto, IGearItem, IGearItemService, IUpdateItemDto } from '../types/gear.types'
import type { GearItemLocalService } from './gearItemLocalService'
import { useGearStore } from '../store/useGearStore'
import { DEFAULT_PAGINATION_LIMIT } from '../utils/constants'
import { gearContainerApiService } from './gearContainerApiService'
import { GearItemApiService } from './gearItemApiService'
import type { TULID } from '@/shared/types/base.type'

export class GearItemHybridService implements IGearItemService {
  private readonly gearItemLocalService: GearItemLocalService
  private readonly gearItemApiService: GearItemApiService

  constructor(gearItemLocalService: GearItemLocalService, gearItemApiService: GearItemApiService) {
    this.gearItemLocalService = gearItemLocalService
    this.gearItemApiService = gearItemApiService
  }

  async createItem(containerId: TULID, data: ICreateItemDto): Promise<IGearItem> {
    let createdItem: IGearItem | null = null

    try {
      // H6 FIX: Transaction boundary - Phase 1: Create item on API
      createdItem = await this.gearItemApiService.createItem(containerId, data)

      try {
        // H6 FIX: Transaction boundary - Phase 2: Sync store with API
        const container = await gearContainerApiService.getContainer(containerId)
        useGearStore().updateContainer(container)
        // Store automatically saves to localStorage via saveToStorage()

        return createdItem
      } catch (syncError) {
        // H6 FIX: Sync failed after create - rollback by deleting created item
        logger.error('Failed to sync store after item creation, rolling back', syncError)
        try {
          await this.gearItemApiService.deleteItem(createdItem.id)
        } catch (rollbackError) {
          logger.error('Rollback failed - data inconsistency detected', rollbackError)
        }
        throw syncError
      }
    } catch (error) {
      // Fallback to localStorage on API error or rollback failure
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.createItem(containerId, data)
    }
  }

  async getItems(containerId: TULID, skip = 0, limit = DEFAULT_PAGINATION_LIMIT): Promise<IGearItem[]> {
    try {
      const items = await this.gearItemApiService.getItems(containerId, skip, limit)
      // Refresh container from API
      const container = await gearContainerApiService.getContainer(containerId)
      useGearStore().updateContainer(container)
      return items
    } catch (error) {
      // Fallback to localStorage on API error
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.getItems(containerId, skip, limit)
    }
  }

  async updateItem(itemId: TULID, data: IUpdateItemDto): Promise<IGearItem> {
    const store = useGearStore()
    // CRITICAL FIX: Get container ID BEFORE update to prevent race condition
    const containerId = store.getContainerIdByItemId(itemId)

    if (!containerId) {
      logger.warn('Container not found for item, falling back to localStorage', itemId)
      return this.gearItemLocalService.updateItem(itemId, data)
    }

    // H6 FIX: Save previous item state for rollback
    const previousItem = store.getContainerById(containerId)?.items.find(item => item.id === itemId)

    try {
      // H6 FIX: Transaction boundary - Phase 1: Update item on API
      const updatedItem = await this.gearItemApiService.updateItem(itemId, data)

      try {
        // H6 FIX: Transaction boundary - Phase 2: Sync store with API
        const updatedContainer = await gearContainerApiService.getContainer(containerId)
        store.updateContainer(updatedContainer)
        // Store automatically saves to localStorage via saveToStorage()

        return updatedItem
      } catch (syncError) {
        // H6 FIX: Sync failed after update - rollback to previous state
        logger.error('Failed to sync store after item update, rolling back', syncError)
        if (previousItem) {
          try {
            await this.gearItemApiService.updateItem(itemId, previousItem)
          } catch (rollbackError) {
            logger.error('Rollback failed - data inconsistency detected', rollbackError)
          }
        }
        throw syncError
      }
    } catch (error) {
      // Fallback to localStorage on API error or rollback failure
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.updateItem(itemId, data)
    }
  }

  async deleteItem(itemId: TULID): Promise<void> {
    const store = useGearStore()
    // CRITICAL FIX: Get container ID BEFORE deletion to prevent race condition
    const containerId = store.getContainerIdByItemId(itemId)

    if (!containerId) {
      logger.warn('Container not found for item, falling back to localStorage', itemId)
      return this.gearItemLocalService.deleteItem(itemId)
    }

    // H6 FIX: Save deleted item for rollback
    const deletedItem = store.getContainerById(containerId)?.items.find(item => item.id === itemId)

    try {
      // H6 FIX: Transaction boundary - Phase 1: Delete item on API
      await this.gearItemApiService.deleteItem(itemId)

      try {
        // H6 FIX: Transaction boundary - Phase 2: Sync store with API
        const updatedContainer = await gearContainerApiService.getContainer(containerId)
        store.updateContainer(updatedContainer)

        // Also remove from localStorage backup
        this.gearItemLocalService.deleteItem(itemId).catch(err => {
          logger.warn('Failed to remove item from localStorage backup:', err)
        })
      } catch (syncError) {
        // H6 FIX: Sync failed after delete - rollback by recreating item
        logger.error('Failed to sync store after item deletion, rolling back', syncError)
        if (deletedItem) {
          try {
            await this.gearItemApiService.createItem(containerId, deletedItem)
          } catch (rollbackError) {
            logger.error('Rollback failed - data inconsistency detected', rollbackError)
          }
        }
        throw syncError
      }
    } catch (error) {
      // Fallback to localStorage on API error or rollback failure
      logger.warn('API failed, falling back to localStorage', error)
      await this.gearItemLocalService.deleteItem(itemId)
    }
  }

  async getItem(itemId: TULID): Promise<IGearItem> {
    return this.gearItemApiService.getItem(itemId)
  }

  async getItemFromContainer(containerId: TULID, itemId: TULID): Promise<IGearItem | undefined> {
    return this.gearItemApiService.getItemFromContainer(containerId, itemId)
  }

  /**
   * Update item and all its linked items
   *
   * For API mode, the backend automatically handles linked items,
   * so we just delegate to updateItem().
   * This method exists for interface compatibility with GearItemLocalService.
   *
   * @param itemId - ID of the item to update
   * @param data - Update data to apply
   * @returns The updated item
   */
  async updateLinkedItems(itemId: TULID, data: IUpdateItemDto): Promise<IGearItem> {
    // Backend automatically propagates changes to all linked items
    return this.updateItem(itemId, data)
  }

  // Batch update order
  async moveItem(itemId: TULID, targetContainerId: TULID): Promise<IGearItem> {
    const store = useGearStore()
    // CRITICAL FIX: Get container ID BEFORE move to prevent race condition
    const containerId = store.getContainerIdByItemId(itemId)

    if (!containerId) {
      logger.warn('Container not found for item, falling back to localStorage', itemId)
      return this.gearItemLocalService.moveItem(itemId, targetContainerId)
    }

    // H6 FIX: Save previous item state for rollback
    const previousItem = store.getContainerById(containerId)?.items.find(item => item.id === itemId)

    try {
      // H6 FIX: Transaction boundary - Phase 1: Move item on API
      const movedItem = await this.gearItemApiService.moveItem(itemId, targetContainerId)

      try {
        // H6 FIX: Transaction boundary - Phase 2: Sync both containers with API
        const sourceContainer = await gearContainerApiService.getContainer(containerId)
        const targetContainer = await gearContainerApiService.getContainer(targetContainerId)
        store.updateContainer(sourceContainer)
        store.updateContainer(targetContainer)
        // Store automatically saves to localStorage via saveToStorage()

        return movedItem
      } catch (syncError) {
        // H6 FIX: Sync failed after move - rollback by moving item back
        logger.error('Failed to sync store after item move, rolling back', syncError)
        if (previousItem) {
          try {
            await this.gearItemApiService.moveItem(itemId, containerId)
          } catch (rollbackError) {
            logger.error('Rollback failed - data inconsistency detected', rollbackError)
          }
        }
        throw syncError
      }
    } catch (error) {
      // Fallback to localStorage on API error or rollback failure
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.moveItem(itemId, targetContainerId)
    }
  }

  async batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]> {
    const store = useGearStore()
    // CRITICAL FIX: Get container ID BEFORE batch update to prevent race condition
    // Assume all items in batch belong to same container (standard practice)
    const containerId = items.length > 0 ? store.getContainerIdByItemId(items[0]!.id) : undefined

    if (!containerId) {
      logger.warn('Container not found for items, falling back to localStorage')
      return this.gearItemLocalService.batchUpdateOrder(items)
    }

    // H6 FIX: Save previous items state for rollback
    const container = store.getContainerById(containerId)
    const itemIds = new Set(items.map(item => item.id))
    const previousItems = container?.items.filter(item => itemIds.has(item.id)) ?? []

    try {
      // H6 FIX: Transaction boundary - Phase 1: Batch update on API
      const updatedItems = await this.gearItemApiService.batchUpdateOrder(items)

      try {
        // H6 FIX: Transaction boundary - Phase 2: Sync store with API
        const updatedContainer = await gearContainerApiService.getContainer(containerId)
        store.updateContainer(updatedContainer)
        // Store automatically saves to localStorage via saveToStorage()

        return updatedItems
      } catch (syncError) {
        // H6 FIX: Sync failed after batch update - rollback to previous state
        logger.error('Failed to sync store after batch update, rolling back', syncError)
        if (previousItems.length > 0) {
          try {
            await this.gearItemApiService.batchUpdateOrder(previousItems)
          } catch (rollbackError) {
            logger.error('Rollback failed - data inconsistency detected', rollbackError)
          }
        }
        throw syncError
      }
    } catch (error) {
      // Fallback to localStorage on API error or rollback failure
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.batchUpdateOrder(items)
    }
  }
}
