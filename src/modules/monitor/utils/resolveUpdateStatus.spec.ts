import { describe, expect, it } from 'vitest'
import {
  resolveSystemSnapshotStatus,
  resolveSystemState,
  resolveUpdateStatus,
} from './resolveUpdateStatus'

describe('resolveUpdateStatus', () => {
  it('returns null for empty status', () => {
    expect(resolveUpdateStatus(null, 0)).toBeNull()
    expect(resolveUpdateStatus(undefined, 0)).toBeNull()
  })

  it('passes through failed, reboot_required and up_to_date', () => {
    expect(resolveUpdateStatus('failed', 3)).toBe('failed')
    expect(resolveUpdateStatus('reboot_required', 3)).toBe('reboot_required')
    expect(resolveUpdateStatus('up_to_date', 3)).toBe('up_to_date')
  })

  it('maps outdated with security updates to outdated_security', () => {
    expect(resolveUpdateStatus('outdated', 3)).toBe('outdated_security')
  })

  it('maps outdated without security updates to outdated', () => {
    expect(resolveUpdateStatus('outdated', 0)).toBe('outdated')
    expect(resolveUpdateStatus('outdated', undefined)).toBe('outdated')
  })
})

describe('resolveSystemState', () => {
  it('maps outdated system_state with security updates', () => {
    expect(resolveSystemState('outdated', 2)).toBe('outdated_security')
  })

  it('maps outdated system_state without security updates', () => {
    expect(resolveSystemState('outdated', 0)).toBe('outdated')
  })

  it('passes through up_to_date', () => {
    expect(resolveSystemState('up_to_date', 5)).toBe('up_to_date')
  })
})

describe('resolveSystemSnapshotStatus', () => {
  it('resolves outdated snapshot status from security count', () => {
    expect(resolveSystemSnapshotStatus('outdated', 1)).toBe('outdated_security')
    expect(resolveSystemSnapshotStatus('outdated', 0)).toBe('outdated')
  })

  it('passes through non-outdated statuses', () => {
    expect(resolveSystemSnapshotStatus('reboot_required', 5)).toBe('reboot_required')
    expect(resolveSystemSnapshotStatus('failed', 0)).toBe('failed')
  })
})
