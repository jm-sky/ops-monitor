import type { IGearItem } from '../../types/gear.types'
import { gearContainerService } from '../../services/gearContainerService'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Focused composable for container calculations
 *
 * This composable is part of the refactored useGear.ts mega-composable.
 * It handles calculations like weight, readiness, expiration checks.
 *
 * @internal - Use via useGear() facade for backward compatibility
 */
export function useContainerCalculations() {
  const calculateTotalWeight = async (containerId: TUUID): Promise<number> => {
    return await gearContainerService().calculateTotalWeight(containerId)
  }

  const calculateReadinessPercentage = async (containerId: TUUID): Promise<number> => {
    return await gearContainerService().calculateReadinessPercentage(containerId)
  }

  const calculateWeightLimitPercentage = async (containerId: TUUID): Promise<number | null> => {
    return await gearContainerService().calculateWeightLimitPercentage(containerId)
  }

  const isWeightLimitExceeded = async (containerId: TUUID): Promise<boolean> => {
    return await gearContainerService().isWeightLimitExceeded(containerId)
  }

  const getItemsByStatus = async (
    containerId: TUUID,
    status: 'owned' | 'missing' | 'toBuy',
  ): Promise<IGearItem[]> => {
    return await gearContainerService().getItemsByStatus(containerId, status)
  }

  const getExpiredItems = async (containerId: TUUID): Promise<IGearItem[]> => {
    return await gearContainerService().getExpiredItems(containerId)
  }

  const getExpiringSoonItems = async (containerId: TUUID, days: number = 30): Promise<IGearItem[]> => {
    return await gearContainerService().getExpiringSoonItems(containerId, days)
  }

  return {
    calculateTotalWeight,
    calculateReadinessPercentage,
    calculateWeightLimitPercentage,
    isWeightLimitExceeded,
    getItemsByStatus,
    getExpiredItems,
    getExpiringSoonItems,
  }
}
