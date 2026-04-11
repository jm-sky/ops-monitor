import { useBackend } from '@/shared/composables/useBackend'
import { gearItemApiService } from './gearItemApiService'
import { GearItemHybridService } from './gearItemHybridService'
import { GearItemLocalService, gearItemLocalService } from './gearItemLocalService'

/**
 * Gear Item Service Factory
 *
 * Returns appropriate service based on backend status and authentication.
 * When backend is enabled AND user is authenticated, uses API service and synchronizes with store.
 * Otherwise, uses localStorage service.
 */
export const gearItemService = (): GearItemLocalService | GearItemHybridService => {
  const { shouldUseAPI } = useBackend()
  
  if (shouldUseAPI.value) {
    // Wrap API service to sync store and localStorage as backup
    return new GearItemHybridService(gearItemLocalService, gearItemApiService)
  }

  return gearItemLocalService
}

