<script setup lang="ts">
import { Server } from 'lucide-vue-next'
import { computed } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SiteStatus } from '../types'
import { metricLevel, type MetricLevel } from '../composables/useMetricLevel'
import SiteStatusBadge from './SiteStatusBadge.vue'

interface HealthComponent {
  status: string
  reason?: string
  stale?: boolean
}

const props = defineProps<{
  siteStatus: SiteStatus
  isPrimary?: boolean
  overallStatus: (siteStatus: SiteStatus) => string
  disabledLabel: string
  denseMode?: boolean
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const healthComponents = computed<[string, HealthComponent][]>(() => {
  const raw = props.siteStatus.healthSnapshot?.rawData
  if (!raw || typeof raw.components !== 'object' || !raw.components) return []
  return Object.entries(raw.components as Record<string, HealthComponent>)
})

const COMPONENT_ICONS: Record<string, string> = {
  database: '🗄️',
  cache: '⚡',
  frontend: '🖥️',
  queue: '📬',
  storage: '📦',
  mail: '📧',
}

function componentIcon(name: string): string {
  return COMPONENT_ICONS[name] ?? '🔌'
}

function componentLabel(name: string): string {
  return name.charAt(0).toUpperCase() + name.slice(1)
}

interface SystemMetric {
  label: string
  value: number | null
  level: MetricLevel
}

const systemMetrics = computed<SystemMetric[]>(() => {
  const raw = props.siteStatus.systemSnapshot?.rawData
  if (!raw) return []

  const mem = raw.memory as Record<string, number> | undefined
  const disk = raw.disk as Record<string, number> | undefined

  return [
    { label: 'CPU', value: raw.cpu_percent as number ?? null, level: metricLevel(raw.cpu_percent as number) },
    { label: 'RAM', value: mem?.percent ?? null, level: metricLevel(mem?.percent) },
    { label: 'Disk', value: disk?.percent ?? null, level: metricLevel(disk?.percent) },
  ].filter(m => m.value != null)
})

const worstMetricLevel = computed<MetricLevel>(() => {
  if (systemMetrics.value.some(m => m.level === 'crit')) return 'crit'
  if (systemMetrics.value.some(m => m.level === 'warn')) return 'warn'
  return 'ok'
})
</script>

<template>
  <Card
    :class="[
      'cursor-pointer transition-all hover:shadow-lg hover:scale-101 hover:-translate-y-1 gap-2',
      props.denseMode ? 'w-56 min-h-20 p-3' : '',
      isPrimary && 'ring-2 ring-primary/40',
      worstMetricLevel === 'crit' && 'ring-2 ring-destructive/50',
      worstMetricLevel === 'warn' && !isPrimary && 'ring-2 ring-amber-400/50',
    ]"
    @click="emit('select', props.siteStatus.site.id)"
  >
    <CardHeader :class="props.denseMode ? 'flex flex-col items-center justify-between gap-2 p-0 overflow-hidden' : 'flex flex-row items-start justify-between gap-2 pb-2'">
      <div class="flex items-center gap-2 min-w-0">
        <Server class="size-4 shrink-0 text-muted-foreground" />
        <CardTitle :class="props.denseMode ? 'truncate text-sm' : 'truncate text-base'">
          {{ props.siteStatus.site.name }}
        </CardTitle>
      </div>
      <SiteStatusBadge :status="props.overallStatus(props.siteStatus)" />
    </CardHeader>
    <CardContent :class="props.denseMode ? 'pt-1 px-0 pb-0 space-y-1 text-xs text-muted-foreground' : 'space-y-2 text-sm text-muted-foreground'">
      <div v-if="!props.denseMode && props.siteStatus.site.description" class="truncate">
        {{ props.siteStatus.site.description }}
      </div>
      <div v-if="!props.denseMode" class="flex flex-wrap gap-4 pt-1">
        <span v-if="props.siteStatus.healthSnapshot && !healthComponents.length" class="flex items-center gap-1">
          <span class="font-medium text-foreground">Health:</span>
          <SiteStatusBadge :status="props.siteStatus.healthSnapshot.status ?? 'unknown'" size="sm" />
        </span>
        <span v-if="props.siteStatus.systemSnapshot" class="flex items-center gap-1">
          <span class="font-medium text-foreground">System:</span>
          <SiteStatusBadge :status="props.siteStatus.systemSnapshot.status ?? 'unknown'" size="sm" />
        </span>
      </div>
      <div v-if="!props.denseMode && healthComponents.length" class="grid grid-cols-2 gap-x-6 gap-y-1 pt-1">
        <span
          v-for="[name, component] in healthComponents"
          :key="name"
          class="flex items-center justify-between gap-2 text-xs"
          :title="component.reason"
        >
          <div class="flex items-center gap-1">
            <span>{{ componentIcon(name) }}</span>
            <span class="text-muted-foreground">{{ componentLabel(name) }}:</span>
          </div>
          <SiteStatusBadge :status="component.status" size="sm" />
          <span v-if="component.stale" class="text-muted-foreground/60" title="Status może być nieaktualny">~</span>
        </span>
      </div>
      <div
        v-if="!props.denseMode && props.siteStatus.healthSnapshot?.status === 'failed' && props.siteStatus.healthSnapshot.error"
        class="truncate text-xs text-destructive"
      >
        Health: {{ props.siteStatus.healthSnapshot.error }}
      </div>
      <div
        v-if="!props.denseMode && props.siteStatus.systemSnapshot?.status === 'failed' && props.siteStatus.systemSnapshot.error"
        class="truncate text-xs text-destructive"
      >
        System: {{ props.siteStatus.systemSnapshot.error }}
      </div>
      <div v-if="!props.denseMode && worstMetricLevel !== 'ok'" class="flex flex-wrap gap-1.5 pt-1">
        <span
          v-for="metric in systemMetrics.filter(m => m.level !== 'ok')"
          :key="metric.label"
          :class="[
            'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
            metric.level === 'crit'
              ? 'bg-destructive/10 text-destructive'
              : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
          ]"
        >
          {{ metric.label }} {{ metric.value }}%
        </span>
      </div>
      <div v-if="!props.siteStatus.site.enabled" :class="props.denseMode ? 'text-[11px] text-muted-foreground italic' : 'text-xs text-muted-foreground italic'">
        {{ props.disabledLabel }}
      </div>
    </CardContent>
  </Card>
</template>
