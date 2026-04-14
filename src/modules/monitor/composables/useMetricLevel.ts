export type MetricLevel = 'ok' | 'warn' | 'crit'

interface Thresholds {
  warn: number
  crit: number
}

const DEFAULTS: Thresholds = { warn: 80, crit: 95 }

export function metricLevel(value: number | null | undefined, thresholds: Thresholds = DEFAULTS): MetricLevel {
  if (value == null) return 'ok'
  if (value >= thresholds.crit) return 'crit'
  if (value >= thresholds.warn) return 'warn'
  return 'ok'
}

export function metricValueClass(level: MetricLevel): string {
  switch (level) {
    case 'crit': return 'font-semibold text-destructive'
    case 'warn': return 'font-semibold text-amber-600 dark:text-amber-400'
    default: return ''
  }
}

export function metricBarClass(level: MetricLevel): string {
  switch (level) {
    case 'crit': return 'bg-destructive'
    case 'warn': return 'bg-amber-500'
    default: return 'bg-primary'
  }
}
