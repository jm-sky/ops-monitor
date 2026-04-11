import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import { hasLocalData, migrateLocalDataToAPI } from './dataMigrationService'
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'
import { gearItemApiService } from './gearItemApiService'

// Helper to generate deterministic UUIDs for testing
function generateTestUUID(seed: string): string {
  // Simple hash function to generate consistent UUIDs for testing
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = ((hash << 5) - hash) + seed.charCodeAt(i)
    hash = hash & hash // Convert to 32bit integer
  }
  const hex = Math.abs(hash).toString(16).padStart(8, '0')
  // Format as UUID: 8-4-4-4-12
  return `${hex.slice(0, 8)}-${hex.slice(0, 4)}-${hex.slice(4, 8)}-${hex.slice(0, 4)}-${hex.slice(0, 12).padEnd(12, '0')}`
}

// Mock dependencies
vi.mock('./gearContainerApiService')
vi.mock('./gearContainerLocalService')
vi.mock('./gearItemApiService')

describe('dataMigrationService - CRITICAL FIX: Circular Dependencies', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Topological Sort - Dependency Order', () => {
    it('should migrate parent containers before children', async () => {
      // Arrange
      const childContainer: IGearContainer = {
        id: 'child-1',
        name: 'Child Container',
        parentContainerId: 'parent-1',
        items: [],
        type: 'pouch',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const parentContainer: IGearContainer = {
        id: 'parent-1',
        name: 'Parent Container',
        parentContainerId: null,
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      // Note: Child is listed BEFORE parent in localStorage (wrong order)
      const localContainers = [childContainer, parentContainer]

      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue(localContainers)

      const createContainerCalls: string[] = []
      vi.spyOn(gearContainerApiService, 'createContainer').mockImplementation(async (data) => {
        createContainerCalls.push(data.name)
        return {
          ...data,
          id: `api-${data.name}`,
          items: [],
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        } as IGearContainer
      })

      vi.spyOn(gearContainerApiService, 'getContainers').mockResolvedValue([])
      vi.spyOn(gearItemApiService, 'createItem').mockResolvedValue({} as unknown as IGearItem)

      // Act
      await migrateLocalDataToAPI()

      // Assert - CRITICAL: Parent should be created BEFORE child
      expect(createContainerCalls).toEqual(['Parent Container', 'Child Container'])
    })

    it('should handle deeply nested containers (3+ levels)', async () => {
      // Arrange
      const grandchild: IGearContainer = {
        id: 'grandchild-1',
        name: 'Grandchild',
        parentContainerId: 'child-1',
        items: [],
        type: 'pouch',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const child: IGearContainer = {
        id: 'child-1',
        name: 'Child',
        parentContainerId: 'parent-1',
        items: [],
        type: 'bag',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const parent: IGearContainer = {
        id: 'parent-1',
        name: 'Parent',
        parentContainerId: null,
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      // Scrambled order in localStorage
      const localContainers = [grandchild, parent, child]

      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue(localContainers)

      const createContainerCalls: string[] = []
      vi.spyOn(gearContainerApiService, 'createContainer').mockImplementation(async (data) => {
        createContainerCalls.push(data.name)
        return {
          ...data,
          id: `api-${data.name}`,
          items: [],
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        } as IGearContainer
      })

      vi.spyOn(gearContainerApiService, 'getContainers').mockResolvedValue([])
      vi.spyOn(gearItemApiService, 'createItem').mockResolvedValue({} as unknown as IGearItem)

      // Act
      await migrateLocalDataToAPI()

      // Assert - CRITICAL: Should create in dependency order
      expect(createContainerCalls).toEqual(['Parent', 'Child', 'Grandchild'])
    })
  })

  describe('Circular Dependency Detection', () => {
    it('should break circular dependencies by setting parent to null', async () => {
      // Arrange
      const container1: IGearContainer = {
        id: 'container-1',
        name: 'Container 1',
        parentContainerId: 'container-2', // Points to container 2
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const container2: IGearContainer = {
        id: 'container-2',
        name: 'Container 2',
        parentContainerId: 'container-1', // Points back to container 1 (CIRCULAR!)
        items: [],
        type: 'bag',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const localContainers = [container1, container2]

      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue(localContainers)

      const createContainerCalls: Array<{ name: string, parentId: string | null | undefined }> = []
      vi.spyOn(gearContainerApiService, 'createContainer').mockImplementation(async (data) => {
        createContainerCalls.push({ name: data.name, parentId: data.parentContainerId })
        return {
          ...data,
          id: `api-${data.name}`,
          items: [],
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        } as IGearContainer
      })

      vi.spyOn(gearContainerApiService, 'getContainers').mockResolvedValue([])
      vi.spyOn(gearItemApiService, 'createItem').mockResolvedValue({} as unknown as IGearItem)

      // Mock console.warn to verify warning is logged
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      // Act
      await migrateLocalDataToAPI()

      // Assert - CRITICAL: Circular dependency should be broken
      // At least one container should have parentId set to null
      const nullParents = createContainerCalls.filter(c => c.parentId === null)
      expect(nullParents.length).toBeGreaterThan(0)

      // Verify warning was logged
      expect(warnSpy).toHaveBeenCalledWith(expect.stringContaining('Circular dependency detected'))

      warnSpy.mockRestore()
    })
  })

  describe('Orphaned Containers', () => {
    it('should handle orphaned containers (parent does not exist)', async () => {
      // Arrange
      const orphanedContainer: IGearContainer = {
        id: 'orphan-1',
        name: 'Orphaned Container',
        parentContainerId: 'non-existent-parent', // Parent doesn't exist
        items: [],
        type: 'pouch',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const localContainers = [orphanedContainer]

      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue(localContainers)

      const createContainerCalls: Array<{ name: string, parentId: string | null | undefined }> = []
      vi.spyOn(gearContainerApiService, 'createContainer').mockImplementation(async (data) => {
        createContainerCalls.push({ name: data.name, parentId: data.parentContainerId })
        return {
          ...data,
          id: `api-${data.name}`,
          items: [],
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        } as IGearContainer
      })

      vi.spyOn(gearContainerApiService, 'getContainers').mockResolvedValue([])
      vi.spyOn(gearItemApiService, 'createItem').mockResolvedValue({} as unknown as IGearItem)

      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      // Act
      await migrateLocalDataToAPI()

      // Assert - CRITICAL: Orphaned container should have parent set to null
      expect(createContainerCalls).toEqual([
        { name: 'Orphaned Container', parentId: null },
      ])

      expect(warnSpy).toHaveBeenCalledWith(expect.stringContaining('Parent container not found'))

      warnSpy.mockRestore()
    })
  })

  describe('ID Mapping', () => {
    it('should map old localStorage IDs to new API IDs for parent references', async () => {
      // Arrange
      const parent: IGearContainer = {
        id: 'local-parent-id',
        name: 'Parent',
        parentContainerId: null,
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const child: IGearContainer = {
        id: 'local-child-id',
        name: 'Child',
        parentContainerId: 'local-parent-id', // Uses old localStorage ID
        items: [],
        type: 'pouch',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const localContainers = [child, parent]

      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue(localContainers)

      const createContainerCalls: Array<{ name: string, parentId: string | null | undefined }> = []
      vi.spyOn(gearContainerApiService, 'createContainer').mockImplementation(async (data) => {
        // Generate deterministic UUID based on name for testing
        const newId = generateTestUUID(`api-${data.name.toLowerCase()}`)
        createContainerCalls.push({ name: data.name, parentId: data.parentContainerId })
        return {
          ...data,
          id: newId, // API generates new UUID
          items: [],
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        } as IGearContainer
      })

      vi.spyOn(gearContainerApiService, 'getContainers').mockResolvedValue([])
      vi.spyOn(gearItemApiService, 'createItem').mockResolvedValue({} as unknown as IGearItem)

      // Act
      await migrateLocalDataToAPI()

      // Assert - CRITICAL: Child should reference new API parent ID, not old localStorage ID
      expect(createContainerCalls).toHaveLength(2)
      expect(createContainerCalls[0]).toEqual({ name: 'Parent', parentId: null })
      // Child should reference parent's new UUID (generated from 'api-parent')
      const parentApiId = generateTestUUID('api-parent')
      expect(createContainerCalls[1]).toEqual({ name: 'Child', parentId: parentApiId })
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty localStorage', async () => {
      // Arrange
      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue([])

      const createContainerSpy = vi.spyOn(gearContainerApiService, 'createContainer')

      // Act
      await migrateLocalDataToAPI()

      // Assert
      expect(createContainerSpy).not.toHaveBeenCalled()
    })

    it('should continue migration even if one container fails', async () => {
      // Arrange
      const container1: IGearContainer = {
        id: '1',
        name: 'Container 1',
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const container2: IGearContainer = {
        id: '2',
        name: 'Container 2',
        items: [],
        type: 'bag',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      vi.spyOn(gearContainerLocalService, 'getAllContainers').mockResolvedValue([container1, container2])

      const createCalls: string[] = []
      vi.spyOn(gearContainerApiService, 'createContainer').mockImplementation(async (data) => {
        createCalls.push(data.name)
        if (data.name === 'Container 1') {
          throw new Error('API error')
        }
        return {
          ...data,
          id: `api-${data.name}`,
          items: [],
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        } as IGearContainer
      })

      vi.spyOn(gearContainerApiService, 'getContainers').mockResolvedValue([])
      vi.spyOn(gearItemApiService, 'createItem').mockResolvedValue({} as unknown as IGearItem)

      const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Act
      await migrateLocalDataToAPI()

      // Assert - Should attempt both, even if first fails
      expect(createCalls).toEqual(['Container 1', 'Container 2'])
      expect(errorSpy).toHaveBeenCalled()

      errorSpy.mockRestore()
    })
  })

  describe('hasLocalData', () => {
    it('should return true if localStorage has containers', () => {
      // Arrange
      const containers: IGearContainer[] = [
        { id: '1', name: 'Test', items: [], type: 'backpack', isPublic: false, favorite: false, userRatingCount: 0, createdAt: '2024-01-01', updatedAt: '2024-01-01' },
      ]
      localStorage.setItem('gear-stack:containers', JSON.stringify(containers))

      // Act
      const result = hasLocalData()

      // Assert
      expect(result).toBe(true)
    })

    it('should return false if localStorage is empty', () => {
      // Act
      const result = hasLocalData()

      // Assert
      expect(result).toBe(false)
    })

    it('should return false if localStorage has invalid JSON', () => {
      // Arrange
      localStorage.setItem('gear-stack:containers', 'invalid json')

      // Act
      const result = hasLocalData()

      // Assert
      expect(result).toBe(false)
    })
  })
})
