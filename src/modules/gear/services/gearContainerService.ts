import { useBackend } from '@/shared/composables/useBackend'
import { logger } from '@/shared/utils/logger'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'

/**
 * Gear Container Service Factory
 *
 * Returns appropriate service based on backend status and authentication.
 * When backend is enabled AND user is authenticated, uses API service and synchronizes with store.
 * Otherwise, uses localStorage service.
 */
export const gearContainerService = () => {
  const { shouldUseAPI } = useBackend()
  
  if (shouldUseAPI.value) {
    // Wrap API service to sync store and localStorage as backup
    return {
      ...gearContainerApiService,
      async createContainer(data: Parameters<typeof gearContainerApiService.createContainer>[0]) {
        try {
          const container = await gearContainerApiService.createContainer(data)
          const store = useGearStore()
          store.addContainer(container)
          // Store automatically saves to localStorage via saveToStorage()
          return container
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.createContainer(data)
        }
      },
      async updateContainer(id: Parameters<typeof gearContainerApiService.updateContainer>[0], data: Parameters<typeof gearContainerApiService.updateContainer>[1]) {
        try {
          const container = await gearContainerApiService.updateContainer(id, data)
          const store = useGearStore()
          store.updateContainer(container)
          // Store automatically saves to localStorage via saveToStorage()
          return container
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.updateContainer(id, data)
        }
      },
      async deleteContainer(id: Parameters<typeof gearContainerApiService.deleteContainer>[0]) {
        const store = useGearStore()
        // Backup container data before deletion for potential rollback
        const containerBackup = store.getContainerById(id)

        let apiDeleteSucceeded = false

        try {
          // Phase 1: Delete from API
          await gearContainerApiService.deleteContainer(id)
          apiDeleteSucceeded = true

          try {
            // Phase 2: Delete from store (which also saves to localStorage)
            store.removeContainer(id)
          } catch (localError) {
            // CRITICAL: If localStorage deletion fails, we need to restore to API
            // This prevents data inconsistency between API and localStorage
            logger.critical('Failed to remove container from localStorage after API deletion', localError)

            if (containerBackup) {
              try {
                // Attempt to restore container to API
                await gearContainerApiService.createContainer({
                  name: containerBackup.name,
                  description: containerBackup.description,
                  type: containerBackup.type,
                  parentContainerId: containerBackup.parentContainerId,
                  maxWeight: containerBackup.maxWeight,
                  maxWeightUnit: containerBackup.maxWeightUnit,
                  weight: containerBackup.weight,
                  weightUnit: containerBackup.weightUnit,
                  color: containerBackup.color,
                  brand: containerBackup.brand,
                  price: containerBackup.price,
                  url: containerBackup.url,
                  hideWhenNested: containerBackup.hideWhenNested,
                })
                logger.warn('Container restored to API after localStorage deletion failure')
              } catch (restoreError) {
                logger.critical('Failed to restore container to API', restoreError)
                // At this point, data is lost from API but exists in localStorage
                // Throw error to notify user
                throw new Error('Data synchronization failed. Please refresh and try again.')
              }
            }

            throw localError
          }
        } catch (error) {
          // Only fallback to localStorage if API deletion failed
          // If API deletion succeeded but localStorage failed, re-throw the error
          if (!apiDeleteSucceeded) {
            logger.warn('API failed, falling back to localStorage', error)
            await gearContainerLocalService.deleteContainer(id)
          } else {
            // Re-throw localStorage/rollback errors
            throw error
          }
        }
      },
      async getContainers(skip = 0, limit = 100) {
        try {
          const containers = await gearContainerApiService.getContainers(skip, limit)
          useGearStore().setContainers(containers)
          return containers
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.getContainers(skip, limit)
        }
      },
      async getContainer(id: Parameters<typeof gearContainerApiService.getContainer>[0]) {
        try {
          const container = await gearContainerApiService.getContainer(id)
          const store = useGearStore()
          const existing = store.getContainerById(id)
          if (existing) {
            store.updateContainer(container)
          } else {
            store.addContainer(container)
          }
          return container
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.getContainer(id)
        }
      },
      // Delegate statistics methods
      getContainerWeight: gearContainerApiService.getContainerWeight.bind(gearContainerApiService),
      getContainerReadiness: gearContainerApiService.getContainerReadiness.bind(gearContainerApiService),
      // Add methods from local service that are not in API service
      async deleteAllContainers() {
        const store = useGearStore()
        // Backup all containers for potential rollback
        const containersBackup = [...store.getAllContainers]

        let apiDeleteSucceeded = false

        try {
          // Phase 1: Delete all from API
          await gearContainerApiService.deleteAllContainers()
          apiDeleteSucceeded = true

          try {
            // Phase 2: Clear store and localStorage
            store.clearAllContainers()
          } catch (localError) {
            // CRITICAL: If localStorage clear fails, restore to API
            logger.critical('Failed to clear localStorage after API deletion', localError)

            if (containersBackup.length > 0) {
              try {
                // Attempt to restore all containers to API
                for (const container of containersBackup) {
                  await gearContainerApiService.createContainer({
                    name: container.name,
                    description: container.description,
                    type: container.type,
                    parentContainerId: container.parentContainerId,
                    maxWeight: container.maxWeight,
                    maxWeightUnit: container.maxWeightUnit,
                    weight: container.weight,
                    weightUnit: container.weightUnit,
                    color: container.color,
                    brand: container.brand,
                    price: container.price,
                    url: container.url,
                    hideWhenNested: container.hideWhenNested,
                  })
                }
                logger.warn('Containers restored to API after localStorage clear failure')
              } catch (restoreError) {
                logger.critical('Failed to restore containers to API', restoreError)
                throw new Error('Data synchronization failed. Please refresh and try again.')
              }
            }

            throw localError
          }
        } catch (error) {
          // Only fallback to localStorage if API deletion failed
          // If API deletion succeeded but localStorage failed, re-throw the error
          if (!apiDeleteSucceeded) {
            logger.warn('API failed, falling back to localStorage', error)
            await gearContainerLocalService.deleteAllContainers()
          } else {
            // Re-throw localStorage/rollback errors
            throw error
          }
        }
      },
      getAllContainers: gearContainerLocalService.getAllContainers.bind(gearContainerLocalService),
      getRootContainers: gearContainerLocalService.getRootContainers.bind(gearContainerLocalService),
      getNestedContainers: gearContainerLocalService.getNestedContainers.bind(gearContainerLocalService),
      calculateTotalWeight: gearContainerLocalService.calculateTotalWeight.bind(gearContainerLocalService),
      calculateReadinessPercentage: gearContainerLocalService.calculateReadinessPercentage.bind(gearContainerLocalService),
      calculateWeightLimitPercentage: gearContainerLocalService.calculateWeightLimitPercentage.bind(gearContainerLocalService),
      isWeightLimitExceeded: gearContainerLocalService.isWeightLimitExceeded.bind(gearContainerLocalService),
      getItemsByStatus: gearContainerLocalService.getItemsByStatus.bind(gearContainerLocalService),
      getExpiredItems: gearContainerLocalService.getExpiredItems.bind(gearContainerLocalService),
      getExpiringSoonItems: gearContainerLocalService.getExpiringSoonItems.bind(gearContainerLocalService),
      moveItem: gearContainerLocalService.moveItem.bind(gearContainerLocalService),
      exportData: gearContainerLocalService.exportData.bind(gearContainerLocalService),
      importData: gearContainerLocalService.importData.bind(gearContainerLocalService),
      cloneContainer: gearContainerLocalService.cloneContainer.bind(gearContainerLocalService),
      // Item Catalog Operations
      getAllItemsForCatalog: gearContainerLocalService.getAllItemsForCatalog.bind(gearContainerLocalService),
      getItemWithContainer: gearContainerLocalService.getItemWithContainer.bind(gearContainerLocalService),
    }
  }

  return gearContainerLocalService
}

