import { apiClient } from '@/shared/services/apiClient'
import type { AlertChannel, AlertChannelCreate, AlertChannelUpdate, AlertEvent } from '../types/alerts'

class AlertChannelService {
  async list(): Promise<AlertChannel[]> {
    const response = await apiClient.get<AlertChannel[]>('/monitor/alert-channels')
    return response.data
  }

  async create(data: AlertChannelCreate): Promise<AlertChannel> {
    const response = await apiClient.post<AlertChannel>('/monitor/alert-channels', data)
    return response.data
  }

  async update(id: string, data: AlertChannelUpdate): Promise<AlertChannel> {
    const response = await apiClient.put<AlertChannel>(`/monitor/alert-channels/${id}`, data)
    return response.data
  }

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/monitor/alert-channels/${id}`)
  }

  async test(id: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      `/monitor/alert-channels/${id}/test`,
    )
    return response.data
  }

  async getAlertEvents(options?: { siteId?: string; limit?: number }): Promise<AlertEvent[]> {
    const response = await apiClient.get<AlertEvent[]>('/monitor/alert-events', {
      params: {
        ...(options?.siteId && { site_id: options.siteId }),
        ...(options?.limit && { limit: options.limit }),
      },
    })
    return response.data
  }
}

export const alertChannelService = new AlertChannelService()
