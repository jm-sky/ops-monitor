import { describe, expect, it } from 'vitest'
import { formatMonitorDate, formatUptime } from './useMonitorFormatters'

describe('useMonitorFormatters', () => {
  describe('formatMonitorDate', () => {
    it('returns em dash for empty values', () => {
      expect(formatMonitorDate(null)).toBe('—')
      expect(formatMonitorDate(undefined)).toBe('—')
    })

    it('formats valid ISO timestamps', () => {
      const formatted = formatMonitorDate('2026-01-01T12:34:56Z')
      expect(formatted).not.toBe('—')
      expect(formatted.length).toBeGreaterThan(0)
    })
  })

  describe('formatUptime', () => {
    it('returns em dash for invalid values', () => {
      expect(formatUptime(null)).toBe('—')
      expect(formatUptime(undefined)).toBe('—')
      expect(formatUptime(Number.NaN)).toBe('—')
    })

    it('formats values under one day', () => {
      expect(formatUptime(3661)).toBe('1h 1m')
    })

    it('formats values above one day', () => {
      expect(formatUptime(90061)).toBe('1d 1h 1m')
    })
  })
})
