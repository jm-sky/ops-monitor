import type { IItemWithContainer } from '../../utils/allItemsColumns'
import { gearContainerService } from '../../services/gearContainerService'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Focused composable for item catalog operations
 *
 * This composable is part of the refactored useGear.ts mega-composable.
 * It handles operations related to the global item catalog view.
 *
 * @internal - Use via useGear() facade for backward compatibility
 */
export function useItemCatalog() {
  const getAllItemsForCatalog = (excludeContainerId?: TUUID): IItemWithContainer[] => {
    return gearContainerService().getAllItemsForCatalog(excludeContainerId)
  }

  const getItemWithContainer = (itemId: TUUID): IItemWithContainer | undefined => {
    return gearContainerService().getItemWithContainer(itemId)
  }

  return {
    getAllItemsForCatalog,
    getItemWithContainer,
  }
}
