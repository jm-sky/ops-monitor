<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { VisArea, VisAxis, VisLine, VisXYContainer } from '@unovis/vue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SiteSnapshot, SystemRawData } from '../types'
import { formatMonitorDate } from '../composables/useMonitorFormatters'
import { monitorQueryKeys } from '../services/monitorQueries'
import { monitorService } from '../services/monitorService'

const props = defineProps<{
  siteId: string | null
}>()

const { t } = useI18n()

const CHART_LIMIT = 48

const { data: systemChartSnapshots } = useQuery<SiteSnapshot<SystemRawData>[]>({
  queryKey: computed(() => props.siteId
    ? [...monitorQueryKeys.snapshots(props.siteId, 'system'), 'chart', CHART_LIMIT] as const
    : [...monitorQueryKeys.all, 'system-chart', 'empty'] as const),
  queryFn: () => props.siteId
    ? monitorService.getSnapshots(props.siteId, 'system', CHART_LIMIT)
    : Promise.resolve([]),
  enabled: computed(() => Boolean(props.siteId)),
  placeholderData: previousData => previousData,
})

interface ChartPoint {
  index: number
  cpu: number
  ram: number
  disk: number
  label: string
}

const chartData = computed<ChartPoint[]>(() => {
  if (!systemChartSnapshots.value) return []
  return [...systemChartSnapshots.value]
    .reverse()
    .slice(-CHART_LIMIT)
    .map((snap, i) => ({
      index: i,
      cpu: snap.rawData?.cpu_percent ?? 0,
      ram: snap.rawData?.memory?.percent ?? 0,
      disk: snap.rawData?.disk?.percent ?? 0,
      label: formatMonitorDate(snap.polledAt),
    }))
})

const chartLabels = computed(() => chartData.value.map(d => d.label))

function xAccessor(_d: ChartPoint, i: number) {
  return i
}

function yAxisFormat(v: number) {
  return `${v}%`
}

function xAxisFormat(i: number) {
  return chartLabels.value[i] ?? ''
}
</script>

<template>
  <div v-if="chartData.length > 1" class="mb-8 border-b pb-4">
    <div class="mb-2 flex gap-4 text-xs text-muted-foreground">
      <span class="flex items-center gap-1.5">
        <span class="inline-block size-2.5 rounded-sm bg-blue-500" />
        {{ t('monitor.metrics.cpu', 'CPU') }}
      </span>
      <span class="flex items-center gap-1.5">
        <span class="inline-block size-2.5 rounded-sm bg-emerald-500" />
        {{ t('monitor.metrics.ram', 'RAM') }}
      </span>
      <span class="flex items-center gap-1.5">
        <span class="inline-block size-2.5 rounded-sm bg-amber-500" />
        {{ t('monitor.metrics.disk', 'Disk') }}
      </span>
    </div>
    <VisXYContainer :data="chartData" :height="160" class="w-full">
      <VisArea
        :x="xAccessor"
        :y="(d: ChartPoint) => d.cpu"
        color="#3b82f6"
        :opacity="0.15"
      />
      <VisLine
        :x="xAccessor"
        :y="(d: ChartPoint) => d.cpu"
        color="#3b82f6"
      />
      <VisArea
        :x="xAccessor"
        :y="(d: ChartPoint) => d.ram"
        color="#10b981"
        :opacity="0.15"
      />
      <VisLine
        :x="xAccessor"
        :y="(d: ChartPoint) => d.ram"
        color="#10b981"
      />
      <VisArea
        :x="xAccessor"
        :y="(d: ChartPoint) => d.disk"
        color="#f59e0b"
        :opacity="0.15"
      />
      <VisLine
        :x="xAccessor"
        :y="(d: ChartPoint) => d.disk"
        color="#f59e0b"
      />
      <VisAxis type="y" :tick-format="yAxisFormat" :num-ticks="5" />
      <VisAxis type="x" :tick-format="xAxisFormat" :num-ticks="5" />
    </VisXYContainer>
  </div>
</template>
