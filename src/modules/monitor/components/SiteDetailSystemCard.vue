<script setup lang="ts">
import { AlertTriangle, Braces } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { SiteSnapshot, SystemRawData } from '../types'
import { metricBarClass, metricLevel, metricValueClass } from '../composables/useMetricLevel'
import { formatGb, formatMbToGb, formatMonitorDate, formatTimeAgo, formatUptime } from '../composables/useMonitorFormatters'
import { resolveSystemSnapshotStatus } from '../utils/resolveUpdateStatus'
import SiteStatusBadge from './SiteStatusBadge.vue'
import SystemMetricsChart from './SystemMetricsChart.vue'
import SystemStateBadge from './SystemStateBadge.vue'

const props = defineProps<{
  snapshot: SiteSnapshot<SystemRawData> | null
  hasSystemUrl?: boolean
}>()

const emit = defineEmits<{
  viewRawResponse: []
  configureUrl: []
}>()

const { t } = useI18n()

const rawData = computed(() => props.snapshot?.rawData ?? null)

const updatesAvailable = computed(() => rawData.value?.updates_available ?? 0)
const securityUpdates = computed(() => rawData.value?.security_updates ?? null)
const rebootRequired = computed(() => rawData.value?.reboot_required ?? false)
const rebootReason = computed(() => rawData.value?.reboot_reason ?? null)
const systemState = computed(() => rawData.value?.system_state ?? null)
const rebootDetectedAt = computed(() => rawData.value?.reboot_detected_at ?? null)
const rebootDetectedAtFull = computed(() =>
  formatMonitorDate(rebootDetectedAt.value),
)
const rebootDetectedAtAgo = computed(() =>
  formatTimeAgo(rebootDetectedAt.value),
)

const systemDisplayStatus = computed(() =>
  resolveSystemSnapshotStatus(
    props.snapshot?.status,
    securityUpdates.value ?? undefined,
  ),
)
</script>

<template>
  <Card class="h-full" :class="{ 'py-2 bg-muted/50 opacity-80': !hasSystemUrl }">
    <CardHeader class="flex flex-row items-center justify-between" :class="hasSystemUrl ? 'pb-3': 'pb-0 gap-0'">
      <CardTitle>{{ t('monitor.system', 'System') }}</CardTitle>
      <div class="flex items-center gap-2">
        <Button
          v-if="snapshot?.rawData"
          variant="outline"
          size="xs"
          :aria-label="t('monitor.viewRawResponse', 'View full response')"
          :title="t('monitor.viewRawResponse', 'View full response')"
          class="h-6"
          @click="emit('viewRawResponse')"
        >
          <Braces class="size-3" /> {{ t('monitor.fullResponse', 'Full response') }}
        </Button>
        <SiteStatusBadge v-if="hasSystemUrl" :status="systemDisplayStatus" />
        <Button
          v-else
          variant="outline"
          size="sm"
          @click="emit('configureUrl')"
        >
          {{ t('monitor.configureUrl', 'Configure URL') }}
        </Button>
      </div>
    </CardHeader>
    <CardContent v-if="hasSystemUrl" class="space-y-4 text-sm">
      <template v-if="snapshot">
        <div class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.lastPolled', 'Last polled') }}</span>
          <span class="text-right">{{ formatMonitorDate(snapshot.polledAt) }}</span>
        </div>
        <div v-if="snapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
          {{ snapshot.error }}
        </div>
      </template>
      <template v-if="rawData">
        <SystemMetricsChart :site-id="snapshot?.siteId ?? null" />

        <div class="space-y-1.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">{{ t('monitor.metrics.cpu', 'CPU') }}</span>
            <span :class="metricValueClass(metricLevel(rawData.cpu_percent))">
              {{ rawData.cpu_percent ?? 0 }}%
            </span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted/60">
            <div
              :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(rawData.cpu_percent))]"
              :style="{ width: `${rawData.cpu_percent ?? 0}%` }"
            />
          </div>
        </div>
        <div class="space-y-1.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">{{ t('monitor.metrics.ram', 'RAM') }}</span>
            <span :class="metricValueClass(metricLevel(rawData.memory?.percent))">
              {{ rawData.memory?.percent ?? 0 }}%
              ({{ formatMbToGb(rawData.memory?.used_mb) }} /
              {{ formatMbToGb(rawData.memory?.total_mb) }} GB)
            </span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted/60">
            <div
              :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(rawData.memory?.percent))]"
              :style="{ width: `${rawData.memory?.percent ?? 0}%` }"
            />
          </div>
        </div>
        <div class="space-y-1.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">{{ t('monitor.metrics.disk', 'Disk') }}</span>
            <span :class="metricValueClass(metricLevel(rawData.disk?.percent))">
              {{ rawData.disk?.percent ?? 0 }}%
              ({{ formatGb(rawData.disk?.used_gb) }} /
              {{ formatGb(rawData.disk?.total_gb) }} GB)
            </span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted/60">
            <div
              :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(rawData.disk?.percent))]"
              :style="{ width: `${rawData.disk?.percent ?? 0}%` }"
            />
          </div>
        </div>
        <div class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.uptime', 'Uptime') }}</span>
          <span class="text-right">{{ formatUptime(rawData.uptime_seconds) }}</span>
        </div>
        <div class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.updates', 'Updates') }}</span>
          <span class="text-right">{{ updatesAvailable }}</span>
        </div>
        <div v-if="securityUpdates !== null" class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.securityUpdates', 'Security updates') }}</span>
          <span class="text-right">{{ securityUpdates }}</span>
        </div>
        <div v-if="systemState" class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.systemState', 'System state') }}</span>
          <div class="flex justify-end">
            <SystemStateBadge :state="systemState" :security-updates="securityUpdates" />
          </div>
        </div>
        <div v-if="rebootDetectedAt" class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.rebootDetectedAt', 'Reboot detected at') }}</span>
          <div class="flex justify-end">
            <Tooltip :delay-duration="150">
              <TooltipTrigger as-child>
                <span class="cursor-help underline decoration-dotted underline-offset-4">
                  {{ rebootDetectedAtAgo }}
                </span>
              </TooltipTrigger>
              <TooltipContent side="top">
                {{ rebootDetectedAtFull }}
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
        <div
          v-if="rebootRequired"
          class="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300"
        >
          <AlertTriangle class="size-3.5 shrink-0" />
          {{ t('monitor.rebootRequired', 'Reboot required') }}
          <template v-if="rebootReason">
            : {{ rebootReason }}
          </template>
        </div>
      </template>
      <p v-if="!snapshot" class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
