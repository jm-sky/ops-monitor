import { monitorService } from './monitorService'
import type { MonitorRuntimeConfig, SiteStatus, SnapshotType } from '@/modules/monitor/types'

export const monitorQueryKeys = {
  all: ['monitor'] as const,
  config: () => [...monitorQueryKeys.all, 'config'] as const,
  site: (siteId: string) => [...monitorQueryKeys.all, 'site', siteId] as const,
  siteStatuses: () => [...monitorQueryKeys.all, 'site-statuses'] as const,
  snapshots: (siteId: string, type: SnapshotType) =>
    [...monitorQueryKeys.all, 'snapshots', siteId, type] as const,
  snapshotsPage: (siteId: string, type: SnapshotType, limit: number, offset: number) =>
    [...monitorQueryKeys.all, 'snapshots-page', siteId, type, limit, offset] as const,
} as const

export async function fetchSiteStatuses(): Promise<SiteStatus[]> {
  return monitorService.listSiteStatuses()
}

export async function fetchMonitorConfig(): Promise<MonitorRuntimeConfig> {
  return monitorService.getConfig()
}
