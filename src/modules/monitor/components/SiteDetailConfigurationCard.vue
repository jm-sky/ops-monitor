<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Input from '@/components/ui/input/Input.vue'
import { ToClipboard } from '@/components/ui/to-clipboard'
import type { Site } from '../types'

const props = defineProps<{
  savingServerLabel: boolean
  site: Site
}>()

const serverLabelDraft = defineModel<string>('serverLabelDraft', { required: true })

const emit = defineEmits<{
  saveServerLabel: []
}>()

const { t } = useI18n()
</script>

<template>
  <Card class="md:col-span-2">
    <CardHeader>
      <CardTitle>{{ t('monitor.configuration', 'Configuration') }}</CardTitle>
    </CardHeader>
    <CardContent class="grid gap-x-8 gap-y-2 text-sm sm:grid-cols-2">
      <div class="flex flex-wrap justify-between">
        <span class="text-muted-foreground">{{ t('monitor.fields.healthUrl', 'Health URL') }}</span>
        <ToClipboard :value="props.site.healthUrl" />
      </div>
      <div class="flex flex-wrap justify-between overflow-hidden">
        <span class="text-muted-foreground">{{ t('monitor.fields.systemUrl', 'System URL') }}</span>
        <ToClipboard :value="props.site.systemUrl ?? ''" />
      </div>
      <div class="flex flex-wrap justify-between">
        <span class="text-muted-foreground">{{ t('monitor.fields.pollingHealth', 'Health interval') }}</span>
        <span>{{ props.site.pollingHealth }}s</span>
      </div>
      <div class="flex flex-wrap justify-between">
        <span class="text-muted-foreground">{{ t('monitor.fields.pollingSystem', 'System interval') }}</span>
        <span>{{ props.site.pollingSystem }}s</span>
      </div>
      <div class="flex flex-wrap justify-between">
        <span class="text-muted-foreground">{{ t('common.status', 'Status') }}</span>
        <Badge :variant="props.site.enabled ? 'success' : 'secondary'">
          {{ props.site.enabled ? t('monitor.enabled', 'Enabled') : t('monitor.disabled', 'Disabled') }}
        </Badge>
      </div>
      <div class="space-y-2 sm:col-span-2">
        <div class="text-muted-foreground">
          {{ t('monitor.fields.serverLabel', 'Server (optional)') }}
        </div>
        <div class="flex flex-wrap gap-2 md:flex-nowrap">
          <Input
            v-model="serverLabelDraft"
            placeholder="srv-prod-1"
          />
          <Button
            size="sm"
            :disabled="props.savingServerLabel"
            @click="emit('saveServerLabel')"
          >
            {{ props.savingServerLabel ? t('common.saving', 'Saving…') : t('common.save', 'Save') }}
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
