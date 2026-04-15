<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'

const props = defineProps<{
  status: string | null
  size?: 'sm' | 'default'
}>()

const { t } = useI18n()

function colorClass(status: string | null): string {
  switch (status) {
    case 'degraded':
    case 'outdated':
    case 'reboot_required':
      return 'border-amber-200 bg-amber-100 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300'
    case 'failed':
      return 'border-destructive/40 bg-destructive/10 text-destructive'
    case 'ok':
    case 'up_to_date':
      return 'border-emerald-200 bg-emerald-100 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
    default:
      return ''
  }
}

function label(status: string | null): string {
  switch (status) {
    case 'degraded': return t('monitor.status.degraded', 'Degraded')
    case 'failed': return t('monitor.status.failed', 'Failed')
    case 'ok': return t('monitor.status.ok', 'OK')
    case 'outdated': return t('monitor.status.outdated', 'Outdated')
    case 'reboot_required': return t('monitor.status.rebootRequired', 'Reboot required')
    case 'up_to_date': return t('monitor.status.upToDate', 'Up to date')
    default: return status ?? t('common.unknown', 'Unknown')
  }
}

const sizeClass = computed(() =>
  props.size === 'sm'
    ? 'h-5 rounded-md px-2 text-[11px] font-medium'
    : 'h-6 rounded-md px-2.5 text-xs font-medium',
)
</script>

<template>
  <Badge variant="outline" :class="[sizeClass, colorClass(status)]">
    {{ label(status) }}
  </Badge>
</template>
