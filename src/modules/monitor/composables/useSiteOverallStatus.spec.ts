import { describe, expect, it } from 'vitest'
import type { Site, SiteStatus } from '../types'
import { siteOverallStatus } from './useSiteOverallStatus'

const baseSite: Site = {
  id: 'site-1',
  name: 'Server',
  description: null,
  healthUrl: null,
  systemUrl: 'https://example.com/system',
  token: null,
  tags: null,
  enabled: true,
  pollingHealth: 300,
  pollingSystem: 300,
  pollingUpdates: 43200,
  pollingReboot: 1800,
  teamsWebhookUrl: null,
  serverLabel: null,
  environment: null,
  ip: null,
  verifySSL: true,
  expectedMeta: null,
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
}

function makeStatus(overrides: Partial<SiteStatus>): SiteStatus {
  return {
    site: baseSite,
    healthSnapshot: null,
    systemSnapshot: null,
    ...overrides,
  }
}

const systemSnapshotBase = {
  id: 'snap-2',
  siteId: baseSite.id,
  snapshotType: 'system' as const,
  error: null,
  metaMismatches: null,
  polledAt: '2026-01-01T00:00:00Z',
}

describe('siteOverallStatus', () => {
  it('ignores failed health snapshot when health URL is not configured', () => {
    const status = makeStatus({
      healthSnapshot: {
        id: 'snap-1',
        siteId: baseSite.id,
        snapshotType: 'health',
        status: 'failed',
        rawData: null,
        error: 'Connection timeout',
        metaMismatches: null,
        polledAt: '2026-01-01T00:00:00Z',
      },
      systemSnapshot: {
        ...systemSnapshotBase,
        status: 'up_to_date',
        rawData: null,
      },
    })

    expect(siteOverallStatus(status)).toBe('ok')
  })

  it('uses health status when health URL is configured', () => {
    const status = makeStatus({
      site: { ...baseSite, healthUrl: 'https://example.com/health' },
      healthSnapshot: {
        id: 'snap-1',
        siteId: baseSite.id,
        snapshotType: 'health',
        status: 'failed',
        rawData: null,
        error: 'HTTP 500',
        metaMismatches: null,
        polledAt: '2026-01-01T00:00:00Z',
      },
    })

    expect(siteOverallStatus(status)).toBe('failed')
  })

  it('returns outdated_security when system is outdated with security updates', () => {
    const status = makeStatus({
      systemSnapshot: {
        ...systemSnapshotBase,
        status: 'outdated',
        rawData: { security_updates: 3 },
      },
    })

    expect(siteOverallStatus(status)).toBe('outdated_security')
  })

  it('returns outdated when system is outdated without security updates', () => {
    const status = makeStatus({
      systemSnapshot: {
        ...systemSnapshotBase,
        status: 'outdated',
        rawData: { security_updates: 0 },
      },
    })

    expect(siteOverallStatus(status)).toBe('outdated')
  })

  it('prefers reboot_required over outdated_security', () => {
    const status = makeStatus({
      systemSnapshot: {
        ...systemSnapshotBase,
        status: 'reboot_required',
        rawData: { security_updates: 5 },
      },
    })

    expect(siteOverallStatus(status)).toBe('reboot_required')
  })

  it('prefers degraded health over outdated_security system status', () => {
    const status = makeStatus({
      site: { ...baseSite, healthUrl: 'https://example.com/health' },
      healthSnapshot: {
        id: 'snap-1',
        siteId: baseSite.id,
        snapshotType: 'health',
        status: 'degraded',
        rawData: null,
        error: null,
        metaMismatches: null,
        polledAt: '2026-01-01T00:00:00Z',
      },
      systemSnapshot: {
        ...systemSnapshotBase,
        status: 'outdated',
        rawData: { security_updates: 2 },
      },
    })

    expect(siteOverallStatus(status)).toBe('degraded')
  })
})
