<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import type { AlertChannelFilters } from '../types/alerts'

const props = defineProps<{ filters?: AlertChannelFilters | null }>()

const { t } = useI18n()

const chips = computed<string[]>(() => {
  const f = props.filters
  if (!f) return []
  const items: string[] = []

  if (f.alert_types?.length && f.alert_types.length < 4) {
    const labels = f.alert_types.map(type =>
      t(`monitor.alerts.type.${type}`, type),
    )
    items.push(labels.join(', '))
  }

  if (f.min_health_severity === 'failed') {
    items.push(t('monitor.alerts.filters.severity.failed', 'Failed only'))
  }

  if (f.site_ids?.length) {
    items.push(t('monitor.alerts.filters.summary.sites', { n: f.site_ids.length }))
  }

  if (f.tags?.length) {
    items.push(t('monitor.alerts.filters.summary.tags', { n: f.tags.length }))
  }

  if (f.quiet_hours?.enabled) {
    items.push(t('monitor.alerts.filters.summary.quiet', {
      start: f.quiet_hours.start,
      end: f.quiet_hours.end,
    }))
  }

  if (f.re_alert_after_minutes && f.re_alert_after_minutes >= 1) {
    items.push(t('monitor.alerts.filters.summary.cooldown', {
      n: f.re_alert_after_minutes,
    }))
  }

  return items
})
</script>

<template>
  <div v-if="chips.length > 0" class="flex flex-wrap items-center gap-1.5">
    <Badge
      v-for="(chip, idx) in chips"
      :key="idx"
      variant="secondary"
      class="text-[10px] font-normal"
    >
      {{ chip }}
    </Badge>
  </div>
</template>
