import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { IGearContainer, IUpdateContainerDto } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import {
  calculateReadinessPercentageSync,
  calculateTotalWeightSync,
} from '../utils/containerCalculations'
import { useGear } from './useGear'
import type { TUUID } from '@/shared/types/base.type'

export function useContainer(containerId?: TUUID) {
  const route = useRoute()
  const store = useGearStore()
  const { updateContainer, deleteContainer } = useGear()

  // Pobierz ID z route jeśli nie podano
  const id = computed<TUUID>(() => containerId ?? (route.params.id as string))

  // Container data - use store directly for synchronous access in computed
  const container = computed<IGearContainer | undefined>(() => {
    return store.getContainerById(id.value)
  })

  // Computed properties - use sync helpers for computed
  const totalWeight = computed<number>(() => {
    if (!container.value) return 0
    return calculateTotalWeightSync(container.value, store.getAllContainers)
  })

  const readinessPercentage = computed<number>(() => {
    if (!container.value) return 0
    return calculateReadinessPercentageSync(container.value)
  })

  const itemsCount = computed<number>(() => {
    return container.value?.items.length ?? 0
  })

  // Actions
  const update = async (data: IUpdateContainerDto): Promise<IGearContainer | undefined> => {
    if (!container.value) return undefined
    return await updateContainer(container.value.id, data)
  }

  const remove = async (): Promise<void> => {
    if (!container.value) return
    await deleteContainer(container.value.id)
  }

  return {
    container,
    totalWeight,
    readinessPercentage,
    itemsCount,
    update,
    remove,
  }
}

