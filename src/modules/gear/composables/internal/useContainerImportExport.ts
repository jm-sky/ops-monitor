import type { IGearContainer } from '../../types/gear.types'
import { gearContainerService } from '../../services/gearContainerService'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Focused composable for container import/export operations
 *
 * This composable is part of the refactored useGear.ts mega-composable.
 * It handles JSON import/export and container cloning operations.
 *
 * @internal - Use via useGear() facade for backward compatibility
 */
export function useContainerImportExport() {
  const exportData = async (): Promise<string> => {
    return await gearContainerService().exportData()
  }

  const importData = async (json: string): Promise<void> => {
    await gearContainerService().importData(json)
  }

  const cloneContainer = async (
    containerId: TUUID,
    options: {
      newName: string
      includeNestedContainers?: boolean
      includePrices?: boolean
    },
  ): Promise<IGearContainer> => {
    return await gearContainerService().cloneContainer(containerId, options)
  }

  return {
    exportData,
    importData,
    cloneContainer,
  }
}
