<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import type { BadgeVariants } from '@/components/ui/badge'

defineProps<{
  status: string | null
  size?: 'sm' | 'default'
}>()

const { t } = useI18n()

function variant(status: string | null): BadgeVariants['variant'] {
  switch (status) {
    case 'degraded':
    case 'outdated':
    case 'reboot_required':
      return 'outline'
    case 'failed':
      return 'destructive'
    case 'ok':
    case 'up_to_date':
      return 'success'
    default:
      return 'secondary'
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
</script>

<template>
  <Badge :variant="variant(status)">
    {{ label(status) }}
  </Badge>
</template>
