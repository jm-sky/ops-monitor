<script setup lang="ts">
import { AlertTriangle, Braces } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { HealthRawData, SiteSnapshot } from '../types'
import { formatMonitorDate } from '../composables/useMonitorFormatters'
import ComponentHealthBadge from './ComponentHealthBadge.vue'
import SiteStatusBadge from './SiteStatusBadge.vue'

const props = defineProps<{
  snapshot: SiteSnapshot<HealthRawData> | null
}>()

const emit = defineEmits<{
  viewRawResponse: []
}>()

const { t } = useI18n()

const components = computed(() => {
  if (!props.snapshot?.rawData?.components) return []
  return Object.entries(props.snapshot.rawData.components)
})

const metaEntries = computed(() => {
  const meta = props.snapshot?.rawData?.meta
  if (!meta) return []
  return Object.entries(meta)
})

const mismatches = computed(() => props.snapshot?.metaMismatches ?? [])
</script>

<template>
  <Card class="h-full">
    <CardHeader class="flex flex-row items-center justify-between pb-3">
      <CardTitle>{{ t('monitor.health', 'Health') }}</CardTitle>
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
    <CardContent class="space-y-4 text-sm">
      <template v-if="snapshot">
        <div class="grid grid-cols-[9rem_1fr] items-center gap-2">
          <span class="text-muted-foreground">{{ t('monitor.lastPolled', 'Last polled') }}</span>
          <span class="text-right">{{ formatMonitorDate(snapshot.polledAt) }}</span>
        </div>
        <div v-if="snapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
          {{ snapshot.error }}
        </div>
        <template v-if="components.length > 0">
          <div class="border-t pt-2" />
          <div
            v-for="[key, comp] in components"
            :key="key"
            class="grid grid-cols-[9rem_minmax(0,1fr)_auto] items-center gap-x-3 gap-y-1"
          >
            <span class="text-muted-foreground capitalize">{{ key }}</span>
            <span
              v-if="comp?.reason"
              class="truncate text-right text-xs text-amber-700 dark:text-amber-400"
            >
              {{ comp.reason }}
            </span>
            <span v-else />
            <div class="flex justify-end">
              <ComponentHealthBadge
                :component-name="key"
                :status="comp?.status ?? null"
                :raw-data="snapshot?.rawData ?? null"
              />
            </div>
          </div>
        </template>
        <template v-if="metaEntries.length > 0">
          <div class="border-t pt-2" />
          <div
            v-for="[key, value] in metaEntries"
            :key="key"
            class="grid grid-cols-[9rem_1fr] items-center gap-2"
          >
            <span class="text-muted-foreground">{{ key }}</span>
            <span class="text-right font-mono text-xs">{{ value }}</span>
          </div>
        </template>
        <div
          v-if="mismatches.length > 0"
          class="rounded border border-amber-400/40 bg-amber-50 px-3 py-2 dark:bg-amber-950/30"
        >
          <div class="mb-1 flex items-center gap-1.5 text-amber-700 dark:text-amber-400">
            <AlertTriangle class="size-3.5 shrink-0" />
            <span class="text-xs font-medium">{{ t('monitor.metaMismatch', 'Expected meta mismatch') }}</span>
          </div>
          <ul class="space-y-0.5 text-xs text-amber-700 dark:text-amber-400">
            <li v-for="msg in mismatches" :key="msg">
              {{ msg }}
            </li>
          </ul>
        </div>
      </template>
      <p v-else class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
