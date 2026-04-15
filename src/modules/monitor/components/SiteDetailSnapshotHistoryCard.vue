<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { VisArea, VisAxis, VisLine, VisXYContainer } from '@unovis/vue'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { HealthRawData, Site, SiteSnapshot, SystemRawData } from '../types'
import { metricLevel, metricValueClass } from '../composables/useMetricLevel'
import { formatMonitorDate } from '../composables/useMonitorFormatters'
import { monitorQueryKeys } from '../services/monitorQueries'
import { monitorService } from '../services/monitorService'
import SiteStatusBadge from './SiteStatusBadge.vue'

const props = defineProps<{
  site: Site
}>()

const { t } = useI18n()

const hasHealth = computed(() => !!props.site.healthUrl)
const hasSystem = computed(() => !!props.site.systemUrl)
const defaultTab = computed(() => (hasHealth.value ? 'health' : 'system'))
const activeTab = ref(defaultTab.value)

// ── Health snapshots ────────────────────────────────────────────────────────

const { data: healthSnapshots, isLoading: healthLoading } = useQuery<SiteSnapshot<HealthRawData>[]>({
  queryKey: computed(() => monitorQueryKeys.snapshots(props.site.id, 'health')),
  queryFn: () => monitorService.getSnapshots(props.site.id, 'health', 100),
  enabled: hasHealth,
})

function nonOkComponents(snap: SiteSnapshot<HealthRawData>): string[] {
  const components = snap.rawData?.components ?? {}
  return Object.entries(components)
    .filter(([, c]) => c?.status && c.status !== 'ok')
    .map(([key]) => key)
}

// ── System snapshots ────────────────────────────────────────────────────────

const { data: systemSnapshots, isLoading: systemLoading } = useQuery<SiteSnapshot<SystemRawData>[]>({
  queryKey: computed(() => monitorQueryKeys.snapshots(props.site.id, 'system')),
  queryFn: () => monitorService.getSnapshots(props.site.id, 'system', 100),
  enabled: hasSystem,
})

interface ChartPoint {
  index: number
  cpu: number
  ram: number
  disk: number
  label: string
}

const CHART_LIMIT = 48

const chartData = computed<ChartPoint[]>(() => {
  if (!systemSnapshots.value) return []
  return [...systemSnapshots.value]
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
  <Card>
    <CardHeader class="pb-3">
      <CardTitle>{{ t('monitor.history.title', 'History') }}</CardTitle>
    </CardHeader>
    <CardContent>
      <Tabs v-model="activeTab">
        <TabsList v-if="hasHealth && hasSystem" class="mb-4">
          <TabsTrigger value="health">
            {{ t('monitor.health', 'Health') }}
          </TabsTrigger>
          <TabsTrigger value="system">
            {{ t('monitor.system', 'System') }}
          </TabsTrigger>
        </TabsList>

        <!-- ── Health history ─────────────────────────────────────────── -->
        <TabsContent value="health">
          <div v-if="healthLoading" class="py-6 text-center text-sm text-muted-foreground">
            {{ t('common.loading', 'Loading...') }}
          </div>
          <div v-else-if="!healthSnapshots?.length" class="py-6 text-center text-sm text-muted-foreground">
            {{ t('monitor.noData', 'No data yet') }}
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b text-left text-xs text-muted-foreground">
                  <th class="pb-2 pr-4 font-medium">
                    {{ t('monitor.history.time', 'Time') }}
                  </th>
                  <th class="pb-2 pr-4 font-medium">
                    {{ t('monitor.history.status', 'Status') }}
                  </th>
                  <th class="pb-2 font-medium">
                    {{ t('monitor.history.issues', 'Issues') }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="snap in healthSnapshots"
                  :key="snap.id"
                  class="border-b last:border-0"
                >
                  <td class="py-2 pr-4 text-xs text-muted-foreground whitespace-nowrap">
                    {{ formatMonitorDate(snap.polledAt) }}
                  </td>
                  <td class="py-2 pr-4">
                    <SiteStatusBadge :status="snap.status" />
                  </td>
                  <td class="py-2 text-xs">
                    <span v-if="snap.error" class="text-destructive">{{ snap.error }}</span>
                    <span v-else-if="nonOkComponents(snap).length" class="text-amber-600 dark:text-amber-400">
                      {{ nonOkComponents(snap).join(', ') }}
                    </span>
                    <span v-else class="text-muted-foreground">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </TabsContent>

        <!-- ── System history ─────────────────────────────────────────── -->
        <TabsContent value="system">
          <div v-if="systemLoading" class="py-6 text-center text-sm text-muted-foreground">
            {{ t('common.loading', 'Loading...') }}
          </div>
          <div v-else-if="!systemSnapshots?.length" class="py-6 text-center text-sm text-muted-foreground">
            {{ t('monitor.noData', 'No data yet') }}
          </div>
          <template v-else>
            <!-- Chart -->
            <div v-if="chartData.length > 1" class="mb-6">
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

            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b text-left text-xs text-muted-foreground">
                    <th class="pb-2 pr-4 font-medium">
                      {{ t('monitor.history.time', 'Time') }}
                    </th>
                    <th class="pb-2 pr-3 font-medium">
                      {{ t('monitor.metrics.cpu', 'CPU') }}
                    </th>
                    <th class="pb-2 pr-3 font-medium">
                      {{ t('monitor.metrics.ram', 'RAM') }}
                    </th>
                    <th class="pb-2 pr-4 font-medium">
                      {{ t('monitor.metrics.disk', 'Disk') }}
                    </th>
                    <th class="pb-2 font-medium">
                      {{ t('monitor.history.status', 'Status') }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="snap in systemSnapshots"
                    :key="snap.id"
                    class="border-b last:border-0"
                  >
                    <td class="py-2 pr-4 text-xs text-muted-foreground whitespace-nowrap">
                      {{ formatMonitorDate(snap.polledAt) }}
                    </td>
                    <td class="py-2 pr-3">
                      <span
                        class="text-xs"
                        :class="metricValueClass(metricLevel(snap.rawData?.cpu_percent))"
                      >
                        {{ snap.rawData?.cpu_percent != null ? `${snap.rawData.cpu_percent}%` : '—' }}
                      </span>
                    </td>
                    <td class="py-2 pr-3">
                      <span
                        class="text-xs"
                        :class="metricValueClass(metricLevel(snap.rawData?.memory?.percent))"
                      >
                        {{ snap.rawData?.memory?.percent != null ? `${snap.rawData.memory.percent}%` : '—' }}
                      </span>
                    </td>
                    <td class="py-2 pr-4">
                      <span
                        class="text-xs"
                        :class="metricValueClass(metricLevel(snap.rawData?.disk?.percent))"
                      >
                        {{ snap.rawData?.disk?.percent != null ? `${snap.rawData.disk.percent}%` : '—' }}
                      </span>
                    </td>
                    <td class="py-2">
                      <SiteStatusBadge :status="snap.status" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </TabsContent>
      </Tabs>
    </CardContent>
  </Card>
</template>
