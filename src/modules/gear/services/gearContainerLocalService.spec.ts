import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import type { ICreateContainerDto } from '../types/gear.types'
import { gearContainerLocalService } from './gearContainerLocalService'

describe('gearContainerLocalService - UUID support', () => {
  beforeEach(() => {
    // Reset Pinia store before each test
    setActivePinia(createPinia())
  })

  describe('createContainer with UUID', () => {
    it('should use provided UUID when creating container', async () => {
      const customUuid = '123e4567-e89b-12d3-a456-426614174000'
      const containerData: ICreateContainerDto = {
        id: customUuid,
        name: 'Test Container',
        type: 'backpack',
      }

      const container = await gearContainerLocalService.createContainer(containerData)

      expect(container.id).toBe(customUuid)
      expect(container.name).toBe('Test Container')
    })

    it('should generate new UUID when UUID is not provided', async () => {
      const containerData: ICreateContainerDto = {
        name: 'Test Container',
        type: 'backpack',
      }

      const container = await gearContainerLocalService.createContainer(containerData)

      expect(container.id).toBeTruthy()
      expect(container.id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)
      expect(container.name).toBe('Test Container')
    })

    it('should generate new UUID when UUID is null', async () => {
      const containerData: ICreateContainerDto = {
        id: null,
        name: 'Test Container',
        type: 'backpack',
      }

      const container = await gearContainerLocalService.createContainer(containerData)

      expect(container.id).toBeTruthy()
      expect(container.id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)
      expect(container.name).toBe('Test Container')
    })

    it('should preserve UUID when creating container with all fields', async () => {
      const customUuid = '987fcdeb-51a2-43b1-9c4d-5e6f7a8b9c0d'
      const containerData: ICreateContainerDto = {
        id: customUuid,
        name: 'Full Container',
        type: 'backpack',
        description: 'Test description',
        color: 'jeans' as const,
        brand: 'Test Brand',
        price: 100,
        weight: 2000,
        weightUnit: 'g',
        url: 'https://example.com',
      }

      const container = await gearContainerLocalService.createContainer(containerData)

      expect(container.id).toBe(customUuid)
      expect(container.name).toBe('Full Container')
      expect(container.description).toBe('Test description')
      expect(container.color).toBe('jeans')
      expect(container.brand).toBe('Test Brand')
      expect(container.price).toBe(100)
      expect(container.weight).toBe(2000)
      expect(container.weightUnit).toBe('g')
      expect(container.url).toBe('https://example.com')
    })

    it('should create multiple containers with provided UUIDs', async () => {
      const uuid1 = '11111111-1111-1111-1111-111111111111'
      const uuid2 = '22222222-2222-2222-2222-222222222222'

      const container1 = await gearContainerLocalService.createContainer({
        id: uuid1,
        name: 'Container 1',
        type: 'backpack',
      })

      const container2 = await gearContainerLocalService.createContainer({
        id: uuid2,
        name: 'Container 2',
        type: 'bag',
      })

      expect(container1.id).toBe(uuid1)
      expect(container2.id).toBe(uuid2)
      expect(container1.id).not.toBe(container2.id)
    })
  })
})
