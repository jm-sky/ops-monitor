import type { MonitorOverallStatus, SiteStatus } from '../types'
import { resolveUpdateStatus } from '../utils/resolveUpdateStatus'

export function siteOverallStatus(s: SiteStatus): MonitorOverallStatus {
  const h = s.site.healthUrl ? s.healthSnapshot?.status : undefined
  const sys = s.site.systemUrl ? s.systemSnapshot?.status : undefined
  if (h === 'failed' || sys === 'failed') return 'failed'
  if (h === 'degraded') return 'degraded'
  if (sys === 'reboot_required') return 'reboot_required'
  const updateStatus = resolveUpdateStatus(sys, s.systemSnapshot?.rawData?.security_updates)
  if (updateStatus === 'outdated_security') return 'outdated_security'
  if (updateStatus === 'outdated') return 'outdated'
  if (h === 'ok' || sys === 'up_to_date') return 'ok'
  return 'unknown'
}
