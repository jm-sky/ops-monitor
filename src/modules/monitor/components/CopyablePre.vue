<script setup lang="ts">
import { refAutoReset } from '@vueuse/core'
import { Check, Copy } from 'lucide-vue-next'
import { computed, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { copyToClipboard } from '@/lib/copyToClipboard'

const props = defineProps<{
  value: string
}>()

const { t } = useI18n()
const preRef = useTemplateRef<HTMLPreElement>('preRef')
const copied = refAutoReset(false, 3000)

const hasValue = computed(() => Boolean(props.value))

async function copyValue() {
  if (!props.value) return

  const result = await copyToClipboard(props.value, {
    selectElement: preRef.value ?? undefined,
  })

  if (result === 'copied') {
    copied.value = true
    toast.success(t('common.copyToClipboard.copied', 'Copied to clipboard'))
    return
  }

  if (result === 'selected') {
    copied.value = true
    toast.info(t('common.copyToClipboard.manualFallback', 'Text selected — press Ctrl+C to copy'))
    return
  }

  toast.error(t('common.copyFailed', 'Failed to copy'))
}
</script>

<template>
  <div class="relative min-w-0">
    <Tooltip :delay-duration="150">
      <TooltipTrigger as-child>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          class="absolute top-2 right-2 size-8"
          :disabled="!hasValue"
          :aria-label="copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy')"
          @click="copyValue"
        >
          <Check v-if="copied" class="size-4" />
          <Copy v-else class="size-4" />
        </Button>
      </TooltipTrigger>
      <TooltipContent side="left">
        {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
      </TooltipContent>
    </Tooltip>
    <pre
      ref="preRef"
      class="rounded-md bg-muted p-4 pr-12 text-xs leading-5 font-mono whitespace-pre-wrap wrap-break-word max-h-[min(70vh,600px)] overflow-y-auto overflow-x-hidden"
    >{{ value }}</pre>
  </div>
</template>
