import type { HealthComponent, HealthRawData, MetaValue } from '../types'

export interface ComponentIssuePayload {
  meta?: Record<string, MetaValue>
  errors: string[]
  status?: string
  version?: string
  checked_at?: string
  component: Record<string, HealthComponent>
}

const ISSUE_STATUSES = new Set(['degraded', 'failed'])

function componentErrorPrefix(componentName: string): string {
  return `${componentName}:`
}

export function filterComponentErrors(
  errors: string[] | undefined,
  componentName: string,
  reason?: string,
): string[] {
  const prefix = componentErrorPrefix(componentName)
  const matched = (errors ?? []).filter(error => error.startsWith(prefix))
  if (matched.length > 0) return matched
  if (reason) return [`${prefix} ${reason}`]
  return []
}

export function isComponentIssueCopyable(
  status: string | undefined,
  reason: string | undefined,
  errors: string[] | undefined,
  componentName: string,
): boolean {
  if (!status || !ISSUE_STATUSES.has(status)) return false
  if (reason) return true
  const prefix = componentErrorPrefix(componentName)
  return (errors ?? []).some(error => error.startsWith(prefix))
}

function omitUndefined<T extends Record<string, unknown>>(obj: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(obj).filter(([, value]) => value !== undefined),
  ) as Partial<T>
}

export function buildComponentIssuePayload(
  rawData: HealthRawData,
  componentName: string,
): ComponentIssuePayload | null {
  const component = rawData.components?.[componentName]
  if (!component) return null

  const errors = filterComponentErrors(rawData.errors, componentName, component.reason)
  if (!isComponentIssueCopyable(component.status, component.reason, rawData.errors, componentName)) {
    return null
  }

  const checkedAt = typeof rawData.checked_at === 'string' ? rawData.checked_at : undefined

  return omitUndefined({
    meta: rawData.meta,
    errors,
    status: rawData.status,
    version: rawData.version,
    checked_at: checkedAt,
    component: { [componentName]: component },
  }) as ComponentIssuePayload
}
