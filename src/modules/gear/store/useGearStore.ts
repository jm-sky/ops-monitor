import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { CONTAINERS_STORAGE_KEY } from '@/shared/config/config'
import { logger } from '@/shared/utils/logger'
import type { IGearContainer } from '../types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

// H5 FIX: Helper for loading from localStorage (synchronous for backward compatibility)
function loadFromStorageSync(): IGearContainer[] {
  const stored = localStorage.getItem(CONTAINERS_STORAGE_KEY)
  if (stored) {
    try {
      const containers = JSON.parse(stored) as IGearContainer[]
      // Migration: Add default weightUnit for items that don't have it
      return containers.map(container => ({
        ...container,
        items: container.items.map(item => ({
          ...item,
          weightUnit: item.weightUnit ?? 'g',
        })),
      }))
    } catch (error) {
      logger.error('Error loading from storage:', error)
    }
  }
  return []
}

// H5 FIX: Asynchronous loading to avoid blocking main thread
// Uses queueMicrotask to defer parsing until after initial render
async function loadFromStorageAsync(): Promise<IGearContainer[]> {
  return new Promise((resolve) => {
    // Defer parsing to not block main thread during app initialization
    queueMicrotask(() => {
      resolve(loadFromStorageSync())
    })
  })
}

/**
 * Gear Store (Setup Style)
 *
 * M2 FIX: Converted from Options API to Setup style for consistency with useGearSettingsStore
 *
 * Benefits of Setup style:
 * - Better TypeScript inference
 * - More flexible composition
 * - Consistent with Vue 3 Composition API
 * - Matches pattern in useGearSettingsStore
 */
export const useGearStore = defineStore('gear', () => {
  // ========== State ==========
  const containers = ref<IGearContainer[]>([])
  const isInitialized = ref<boolean>(false)

  // ========== Getters (Computed) ==========

  /**
   * Get container by ID
   */
  const getContainerById = computed(() => {
    return (id: TUUID): IGearContainer | undefined => {
      return containers.value.find(c => c.id === id)
    }
  })

  /**
   * Get all containers
   */
  const getAllContainers = computed<IGearContainer[]>(() => {
    return containers.value
  })

  /**
   * Find container ID by item ID (O(n) lookup)
   */
  const getContainerIdByItemId = computed(() => {
    return (itemId: TUUID): TUUID | undefined => {
      for (const container of containers.value) {
        if (container.items.some(item => item.id === itemId)) {
          return container.id
        }
      }
      return undefined
    }
  })

  /**
   * Find container by item ID (returns full container)
   */
  const getContainerByItemId = computed(() => {
    return (itemId: TUUID): IGearContainer | undefined => {
      return containers.value.find(container =>
        container.items.some(item => item.id === itemId),
      )
    }
  })

  // ========== Actions ==========

  /**
   * Save containers to localStorage
   */
  function saveToStorage(): void {
    try {
      localStorage.setItem(CONTAINERS_STORAGE_KEY, JSON.stringify(containers.value))
    } catch (error) {
      logger.error('Error saving to storage:', error)
    }
  }

  /**
   * Set all containers (replaces current state)
   */
  function setContainers(newContainers: IGearContainer[]): void {
    containers.value = newContainers
    saveToStorage()
  }

  /**
   * Add a new container
   */
  function addContainer(container: IGearContainer): void {
    containers.value.push(container)
    saveToStorage()
  }

  /**
   * Update an existing container
   */
  function updateContainer(container: IGearContainer): void {
    const index = containers.value.findIndex(c => c.id === container.id)
    if (index !== -1) {
      containers.value[index] = container
      saveToStorage()
    }
  }

  /**
   * Remove a container by ID
   */
  function removeContainer(id: TUUID): void {
    containers.value = containers.value.filter(c => c.id !== id)
    saveToStorage()
  }

  /**
   * Clear all containers
   */
  function clearAllContainers(): void {
    containers.value = []
    saveToStorage()
  }

  /**
   * H5 FIX: Asynchronous initialization to avoid blocking main thread
   */
  async function initialize(): Promise<void> {
    if (isInitialized.value) return

    containers.value = await loadFromStorageAsync()
    isInitialized.value = true
  }

  /**
   * Synchronous loading (for backward compatibility, prefer initialize() for better performance)
   */
  function loadFromStorage(): void {
    containers.value = loadFromStorageSync()
    isInitialized.value = true
  }

  // ========== Return Public API ==========
  return {
    // State
    containers,
    isInitialized,

    // Getters
    getContainerById,
    getAllContainers,
    getContainerIdByItemId,
    getContainerByItemId,

    // Actions
    setContainers,
    addContainer,
    updateContainer,
    removeContainer,
    clearAllContainers,
    initialize,
    loadFromStorage,
    saveToStorage,
  }
})

