import { describe, expect, it } from 'vitest'
import {
  groupBackgroundClass,
  groupBorderClass,
  groupHasCriticalIssue,
  groupHasIssue,
  groupIconClass,
  statusColorClass,
  statusSeverity,
} from './statusStyles'

describe('statusStyles — cert_expired', () => {
  it('treats cert_expired with the same severity/color as failed', () => {
    expect(statusSeverity('cert_expired')).toBe(statusSeverity('failed'))
    expect(statusColorClass('cert_expired')).toBe(statusColorClass('failed'))
  })

  it('marks group as critical for cert_expired, like failed', () => {
    expect(groupHasCriticalIssue('cert_expired')).toBe(true)
    expect(groupHasIssue('cert_expired')).toBe(true)
  })

  it('uses the same group border/background/icon classes as failed', () => {
    expect(groupBorderClass('cert_expired')).toBe(groupBorderClass('failed'))
    expect(groupBackgroundClass('cert_expired')).toBe(groupBackgroundClass('failed'))
    expect(groupIconClass('cert_expired')).toBe(groupIconClass('failed'))
  })
})

describe('statusStyles — expiring_soon', () => {
  it('treats expiring_soon with the same severity/color as degraded', () => {
    expect(statusSeverity('expiring_soon')).toBe(statusSeverity('degraded'))
    expect(statusColorClass('expiring_soon')).toBe(statusColorClass('degraded'))
  })

  it('is not a critical issue', () => {
    expect(groupHasCriticalIssue('expiring_soon')).toBe(false)
  })
})
