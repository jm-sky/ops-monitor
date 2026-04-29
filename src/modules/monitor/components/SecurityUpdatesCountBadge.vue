<script setup lang="ts">
import { ShieldAlert } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  count: number
}>()

const { t } = useI18n()

const hasSecurityUpdates = computed(() => props.count > 0)

const securityUpdatesTitle = computed(() =>
  t('monitor.securityUpdatesAvailable', { count: props.count }),
)
</script>

<template>
  <span
    v-if="hasSecurityUpdates"
    class="inline-flex items-center gap-1 rounded-md border border-amber-300 bg-amber-100 px-1.5 py-0.5 text-[11px] font-medium text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-300"
    :title="securityUpdatesTitle"
  >
    <ShieldAlert class="size-3" />
    {{ count }}
  </span>
</template>
