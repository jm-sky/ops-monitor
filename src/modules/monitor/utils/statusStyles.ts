import type { MonitorOverallStatus } from '../types'

export type DisplayStatus = MonitorOverallStatus | string | null

const SEVERITY: Record<string, number> = {
  failed: 6,
  degraded: 5,
  reboot_required: 4,
  outdated_security: 3,
  outdated: 2,
  ok: 1,
  up_to_date: 1,
  unknown: 0,
}

const COLOR_CLASS: Record<string, string> = {
  failed: 'border-destructive/40 bg-destructive/10 text-destructive',
  degraded: 'border-amber-200 bg-amber-100 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300',
  reboot_required: 'border-orange-200 bg-orange-100 text-orange-800 dark:border-orange-800 dark:bg-orange-950 dark:text-orange-300',
  outdated_security: 'border-orange-300 bg-orange-100 text-orange-900 dark:border-orange-700 dark:bg-orange-950 dark:text-orange-300',
  outdated: 'border-slate-200 bg-slate-100 text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300',
  ok: 'border-emerald-200 bg-emerald-100 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300',
  up_to_date: 'border-emerald-200 bg-emerald-100 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300',
}

const LABEL_KEY: Record<string, string> = {
  degraded: 'monitor.status.degraded',
  failed: 'monitor.status.failed',
  ok: 'monitor.status.ok',
  outdated: 'monitor.status.outdated',
  outdated_security: 'monitor.status.outdatedSecurity',
  reboot_required: 'monitor.status.rebootRequired',
  up_to_date: 'monitor.status.upToDate',
}

const LABEL_FALLBACK: Record<string, string> = {
  degraded: 'Degraded',
  failed: 'Failed',
  ok: 'OK',
  outdated: 'Outdated',
  outdated_security: 'Security updates',
  reboot_required: 'Reboot required',
  up_to_date: 'Up to date',
}

const GROUP_BORDER_CLASS: Record<string, string> = {
  failed: 'border-destructive/60',
  degraded: 'border-amber-400/60',
  reboot_required: 'border-orange-400/60',
  outdated_security: 'border-orange-400/50',
  outdated: 'border-slate-300/60 dark:border-slate-600/60',
}

const GROUP_BG_CLASS: Record<string, string> = {
  failed: 'bg-destructive/5',
  degraded: 'bg-amber-500/5',
  reboot_required: 'bg-orange-500/5',
  outdated_security: 'bg-orange-500/5',
  outdated: 'bg-slate-500/5',
}

const GROUP_ICON_CLASS: Record<string, string> = {
  failed: 'text-destructive',
  degraded: 'text-amber-500',
  reboot_required: 'text-orange-500',
  outdated_security: 'text-orange-500',
  outdated: 'text-slate-400',
}

function normalizeStatus(status: DisplayStatus): string {
  return status ?? 'unknown'
}

export function statusSeverity(status: DisplayStatus): number {
  return SEVERITY[normalizeStatus(status)] ?? 0
}

export function statusColorClass(status: DisplayStatus): string {
  return COLOR_CLASS[normalizeStatus(status)] ?? ''
}

export function statusLabelKey(status: DisplayStatus): string | null {
  return LABEL_KEY[normalizeStatus(status)] ?? null
}

export function statusLabelFallback(status: DisplayStatus): string {
  const key = normalizeStatus(status)
  return LABEL_FALLBACK[key] ?? key
}

export function statusShowsShieldIcon(status: DisplayStatus): boolean {
  return normalizeStatus(status) === 'outdated_security'
}

export function groupBorderClass(status: DisplayStatus): string {
  return GROUP_BORDER_CLASS[normalizeStatus(status)] ?? ''
}

export function groupBackgroundClass(status: DisplayStatus): string {
  return GROUP_BG_CLASS[normalizeStatus(status)] ?? ''
}

export function groupIconClass(status: DisplayStatus): string {
  return GROUP_ICON_CLASS[normalizeStatus(status)] ?? 'text-amber-500'
}

export function groupHasIssue(status: DisplayStatus): boolean {
  const normalized = normalizeStatus(status)
  return normalized !== 'ok' && normalized !== 'unknown' && normalized !== 'up_to_date'
}

export function groupHasCriticalIssue(status: DisplayStatus): boolean {
  return normalizeStatus(status) === 'failed'
}
