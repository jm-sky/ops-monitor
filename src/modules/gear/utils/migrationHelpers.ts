import { logger } from '@/shared/utils/logger'
import type { IGearContainer } from '../types/gear.types'
import { isValidULID, isValidUUID } from './validation'

/**
 * CRITICAL FIX: Sort containers by dependency order (topological sort)
 * This ensures parent containers are created before their children
 * Prevents circular dependency issues and orphaned containers
 */
export function sortContainersByDependency(containers: IGearContainer[]): IGearContainer[] {
  const sorted: IGearContainer[] = []
  const visited = new Set<string>()
  const visiting = new Set<string>() // For cycle detection

  function visit(container: IGearContainer): void {
    if (visited.has(container.id)) return

    // Detect circular dependencies
    if (visiting.has(container.id)) {
      logger.warn(`Circular dependency detected for container: ${container.name}`)
      // Break the cycle by setting parentContainerId to null
      container.parentContainerId = null
      return
    }

    visiting.add(container.id)

    // Visit parent first if it exists
    if (container.parentContainerId) {
      const parent = containers.find(c => c.id === container.parentContainerId)
      if (parent) {
        visit(parent)
      } else {
        // Parent not found - orphaned container, set parent to null
        logger.warn(`Parent container not found for ${container.name}, setting parent to null`)
        container.parentContainerId = null
      }
    }

    visiting.delete(container.id)
    visited.add(container.id)
    sorted.push(container)
  }

  // Visit all containers
  containers.forEach(container => visit(container))

  return sorted
}

/**
 * Check if an ID is in valid format (ULID or UUID)
 */
function isValidIdFormat(id: string): boolean {
  return isValidULID(id) || isValidUUID(id)
}

/**
 * Map old parent container ID to new API-generated ID
 * Handles various edge cases including orphaned containers, circular dependencies, and ID format validation
 *
 * @param parentContainerId - Original parent container ID from localStorage
 * @param containerData - Container data for logging purposes
 * @param sortedContainers - All containers sorted by dependency order
 * @param currentIndex - Current index in the sorted containers array
 * @param idMapping - Map of old IDs to new API-generated IDs
 * @returns Mapped parent container ID or null if mapping fails
 */
export function mapParentContainerId(
  parentContainerId: string | null | undefined,
  containerData: { name: string },
  sortedContainers: IGearContainer[],
  currentIndex: number,
  idMapping: Map<string, string>,
): string | null {
  if (!parentContainerId) {
    return null
  }

  const isValidId = isValidIdFormat(parentContainerId)

  // Case 1: Parent ID found in mapping - use mapped ID (this is the correct API-generated ID)
  if (idMapping.has(parentContainerId)) {
    const mappedId = idMapping.get(parentContainerId) ?? null
    if (mappedId && isValidIdFormat(mappedId)) {
      return mappedId
    }
    // Mapped ID is neither ULID nor UUID - this shouldn't happen in real scenarios
    // but could happen in tests with incorrect mocks
    logger.warn(`Mapped parent ID ${mappedId} for ${containerData.name} is not a valid ULID or UUID. Setting to null to avoid validation error.`)
    return null
  }

  // Case 2: Parent ID is not in mapping and not a valid format - this is an old localStorage ID
  if (!isValidId) {
    const parentIndex = sortedContainers.findIndex(c => c.id === parentContainerId)
    if (parentIndex === -1) {
      // Parent doesn't exist - already handled by sorting (should be null), but handle edge case
      logger.warn(`Parent container ${parentContainerId} not found in sorted containers. Setting parent to null for ${containerData.name}.`)
      return null
    }
    if (parentIndex < currentIndex) {
      // Parent should have been processed already - check if mapping exists for parent's old ID
      const parentContainer = sortedContainers[parentIndex]
      if (!parentContainer) {
        logger.warn(`Parent container at index ${parentIndex} is undefined. Setting parent to null for ${containerData.name}.`)
        return null
      }

      if (idMapping.has(parentContainer.id)) {
        // Parent was processed and mapping exists - use mapped ID
        const mappedId = idMapping.get(parentContainer.id) ?? null
        if (mappedId && isValidIdFormat(mappedId)) {
          return mappedId
        }
        logger.warn(`Mapped parent ID ${mappedId} for ${containerData.name} is not a valid ULID or UUID. Setting to null to avoid validation error.`)
        return null
      }
      // Parent was processed but mapping not set - parent may have failed to migrate
      logger.warn(`Parent container ${parentContainerId} was processed before ${containerData.name} (index ${parentIndex} < ${currentIndex}) but mapping not set. Parent may have failed to migrate. Setting parent to null.`)
      return null
    }
    // Parent comes after current container - this shouldn't happen with correct sorting
    logger.error(`Parent container ${parentContainerId} comes after ${containerData.name} in sorted order (index ${parentIndex} >= ${currentIndex}). Sorting may have failed. Setting parent to null.`)
    return null
  }

  // Case 3: Parent ID is a valid ULID/UUID but not in mapping - this shouldn't happen in normal flow
  // but could happen if ULID/UUID was passed directly. Check if parent exists in sorted containers.
  const parentIndex = sortedContainers.findIndex(c => c.id === parentContainerId)
  if (parentIndex === -1 || parentIndex >= currentIndex) {
    // Parent doesn't exist or comes after - set to null
    logger.warn(`Parent container ID ${parentContainerId} (ULID/UUID) not found or not yet processed. Setting parent to null for ${containerData.name}.`)
    return null
  }

  // Parent exists and comes before - should have been processed, but mapping not found
  // This is an edge case - return null to be safe
  logger.warn(`Parent container ID ${parentContainerId} (ULID/UUID) exists but mapping not found. Setting parent to null for ${containerData.name}.`)
  return null
}

