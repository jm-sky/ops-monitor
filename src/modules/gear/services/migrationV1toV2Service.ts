/**
 * Migration utility from V1 to V2 unified model
 *
 * This service provides utilities to migrate data from the old dual-model structure
 * (IGearContainer + IGearItem) to the unified V2 model (IGearItemV2).
 *
 * Migration mapping:
 * - IGearContainer → IGearItemV2 (itemType='container')
 * - IGearItem → IGearItemV2 (itemType='item')
 * - parentContainerId → parentItemId
 * - containerId → parentItemId
 * - order → orderIndex
 * - nested containerId → REMOVED (legacy, unused)
 *
 * @module gear/services/migration
 */

import type { IGearContainer, IGearItem } from '../types/gear.types'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearStore } from '../store/useGearStore'
import { useGearStoreV2 } from '../store/useGearStoreV2'

export const migrationV1toV2Service = {
  /**
   * Convert V1 container to V2 item (itemType='container')
   */
  convertContainerToV2(container: IGearContainer): IGearItemV2 {
    return {
      id: container.id,
      userId: container.authorId || 'local-user',
      itemType: 'container',
      parentItemId: container.parentContainerId,

      // Common fields
      name: container.name,
      description: container.description,
      brand: container.brand,
      price: container.price,
      currency: container.currency,
      weight: container.weight,
      weightUnit: container.weightUnit,
      url: container.url,
      color: container.color,
      notes: undefined,

      // Container-specific
      containerType: container.type,
      maxWeight: container.maxWeight,
      maxWeightUnit: container.maxWeightUnit,
      hideWhenNested: container.hideWhenNested,
      isPublic: container.isPublic,
      favorite: container.favorite,
      showItemImages: container.showItemImages,

      // Container ratings
      ownerRating: container.ownerRating,
      userRating: container.userRating,
      averageUserRating: container.averageUserRating,
      userRatingCount: container.userRatingCount,

      // Container author
      authorName: container.authorName,
      authorId: container.authorId,

      // Item-specific (null for containers)
      category: undefined,
      quantity: undefined,
      status: undefined,
      priority: undefined,
      expirationDate: undefined,
      quality: undefined,
      wearable: undefined,
      consumable: undefined,
      orderIndex: undefined,
      showOnContainer: undefined,

      // Linking
      linkedItemId: undefined,
      catalogueItemId: undefined,

      // Metadata
      createdAt: container.createdAt,
      updatedAt: container.updatedAt,
    }
  },

  /**
   * Convert V1 item to V2 item (itemType='item')
   */
  convertItemToV2(item: IGearItem, containerId: string): IGearItemV2 {
    return {
      id: item.id,
      userId: 'local-user', // V1 items don't have userId
      itemType: 'item',
      parentItemId: containerId, // container_id → parent_item_id

      // Common fields
      name: item.name,
      description: undefined,
      brand: item.brand,
      price: item.price,
      currency: item.currency,
      weight: item.weight,
      weightUnit: item.weightUnit,
      url: item.url,
      color: item.color,
      notes: item.notes,

      // Container-specific (null for items)
      containerType: undefined,
      maxWeight: undefined,
      maxWeightUnit: undefined,
      hideWhenNested: undefined,
      isPublic: undefined,
      favorite: undefined,
      showItemImages: undefined,

      // Item-specific
      category: item.category,
      quantity: item.quantity,
      status: item.status,
      priority: item.priority,
      expirationDate: item.expirationDate,
      quality: item.quality,
      wearable: item.wearable,
      consumable: item.consumable,
      orderIndex: item.order, // order → orderIndex
      showOnContainer: item.showOnContainer,

      // Item image
      primaryImageUrl: item.primaryImageUrl,

      // Linking
      linkedItemId: item.linkedItemId,
      catalogueItemId: item.catalogueItemId,

      // Metadata
      createdAt: item.createdAt,
      updatedAt: item.updatedAt,
    }
  },

  /**
   * Perform full migration from V1 store to V2 store
   *
   * This will:
   * 1. Read all containers and items from V1 store
   * 2. Convert to V2 format
   * 3. Write to V2 store
   * 4. Preserve all data relationships
   */
  async performMigration(): Promise<{
    containersConverted: number
    itemsConverted: number
    total: number
  }> {
    const storeV1 = useGearStore()
    const storeV2 = useGearStoreV2()

    const containersV1 = storeV1.getAllContainers
    const itemsV2: IGearItemV2[] = []

    // Convert containers
    for (const container of containersV1) {
      itemsV2.push(this.convertContainerToV2(container))

      // Convert items in this container
      for (const item of container.items) {
        itemsV2.push(this.convertItemToV2(item, container.id))
      }
    }

    // Write to V2 store
    storeV2.setItems(itemsV2)

    return {
      containersConverted: containersV1.length,
      itemsConverted: itemsV2.length - containersV1.length,
      total: itemsV2.length,
    }
  },

  /**
   * Check if migration is needed
   *
   * Returns true if V1 store has data but V2 store is empty
   */
  isMigrationNeeded(): boolean {
    const storeV1 = useGearStore()
    const storeV2 = useGearStoreV2()

    const hasV1Data = storeV1.getAllContainers.length > 0
    const hasV2Data = storeV2.getAllItems.length > 0

    return hasV1Data && !hasV2Data
  },

  /**
   * Get migration summary (dry run)
   */
  getMigrationSummary(): {
    v1Containers: number
    v1Items: number
    v2ItemsTotal: number
  } {
    const storeV1 = useGearStore()
    const containersV1 = storeV1.getAllContainers

    let itemCount = 0
    for (const container of containersV1) {
      itemCount += container.items.length
    }

    return {
      v1Containers: containersV1.length,
      v1Items: itemCount,
      v2ItemsTotal: containersV1.length + itemCount,
    }
  },
}
