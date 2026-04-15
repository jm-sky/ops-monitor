import { apiClient } from '@/shared/services/apiClient'
import type { Site, SiteCreate, SiteSnapshot, SiteStatus, SiteUpdate } from '@/modules/monitor/types'

class MonitorService {
  async listSites(): Promise<Site[]> {
    const response = await apiClient.get<Site[]>('/monitor/sites')
    return response.data
  }

  async listSiteStatuses(): Promise<SiteStatus[]> {
    const response = await apiClient.get<SiteStatus[]>('/monitor/site-statuses')
    return response.data
  }

  async getSite(id: string): Promise<SiteStatus> {
    const response = await apiClient.get<SiteStatus>(`/monitor/sites/${id}`)
    return response.data
  }

  async createSite(data: SiteCreate): Promise<Site> {
    const response = await apiClient.post<Site>('/monitor/sites', data)
    return response.data
  }

  async updateSite(id: string, data: SiteUpdate): Promise<Site> {
    const response = await apiClient.put<Site>(`/monitor/sites/${id}`, data)
    return response.data
  }

  async deleteSite(id: string): Promise<void> {
    await apiClient.delete(`/monitor/sites/${id}`)
  }

  async getSnapshots(siteId: string, type: 'health' | 'system', limit = 100): Promise<SiteSnapshot[]> {
    const response = await apiClient.get<SiteSnapshot[]>(
      `/monitor/sites/${siteId}/snapshots/${type}`,
      { params: { limit } },
    )
    return response.data
  }

  async pollNow(siteId: string): Promise<void> {
    await apiClient.post(`/monitor/sites/${siteId}/poll`)
  }
}

export const monitorService = new MonitorService()
