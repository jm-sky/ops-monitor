import type { TDateTime } from '@/shared/types/base.type'

export type MetaValue = string | number | boolean

export interface Site {
  id: string
  name: string
  description: string | null
  healthUrl: string | null
  systemUrl: string | null
  token: string | null
  tags: string[] | null
  enabled: boolean
  pollingHealth: number
  pollingSystem: number
  pollingUpdates: number
  pollingReboot: number
  teamsWebhookUrl: string | null
  serverLabel: string | null
  environment: string | null
  ip: string | null
  verifySSL: boolean
  expectedMeta: Record<string, MetaValue> | null
  createdAt: TDateTime
  updatedAt: TDateTime
}

export interface HealthComponent {
  reason?: string
  stale?: boolean
  status?: string
}

export interface HealthRawData {
  schema_version?: number
  components?: Record<string, HealthComponent>
  status?: string
  version?: string
  environment?: string
  last_activity?: string
  errors?: string[]
  meta?: Record<string, MetaValue>
  [key: string]: unknown
}

export interface SystemResourceData {
  percent?: number
  total_mb?: number
  used_mb?: number
}

export interface SystemDiskData {
  percent?: number
  total_gb?: number
  used_gb?: number
}

export interface SystemRawData {
  cpu_percent?: number
  disk?: SystemDiskData
  memory?: SystemResourceData
  reboot_detected_at?: string
  reboot_reason?: string
  reboot_required?: boolean
  security_updates?: number
  system_state?: string
  updates_available?: number
  uptime_seconds?: number
  [key: string]: unknown
}

export interface SiteSnapshot<TRawData = Record<string, unknown>> {
  id: string
  siteId: string
  snapshotType: 'health' | 'system'
  status: string | null
  rawData: TRawData | null
  metaMismatches: string[] | null
  error: string | null
  polledAt: TDateTime
}

export interface SiteStatus {
  site: Site
  healthSnapshot: SiteSnapshot<HealthRawData> | null
  systemSnapshot: SiteSnapshot<SystemRawData> | null
}

export interface SiteCreate {
  name: string
  description?: string | null
  healthUrl?: string | null
  systemUrl?: string | null
  token?: string | null
  tags?: string[] | null
  enabled?: boolean
  pollingHealth?: number
  pollingSystem?: number
  pollingUpdates?: number
  pollingReboot?: number
  teamsWebhookUrl?: string | null
  serverLabel?: string | null
  environment?: string | null
  ip?: string | null
  verifySSL?: boolean
  expectedMeta?: Record<string, MetaValue> | null
}

export type SiteUpdate = Partial<SiteCreate>

export type AppStatus = 'ok' | 'degraded' | 'failed'
export type RebootStatus = 'ok' | 'reboot_required'
export type UpdateStatus = 'up_to_date' | 'outdated'
