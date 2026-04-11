import { apiClient } from '@/shared/services/apiClient'
import type { IGearItemService } from '../types/gear.types'
import type {
  ICreateItemDto,
  IGearItem,
  IUpdateItemDto,
} from '@/modules/gear/types/gear.types'
import type { TULID } from '@/shared/types/base.type'

/**
 * Gear Item API Service
 *
 * Provides methods to interact with item API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
export class GearItemApiService implements IGearItemService {
  // Item operations
  async createItem(containerId: TULID, data: ICreateItemDto): Promise<IGearItem> {
    const response = await apiClient.post<IGearItem>(`/gear/containers/${containerId}/items`, data)
    return response.data
  }

  async getItems(containerId: TULID, skip = 0, limit = 100): Promise<IGearItem[]> {
    const response = await apiClient.get<IGearItem[]>(`/gear/containers/${containerId}/items`, {
      params: { skip, limit },
    })
    return response.data
  }

  async getAllItems(skip = 0, limit = 100): Promise<IGearItem[]> {
    const response = await apiClient.get<IGearItem[]>('/gear/items', {
      params: { skip, limit },
    })
    return response.data
  }

  async getItem(itemId: TULID): Promise<IGearItem> {
    const response = await apiClient.get<IGearItem>(`/gear/items/${itemId}`)
    return response.data
  }

  // TODO: Implement in backend
  async getItemFromContainer(containerId: TULID, itemId: TULID): Promise<IGearItem | undefined> {
    const response = await apiClient.get<IGearItem>(`/gear/containers/${containerId}/items/${itemId}`)
    return response.data
  }

  async updateItem(itemId: TULID, data: IUpdateItemDto): Promise<IGearItem> {
    // Axios automatically omits undefined, middleware converts empty strings to null
    // Backend handles all weight units (g, kg, oz, lb)
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}`, data)
    return response.data
  }

  async moveItem(itemId: TULID, targetContainerId: TULID): Promise<IGearItem> {
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}/move`, {
      targetContainerId,
    })
    return response.data
  }

  async deleteItem(itemId: TULID): Promise<void> {
    await apiClient.delete(`/gear/items/${itemId}`)
  }

  /**
   * Batch update items order
   * Updates multiple items' order field using batch API endpoint
   */
  async batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]> {
    if (items.length === 0) {
      return Promise.resolve([])
    }

    // Prepare batch request payload
    const batchRequest = {
      items: items.map(item => ({
        id: item.id,
        order: item.order ?? 0,
      })),
    }

    // Call batch endpoint
    const response = await apiClient.patch<IGearItem[]>('/gear/items/batch-order', batchRequest)
    return response.data
  }
}

export const gearItemApiService = new GearItemApiService()

