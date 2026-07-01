import { describe, expect, it } from 'vitest'
import type { HealthRawData } from '../types'
import {
  buildComponentIssuePayload,
  filterComponentErrors,
  isComponentIssueCopyable,
} from './buildComponentIssuePayload'

const sampleRawData: HealthRawData = {
  status: 'degraded',
  version: '2.1.8',
  checked_at: '2026-07-01T09:10:06+02:00',
  meta: {
    ksef_env: 'prod',
    failed_jobs_query: 0,
    callback_failures_15m: 0,
    invoice_queries_failed: 208,
  },
  errors: [
    'invoice_queries: 208 queries failed',
    'other: unrelated error',
  ],
  components: {
    invoice_queries: {
      reason: '208 queries failed',
      status: 'degraded',
      metrics: {
        failed: 208,
        processing: 2853,
        stuck_processing: 0,
      },
      checked_at: '2026-07-01T09:10:07+02:00',
    },
  },
}

describe('filterComponentErrors', () => {
  it('filters errors by component prefix', () => {
    expect(
      filterComponentErrors(sampleRawData.errors, 'invoice_queries', '208 queries failed'),
    ).toEqual(['invoice_queries: 208 queries failed'])
  })

  it('falls back to reason when no matching errors', () => {
    expect(
      filterComponentErrors(['other: unrelated'], 'invoice_queries', '208 queries failed'),
    ).toEqual(['invoice_queries: 208 queries failed'])
  })

  it('returns empty array when no matches and no reason', () => {
    expect(filterComponentErrors(['other: unrelated'], 'invoice_queries')).toEqual([])
  })
})

describe('isComponentIssueCopyable', () => {
  it('returns true for degraded with reason', () => {
    expect(
      isComponentIssueCopyable('degraded', '208 queries failed', [], 'invoice_queries'),
    ).toBe(true)
  })

  it('returns true for failed with matching error entry', () => {
    expect(
      isComponentIssueCopyable('failed', undefined, ['db: connection lost'], 'db'),
    ).toBe(true)
  })

  it('returns false for ok status', () => {
    expect(isComponentIssueCopyable('ok', 'some reason', [], 'db')).toBe(false)
  })

  it('returns false for degraded without reason or matching errors', () => {
    expect(isComponentIssueCopyable('degraded', undefined, ['other: x'], 'db')).toBe(false)
  })
})

describe('buildComponentIssuePayload', () => {
  it('builds full payload for degraded component with metrics', () => {
    expect(buildComponentIssuePayload(sampleRawData, 'invoice_queries')).toEqual({
      meta: sampleRawData.meta,
      errors: ['invoice_queries: 208 queries failed'],
      status: 'degraded',
      version: '2.1.8',
      checked_at: '2026-07-01T09:10:06+02:00',
      component: {
        invoice_queries: sampleRawData.components!.invoice_queries,
      },
    })
  })

  it('omits undefined top-level fields', () => {
    const rawData: HealthRawData = {
      status: 'degraded',
      components: {
        cache: {
          status: 'degraded',
          reason: 'High miss rate',
        },
      },
    }

    expect(buildComponentIssuePayload(rawData, 'cache')).toEqual({
      errors: ['cache: High miss rate'],
      status: 'degraded',
      component: {
        cache: rawData.components!.cache,
      },
    })
  })

  it('returns null for non-issue component', () => {
    const rawData: HealthRawData = {
      status: 'ok',
      components: {
        database: { status: 'ok' },
      },
    }

    expect(buildComponentIssuePayload(rawData, 'database')).toBeNull()
  })

  it('returns null when component is missing', () => {
    expect(buildComponentIssuePayload(sampleRawData, 'missing')).toBeNull()
  })
})
