<script setup lang="ts">
import { Server } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SiteStatus } from '../types'
import SiteStatusBadge from './SiteStatusBadge.vue'

const props = defineProps<{
  siteStatus: SiteStatus
  isPrimary?: boolean
  overallStatus: (siteStatus: SiteStatus) => string
  disabledLabel: string
}>()

const emit = defineEmits<{
  select: [id: string]
}>()
</script>

<template>
  <Card
    :class="[
      'cursor-pointer transition-shadow hover:shadow-md',
      isPrimary && 'ring-2 ring-primary/40',
    ]"
    @click="emit('select', props.siteStatus.site.id)"
  >
    <CardHeader class="flex flex-row items-start justify-between gap-2 pb-2">
      <div class="flex items-center gap-2 min-w-0">
        <Server class="size-4 shrink-0 text-muted-foreground" />
        <CardTitle class="truncate text-base">
          {{ props.siteStatus.site.name }}
        </CardTitle>
      </div>
      <SiteStatusBadge :status="props.overallStatus(props.siteStatus)" />
    </CardHeader>
    <CardContent class="space-y-1 text-sm text-muted-foreground">
      <div v-if="props.siteStatus.site.description" class="truncate">
        {{ props.siteStatus.site.description }}
      </div>
      <div class="flex flex-wrap gap-2 pt-1">
        <span v-if="props.siteStatus.healthSnapshot" class="flex items-center gap-1">
          <span class="font-medium text-foreground">Health:</span>
          <SiteStatusBadge :status="props.siteStatus.healthSnapshot.status ?? 'unknown'" size="sm" />
        </span>
        <span v-if="props.siteStatus.systemSnapshot" class="flex items-center gap-1">
          <span class="font-medium text-foreground">System:</span>
          <SiteStatusBadge :status="props.siteStatus.systemSnapshot.status ?? 'unknown'" size="sm" />
        </span>
      </div>
      <div
        v-if="props.siteStatus.healthSnapshot?.status === 'failed' && props.siteStatus.healthSnapshot.error"
        class="truncate text-xs text-destructive"
      >
        Health: {{ props.siteStatus.healthSnapshot.error }}
      </div>
      <div
        v-if="props.siteStatus.systemSnapshot?.status === 'failed' && props.siteStatus.systemSnapshot.error"
        class="truncate text-xs text-destructive"
      >
        System: {{ props.siteStatus.systemSnapshot.error }}
      </div>
      <div v-if="!props.siteStatus.site.enabled" class="text-xs text-muted-foreground italic">
        {{ props.disabledLabel }}
      </div>
    </CardContent>
  </Card>
</template>
