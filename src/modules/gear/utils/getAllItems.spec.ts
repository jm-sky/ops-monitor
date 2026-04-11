import { describe, expect, it } from 'vitest'
import type { IGearContainer } from '../types/gear.types'
import { getAllItems } from './getAllItems'

describe('getAllItems', () => {
  const createMockContainer = (
    id: string,
    name: string,
    items: IGearContainer['items'] = [],
  ): IGearContainer => ({
    id,
    name,
    type: 'backpack',
    isPublic: false,
    favorite: false,
    items,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
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

  it('should return empty array for empty containers list', () => {
    const containers: IGearContainer[] = []
    const result = getAllItems(containers)
    expect(result).toEqual([])
  })

  it('should include container properties when container is added as item', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
    ])
    container.type = 'backpack'
    container.color = 'jeans'
    container.brand = 'Osprey'

    const result = getAllItems([container])

    const containerItem = result.find(item => item.isContainer === true)
    expect(containerItem).toBeDefined()
    expect(containerItem?.name).toBe('Backpack')
    expect(containerItem?.containerType).toBe('backpack')
    expect(containerItem?.containerColor).toBe('jeans')
    expect(containerItem?.brand).toBe('Osprey')
    expect(containerItem?.isContainer).toBe(true)
  })

  it('should return all items from single container (including container itself)', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
      createMockItem('item-2', 'Knife'),
    ])

    const result = getAllItems([container])

    expect(result).toHaveLength(3) // Container + 2 items
    // First item should be the container itself
    expect(result[0]?.name).toBe('Backpack')
    expect(result[0]?.isContainer).toBe(true)
    expect(result[0]?.containerId).toBe('container-1')
    expect(result[0]?.containerName).toBe('Backpack')
    // Then regular items
    expect(result[1]?.name).toBe('Water Bottle')
    expect(result[1]?.isContainer).toBe(false)
    expect(result[1]?.containerId).toBe('container-1')
    expect(result[2]?.name).toBe('Knife')
    expect(result[2]?.isContainer).toBe(false)
  })

  it('should return all items from multiple containers (including containers themselves)', () => {
    const container1 = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
    ])
    const container2 = createMockContainer('container-2', 'Pouch', [
      createMockItem('item-2', 'Knife'),
      createMockItem('item-3', 'Flashlight'),
    ])

    const result = getAllItems([container1, container2])

    expect(result).toHaveLength(5) // 2 containers + 3 items
    // First container
    expect(result[0]?.name).toBe('Backpack')
    expect(result[0]?.isContainer).toBe(true)
    expect(result[0]?.containerName).toBe('Backpack')
    // First container's items
    expect(result[1]?.name).toBe('Water Bottle')
    expect(result[1]?.isContainer).toBe(false)
    expect(result[1]?.containerName).toBe('Backpack')
    // Second container
    expect(result[2]?.name).toBe('Pouch')
    expect(result[2]?.isContainer).toBe(true)
    expect(result[2]?.containerName).toBe('Pouch')
    // Second container's items
    expect(result[3]?.name).toBe('Knife')
    expect(result[3]?.isContainer).toBe(false)
    expect(result[3]?.containerName).toBe('Pouch')
    expect(result[4]?.name).toBe('Flashlight')
    expect(result[4]?.isContainer).toBe(false)
    expect(result[4]?.containerName).toBe('Pouch')
  })

  it('should exclude items from specified container', () => {
    const container1 = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
    ])
    const container2 = createMockContainer('container-2', 'Pouch', [
      createMockItem('item-2', 'Knife'),
    ])

    const result = getAllItems([container1, container2], 'container-1')

    expect(result).toHaveLength(1)
    expect(result[0]?.name).toBe('Knife')
    expect(result[0]?.containerId).toBe('container-2')
  })

  it('should include all item properties', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle', {
        category: 'water',
        quantity: 2,
        weight: 500,
        weightUnit: 'g',
        status: 'owned',
        priority: 'high',
        brand: 'CamelBak',
        color: 'Black',
        expirationDate: '2025-12-31',
        wearable: false,
        consumable: true,
      }),
    ])

    const result = getAllItems([container])

    // Find the item (container is first, then items)
    const item = result.find(r => r.id === 'item-1')
    expect(item).toMatchObject({
      id: 'item-1',
      name: 'Water Bottle',
      category: 'water',
      containerId: 'container-1',
      containerName: 'Backpack',
      quantity: 2,
      weight: 500,
      weightUnit: 'g',
      status: 'owned',
      priority: 'high',
      brand: 'CamelBak',
      color: 'Black',
      expirationDate: '2025-12-31',
      wearable: false,
      consumable: true,
    })
  })

  it('should handle optional fields with defaults', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Item', {
        weightUnit: undefined,
        brand: null,
        color: null,
        expirationDate: null,
        wearable: null,
        consumable: null,
      }),
    ])

    const result = getAllItems([container])

    // Find the item (container is first, then items)
    const item = result.find(r => r.id === 'item-1')
    expect(item?.weightUnit).toBe('g') // Default
    expect(item?.brand).toBeUndefined()
    expect(item?.color).toBeUndefined()
    expect(item?.expirationDate).toBeUndefined()
    expect(item?.wearable).toBeUndefined()
    expect(item?.consumable).toBeUndefined()
  })

  it('should handle container color with default', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Item'),
    ])
    container.color = undefined

    const result = getAllItems([container])

    expect(result[0]?.containerColor).toBe('default')
  })

  it('should handle container with no items (still includes container itself)', () => {
    const container = createMockContainer('container-1', 'Empty Backpack', [])

    const result = getAllItems([container])

    expect(result).toHaveLength(1) // Container itself
    expect(result[0]?.name).toBe('Empty Backpack')
    expect(result[0]?.isContainer).toBe(true)
  })

  it('should preserve item order from containers', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'First'),
      createMockItem('item-2', 'Second'),
      createMockItem('item-3', 'Third'),
    ])

    const result = getAllItems([container])

    // Container is first, then items
    expect(result[0]?.name).toBe('Backpack') // Container first
    expect(result[1]?.name).toBe('First')
    expect(result[2]?.name).toBe('Second')
    expect(result[3]?.name).toBe('Third')
  })
})

