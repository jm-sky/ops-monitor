<script setup lang="ts">
import { Globe } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'

const props = defineProps<{
  size: 'sm' | 'default'
  denseMode: boolean
}>()

const { t } = useI18n()

const sizeClass = computed(() =>
  props.size === 'sm'
    ? 'h-5.5 rounded-md px-2 text-[11px] font-medium'
    : 'h-6 rounded-md px-2.5 text-xs font-medium',
)
</script>

<template>
  <Badge
    variant="outline"
    :class="[sizeClass, 'border-sky-500/30 bg-sky-100/50 text-sky-700 dark:bg-sky-950 dark:text-sky-300']"
    :title="t('monitor.internetFacingTitle', 'Exposed to the Internet')"
  >
    <span class="inline-flex items-center gap-1">
      <Globe class="size-3" />
      <template v-if="!props.denseMode">{{ t('monitor.internetFacingBadge', 'Internet') }}</template>
    </span>
  </Badge>
</template>
