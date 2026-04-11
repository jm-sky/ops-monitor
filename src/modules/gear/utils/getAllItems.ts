import { config } from '@/shared/config/config'
import type { IGearContainer } from '../types/gear.types'
import type { IItemWithContainer } from './allItemsColumns'
import { DEFAULT_ITEM_CATEGORY, DEFAULT_ITEM_COLOR, DEFAULT_ITEM_PRIORITY, DEFAULT_ITEM_STATUS } from './constants'
import { calculateTotalWeightSync } from './containerCalculations'
import { convertFromGrams } from './formatWeight'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Get all items from all containers with container information
 * Also includes containers themselves as items (containers are items too)
 * @param containers - Array of containers to search
 * @param excludeContainerId - Optional container ID to exclude from results
 */
export function getAllItems(containers: IGearContainer[], excludeContainerId?: TUUID): IItemWithContainer[] {
  const allItems: IItemWithContainer[] = []

  containers.forEach(container => {
    const isExcluded = excludeContainerId && container.id === excludeContainerId

    // Skip excluded container entirely
    if (isExcluded) {
      return
    }

    // When excluding a container, don't add any containers as items, only regular items
    // When not excluding, add container first, then items
    const shouldIncludeContainerAsItem = !excludeContainerId

    if (shouldIncludeContainerAsItem) {
      // Add container itself as an item (containers are items too)
      // Calculate total weight (container weight + all items weight) in grams
      const containerTotalWeightGrams = calculateTotalWeightSync(container, containers)
      // Use container's weight unit if set, otherwise use default from config
      const displayWeightUnit = container.weightUnit ?? config.defaults.preferredWeightUnit
      // Convert total weight from grams to display unit
      const displayWeight = convertFromGrams(containerTotalWeightGrams, displayWeightUnit)

      allItems.push({
        id: container.id,
        name: container.name,
        category: DEFAULT_ITEM_CATEGORY, // Containers use 'other' category
        containerId: container.id,
        containerName: container.name,
        containerColor: container.color ?? DEFAULT_ITEM_COLOR,
        quantity: 1,
        weight: displayWeight,
        weightUnit: displayWeightUnit,
        status: DEFAULT_ITEM_STATUS, // Containers are always owned
        priority: DEFAULT_ITEM_PRIORITY, // Default priority for containers
        brand: container.brand ?? undefined,
        color: undefined, // Containers don't have color field (they have containerColor)
        expirationDate: undefined,
        wearable: false,
        consumable: false,
        isContainer: true,
        containerType: container.type,
      })
    }

    // Add regular items from container
    container.items.forEach(item => {
      // Use container data from API if available, otherwise fallback to local container
      const containerInfo = item.container
      allItems.push({
        id: item.id,
        name: item.name,
        category: item.category,
        containerId: container.id,
        containerName: containerInfo?.name ?? container.name,
        containerColor: containerInfo?.color ?? container.color ?? DEFAULT_ITEM_COLOR,
        containerType: containerInfo?.type ?? container.type, // Add container type for regular items
        quantity: item.quantity,
        weight: item.weight,
        weightUnit: item.weightUnit ?? config.defaults.preferredWeightUnit,
        status: item.status,
        priority: item.priority,
        brand: item.brand ?? undefined,
        color: item.color ?? undefined,
        expirationDate: item.expirationDate ?? undefined,
        wearable: item.wearable ?? undefined,
        consumable: item.consumable ?? undefined,
        isContainer: false,
        primaryImageUrl: item.primaryImageUrl ?? undefined,
      })
    })
  })

  return allItems
}

