import { ref } from 'vue'
import type { IGearItem, IUpdateItemDto } from '../types/gear.types'
import { useGear } from './useGear'

/**
 * Composable for inline item editing
 * Handles save on blur and Enter
 */
export function useInlineItemEditing(item: IGearItem) {
  const { updateItem } = useGear()
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Save function
  async function save(updates: IUpdateItemDto): Promise<IGearItem | null> {
    isLoading.value = true
    error.value = null

    try {
      const updated = await updateItem(item.id, updates)
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to update item')
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    save, // Save function for blur and Enter
  }
}

