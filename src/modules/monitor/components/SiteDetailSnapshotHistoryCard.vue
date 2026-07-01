<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Pagination from '@/components/data-table/Pagination.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { HealthRawData, Site, SiteSnapshot, SslRawData, SystemRawData } from '../types'
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
const hasSsl = computed(() => !!props.site.sslCheckUrl)
const availableTabsCount = computed(() =>
  [hasHealth.value, hasSystem.value, hasSsl.value].filter(Boolean).length,
)
const defaultTab = computed(() => {
  if (hasHealth.value) return 'health'
  if (hasSystem.value) return 'system'
  return 'ssl'
})
const activeTab = ref(defaultTab.value)

const showHistory = ref(false)

const PAGE_SIZE_OPTIONS = [10, 50, 100]

const healthPage = ref(1)
const healthPageSize = ref(10)
const healthOffset = computed(() => (healthPage.value - 1) * healthPageSize.value)

const systemPage = ref(1)
const systemPageSize = ref(10)
const systemOffset = computed(() => (systemPage.value - 1) * systemPageSize.value)

const sslPage = ref(1)
const sslPageSize = ref(10)
const sslOffset = computed(() => (sslPage.value - 1) * sslPageSize.value)

function setHealthPage(p: number) {
  healthPage.value = p
}

function setHealthPageSize(s: number) {
  healthPageSize.value = s
  healthPage.value = 1
}

function setSystemPage(p: number) {
  systemPage.value = p
}

function setSystemPageSize(s: number) {
  systemPageSize.value = s
  systemPage.value = 1
}

function setSslPage(p: number) {
  sslPage.value = p
}

function setSslPageSize(s: number) {
  sslPageSize.value = s
  sslPage.value = 1
}

// ── Health snapshots ────────────────────────────────────────────────────────

const { data: healthPageData, isLoading: healthLoading } = useQuery({
  queryKey: computed(() => monitorQueryKeys.snapshotsPage(
    props.site.id,
    'health',
    healthPageSize.value,
    healthOffset.value,
  )),
  queryFn: () => monitorService.getSnapshotsPage(props.site.id, 'health', {
    limit: healthPageSize.value,
    offset: healthOffset.value,
  }),
  enabled: computed(() => showHistory.value && hasHealth.value),
  placeholderData: previousData => previousData,
})

const healthSnapshots = computed(() => (healthPageData.value?.items ?? []) as SiteSnapshot<HealthRawData>[])
const healthTotal = computed(() => healthPageData.value?.total ?? 0)

function nonOkComponents(snap: SiteSnapshot<HealthRawData>): string[] {
  const components = snap.rawData?.components ?? {}
  return Object.entries(components)
    .filter(([, c]) => c?.status && c.status !== 'ok')
    .map(([key]) => key)
}

// ── System snapshots ────────────────────────────────────────────────────────

const { data: systemPageData, isLoading: systemLoading } = useQuery({
  queryKey: computed(() => monitorQueryKeys.snapshotsPage(
    props.site.id,
    'system',
    systemPageSize.value,
    systemOffset.value,
  )),
  queryFn: () => monitorService.getSnapshotsPage(props.site.id, 'system', {
    limit: systemPageSize.value,
    offset: systemOffset.value,
  }),
  enabled: computed(() => showHistory.value && hasSystem.value),
  placeholderData: previousData => previousData,
})

const systemSnapshots = computed(() => (systemPageData.value?.items ?? []) as SiteSnapshot<SystemRawData>[])
const systemTotal = computed(() => systemPageData.value?.total ?? 0)

// ── SSL snapshots ───────────────────────────────────────────────────────────

const { data: sslPageData, isLoading: sslLoading } = useQuery({
  queryKey: computed(() => monitorQueryKeys.snapshotsPage(
    props.site.id,
    'ssl',
    sslPageSize.value,
    sslOffset.value,
  )),
  queryFn: () => monitorService.getSnapshotsPage(props.site.id, 'ssl', {
    limit: sslPageSize.value,
    offset: sslOffset.value,
  }),
  enabled: computed(() => showHistory.value && hasSsl.value),
  placeholderData: previousData => previousData,
})

