<script setup lang="ts">
import { ArrowLeft, SearchX } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'

const emit = defineEmits<{
  back: []
}>()

const { t } = useI18n()
</script>

<template>
  <div
    class="mt-12 flex flex-col items-center gap-4 rounded-lg border border-dashed bg-muted/20 px-6 py-12 text-center"
  >
    <div class="rounded-full bg-muted p-4">
      <SearchX class="size-12 text-muted-foreground" />
    </div>
    <p class="text-xl font-semibold">
      {{ t('monitor.siteNotFoundTitle', 'Site not found') }}
    </p>
    <p class="max-w-xl text-sm text-muted-foreground">
      {{ t('monitor.siteNotFoundDescription', 'The site you are trying to open does not exist or the URL is invalid.') }}
    </p>
    <Button class="mt-2" @click="emit('back')">
      <ArrowLeft class="size-4" />
      {{ t('monitor.goBackToMonitor', 'Wróć') }}
    </Button>
  </div>
</template>
