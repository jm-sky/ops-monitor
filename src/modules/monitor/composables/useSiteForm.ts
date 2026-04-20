import type { MetaValue, Site } from '../types'

export interface SiteFormData {
  name: string
  serverLabel: string
  environment: string
  ip: string
  tags: string[]
  healthUrl: string
  systemUrl: string
  token: string
  enabled: boolean
  pollingHealth: number
  pollingSystem: number
  verifySSL: boolean
  expectedMeta: Record<string, string>
}

const SITE_FORM_DEFAULTS: SiteFormData = {
  name: '',
  serverLabel: '',
  environment: '',
  ip: '',
  tags: [],
  healthUrl: '',
  systemUrl: '',
  token: '',
  enabled: true,
  pollingHealth: 300,
  pollingSystem: 300,
  verifySSL: true,
  expectedMeta: {},
}

export function createDefaultSiteForm(): SiteFormData {
  return { ...SITE_FORM_DEFAULTS, expectedMeta: {} }
}

export function siteToForm(site: Site): SiteFormData {
  return {
    name: site.name,
    serverLabel: site.serverLabel ?? '',
    environment: site.environment ?? '',
    ip: site.ip ?? '',
    tags: site.tags ?? [],
    healthUrl: site.healthUrl ?? '',
    systemUrl: site.systemUrl ?? '',
    token: '',
    enabled: site.enabled,
    pollingHealth: site.pollingHealth,
    pollingSystem: site.pollingSystem,
    verifySSL: site.verifySSL,
    expectedMeta: site.expectedMeta
      ? Object.fromEntries(Object.entries(site.expectedMeta).map(([k, v]) => [k, String(v)]))
      : {},
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

export function toNullableMeta(
  value: Record<string, string>,
): Record<string, MetaValue> | null {
  const entries = Object.entries(value)
    .map(([k, v]): [string, string] => [k.trim(), v.trim()])
    .filter(([k]) => k.length > 0)

  if (entries.length === 0) return null

  return Object.fromEntries(
    entries.map(([k, v]) => {
      if (v === 'true') return [k, true]
      if (v === 'false') return [k, false]
      const num = Number(v)
      if (v !== '' && !isNaN(num)) return [k, num]
      return [k, v]
    }),
  )
}
