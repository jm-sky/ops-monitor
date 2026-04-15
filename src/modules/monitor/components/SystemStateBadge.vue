<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'

const props = defineProps<{
  state: string | null
}>()

const { t } = useI18n()

const colorClass = computed(() => {
  switch (props.state) {
    case 'up_to_date':
      return 'border-emerald-200 bg-emerald-100 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
    case 'outdated':
      return 'border-amber-200 bg-amber-100 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300'
    default:
      return ''
  }
})

const label = computed(() => {
  switch (props.state) {
    case 'up_to_date':
      return t('monitor.status.upToDate', 'Up to date')
    case 'outdated':
      return t('monitor.status.outdated', 'Outdated')
    default:
      return props.state ?? t('common.unknown', 'Unknown')
  }
})
</script>

<template>
  <Badge variant="outline" :class="colorClass">
    {{ label }}
  </Badge>
</template>
