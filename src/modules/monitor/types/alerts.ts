export type AlertChannelType = 'teams' | 'email' | 'telegram'
export type AlertType = 'health' | 'reboot' | 'updates'
export type HealthSeverity = 'degraded' | 'failed'

export interface QuietHoursConfig {
  enabled: boolean
  start: string
  end: string
  timezone: string
}

export interface AlertChannelFilters {
  alert_types: AlertType[]
  min_health_severity: HealthSeverity
  site_ids: string[]
  tags: string[]
  quiet_hours: QuietHoursConfig
  re_alert_after_minutes: number | null
}

export const DEFAULT_QUIET_HOURS: QuietHoursConfig = {
  enabled: false,
  start: '22:00',
  end: '07:00',
  timezone: 'Europe/Warsaw',
}

export const DEFAULT_FILTERS: AlertChannelFilters = {
  alert_types: [],
  min_health_severity: 'degraded',
  site_ids: [],
  tags: [],
  quiet_hours: { ...DEFAULT_QUIET_HOURS },
  re_alert_after_minutes: null,
}

export interface AlertChannel {
  id: string
  name: string
  type: AlertChannelType
  enabled: boolean
  config: Record<string, unknown>
  filters: AlertChannelFilters
  createdAt: string
  updatedAt: string
}

export interface AlertChannelCreate {
  name: string
  type: AlertChannelType
  enabled?: boolean
  config: Record<string, unknown>
  filters?: AlertChannelFilters
}

export interface AlertChannelUpdate {
  name?: string
  enabled?: boolean
  config?: Record<string, unknown>
  filters?: AlertChannelFilters
}

export interface TeamsConfig {
  webhook_url: string
}

export interface EmailConfig {
  to: string[]
  subject_prefix?: string
}

export interface TelegramConfig {
  bot_token: string
  chat_id: string
}

export interface AlertEvent {
  id: string
  siteId: string
  siteName: string
  channelId: string
  channelName: string
  alertType: string
  status: string
  sentAt: string
}
