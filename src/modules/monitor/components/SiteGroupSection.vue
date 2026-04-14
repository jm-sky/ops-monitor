<script setup lang="ts">
import type { SiteStatus } from '../types'
import SiteStatusCard from './SiteStatusCard.vue'

interface SiteGroup {
  key: string
  label: string
  items: SiteStatus[]
}

const props = defineProps<{
  group: SiteGroup
  overallStatus: (siteStatus: SiteStatus) => string
  disabledLabel: string
}>()

const emit = defineEmits<{
  selectSite: [id: string]
}>()
</script>

<template>
  <section class="space-y-3">
    <h2 class="text-sm font-medium text-muted-foreground">
      {{ props.group.label }}
    </h2>
    <div class="rounded-lg border p-4">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <SiteStatusCard
          v-for="(siteStatus, index) in props.group.items"
          :key="siteStatus.site.id"
          :site-status="siteStatus"
          :is-primary="index === 0"
          :overall-status="props.overallStatus"
          :disabled-label="props.disabledLabel"
          @select="emit('selectSite', $event)"
        />
      </div>
    </div>
  </section>
</template>
