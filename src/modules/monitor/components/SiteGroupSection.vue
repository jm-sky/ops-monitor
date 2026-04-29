<script setup lang="ts">
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

function hasBadServerHealth(group: SiteGroup): boolean {
  if (group.key === '__ungrouped__') return false

  const serverSiteStatus = group.items.find(siteStatus => siteStatus.site.name === group.key)
  const healthStatus = serverSiteStatus?.healthSnapshot?.status

  return healthStatus === 'failed' || healthStatus === 'degraded'
}
</script>

<template>
  <section :class="props.denseMode ? 'space-y-3 min-w-32 max-w-full flex-1' : 'space-y-3'">
    <h2 class="text-sm font-medium text-muted-foreground">
      {{ props.group.label }}
    </h2>
    <div
      :class="[
        'rounded-xl border-2 border-dashed p-4',
        hasBadServerHealth(props.group) && 'border-destructive/50',
      ]"
    >
      <div
        :class="[
          props.denseMode
            ? 'flex flex-wrap gap-2'
            : 'grid gap-4 sm:grid-cols-2 lg:grid-cols-3',
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
