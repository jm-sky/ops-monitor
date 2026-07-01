<script setup lang="ts">
import { Braces } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SiteSnapshot, SslRawData } from '../types'
import { formatMonitorDate, formatTimeAgo } from '../composables/useMonitorFormatters'
import SiteStatusBadge from './SiteStatusBadge.vue'

defineProps<{
  snapshot: SiteSnapshot<SslRawData> | null
}>()

const emit = defineEmits<{
  viewRawResponse: []
}>()

const { t } = useI18n()
</script>

<template>
  <Card class="h-full">
    <CardHeader class="flex flex-row items-center justify-between pb-3">
      <CardTitle>{{ t('monitor.ssl', 'SSL') }}</CardTitle>
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
        <template v-else-if="snapshot.rawData">
          <div class="grid grid-cols-[9rem_1fr] items-center gap-2">
            <span class="text-muted-foreground">{{ t('monitor.sslDaysRemaining', 'Days remaining') }}</span>
            <span class="text-right">{{ snapshot.rawData.days_remaining ?? '—' }}</span>
          </div>
          <div class="grid grid-cols-[9rem_1fr] items-center gap-2">
            <span class="text-muted-foreground">{{ t('monitor.sslExpiresAt', 'Expires') }}</span>
            <span class="text-right">
              {{ formatMonitorDate(snapshot.rawData.not_after) }}
              <span class="text-muted-foreground">({{ formatTimeAgo(snapshot.rawData.not_after) }})</span>
            </span>
          </div>
          <div v-if="snapshot.rawData.issuer" class="grid grid-cols-[9rem_1fr] items-center gap-2">
            <span class="text-muted-foreground">{{ t('monitor.sslIssuer', 'Issuer') }}</span>
            <span class="truncate text-right" :title="snapshot.rawData.issuer">{{ snapshot.rawData.issuer }}</span>
          </div>
          <div v-if="snapshot.rawData.subject" class="grid grid-cols-[9rem_1fr] items-center gap-2">
            <span class="text-muted-foreground">{{ t('monitor.sslSubject', 'Subject') }}</span>
            <span class="truncate text-right" :title="snapshot.rawData.subject">{{ snapshot.rawData.subject }}</span>
          </div>
        </template>
      </template>
      <p v-else class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
