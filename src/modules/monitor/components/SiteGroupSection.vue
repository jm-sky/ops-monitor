<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import type { MonitorOverallStatus, SiteStatus } from '../types'
import SiteStatusCard from './SiteStatusCard.vue'

interface SiteGroup {
  key: string
  label: string
  items: SiteStatus[]
}

const props = defineProps<{
  group: SiteGroup
  overallStatus: (siteStatus: SiteStatus) => MonitorOverallStatus
  disabledLabel: string
  denseMode?: boolean
}>()

const emit = defineEmits<{
  selectSite: [id: string]
}>()

function groupPrimaryStatus(group: SiteGroup): MonitorOverallStatus | 'unknown' | null {
  if (group.key === '__ungrouped__') return null

  const serverSiteStatus = group.items.find(siteStatus => siteStatus.site.name === group.key)
  if (!serverSiteStatus) return null

  const healthStatus = (serverSiteStatus.healthSnapshot?.status ?? null) as MonitorOverallStatus | null
  const systemStatus = (serverSiteStatus.systemSnapshot?.status ?? null) as MonitorOverallStatus | null

  if (healthStatus === 'failed' || systemStatus === 'failed') return 'failed'
  if (healthStatus === 'degraded' || systemStatus === 'degraded') return 'degraded'
  if (systemStatus === 'reboot_required') return 'reboot_required'
  if (systemStatus === 'outdated') return 'outdated'
  if (healthStatus === 'ok' || systemStatus === 'up_to_date') return 'ok'
  return 'unknown'
}

function groupHasIssue(group: SiteGroup): boolean {
  const status = groupPrimaryStatus(group)
  if (!status || status === 'ok') return false
  return status !== 'unknown'
}

function groupHasCriticalIssue(group: SiteGroup): boolean {
  return groupPrimaryStatus(group) === 'failed'
}

function hasBadServerHealth(group: SiteGroup): boolean {
  if (group.key === '__ungrouped__') return false

  const serverSiteStatus = group.items.find(siteStatus => siteStatus.site.name === group.key)
  const healthStatus = serverSiteStatus?.healthSnapshot?.status

  return healthStatus === 'failed' || healthStatus === 'degraded'
}
</script>

<template>
  <section :class="props.denseMode ? 'space-y-2 min-w-0 break-inside-avoid' : 'space-y-3'">
    <h2 class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
      <AlertTriangle
        v-if="groupHasIssue(props.group)"
        :class="[
          'size-4 shrink-0',
          groupHasCriticalIssue(props.group) ? 'text-destructive' : 'text-amber-500',
        ]"
        :title="String(groupPrimaryStatus(props.group) ?? '')"
      />
      <span class="min-w-0 truncate">{{ props.group.label }}</span>
    </h2>
    <div
      :class="[
        props.denseMode ? 'rounded-xl border-2 border-dashed p-3' : 'rounded-xl border-2 border-dashed p-4',
        hasBadServerHealth(props.group) && 'border-destructive/50',
        groupHasCriticalIssue(props.group) && 'border-destructive/60',
        groupHasIssue(props.group) && !groupHasCriticalIssue(props.group) && 'border-amber-400/60',
        groupHasCriticalIssue(props.group) && 'bg-destructive/5',
        groupHasIssue(props.group) && !groupHasCriticalIssue(props.group) && 'bg-amber-500/5',
      ]"
    >
      <div
        :class="[
          props.denseMode ? 'grid gap-2 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]' : 'grid gap-4 sm:grid-cols-2 lg:grid-cols-3',
        ]"
      >
        <SiteStatusCard
          v-for="(siteStatus, index) in props.group.items"
          :key="siteStatus.site.id"
          :site-status="siteStatus"
          :is-primary="index === 0"
          :overall-status="props.overallStatus"
          :disabled-label="props.disabledLabel"
          :dense-mode="props.denseMode"
          @select="emit('selectSite', $event)"
        />
      </div>
    </div>
  </section>
</template>
