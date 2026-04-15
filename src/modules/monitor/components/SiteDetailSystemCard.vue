<script setup lang="ts">
import { Braces } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { SiteSnapshot, SystemRawData } from '../types'
import { metricBarClass, metricLevel, metricValueClass } from '../composables/useMetricLevel'
import { formatMonitorDate, formatTimeAgo, formatUptime } from '../composables/useMonitorFormatters'
import SiteStatusBadge from './SiteStatusBadge.vue'
import SystemStateBadge from './SystemStateBadge.vue'

const props = defineProps<{
  snapshot: SiteSnapshot<SystemRawData> | null
}>()

const emit = defineEmits<{
  viewRawResponse: []
}>()

const { t } = useI18n()

const rawData = computed(() => props.snapshot?.rawData ?? null)

function getNumber(
  data: SystemRawData | null,
  snakeKey: string,
  camelKey: string,
): number | null {
  if (!data) return null
  const value = data[snakeKey] ?? data[camelKey]
  return typeof value === 'number' ? value : null
}

function getString(
  data: SystemRawData | null,
  snakeKey: string,
  camelKey: string,
): string | null {
  if (!data) return null
  const value = data[snakeKey] ?? data[camelKey]
  return typeof value === 'string' && value.length > 0 ? value : null
}

function getBoolean(
  data: SystemRawData | null,
  snakeKey: string,
  camelKey: string,
): boolean {
  if (!data) return false
  const value = data[snakeKey] ?? data[camelKey]
  return Boolean(value)
}

const updatesAvailable = computed(() =>
  getNumber(rawData.value, 'updates_available', 'updatesAvailable') ?? 0,
)
const securityUpdates = computed(() =>
  getNumber(rawData.value, 'security_updates', 'securityUpdates'),
)
const rebootRequired = computed(() =>
  getBoolean(rawData.value, 'reboot_required', 'rebootRequired'),
)
const rebootReason = computed(() =>
  getString(rawData.value, 'reboot_reason', 'rebootReason'),
)
const systemState = computed(() =>
  getString(rawData.value, 'system_state', 'systemState'),
)
const rebootDetectedAt = computed(() =>
  getString(rawData.value, 'reboot_detected_at', 'rebootDetectedAt'),
)
const rebootDetectedAtFull = computed(() =>
  formatMonitorDate(rebootDetectedAt.value),
)
const rebootDetectedAtAgo = computed(() =>
  formatTimeAgo(rebootDetectedAt.value),
)
</script>

<template>
  <Card>
    <CardHeader class="flex flex-row items-center justify-between">
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
        <SiteStatusBadge :status="snapshot?.status ?? null" />
      </div>
    </CardHeader>
    <CardContent class="space-y-2 text-sm">
      <template v-if="snapshot">
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.lastPolled', 'Last polled') }}</span>
          <span>{{ formatMonitorDate(snapshot.polledAt) }}</span>
        </div>
        <div v-if="snapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
          {{ snapshot.error }}
        </div>
      </template>
      <template v-if="rawData">
        <div class="space-y-0.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">{{ t('monitor.metrics.cpu', 'CPU') }}</span>
            <span :class="metricValueClass(metricLevel(rawData.cpu_percent))">
              {{ rawData.cpu_percent ?? 0 }}%
            </span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(rawData.cpu_percent))]"
              :style="{ width: `${rawData.cpu_percent ?? 0}%` }"
            />
          </div>
        </div>
        <div class="space-y-0.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">{{ t('monitor.metrics.ram', 'RAM') }}</span>
            <span :class="metricValueClass(metricLevel(rawData.memory?.percent))">
              {{ rawData.memory?.percent ?? 0 }}%
              ({{ ((rawData.memory?.used_mb ?? 0) / 1024).toFixed(1) }} /
              {{ ((rawData.memory?.total_mb ?? 0) / 1024).toFixed(1) }} GB)
            </span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(rawData.memory?.percent))]"
              :style="{ width: `${rawData.memory?.percent ?? 0}%` }"
            />
          </div>
        </div>
        <div class="space-y-0.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">{{ t('monitor.metrics.disk', 'Disk') }}</span>
            <span :class="metricValueClass(metricLevel(rawData.disk?.percent))">
              {{ rawData.disk?.percent ?? 0 }}%
              ({{ rawData.disk?.used_gb?.toFixed(1) ?? '0.0' }} /
              {{ rawData.disk?.total_gb?.toFixed(1) ?? '0.0' }} GB)
            </span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(rawData.disk?.percent))]"
              :style="{ width: `${rawData.disk?.percent ?? 0}%` }"
            />
          </div>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.uptime', 'Uptime') }}</span>
          <span>{{ formatUptime(rawData.uptime_seconds) }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.updates', 'Updates') }}</span>
          <span>{{ updatesAvailable }}</span>
        </div>
        <div v-if="securityUpdates !== null" class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.securityUpdates', 'Security updates') }}</span>
          <span>{{ securityUpdates }}</span>
        </div>
        <div v-if="systemState" class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.systemState', 'System state') }}</span>
          <SystemStateBadge :state="systemState" />
        </div>
        <div v-if="rebootDetectedAt" class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.rebootDetectedAt', 'Reboot detected at') }}</span>
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
        <div
          v-if="rebootRequired"
          class="rounded bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-300"
        >
          {{ t('monitor.rebootRequired', 'Reboot required') }}
          <template v-if="rebootReason">: {{ rebootReason }}</template>
        </div>
      </template>
      <p v-if="!snapshot" class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
