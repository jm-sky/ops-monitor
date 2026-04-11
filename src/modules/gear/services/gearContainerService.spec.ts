import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearContainer } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'
import { gearContainerService } from './gearContainerService'

// Mock dependencies
vi.mock('@/shared/composables/useBackend')
vi.mock('./gearContainerApiService')
vi.mock('./gearContainerLocalService')

describe('gearContainerService - CRITICAL FIX: Data Consistency', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('deleteContainer - Two-Phase Commit', () => {
    it('should successfully delete from API and localStorage', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(useBackend).mockReturnValue({ shouldUseAPI: { value: true } } as any)

      const store = useGearStore()
      store.addContainer(mockContainer)

      const deleteApiSpy = vi.spyOn(gearContainerApiService, 'deleteContainer').mockResolvedValue()
      vi.spyOn(gearContainerLocalService, 'deleteContainer') // Spy setup for potential fallback

      // Act
      const service = gearContainerService()
      await service.deleteContainer('container-1')

      // Assert
      expect(deleteApiSpy).toHaveBeenCalledWith('container-1')
      expect(store.getContainerById('container-1')).toBeUndefined()
    })

    it('should rollback API deletion if localStorage fails', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(useBackend).mockReturnValue({ shouldUseAPI: { value: true } } as any)

      const store = useGearStore()
      store.addContainer(mockContainer)

      // Mock API deletion to succeed
      const deleteApiSpy = vi.spyOn(gearContainerApiService, 'deleteContainer').mockResolvedValue()

      // Mock createContainer for rollback
      const createApiSpy = vi.spyOn(gearContainerApiService, 'createContainer').mockResolvedValue(mockContainer)

      // Mock store.removeContainer to throw error (simulating localStorage failure)
      const originalRemoveContainer = store.removeContainer
      store.removeContainer = vi.fn().mockImplementation(() => {
        throw new Error('localStorage quota exceeded')
      })

      // Act & Assert
      const service = gearContainerService()
      await expect(service.deleteContainer('container-1')).rejects.toThrow('localStorage quota exceeded')

      // Verify rollback was attempted
      expect(deleteApiSpy).toHaveBeenCalledWith('container-1')
      expect(createApiSpy).toHaveBeenCalledWith(expect.objectContaining({
        name: 'Test Container',
        type: 'backpack',
      }))

      // Cleanup
      store.removeContainer = originalRemoveContainer
    })

    it('should throw user-friendly error if rollback fails', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(useBackend).mockReturnValue({ shouldUseAPI: { value: true } } as any)

      const store = useGearStore()
      store.addContainer(mockContainer)

      // Mock API deletion to succeed
      vi.spyOn(gearContainerApiService, 'deleteContainer').mockResolvedValue()

      // Mock createContainer to fail (rollback fails)
      vi.spyOn(gearContainerApiService, 'createContainer').mockRejectedValue(new Error('Network error'))

      // Mock store.removeContainer to throw error
      const originalRemoveContainer = store.removeContainer
      store.removeContainer = vi.fn().mockImplementation(() => {
        throw new Error('localStorage quota exceeded')
      })

      // Act & Assert
      const service = gearContainerService()
      await expect(service.deleteContainer('container-1')).rejects.toThrow('Data synchronization failed')

      // Cleanup
      store.removeContainer = originalRemoveContainer
    })
  })

  describe('deleteAllContainers - Two-Phase Commit', () => {
    it('should successfully delete all from API and localStorage', async () => {
      // Arrange
      const mockContainers: IGearContainer[] = [
        { id: '1', name: 'Container 1', items: [], type: 'backpack', isPublic: false, favorite: false, userRatingCount: 0, createdAt: '2024-01-01', updatedAt: '2024-01-01' },
        { id: '2', name: 'Container 2', items: [], type: 'bag', isPublic: false, favorite: false, userRatingCount: 0, createdAt: '2024-01-01', updatedAt: '2024-01-01' },
      ]

// eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(useBackend).mockReturnValue({ shouldUseAPI: { value: true } } as any)

      const store = useGearStore()
      store.setContainers(mockContainers)

      const deleteAllApiSpy = vi.spyOn(gearContainerApiService, 'deleteAllContainers').mockResolvedValue()

      // Act
      const service = gearContainerService()
      await service.deleteAllContainers()

      // Assert
      expect(deleteAllApiSpy).toHaveBeenCalled()
      expect(store.getAllContainers).toHaveLength(0)
    })

    it('should rollback API deletion if localStorage clear fails', async () => {
      // Arrange
      const mockContainers: IGearContainer[] = [
        { id: '1', name: 'Container 1', items: [], type: 'backpack', isPublic: false, favorite: false, userRatingCount: 0, createdAt: '2024-01-01', updatedAt: '2024-01-01' },
        { id: '2', name: 'Container 2', items: [], type: 'bag', isPublic: false, favorite: false, userRatingCount: 0, createdAt: '2024-01-01', updatedAt: '2024-01-01' },
      ]

// eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(useBackend).mockReturnValue({ shouldUseAPI: { value: true } } as any)

      const store = useGearStore()
      store.setContainers(mockContainers)

      // Mock API deletion to succeed
      const deleteAllApiSpy = vi.spyOn(gearContainerApiService, 'deleteAllContainers').mockResolvedValue()

      // Mock createContainer for rollback
      const createApiSpy = vi.spyOn(gearContainerApiService, 'createContainer')
        .mockResolvedValueOnce(mockContainers[0]!)
        .mockResolvedValueOnce(mockContainers[1]!)

      // Mock store.clearAllContainers to throw error
      const originalClearAll = store.clearAllContainers
      store.clearAllContainers = vi.fn().mockImplementation(() => {
        throw new Error('localStorage quota exceeded')
      })

      // Act & Assert
      const service = gearContainerService()
      await expect(service.deleteAllContainers()).rejects.toThrow('localStorage quota exceeded')

      // Verify rollback was attempted for all containers
      expect(deleteAllApiSpy).toHaveBeenCalled()
      expect(createApiSpy).toHaveBeenCalledTimes(2)

      // Cleanup
      store.clearAllContainers = originalClearAll
    })
  })

  describe('Fallback to localStorage on API error', () => {
    it('should fallback to localStorage if API fails', async () => {
      // Arrange
// eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(useBackend).mockReturnValue({ shouldUseAPI: { value: true } } as any)

      const store = useGearStore()
      store.addContainer({
        id: 'container-1',
        name: 'Test Container',
        items: [],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      })

      // Mock API to fail
      vi.spyOn(gearContainerApiService, 'deleteContainer').mockRejectedValue(new Error('Network error'))

      // Mock localStorage deletion to succeed
      const deleteLocalSpy = vi.spyOn(gearContainerLocalService, 'deleteContainer').mockResolvedValue()

      // Act
      const service = gearContainerService()
      await service.deleteContainer('container-1')

      // Assert
      expect(deleteLocalSpy).toHaveBeenCalledWith('container-1')
    })
  })
})
