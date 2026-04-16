import type { Site } from '../types'

export interface SiteFormData {
  name: string
  serverLabel: string
  environment: string
  tags: string[]
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
  environment: '',
  tags: [],
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
    environment: site.environment ?? '',
    tags: site.tags ?? [],
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

export function normalizeTags(value: string[]): string[] {
  const normalized = value
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)

  const seen = new Set<string>()
  return normalized.filter((tag) => {
    const key = tag.toLowerCase()
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

export function toNullableTags(value: string[]): string[] | null {
  const normalized = normalizeTags(value)
  return normalized.length > 0 ? normalized : null
}
