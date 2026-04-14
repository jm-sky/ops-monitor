export type AlertChannelType = 'teams' | 'email' | 'telegram'

export interface AlertChannel {
  id: string
  name: string
  type: AlertChannelType
  enabled: boolean
  config: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

export interface AlertChannelCreate {
  name: string
  type: AlertChannelType
  enabled?: boolean
  config: Record<string, unknown>
}

export interface AlertChannelUpdate {
  name?: string
  enabled?: boolean
  config?: Record<string, unknown>
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
