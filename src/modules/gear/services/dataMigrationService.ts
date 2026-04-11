import { logger } from '@/shared/utils/logger'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { mapParentContainerId, sortContainersByDependency } from '../utils/migrationHelpers'
import { validateContainerDto, validateItemDto } from '../utils/validation'
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'
import { gearItemApiService } from './gearItemApiService'

const STORAGE_KEY = 'gear-stack:containers'

/**
 * Check if there are containers in localStorage
 */
export function hasLocalData(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) return false

  try {
    const containers = JSON.parse(stored) as unknown[]
    return Array.isArray(containers) && containers.length > 0
  } catch {
    return false
  }
}

/**
 * Migrate data from localStorage to API
 * This is called after successful login when local data exists
 *
 * Strategy:
 * 1. Load containers from localStorage
 * 2. For each container, try to create it via API
 * 3. If container already exists (by name or other criteria), skip or update
 * 4. Update store with migrated containers
 *
 * @returns Promise that resolves when migration is complete
 */
export async function migrateLocalDataToAPI(): Promise<void> {
  const localContainers = await gearContainerLocalService.getAllContainers()

  if (localContainers.length === 0) {
    logger.info('No local data to migrate')
    return
  }

  logger.info(`Migrating ${localContainers.length} containers to API...`)

  // CRITICAL FIX: Sort containers by dependency to avoid orphaned containers
  // Make a deep copy to avoid modifying original containers during sorting
  const sortedContainers = sortContainersByDependency(localContainers.map(c => ({ ...c })))
  logger.info('Containers sorted by dependency order')

  const store = useGearStore()
  const migratedContainers: IGearContainer[] = []
  // Map old IDs to new IDs for parent reference updates
  const idMapping = new Map<string, string>()

  for (let i = 0; i < sortedContainers.length; i++) {
    const localContainer = sortedContainers[i]
    if (!localContainer) {
      logger.warn(`Container at index ${i} is undefined, skipping`)
      continue
    }
    try {
      // Create container via API
      // Note: We need to extract items first, as API expects separate creation
      const { items, ...containerData } = localContainer

      // CRITICAL FIX: Map old parent ID to new API-generated ID
      const parentContainerId = mapParentContainerId(
        containerData.parentContainerId,
        containerData,
        sortedContainers,
        i,
        idMapping,
      )

      // M6 FIX: Validate container data before service call
      const containerDto = createContainerDtoFromLocal(containerData, parentContainerId)

      // Create container without items first
      const createdContainer = await gearContainerApiService.createContainer(containerDto)

      // CRITICAL FIX: Store ID mapping for child containers
      idMapping.set(localContainer.id, createdContainer.id)

      // Create items for this container
      await migrateContainerItems(createdContainer.id, createdContainer.name, items)

      migratedContainers.push(createdContainer)
      logger.info(`Migrated container: ${createdContainer.name}`)
    } catch (error) {
      logger.error(`Failed to migrate container ${localContainer.name}:`, error)
      // Continue with other containers
    }
  }

  // Update store with migrated containers
  if (migratedContainers.length > 0) {
    // Fetch all containers from API to get complete data
    const allContainers = await gearContainerApiService.getContainers()
    store.setContainers(allContainers)
    logger.info(`Migration complete: ${migratedContainers.length} containers migrated`)
  }
}

/**
 * Create container DTO from local container data
 */
function createContainerDtoFromLocal(
  containerData: Omit<IGearContainer, 'items' | 'id' | 'createdAt' | 'updatedAt'>,
  parentContainerId: string | null,
) {
  return validateContainerDto({
    name: containerData.name,
    description: containerData.description,
    type: containerData.type,
    parentContainerId,
    maxWeight: containerData.maxWeight,
    maxWeightUnit: containerData.maxWeightUnit,
    weight: containerData.weight,
    weightUnit: containerData.weightUnit,
    color: containerData.color,
    brand: containerData.brand,
    price: containerData.price,
    url: containerData.url,
    hideWhenNested: containerData.hideWhenNested,
  })
}

/**
 * Migrate items for a container
 */
async function migrateContainerItems(
  containerId: string,
  containerName: string,
  items: IGearItem[],
): Promise<void> {
  if (!items || items.length === 0) {
    return
  }

  for (const item of items) {
    try {
      const itemDto = validateItemDto({
        name: item.name,
        category: item.category,
        quantity: item.quantity ?? 1,
        weight: item.weight ?? 0,
        weightUnit: item.weightUnit ?? 'g',
        status: item.status,
        notes: item.notes ?? undefined,
        expirationDate: item.expirationDate ?? undefined,
        priority: item.priority ?? 'medium',
        brand: item.brand ?? undefined,
        color: item.color ?? undefined,
        price: item.price ?? undefined,
        url: item.url ?? undefined,
        quality: item.quality ?? undefined,
        wearable: item.wearable ?? undefined,
        consumable: item.consumable ?? undefined,
      })

      await gearItemApiService.createItem(containerId, itemDto)
    } catch (itemError) {
      logger.warn(`Failed to migrate item ${item.name} for container ${containerName}:`, itemError)
      // Continue with other items
    }
  }
}

/**
 * Check if data should be migrated and prompt user
 * This is a helper that can be used in UI to show migration prompt
 */
export function shouldPromptForMigration(): boolean {
  return hasLocalData()
}

