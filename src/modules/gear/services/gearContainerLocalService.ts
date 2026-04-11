import type {
  ICreateContainerDto,
  IGearContainer,
  IGearItem,
  IUpdateContainerDto,
  TGearItemStatus,
} from '../types/gear.types'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import { useGearStore } from '../store/useGearStore'
import {
  DEFAULT_PAGINATION_LIMIT,
  EXPIRATION_SOON_DAYS,
  GRAMS_PER_KILOGRAM,
  PERCENTAGE_MULTIPLIER,
} from '../utils/constants'
import {
  calculateReadinessPercentageSync,
  calculateTotalWeightSync,
  calculateWeightLimitPercentageSync,
} from '../utils/containerCalculations'
import { getAllNestedContainers, getRootContainers, wouldCreateCircularReference } from '../utils/containerNesting'
import { getAllItems } from '../utils/getAllItems'
import { isSet } from '../utils/helpers'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Gear Container Local Service (LocalStorage implementation)
 *
 * Provides methods to interact with container data stored in localStorage.
 * Pure implementation without feature flag logic.
 */
class GearContainerLocalService {
  private get store() {
    return useGearStore()
  }

  // ========== Containers CRUD ==========

  async createContainer(data: ICreateContainerDto): Promise<IGearContainer> {
    // Validate parent relationship if provided
    if (data.parentContainerId) {
      const allContainers = this.store.getAllContainers
      const newContainerId = crypto.randomUUID()

      if (wouldCreateCircularReference(newContainerId, data.parentContainerId, allContainers)) {
        throw new Error('Cannot create container: would create circular reference')
      }

      const parent = this.store.getContainerById(data.parentContainerId)
      if (!parent) {
        throw new Error(`Parent container with id ${data.parentContainerId} not found`)
      }
    }

    const now = new Date().toISOString()
    const container: IGearContainer = {
      id: data.id ?? crypto.randomUUID(), // Use provided UUID if available, otherwise generate new one
      name: data.name,
      description: data.description,
      type: data.type,
      color: data.color,
      parentContainerId: data.parentContainerId,
      isPublic: data.isPublic ?? false,
      favorite: data.favorite ?? false,
      authorName: null,
      brand: data.brand,
      price: data.price,
      weight: data.weight,
      weightUnit: data.weightUnit,
      url: data.url,
      items: [],
      createdAt: now,
      updatedAt: now,
    }

    this.store.addContainer(container)
    return Promise.resolve(container)
  }

  async updateContainer(id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer> {
    const container = this.store.getContainerById(id)
    if (!container) {
      throw new Error(`Container with id ${id} not found`)
    }

    if (data.parentContainerId !== undefined) {
      const allContainers = this.store.getAllContainers

      if (data.parentContainerId) {
        if (wouldCreateCircularReference(id, data.parentContainerId, allContainers)) {
          throw new Error('Cannot update container: would create circular reference')
        }

        const parent = this.store.getContainerById(data.parentContainerId)
        if (!parent) {
          throw new Error(`Parent container with id ${data.parentContainerId} not found`)
        }
      }
    }

    // Filter out null values and only include set fields
    const updateData: Partial<IGearContainer> = {}
    if (isSet(data.name)) updateData.name = data.name
    if (isSet(data.description)) updateData.description = data.description
    if (isSet(data.type)) updateData.type = data.type
    if (isSet(data.color)) updateData.color = data.color
    if (isSet(data.parentContainerId)) updateData.parentContainerId = data.parentContainerId
    if (isSet(data.hideWhenNested)) updateData.hideWhenNested = data.hideWhenNested
    if (isSet(data.isPublic)) updateData.isPublic = data.isPublic
    if (isSet(data.favorite)) updateData.favorite = data.favorite
    if (isSet(data.brand)) updateData.brand = data.brand
    if (isSet(data.price)) updateData.price = data.price
    if (isSet(data.weight)) updateData.weight = data.weight
    if (isSet(data.weightUnit)) updateData.weightUnit = data.weightUnit
    if (isSet(data.maxWeight)) updateData.maxWeight = data.maxWeight
    if (isSet(data.maxWeightUnit)) updateData.maxWeightUnit = data.maxWeightUnit
    if (isSet(data.url)) updateData.url = data.url

    const updated: IGearContainer = {
      ...container,
      ...updateData,
      updatedAt: new Date().toISOString(),
    }

    this.store.updateContainer(updated)
    return Promise.resolve(updated)
  }

  async deleteContainer(id: TUUID): Promise<void> {
    this.store.removeContainer(id)
    return Promise.resolve()
  }

  async getContainers(skip = 0, limit = DEFAULT_PAGINATION_LIMIT): Promise<IGearContainer[]> {
    const all = this.store.getAllContainers
    return Promise.resolve(all.slice(skip, skip + limit))
  }

  async getContainer(id: TUUID): Promise<IGearContainer> {
    const container = this.store.getContainerById(id)
    if (!container) {
      throw new Error(`Container with id ${id} not found`)
    }
    return Promise.resolve(container)
  }

  async deleteAllContainers(): Promise<void> {
    this.store.clearAllContainers()
    return Promise.resolve()
  }

  async getAllContainers(): Promise<IGearContainer[]> {
    return Promise.resolve(this.store.getAllContainers)
  }

  async getRootContainers(): Promise<IGearContainer[]> {
    return Promise.resolve(getRootContainers(this.store.getAllContainers))
  }

  async getNestedContainers(containerId: TUUID): Promise<IGearContainer[]> {
    return Promise.resolve(getAllNestedContainers(containerId, this.store.getAllContainers))
  }

  // ========== Statistics Operations ==========

  async getContainerWeight(containerId: TUUID): Promise<{ grams: number; kilograms: number }> {
    const grams = await this.calculateTotalWeight(containerId)
    return Promise.resolve({
      grams,
      kilograms: grams / GRAMS_PER_KILOGRAM,
    })
  }

  async getContainerReadiness(containerId: TUUID): Promise<{
    totalItems: number
    ownedItems: number
    missingItems: number
    toBuyItems: number
    readinessPercentage: number
  }> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const totalItems = container.items.length
    const ownedItems = container.items.filter(item => item.status === 'owned').length
    const missingItems = container.items.filter(item => item.status === 'missing').length
    const toBuyItems = container.items.filter(item => item.status === 'toBuy').length
    const readinessPercentage = totalItems > 0 ? Math.round((ownedItems / totalItems) * PERCENTAGE_MULTIPLIER) : 0

    return Promise.resolve({
      totalItems,
      ownedItems,
      missingItems,
      toBuyItems,
      readinessPercentage,
    })
  }

