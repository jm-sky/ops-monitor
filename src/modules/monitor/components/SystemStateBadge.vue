<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { resolveSystemState } from '../utils/resolveUpdateStatus'
import { statusColorClass, statusLabelFallback, statusLabelKey } from '../utils/statusStyles'

const props = defineProps<{
  state: string | null
  securityUpdates?: number | null
}>()

const { t } = useI18n()

const displayState = computed(() =>
  resolveSystemState(props.state, props.securityUpdates ?? undefined),
)

const colorClass = computed(() => statusColorClass(displayState.value ?? props.state))

const label = computed(() => {
  const status = displayState.value ?? props.state
  const key = statusLabelKey(status)
  if (key) return t(key, statusLabelFallback(status))
  return status ?? t('common.unknown', 'Unknown')
})
</script>

<template>
  <Badge variant="outline" class="h-6 rounded-md px-2.5 text-xs font-medium" :class="colorClass">
    {{ label }}
  </Badge>
</template>
