<script setup lang="ts">
import { Braces } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { HealthRawData, SiteSnapshot } from '../types'
import { formatMonitorDate } from '../composables/useMonitorFormatters'
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
</script>

<template>
  <Card>
    <CardHeader class="flex flex-row items-center justify-between">
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
    <CardContent class="space-y-2 text-sm">
      <template v-if="snapshot">
        <div class="flex justify-between">
          <span class="text-muted-foreground">{{ t('monitor.lastPolled', 'Last polled') }}</span>
          <span>{{ formatMonitorDate(snapshot.polledAt) }}</span>
        </div>
        <div v-if="snapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
          {{ snapshot.error }}
        </div>
        <template v-if="components.length > 0">
          <div
            v-for="[key, comp] in components"
            :key="key"
            class="flex justify-between"
          >
            <span class="text-muted-foreground capitalize">{{ key }}</span>
            <SiteStatusBadge :status="comp?.status ?? null" />
          </div>
        </template>
      </template>
      <p v-else class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
