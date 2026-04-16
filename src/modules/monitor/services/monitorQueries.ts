import { monitorService } from './monitorService'
import type { SiteStatus } from '@/modules/monitor/types'

export const monitorQueryKeys = {
  all: ['monitor'] as const,
  site: (siteId: string) => [...monitorQueryKeys.all, 'site', siteId] as const,
  siteStatuses: () => [...monitorQueryKeys.all, 'site-statuses'] as const,
  snapshots: (siteId: string, type: 'health' | 'system') =>
    [...monitorQueryKeys.all, 'snapshots', siteId, type] as const,
  snapshotsPage: (siteId: string, type: 'health' | 'system', limit: number, offset: number) =>
    [...monitorQueryKeys.all, 'snapshots-page', siteId, type, limit, offset] as const,
} as const

export async function fetchSiteStatuses(): Promise<SiteStatus[]> {
  return monitorService.listSiteStatuses()
}
