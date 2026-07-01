<script setup lang="ts">
import { ShieldAlert } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import {
  statusColorClass,
  statusLabelFallback,
  statusLabelKey,
  statusShowsShieldIcon,
} from '../utils/statusStyles'

const props = defineProps<{
  status: string | null
  size?: 'sm' | 'default'
}>()

const { t } = useI18n()

const label = computed(() => {
  const key = statusLabelKey(props.status)
  if (key) return t(key, statusLabelFallback(props.status))
  return props.status ?? t('common.unknown', 'Unknown')
})

const showShield = computed(() => statusShowsShieldIcon(props.status))

const sizeClass = computed(() =>
  props.size === 'sm'
    ? 'h-5 rounded-md px-2 text-[11px] font-medium'
    : 'h-6 rounded-md px-2.5 text-xs font-medium',
)
</script>

<template>
  <Badge variant="outline" :class="[sizeClass, statusColorClass(status)]">
    <span class="inline-flex items-center gap-1">
      <ShieldAlert v-if="showShield" class="size-3 shrink-0" />
      {{ label }}
    </span>
  </Badge>
</template>
