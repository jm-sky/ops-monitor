import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { GearItemApiService } from './gearItemApiService'
import { GearItemHybridService } from './gearItemHybridService'
import { GearItemLocalService } from './gearItemLocalService'

// Mock dependencies
vi.mock('./gearItemApiService')
vi.mock('./gearItemLocalService')
vi.mock('./gearContainerApiService')

describe('GearItemHybridService - CRITICAL FIX: Race Condition', () => {
  let service: GearItemHybridService
  let mockApiService: GearItemApiService
  let mockLocalService: GearItemLocalService

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()

    mockApiService = new GearItemApiService()
    mockLocalService = new GearItemLocalService()
    service = new GearItemHybridService(mockLocalService, mockApiService)
  })

  describe('updateItem - No Race Condition', () => {
    it('should find container before update to prevent race condition', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [
          {
            id: 'item-1',
            name: 'Test Item',
            category: 'tools',
            quantity: 1,
            weight: 100,
            weightUnit: 'g',
            priority: 'medium',
            status: 'owned',
            createdAt: '2024-01-01',
            updatedAt: '2024-01-01',
          },
        ],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const updatedItem: IGearItem = {
        ...mockContainer.items[0]!,
        name: 'Updated Item',
      }

      const store = useGearStore()
      store.addContainer(mockContainer)

      // Mock API calls
      vi.spyOn(mockApiService, 'updateItem').mockResolvedValue(updatedItem)
      vi.spyOn(gearContainerApiService, 'getContainer').mockResolvedValue({
        ...mockContainer,
        items: [updatedItem],
      })

      // Act
      const result = await service.updateItem('item-1', { name: 'Updated Item' })

      // Assert
      expect(result.name).toBe('Updated Item')
      // CRITICAL: Verify container was fetched using correct ID (not from loop)
      expect(gearContainerApiService.getContainer).toHaveBeenCalledWith('container-1')
    })

    it('should handle concurrent updates correctly (no race condition)', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [
          { id: 'item-1', name: 'Item 1', category: 'tools', quantity: 1, weight: 100, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
          { id: 'item-2', name: 'Item 2', category: 'tools', quantity: 1, weight: 200, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
        ],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const store = useGearStore()
      store.addContainer(mockContainer)

      vi.spyOn(mockApiService, 'updateItem')
        .mockResolvedValueOnce({ ...mockContainer.items[0]!, name: 'Updated Item 1' })
        .mockResolvedValueOnce({ ...mockContainer.items[1]!, name: 'Updated Item 2' })

      vi.spyOn(gearContainerApiService, 'getContainer').mockResolvedValue(mockContainer)

      // Act - Simulate concurrent updates
      const promise1 = service.updateItem('item-1', { name: 'Updated Item 1' })
      const promise2 = service.updateItem('item-2', { name: 'Updated Item 2' })

      await Promise.all([promise1, promise2])

      // Assert - CRITICAL: Both should refresh the same container (no race)
      expect(gearContainerApiService.getContainer).toHaveBeenCalledWith('container-1')
      // Should be called twice (once per update), but always with correct container ID
      expect(gearContainerApiService.getContainer).toHaveBeenCalledTimes(2)
    })

    it('should fallback to localStorage if container not found in store', async () => {
      // Arrange
      // Store is empty - item not found

      const localUpdateSpy = vi.spyOn(mockLocalService, 'updateItem').mockResolvedValue({
        id: 'item-1',
        name: 'Updated Item',
        category: 'tools',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      })

      // Act
      await service.updateItem('item-1', { name: 'Updated Item' })

      // Assert - Should fallback to localStorage
      expect(localUpdateSpy).toHaveBeenCalledWith('item-1', { name: 'Updated Item' })
    })
  })

  describe('deleteItem - No Race Condition', () => {
    it('should find container before deletion to prevent race condition', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [
          { id: 'item-1', name: 'Test Item', category: 'tools', quantity: 1, weight: 100, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
        ],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const store = useGearStore()
      store.addContainer(mockContainer)

      vi.spyOn(mockApiService, 'deleteItem').mockResolvedValue()
      vi.spyOn(gearContainerApiService, 'getContainer').mockResolvedValue({
        ...mockContainer,
        items: [],
      })
      vi.spyOn(mockLocalService, 'deleteItem').mockResolvedValue()

      // Act
      await service.deleteItem('item-1')

      // Assert - CRITICAL: Verify container was fetched using correct ID
      expect(gearContainerApiService.getContainer).toHaveBeenCalledWith('container-1')
    })
  })

  describe('batchUpdateOrder - No Race Condition', () => {
    it('should find container before batch update using first item', async () => {
      // Arrange
      const mockContainer: IGearContainer = {
        id: 'container-1',
        name: 'Test Container',
        items: [
          { id: 'item-1', name: 'Item 1', category: 'tools', quantity: 1, weight: 100, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
          { id: 'item-2', name: 'Item 2', category: 'tools', quantity: 1, weight: 200, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
        ],
        type: 'backpack',
        isPublic: false,
        favorite: false,
        userRatingCount: 0,
        createdAt: '2024-01-01',
        updatedAt: '2024-01-01',
      }

      const store = useGearStore()
      store.addContainer(mockContainer)

      vi.spyOn(mockApiService, 'batchUpdateOrder').mockResolvedValue(mockContainer.items)
      vi.spyOn(gearContainerApiService, 'getContainer').mockResolvedValue(mockContainer)

      // Act
      await service.batchUpdateOrder(mockContainer.items)

      // Assert - CRITICAL: Should use first item to find container
      expect(gearContainerApiService.getContainer).toHaveBeenCalledWith('container-1')
    })

    it('should fallback if container not found for batch items', async () => {
      // Arrange
      const items: IGearItem[] = [
        { id: 'item-1', name: 'Item 1', category: 'tools', quantity: 1, weight: 100, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
      ]

      // Store is empty
      const localBatchSpy = vi.spyOn(mockLocalService, 'batchUpdateOrder').mockResolvedValue(items)

      // Act
      await service.batchUpdateOrder(items)

      // Assert
      expect(localBatchSpy).toHaveBeenCalledWith(items)
    })
  })

  describe('Performance Improvement', () => {
    it('should use O(n) lookup instead of O(n²) loop search', async () => {
      // Arrange
      const containers: IGearContainer[] = []
      for (let i = 0; i < 100; i++) {
        containers.push({
          id: `container-${i}`,
          name: `Container ${i}`,
          items: [
            { id: `item-${i}`, name: `Item ${i}`, category: 'tools', quantity: 1, weight: 100, weightUnit: 'g', priority: 'medium', status: 'owned', createdAt: '2024-01-01', updatedAt: '2024-01-01' },
          ],
          type: 'backpack',
          isPublic: false,
          favorite: false,
          userRatingCount: 0,
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01',
        })
      }

      const store = useGearStore()
      store.setContainers(containers)

      // Mock API calls
      vi.spyOn(mockApiService, 'updateItem').mockResolvedValue(containers[99]!.items[0]!)
      vi.spyOn(gearContainerApiService, 'getContainer').mockResolvedValue(containers[99]!)

      const startTime = Date.now()

      // Act - Update item in last container
      await service.updateItem('item-99', { name: 'Updated' })

      const duration = Date.now() - startTime

      // Assert - Should be fast (no O(n²) loop)
      // With O(n) lookup, this should complete in <50ms even with 100 containers
      expect(duration).toBeLessThan(100)
      expect(gearContainerApiService.getContainer).toHaveBeenCalledWith('container-99')
    })
  })
})