  // ========== Business Logic ==========

  /**
   * M3 FIX: Refactored to use centralized calculation utility
   * Delegates to calculateTotalWeightSync() from utils/containerCalculations.ts
   */
  async calculateTotalWeight(containerId: TUUID): Promise<number> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return Promise.resolve(0)
    }

    const allContainers = this.store.getAllContainers
    return Promise.resolve(calculateTotalWeightSync(container, allContainers))
  }

  /**
   * M3 FIX: Refactored to use centralized calculation utility
   * Delegates to calculateReadinessPercentageSync() from utils/containerCalculations.ts
   */
  async calculateReadinessPercentage(containerId: TUUID): Promise<number> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return 0
    }

    return Promise.resolve(calculateReadinessPercentageSync(container))
  }

  /**
   * M3 FIX: Refactored to use centralized calculation utility
   * Delegates to calculateWeightLimitPercentageSync() from utils/containerCalculations.ts
   */
  async calculateWeightLimitPercentage(containerId: TUUID): Promise<number | null> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return null
    }

    const allContainers = this.store.getAllContainers
    return Promise.resolve(calculateWeightLimitPercentageSync(container, allContainers))
  }

  async isWeightLimitExceeded(containerId: TUUID): Promise<boolean> {
    const percentage = await this.calculateWeightLimitPercentage(containerId)
    return Promise.resolve(percentage !== null && percentage > PERCENTAGE_MULTIPLIER)
  }

  async getItemsByStatus(containerId: TUUID, status: TGearItemStatus): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    return Promise.resolve(container.items.filter(item => item.status === status))
  }

  async getExpiredItems(containerId: TUUID): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    const now = new Date()

    return Promise.resolve(container.items.filter(item => {
      if (!item.expirationDate) {
        return false
      }

      const expirationDate = new Date(item.expirationDate)
      return expirationDate < now
    }))
  }

  async getExpiringSoonItems(containerId: TUUID, days: number = EXPIRATION_SOON_DAYS): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    const now = new Date()
    const futureDate = new Date()
    futureDate.setDate(now.getDate() + days)

    return Promise.resolve(container.items.filter(item => {
      if (!item.expirationDate) {
        return false
      }

      const expirationDate = new Date(item.expirationDate)
      return expirationDate >= now && expirationDate <= futureDate
    }))
  }

  async moveItem(containerId: TUUID, itemId: TUUID, newContainerId: TUUID): Promise<void> {
    const sourceContainer = this.store.getContainerById(containerId)
    const targetContainer = this.store.getContainerById(newContainerId)

    if (!sourceContainer || !targetContainer) {
      throw new Error('Source or target container not found')
    }

    const item = sourceContainer.items.find(i => i.id === itemId)
    if (!item) {
      throw new Error(`Item with id ${itemId} not found`)
    }

    const updatedSource: IGearContainer = {
      ...sourceContainer,
      items: sourceContainer.items.filter(i => i.id !== itemId),
      updatedAt: new Date().toISOString(),
    }

    const updatedTarget: IGearContainer = {
      ...targetContainer,
      items: [...targetContainer.items, item],
      updatedAt: new Date().toISOString(),
    }

    this.store.updateContainer(updatedSource)
    this.store.updateContainer(updatedTarget)
    return Promise.resolve()
  }

  // ========== Import/Export ==========

  async exportData(): Promise<string> {
    const containers = this.store.getAllContainers
    return Promise.resolve(JSON.stringify(containers, null, 2))
  }

  async importData(json: string): Promise<void> {
    try {
      const containers: IGearContainer[] = JSON.parse(json)
      if (!Array.isArray(containers)) {
        throw new Error('Invalid data format')
      }
      this.store.setContainers(containers)
      return Promise.resolve()
    } catch (error) {
      throw new Error(`Failed to import data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // ========== Clone/Duplicate ==========

  async cloneContainer(
    containerId: TUUID,
    options: {
      newName: string
      includeNestedContainers?: boolean
      includePrices?: boolean
    },
  ): Promise<IGearContainer> {
    const sourceContainer = this.store.getContainerById(containerId)
    if (!sourceContainer) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const { newName, includeNestedContainers = false, includePrices = true } = options

    const containerIdMap = new Map<TUUID, TUUID>()

    if (includeNestedContainers) {
      const containerIdsToClone = new Set<TUUID>()

      sourceContainer.items.forEach(item => {
        if (item.containerId) {
          containerIdsToClone.add(item.containerId)
        }
      })

      const findAllNestedContainers = (parentId: TUUID): void => {
        const nested = this.store.getContainerById(parentId)
        if (nested) {
          containerIdsToClone.add(parentId)
          nested.items.forEach(item => {
            if (item.containerId) {
              findAllNestedContainers(item.containerId)
            }
          })
        }
      }

      containerIdsToClone.forEach(id => {
        findAllNestedContainers(id)
      })

      const clonedNestedContainers: IGearContainer[] = []
      const clonedIds = new Set<TUUID>()

      const cloneNestedContainer = (oldContainerId: TUUID): void => {
        if (clonedIds.has(oldContainerId)) return

        const oldContainer = this.store.getContainerById(oldContainerId)
        if (!oldContainer) return

        oldContainer.items.forEach(item => {
          if (item.containerId && !clonedIds.has(item.containerId)) {
            cloneNestedContainer(item.containerId)
          }
        })

        const now = new Date().toISOString()
        const newContainerId = crypto.randomUUID()
        containerIdMap.set(oldContainerId, newContainerId)

        const clonedItems: IGearItem[] = oldContainer.items.map(oldItem => {
          const newItemId = crypto.randomUUID()
          const newItem: IGearItem = {
            ...oldItem,
            id: newItemId,
            price: includePrices ? oldItem.price : undefined,
            containerId: oldItem.containerId ? containerIdMap.get(oldItem.containerId) : undefined,
            createdAt: now,
            updatedAt: now,
          }
          return newItem
        })

        const clonedContainer: IGearContainer = {
          ...oldContainer,
          id: newContainerId,
          name: `[Kopia] ${oldContainer.name}`,
          parentContainerId: undefined,
          items: clonedItems,
          price: includePrices ? oldContainer.price : undefined,
          createdAt: now,
          updatedAt: now,
        }

        clonedNestedContainers.push(clonedContainer)
        clonedIds.add(oldContainerId)
      }

      containerIdsToClone.forEach(id => {
        cloneNestedContainer(id)
      })

      clonedNestedContainers.forEach(container => {
        this.store.addContainer(container)
      })
    }

    const now = new Date().toISOString()
    const newContainerId = crypto.randomUUID()

    const clonedItems: IGearItem[] = sourceContainer.items.map(oldItem => {
      const newItemId = crypto.randomUUID()
      const newItem: IGearItem = {
        ...oldItem,
        id: newItemId,
        price: includePrices ? oldItem.price : undefined,
        containerId:
          includeNestedContainers && oldItem.containerId
            ? containerIdMap.get(oldItem.containerId)
            : undefined,
        createdAt: now,
        updatedAt: now,
      }
      return newItem
    })

    const clonedContainer: IGearContainer = {
      ...sourceContainer,
      id: newContainerId,
      name: newName,
      parentContainerId: undefined,
      items: clonedItems,
      price: includePrices ? sourceContainer.price : undefined,
      createdAt: now,
      updatedAt: now,
    }

    this.store.addContainer(clonedContainer)
    return Promise.resolve(clonedContainer)
  }

  // ========== Item Catalog Operations ==========

  /**
   * Get all items from all containers for catalog/autocomplete
   * Excludes items from specified container
   * @param excludeContainerId - Container ID to exclude from results
   * @returns Array of items with container information, sorted alphabetically by name
   */
  getAllItemsForCatalog(excludeContainerId?: TUUID): IItemWithContainer[] {
    const containers = this.store.getAllContainers
    const allItems = getAllItems(containers, excludeContainerId)
    
    // Sort alphabetically by name
    return allItems.sort((a, b) => a.name.localeCompare(b.name))
  }

  /**
   * Get item by ID with container information
   * @param itemId - Item ID to find
   * @returns Item with container information, or undefined if not found
   */
  getItemWithContainer(itemId: TUUID): IItemWithContainer | undefined {
    const containers = this.store.getAllContainers
    const allItems = getAllItems(containers)
    return allItems.find(item => item.id === itemId)
  }
}

export const gearContainerLocalService = new GearContainerLocalService()

