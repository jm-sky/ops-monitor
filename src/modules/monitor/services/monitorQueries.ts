import { monitorService } from './monitorService'
import type { SiteStatus } from '@/modules/monitor/types'

export const monitorQueryKeys = {
  all: ['monitor'] as const,
  site: (siteId: string) => [...monitorQueryKeys.all, 'site', siteId] as const,
  siteStatuses: () => [...monitorQueryKeys.all, 'site-statuses'] as const,
} as const

export async function fetchSiteStatuses(): Promise<SiteStatus[]> {
  return monitorService.listSiteStatuses()
}
