export interface Site {
  id: string
  name: string
  description: string | null
  healthUrl: string | null
  systemUrl: string | null
  token: string | null
  enabled: boolean
  pollingHealth: number
  pollingSystem: number
  pollingUpdates: number
  pollingReboot: number
  teamsWebhookUrl: string | null
  serverLabel: string | null
  verifySSL: boolean
  createdAt: string
  updatedAt: string
}

export interface SiteSnapshot {
  id: string
  siteId: string
  snapshotType: 'health' | 'system'
  status: string | null
  rawData: Record<string, unknown> | null
  error: string | null
  polledAt: string
}

export interface SiteStatus {
  site: Site
  healthSnapshot: SiteSnapshot | null
  systemSnapshot: SiteSnapshot | null
}

export interface SiteCreate {
  name: string
  description?: string | null
  healthUrl?: string | null
  systemUrl?: string | null
  token?: string | null
  enabled?: boolean
  pollingHealth?: number
  pollingSystem?: number
  pollingUpdates?: number
  pollingReboot?: number
  teamsWebhookUrl?: string | null
  serverLabel?: string | null
  verifySSL?: boolean
}

export type SiteUpdate = Partial<SiteCreate>

export type AppStatus = 'ok' | 'degraded' | 'failed'
export type RebootStatus = 'ok' | 'reboot_required'
export type UpdateStatus = 'up_to_date' | 'outdated'
