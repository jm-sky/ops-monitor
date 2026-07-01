<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import type { MonitorOverallStatus, SiteStatus } from '../types'
import { siteOverallStatus } from '../composables/useSiteOverallStatus'
import {
  groupBackgroundClass,
  groupBorderClass,
  groupHasCriticalIssue,
  groupHasIssue,
  groupIconClass,
} from '../utils/statusStyles'
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

  return siteOverallStatus(serverSiteStatus)
}

function hasBadServerHealth(group: SiteGroup): boolean {
  if (group.key === '__ungrouped__') return false

  const serverSiteStatus = group.items.find(siteStatus => siteStatus.site.name === group.key)
  if (!serverSiteStatus?.site.healthUrl) return false

  const healthStatus = serverSiteStatus.healthSnapshot?.status
  return healthStatus === 'failed' || healthStatus === 'degraded'
}
</script>

<template>
  <section :class="props.denseMode ? 'space-y-2 min-w-0 break-inside-avoid' : 'space-y-3'">
    <h2 class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
      <AlertTriangle
        v-if="groupHasIssue(groupPrimaryStatus(props.group))"
        :class="[
          'size-4 shrink-0',
          groupIconClass(groupPrimaryStatus(props.group)),
        ]"
        :title="String(groupPrimaryStatus(props.group) ?? '')"
      />
      <span class="min-w-0 truncate">{{ props.group.label }}</span>
    </h2>
    <div
      :class="[
        props.denseMode ? 'rounded-xl border-2 border-dashed p-3' : 'rounded-xl border-2 border-dashed p-4',
        hasBadServerHealth(props.group) && 'border-destructive/50',
        groupHasIssue(groupPrimaryStatus(props.group)) && groupBorderClass(groupPrimaryStatus(props.group)),
        groupHasCriticalIssue(groupPrimaryStatus(props.group)) && 'bg-destructive/5',
        groupHasIssue(groupPrimaryStatus(props.group)) && !groupHasCriticalIssue(groupPrimaryStatus(props.group)) && groupBackgroundClass(groupPrimaryStatus(props.group)),
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
