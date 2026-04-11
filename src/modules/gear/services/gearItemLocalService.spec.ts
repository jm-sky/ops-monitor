import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import type { ICreateItemDto } from '../types/gear.types'
import { gearContainerLocalService } from './gearContainerLocalService'
import { gearItemLocalService } from './gearItemLocalService'

describe('gearItemLocalService - UUID support', () => {
  let containerId: string

  beforeEach(async () => {
    // Reset Pinia store before each test
    setActivePinia(createPinia())

    // Create a container for testing
    const container = await gearContainerLocalService.createContainer({
      name: 'Test Container',
      type: 'backpack',
    })
    containerId = container.id
  })

  describe('createItem with UUID', () => {
    it('should use provided UUID when creating item', async () => {
      const customUuid = '123e4567-e89b-12d3-a456-426614174000'
      const itemData: ICreateItemDto = {
        id: customUuid,
        name: 'Test Item',
        category: 'tools',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const item = await gearItemLocalService.createItem(containerId, itemData)

      expect(item.id).toBe(customUuid)
      expect(item.name).toBe('Test Item')
    })

    it('should generate new UUID when UUID is not provided', async () => {
      const itemData: ICreateItemDto = {
        name: 'Test Item',
        category: 'tools',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const item = await gearItemLocalService.createItem(containerId, itemData)

      expect(item.id).toBeTruthy()
      expect(item.id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)
      expect(item.name).toBe('Test Item')
    })

    it('should generate new UUID when UUID is null', async () => {
      const itemData: ICreateItemDto = {
        id: null,
        name: 'Test Item',
        category: 'tools',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const item = await gearItemLocalService.createItem(containerId, itemData)

      expect(item.id).toBeTruthy()
      expect(item.id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)
      expect(item.name).toBe('Test Item')
    })

    it('should preserve UUID when creating item with all fields', async () => {
      const customUuid = '987fcdeb-51a2-43b1-9c4d-5e6f7a8b9c0d'
      const itemData: ICreateItemDto = {
        id: customUuid,
        name: 'Full Item',
        category: 'tools',
        quantity: 2,
        weight: 200,
        weightUnit: 'g',
        priority: 'high',
        status: 'toBuy',
        brand: 'Test Brand',
        color: 'Black',
        price: 50,
        currency: 'PLN',
        url: 'https://example.com/item',
        notes: 'Test notes',
        wearable: true,
        consumable: false,
      }

      const item = await gearItemLocalService.createItem(containerId, itemData)

      expect(item.id).toBe(customUuid)
      expect(item.name).toBe('Full Item')
      expect(item.category).toBe('tools')
      expect(item.quantity).toBe(2)
      expect(item.weight).toBe(200)
      expect(item.weightUnit).toBe('g')
      expect(item.priority).toBe('high')
      expect(item.status).toBe('toBuy')
      expect(item.brand).toBe('Test Brand')
      expect(item.color).toBe('Black')
      expect(item.price).toBe(50)
      expect(item.url).toBe('https://example.com/item')
      expect(item.notes).toBe('Test notes')
      expect(item.wearable).toBe(true)
      expect(item.consumable).toBe(false)
    })

    it('should create multiple items with provided UUIDs', async () => {
      const uuid1 = '11111111-1111-1111-1111-111111111111'
      const uuid2 = '22222222-2222-2222-2222-222222222222'

      const item1 = await gearItemLocalService.createItem(containerId, {
        id: uuid1,
        name: 'Item 1',
        category: 'tools',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      })

      const item2 = await gearItemLocalService.createItem(containerId, {
        id: uuid2,
        name: 'Item 2',
        category: 'tools',
        quantity: 1,
        weight: 200,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      })

      expect(item1.id).toBe(uuid1)
      expect(item2.id).toBe(uuid2)
      expect(item1.id).not.toBe(item2.id)
    })
  })
})
