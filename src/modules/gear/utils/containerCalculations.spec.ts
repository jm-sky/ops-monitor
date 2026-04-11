import { describe, expect, it } from 'vitest'
import type { IGearContainer } from '../types/gear.types'
import {
  calculateReadinessPercentageSync,
  calculateTotalWeightSync,
  calculateWeightLimitPercentageSync,
} from './containerCalculations'

describe('containerCalculations', () => {
  const createMockContainer = (
    id: string,
    name: string,
    overrides: Partial<IGearContainer> = {},
  ): IGearContainer => ({
    id,
    name,
    type: 'backpack',
    isPublic: false,
    favorite: false,
    items: [],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    ...overrides,
  })

  const createMockItem = (
    id: string,
    name: string,
    overrides: Partial<IGearContainer['items'][0]> = {},
  ): IGearContainer['items'][0] => ({
    id,
    name,
    category: 'other',
    quantity: 1,
    weight: 100,
    weightUnit: 'g',
    priority: 'medium',
    status: 'owned',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    ...overrides,
  })

  describe('calculateTotalWeightSync', () => {
    it('should return 0 for empty container', () => {
      const container = createMockContainer('container-1', 'Empty Container')
      const result = calculateTotalWeightSync(container, [])
      expect(result).toBe(0)
    })

    it('should calculate weight of container without items', () => {
      const container = createMockContainer('container-1', 'Container', {
        weight: 500,
        weightUnit: 'g',
      })
      const result = calculateTotalWeightSync(container, [])
      expect(result).toBe(500)
    })

    it('should calculate weight of container with items', () => {
      const container = createMockContainer('container-1', 'Container', {
        weight: 500,
        weightUnit: 'g',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 200, weightUnit: 'g' }),
          createMockItem('item-2', 'Item 2', { weight: 300, weightUnit: 'g' }),
        ],
      })
      const result = calculateTotalWeightSync(container, [])
      expect(result).toBe(1000) // 500 + 200 + 300
    })

    it('should handle items with quantity', () => {
      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Item 1', { weight: 100, weightUnit: 'g', quantity: 3 }),
        ],
      })
      const result = calculateTotalWeightSync(container, [])
      expect(result).toBe(300) // 100 * 3
    })

    it('should handle different weight units', () => {
      const container = createMockContainer('container-1', 'Container', {
        weight: 1,
        weightUnit: 'kg',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 500, weightUnit: 'g' }),
        ],
      })
      const result = calculateTotalWeightSync(container, [])
      expect(result).toBe(1500) // 1000g (1kg) + 500g
    })

    it('should handle nested containers', () => {
      const nestedContainer = createMockContainer('nested-1', 'Nested', {
        weight: 200,
        weightUnit: 'g',
        items: [
          createMockItem('nested-item-1', 'Nested Item', { weight: 100, weightUnit: 'g' }),
        ],
      })

      const container = createMockContainer('container-1', 'Container', {
        weight: 500,
        weightUnit: 'g',
        items: [
          createMockItem('item-1', 'Nested Container', {
            containerId: 'nested-1',
            weight: 0,
            weightUnit: 'g',
          }),
        ],
      })

      const result = calculateTotalWeightSync(container, [container, nestedContainer])
      // Container: 500g + nested container (200g + 100g) = 800g
      expect(result).toBe(800)
    })

    it('should handle nested containers with quantity', () => {
      const nestedContainer = createMockContainer('nested-1', 'Nested', {
        weight: 100,
        weightUnit: 'g',
        items: [
          createMockItem('nested-item-1', 'Nested Item', { weight: 50, weightUnit: 'g' }),
        ],
      })

      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Nested Container', {
            containerId: 'nested-1',
            weight: 0,
            weightUnit: 'g',
            quantity: 2,
          }),
        ],
      })

      const result = calculateTotalWeightSync(container, [container, nestedContainer])
      // Nested container: 100g + 50g = 150g, quantity 2 = 300g
      expect(result).toBe(300)
    })

    it('should handle container without weight', () => {
      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Item 1', { weight: 200, weightUnit: 'g' }),
        ],
      })
      const result = calculateTotalWeightSync(container, [])
      expect(result).toBe(200)
    })
  })

  describe('calculateReadinessPercentageSync', () => {
    it('should return 0 for empty container', () => {
      const container = createMockContainer('container-1', 'Empty Container')
      const result = calculateReadinessPercentageSync(container)
      expect(result).toBe(0)
    })

    it('should return 100 when all items are owned', () => {
      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Item 1', { status: 'owned' }),
          createMockItem('item-2', 'Item 2', { status: 'owned' }),
        ],
      })
      const result = calculateReadinessPercentageSync(container)
      expect(result).toBe(100)
    })

    it('should return 0 when no items are owned', () => {
      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Item 1', { status: 'missing' }),
          createMockItem('item-2', 'Item 2', { status: 'toBuy' }),
        ],
      })
      const result = calculateReadinessPercentageSync(container)
      expect(result).toBe(0)
    })

    it('should calculate percentage correctly', () => {
      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Item 1', { status: 'owned' }),
          createMockItem('item-2', 'Item 2', { status: 'owned' }),
          createMockItem('item-3', 'Item 3', { status: 'missing' }),
          createMockItem('item-4', 'Item 4', { status: 'toBuy' }),
        ],
      })
      const result = calculateReadinessPercentageSync(container)
      expect(result).toBe(50) // 2 out of 4 items owned
    })

    it('should round percentage correctly', () => {
      const container = createMockContainer('container-1', 'Container', {
        items: [
          createMockItem('item-1', 'Item 1', { status: 'owned' }),
          createMockItem('item-2', 'Item 2', { status: 'owned' }),
          createMockItem('item-3', 'Item 3', { status: 'owned' }),
        ],
      })
      const result = calculateReadinessPercentageSync(container)
      expect(result).toBe(100) // 3 out of 3 items owned
    })
  })

  describe('calculateWeightLimitPercentageSync', () => {
    it('should return null when no weight limit is set', () => {
      const container = createMockContainer('container-1', 'Container')
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBeNull()
    })

    it('should return 0 when weight limit is 0', () => {
      const container = createMockContainer('container-1', 'Container', {
        maxWeight: 0,
        maxWeightUnit: 'g',
      })
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBe(0)
    })

    it('should calculate percentage correctly', () => {
      const container = createMockContainer('container-1', 'Container', {
        maxWeight: 1000,
        maxWeightUnit: 'g',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 500, weightUnit: 'g' }),
        ],
      })
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBe(50) // 500g / 1000g = 50%
    })

    it('should return 100 when at weight limit', () => {
      const container = createMockContainer('container-1', 'Container', {
        maxWeight: 1000,
        maxWeightUnit: 'g',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 1000, weightUnit: 'g' }),
        ],
      })
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBe(100)
    })

    it('should return over 100 when exceeding weight limit', () => {
      const container = createMockContainer('container-1', 'Container', {
        maxWeight: 1000,
        maxWeightUnit: 'g',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 1500, weightUnit: 'g' }),
        ],
      })
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBe(150) // 1500g / 1000g = 150%
    })

    it('should handle different weight units', () => {
      const container = createMockContainer('container-1', 'Container', {
        maxWeight: 1,
        maxWeightUnit: 'kg',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 500, weightUnit: 'g' }),
        ],
      })
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBe(50) // 500g / 1000g (1kg) = 50%
    })

    it('should include container weight in calculation', () => {
      const container = createMockContainer('container-1', 'Container', {
        weight: 200,
        weightUnit: 'g',
        maxWeight: 1000,
        maxWeightUnit: 'g',
        items: [
          createMockItem('item-1', 'Item 1', { weight: 300, weightUnit: 'g' }),
        ],
      })
      const result = calculateWeightLimitPercentageSync(container, [])
      expect(result).toBe(50) // (200g + 300g) / 1000g = 50%
    })

    it('should handle nested containers in weight calculation', () => {
      const nestedContainer = createMockContainer('nested-1', 'Nested', {
        weight: 100,
        weightUnit: 'g',
        items: [
          createMockItem('nested-item-1', 'Nested Item', { weight: 200, weightUnit: 'g' }),
        ],
      })

      const container = createMockContainer('container-1', 'Container', {
        maxWeight: 1000,
        maxWeightUnit: 'g',
        items: [
          createMockItem('item-1', 'Nested Container', {
            containerId: 'nested-1',
            weight: 0,
            weightUnit: 'g',
          }),
        ],
      })

      const result = calculateWeightLimitPercentageSync(container, [container, nestedContainer])
      // Nested container: 100g + 200g = 300g, limit 1000g = 30%
      expect(result).toBe(30)
    })
  })
})

