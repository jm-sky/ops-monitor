import { describe, expect, it } from 'vitest'
import type { Site } from '../types'
import { createDefaultSiteForm, normalizeTags, siteToForm, toNullableString, toNullableTags } from './useSiteForm'

const baseSite: Site = {
  id: 'site-1',
  name: 'API',
  description: null,
  healthUrl: 'https://example.com/health',
  systemUrl: 'https://example.com/system',
  token: 'secret-token',
  tags: ['core', 'prod'],
  enabled: true,
  pollingHealth: 300,
  pollingSystem: 600,
  pollingUpdates: 3600,
  pollingReboot: 1800,
  teamsWebhookUrl: null,
  serverLabel: 'srv-1',
  environment: 'production',
  ip: '10.0.0.10',
  verifySSL: true,
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
}

describe('useSiteForm', () => {
  it('creates clean default forms', () => {
    const form = createDefaultSiteForm()
    expect(form.name).toBe('')
    expect(form.enabled).toBe(true)
    expect(form.verifySSL).toBe(true)
  })

  it('maps site to edit form without exposing token', () => {
    const form = siteToForm(baseSite)
    expect(form.name).toBe('API')
    expect(form.serverLabel).toBe('srv-1')
    expect(form.environment).toBe('production')
    expect(form.ip).toBe('10.0.0.10')
    expect(form.token).toBe('')
    expect(form.tags).toEqual(['core', 'prod'])
  })

  it('normalizes blank strings to null', () => {
    expect(toNullableString('')).toBeNull()
    expect(toNullableString('   ')).toBeNull()
  })

  it('trims and returns non-empty strings', () => {
    expect(toNullableString(' abc ')).toBe('abc')
  })

  it('normalizes tags', () => {
    expect(normalizeTags(['  prod ', '', 'API', 'api', '  '])).toEqual(['prod', 'API'])
  })

  it('returns null for empty tags', () => {
    expect(toNullableTags([])).toBeNull()
    expect(toNullableTags(['', '   '])).toBeNull()
  })
})
