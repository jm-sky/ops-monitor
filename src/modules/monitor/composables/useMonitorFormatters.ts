export function formatMonitorDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'short',
    timeStyle: 'medium',
  }).format(new Date(iso))
}

export function formatUptime(seconds: number | null | undefined): string {
  if (seconds == null || Number.isNaN(seconds)) return '—'
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return d > 0 ? `${d}d ${h}h ${m}m` : `${h}h ${m}m`
}

export function formatTimeAgo(iso: string | null | undefined): string {
  if (!iso) return '—'

  const timestamp = new Date(iso).getTime()
  if (Number.isNaN(timestamp)) return '—'

  const secondsDiff = Math.round((timestamp - Date.now()) / 1000)
  const absSeconds = Math.abs(secondsDiff)
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })

  if (absSeconds < 60) return rtf.format(secondsDiff, 'second')

  const minutesDiff = Math.round(secondsDiff / 60)
  if (Math.abs(minutesDiff) < 60) return rtf.format(minutesDiff, 'minute')

  const hoursDiff = Math.round(minutesDiff / 60)
  if (Math.abs(hoursDiff) < 24) return rtf.format(hoursDiff, 'hour')

  const daysDiff = Math.round(hoursDiff / 24)
  return rtf.format(daysDiff, 'day')
}
