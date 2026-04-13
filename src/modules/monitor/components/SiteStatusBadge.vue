<script setup lang="ts">
import Badge from '@/components/ui/badge/Badge.vue'
import type { BadgeVariants } from '@/components/ui/badge'

defineProps<{
  status: string | null
  size?: 'sm' | 'default'
}>()

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
    case 'degraded': return 'Degraded'
    case 'failed': return 'Failed'
    case 'ok': return 'OK'
    case 'outdated': return 'Outdated'
    case 'reboot_required': return 'Reboot required'
    case 'up_to_date': return 'Up to date'
    default: return status ?? 'Unknown'
  }
}
</script>

<template>
  <Badge :variant="variant(status)">
    {{ label(status) }}
  </Badge>
</template>