const sslSnapshots = computed(() => (sslPageData.value?.items ?? []) as SiteSnapshot<SslRawData>[])
const sslTotal = computed(() => sslPageData.value?.total ?? 0)
</script>

<template>
  <Card :class="{ 'py-2 bg-muted/50 opacity-80': !showHistory }">
    <CardHeader :class="showHistory ? 'pb-3': 'pb-0 gap-0'">
      <div class="flex items-center justify-between gap-3">
        <CardTitle>{{ t('monitor.history.title', 'History') }}</CardTitle>
        <Button
          variant="outline"
          size="sm"
          @click="showHistory = !showHistory"
        >
          {{ showHistory ? t('monitor.history.hide', 'Hide history') : t('monitor.history.show', 'Show history') }}
        </Button>
      </div>
    </CardHeader>
    <CardContent v-if="showHistory">
      <Tabs v-model="activeTab">
        <TabsList v-if="availableTabsCount > 1" class="mb-4">
          <TabsTrigger v-if="hasHealth" value="health">
            {{ t('monitor.health', 'Health') }}
          </TabsTrigger>
          <TabsTrigger v-if="hasSystem" value="system">
            {{ t('monitor.system', 'System') }}
          </TabsTrigger>
          <TabsTrigger v-if="hasSsl" value="ssl">
            {{ t('monitor.ssl', 'SSL') }}
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
          <div v-else class="space-y-4">
            <div class="overflow-x-auto">
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

            <Pagination
              :page="healthPage"
              :page-size="healthPageSize"
              :total="healthTotal"
              :page-size-options="PAGE_SIZE_OPTIONS"
              @update:page="setHealthPage"
              @update:page-size="setHealthPageSize"
            />
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
            <!-- Table -->
            <div class="space-y-4">
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

              <Pagination
                :page="systemPage"
                :page-size="systemPageSize"
                :total="systemTotal"
                :page-size-options="PAGE_SIZE_OPTIONS"
                @update:page="setSystemPage"
                @update:page-size="setSystemPageSize"
              />
            </div>
          </template>
        </TabsContent>

        <!-- ── SSL history ────────────────────────────────────────────── -->
        <TabsContent value="ssl">
          <div v-if="sslLoading" class="py-6 text-center text-sm text-muted-foreground">
            {{ t('common.loading', 'Loading...') }}
          </div>
          <div v-else-if="!sslSnapshots?.length" class="py-6 text-center text-sm text-muted-foreground">
            {{ t('monitor.noData', 'No data yet') }}
          </div>
          <div v-else class="space-y-4">
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b text-left text-xs text-muted-foreground">
                    <th class="pb-2 pr-4 font-medium">
                      {{ t('monitor.history.time', 'Time') }}
                    </th>
                    <th class="pb-2 pr-4 font-medium">
                      {{ t('monitor.history.status', 'Status') }}
                    </th>
                    <th class="pb-2 pr-4 font-medium">
                      {{ t('monitor.sslDaysRemaining', 'Days remaining') }}
                    </th>
                    <th class="pb-2 font-medium">
                      {{ t('monitor.history.issues', 'Issues') }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="snap in sslSnapshots"
                    :key="snap.id"
                    class="border-b last:border-0"
                  >
                    <td class="py-2 pr-4 text-xs text-muted-foreground whitespace-nowrap">
                      {{ formatMonitorDate(snap.polledAt) }}
                    </td>
                    <td class="py-2 pr-4">
                      <SiteStatusBadge :status="snap.status" />
                    </td>
                    <td class="py-2 pr-4 text-xs">
                      {{ snap.rawData?.days_remaining ?? '—' }}
                    </td>
                    <td class="py-2 text-xs">
                      <span v-if="snap.error" class="text-destructive">{{ snap.error }}</span>
                      <span v-else class="text-muted-foreground">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <Pagination
              :page="sslPage"
              :page-size="sslPageSize"
              :total="sslTotal"
              :page-size-options="PAGE_SIZE_OPTIONS"
              @update:page="setSslPage"
              @update:page-size="setSslPageSize"
            />
          </div>
        </TabsContent>
      </Tabs>
    </CardContent>
  </Card>
</template>
