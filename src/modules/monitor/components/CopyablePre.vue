<script setup lang="ts">
import { refAutoReset, useClipboard } from '@vueuse/core'
import { Check, Copy } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

const props = defineProps<{
  value: string
}>()

const { t } = useI18n()
const { copy } = useClipboard({ legacy: true })
const copied = refAutoReset(false, 3000)

const hasValue = computed(() => Boolean(props.value))

async function copyValue() {
  if (!props.value) return

  try {
    await copy(props.value)
    copied.value = true
    toast.success(t('common.copyToClipboard.copied', 'Copied to clipboard'))
  } catch {
    toast.error(t('common.copyFailed', 'Failed to copy'))
  }
}
</script>

<template>
  <div class="relative">
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
    <pre class="rounded-md bg-muted p-4 pr-12 text-xs leading-5 overflow-x-auto">{{ value }}</pre>
  </div>
</template>
