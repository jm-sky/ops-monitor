<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { copyToClipboard } from '@/lib/copyToClipboard'
import type { HealthRawData } from '../types'
import {
  buildComponentIssuePayload,
  isComponentIssueCopyable,
} from '../utils/buildComponentIssuePayload'
import SiteStatusBadge from './SiteStatusBadge.vue'

const props = defineProps<{
  componentName: string
  status: string | null
  rawData: HealthRawData | null
  size?: 'sm' | 'default'
}>()

const { t } = useI18n()

const component = computed(() => props.rawData?.components?.[props.componentName])

const copyable = computed(() =>
  isComponentIssueCopyable(
    component.value?.status,
    component.value?.reason,
    props.rawData?.errors,
    props.componentName,
  ),
)

async function copyIssueContext() {
  if (!props.rawData) return

  const payload = buildComponentIssuePayload(props.rawData, props.componentName)
  if (!payload) return

  const result = await copyToClipboard(JSON.stringify(payload, null, 2))

  if (result === 'copied') {
    toast.success(t('common.copyToClipboard.copied', 'Copied to clipboard'))
    return
  }

  toast.error(t('common.copyFailed', 'Failed to copy'))
}
</script>

<template>
  <button
    v-if="copyable"
    type="button"
    class="cursor-pointer rounded-md hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    :title="t('monitor.copyComponentIssue', 'Click to copy issue context')"
    @click="copyIssueContext"
  >
    <SiteStatusBadge :status="status" :size="size" />
  </button>
  <SiteStatusBadge v-else :status="status" :size="size" />
</template>
