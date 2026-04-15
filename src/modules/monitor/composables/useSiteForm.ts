import type { Site } from '../types'

export interface SiteFormData {
  name: string
  serverLabel: string
  healthUrl: string
  systemUrl: string
  token: string
  enabled: boolean
  pollingHealth: number
  pollingSystem: number
  verifySSL: boolean
}

const SITE_FORM_DEFAULTS: SiteFormData = {
  name: '',
  serverLabel: '',
  healthUrl: '',
  systemUrl: '',
  token: '',
  enabled: true,
  pollingHealth: 300,
  pollingSystem: 300,
  verifySSL: true,
}

export function createDefaultSiteForm(): SiteFormData {
  return { ...SITE_FORM_DEFAULTS }
}

export function siteToForm(site: Site): SiteFormData {
  return {
    name: site.name,
    serverLabel: site.serverLabel ?? '',
    healthUrl: site.healthUrl ?? '',
    systemUrl: site.systemUrl ?? '',
    token: '',
    enabled: site.enabled,
    pollingHealth: site.pollingHealth,
    pollingSystem: site.pollingSystem,
    verifySSL: site.verifySSL,
  }
}

export function toNullableString(value: string): string | null {
  const nextValue = value.trim()
  return nextValue.length > 0 ? nextValue : null
}
