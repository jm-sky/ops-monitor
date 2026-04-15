<script setup lang="ts">
import { Braces } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SiteSnapshot, SystemRawData } from '../types'
import { metricBarClass, metricLevel, metricValueClass } from '../composables/useMetricLevel'
import { formatMonitorDate, formatUptime } from '../composables/useMonitorFormatters'
import SiteStatusBadge from './SiteStatusBadge.vue'

const props = defineProps<{
  snapshot: SiteSnapshot<SystemRawData> | null
}>()

const emit = defineEmits<{
  viewRawResponse: []
}>()

const { t } = useI18n()

const rawData = computed(() => props.snapshot?.rawData ?? null)
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
              ({{ rawData.memory?.used_mb?.toFixed(0) ?? '0' }} /
              {{ rawData.memory?.total_mb?.toFixed(0) ?? '0' }} MB)
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
          <span>{{ rawData.updates_available ?? 0 }}</span>
        </div>
        <div
          v-if="rawData.reboot_required"
          class="rounded bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-300"
        >
          {{ t('monitor.rebootRequired', 'Reboot required') }}:
          {{ rawData.reboot_reason }}
        </div>
      </template>
      <p v-if="!snapshot" class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
