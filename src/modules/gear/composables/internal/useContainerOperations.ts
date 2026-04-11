import { computed } from 'vue'
import type { ICreateContainerDto, IGearContainer, IUpdateContainerDto } from '../../types/gear.types'
import { gearContainerService } from '../../services/gearContainerService'
import { useGearStore } from '../../store/useGearStore'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Focused composable for container CRUD operations
 *
 * This composable is part of the refactored useGear.ts mega-composable.
 * It handles only container-related operations (create, read, update, delete).
 *
 * @internal - Use via useGear() facade for backward compatibility
 */
export function useContainerOperations() {
  const store = useGearStore()

  // Reactive state from store
  const containers = computed<IGearContainer[]>(() => store.getAllContainers)

  // ========== Container CRUD ==========

  const createContainer = async (data: ICreateContainerDto): Promise<IGearContainer> => {
    return await gearContainerService().createContainer(data)
  }

  const updateContainer = async (id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer> => {
    return await gearContainerService().updateContainer(id, data)
  }

  const deleteContainer = async (id: TUUID): Promise<void> => {
    await gearContainerService().deleteContainer(id)
  }

  const deleteAllContainers = async (): Promise<void> => {
    await gearContainerService().deleteAllContainers()
  }

  const getContainerById = async (id: TUUID): Promise<IGearContainer | undefined> => {
    try {
      return await gearContainerService().getContainer(id)
    } catch {
      return undefined
    }
  }

  const getRootContainers = async (): Promise<IGearContainer[]> => {
    return await gearContainerService().getRootContainers()
  }

  const getNestedContainers = async (containerId: TUUID): Promise<IGearContainer[]> => {
    return await gearContainerService().getNestedContainers(containerId)
  }

  return {
    containers,
    createContainer,
    updateContainer,
    deleteContainer,
    deleteAllContainers,
    getContainerById,
    getRootContainers,
    getNestedContainers,
  }
}
