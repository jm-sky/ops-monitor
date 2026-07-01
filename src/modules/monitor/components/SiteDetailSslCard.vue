<script setup lang="ts">
import { Braces } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
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

function extractCn(dn: string | null | undefined): string {
  if (!dn) return '—'
  const match = /(?:^|,)\s*CN=([^,]+)/.exec(dn)
  return match?.[1] ?? dn
}
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
    <CardContent class="space-y-3 text-sm">
      <template v-if="snapshot">
        <div v-if="snapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
          {{ snapshot.error }}
        </div>
        <div class="grid grid-cols-2 gap-x-4 gap-y-3">
          <div>
            <div class="text-xs text-muted-foreground">
              {{ t('monitor.lastPolled', 'Last polled') }}
            </div>
            <div>{{ formatMonitorDate(snapshot.polledAt) }}</div>
          </div>
          <template v-if="!snapshot.error && snapshot.rawData">
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('monitor.sslExpiresAt', 'Expires') }}
              </div>
              <div>
                {{ formatMonitorDate(snapshot.rawData.not_after) }}
                <span class="text-xs text-muted-foreground">({{ formatTimeAgo(snapshot.rawData.not_after) }})</span>
              </div>
            </div>
            <div v-if="snapshot.rawData.issuer" class="min-w-0">
              <div class="text-xs text-muted-foreground">
                {{ t('monitor.sslIssuer', 'Issuer') }}
              </div>
              <Tooltip :delay-duration="150">
                <TooltipTrigger as-child>
                  <div class="w-fit max-w-full cursor-help truncate underline decoration-dotted underline-offset-4">
                    {{ extractCn(snapshot.rawData.issuer) }}
                  </div>
                </TooltipTrigger>
                <TooltipContent side="top">
                  {{ snapshot.rawData.issuer }}
                </TooltipContent>
              </Tooltip>
            </div>
            <div v-if="snapshot.rawData.subject" class="min-w-0">
              <div class="text-xs text-muted-foreground">
                {{ t('monitor.sslSubject', 'Subject') }}
              </div>
              <Tooltip :delay-duration="150">
                <TooltipTrigger as-child>
                  <div class="w-fit max-w-full cursor-help truncate underline decoration-dotted underline-offset-4">
                    {{ extractCn(snapshot.rawData.subject) }}
                  </div>
                </TooltipTrigger>
                <TooltipContent side="top">
                  {{ snapshot.rawData.subject }}
                </TooltipContent>
              </Tooltip>
            </div>
          </template>
        </div>
      </template>
      <p v-else class="text-muted-foreground">
        {{ t('monitor.noData', 'No data yet') }}
      </p>
    </CardContent>
  </Card>
</template>
