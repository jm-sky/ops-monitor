import { describe, expect, it } from 'vitest'
import { formatMonitorDate, formatPollingInterval, formatUptime } from './useMonitorFormatters'

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

  describe('formatPollingInterval', () => {
    it('returns empty string for invalid values', () => {
      expect(formatPollingInterval(null)).toBe('')
      expect(formatPollingInterval(undefined)).toBe('')
      expect(formatPollingInterval(Number.NaN)).toBe('')
      expect(formatPollingInterval(0)).toBe('')
      expect(formatPollingInterval(-30)).toBe('')
    })

    it('formats seconds-only values', () => {
      expect(formatPollingInterval(30)).toBe('30s')
    })

    it('formats minute values', () => {
      expect(formatPollingInterval(60)).toBe('1 min')
      expect(formatPollingInterval(300)).toBe('5 min')
    })

    it('formats mixed minute and second values', () => {
      expect(formatPollingInterval(90)).toBe('1 min 30s')
    })

    it('formats hour values', () => {
      expect(formatPollingInterval(3600)).toBe('1h')
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
