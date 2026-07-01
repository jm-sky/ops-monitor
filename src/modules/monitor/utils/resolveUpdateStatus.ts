import type { UpdateStatus } from '../types'

export type ResolvedSystemStatus =
  | 'failed'
  | 'reboot_required'
  | 'outdated_security'
  | 'outdated'
  | 'up_to_date'
  | null

export function resolveUpdateStatus(
  systemStatus: string | null | undefined,
  securityUpdates: number | undefined,
): ResolvedSystemStatus {
  if (!systemStatus) return null
  if (systemStatus === 'failed') return 'failed'
  if (systemStatus === 'reboot_required') return 'reboot_required'
  if (systemStatus === 'up_to_date') return 'up_to_date'
  if (systemStatus === 'outdated') {
    return securityUpdates != null && securityUpdates > 0 ? 'outdated_security' : 'outdated'
  }
  return null
}

export function resolveSystemState(
  systemState: string | null | undefined,
  securityUpdates: number | undefined,
): UpdateStatus | null {
  if (!systemState) return null
  if (systemState === 'up_to_date') return 'up_to_date'
  if (systemState === 'outdated') {
    return securityUpdates != null && securityUpdates > 0 ? 'outdated_security' : 'outdated'
  }
  return null
}

export function resolveSystemSnapshotStatus(
  snapshotStatus: string | null | undefined,
  securityUpdates: number | undefined,
): string | null {
  if (!snapshotStatus) return null
  if (snapshotStatus === 'outdated') {
    return securityUpdates != null && securityUpdates > 0 ? 'outdated_security' : 'outdated'
  }
  return snapshotStatus
}
