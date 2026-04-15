<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Input from '@/components/ui/input/Input.vue'
import { ToClipboard } from '@/components/ui/to-clipboard'
import type { Site } from '../types'

const props = defineProps<{
  savingConfig: boolean
  site: Site
}>()

const serverLabelDraft = defineModel<string>('serverLabelDraft', { required: true })
const environmentDraft = defineModel<string>('environmentDraft', { required: true })

const emit = defineEmits<{
  saveConfig: []
}>()

const { t } = useI18n()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('monitor.configuration', 'Configuration') }}</CardTitle>
    </CardHeader>
    <CardContent class="space-y-5 text-sm">
      <div class="grid gap-x-8 gap-y-2 sm:grid-cols-2">
        <div class="sm:col-span-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {{ t('monitor.endpoints', 'Endpoints') }}
        </div>
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
      </div>

      <div class="grid gap-x-8 gap-y-2 border-t pt-5 sm:grid-cols-2">
        <div class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {{ t('monitor.metadata', 'Metadata') }}
        </div>
        <div class="sm:col-span-2 grid gap-4">
          <div class="grid gap-x-8 gap-y-2 sm:grid-cols-2">
            <div class="space-y-2">
              <div class="text-muted-foreground">
                {{ t('monitor.fields.serverLabel', 'Server (optional)') }}
              </div>
              <Input
                v-model="serverLabelDraft"
                placeholder="srv-prod-1"
              />
            </div>
            <div class="space-y-2">
              <div class="text-muted-foreground">
                {{ t('monitor.fields.environment', 'Environment (optional)') }}
              </div>
              <Input
                v-model="environmentDraft"
                placeholder="production"
              />
            </div>
          </div>
          <div class="mt-2 flex justify-end">
            <Button
              size="sm"
              :disabled="props.savingConfig"
              :aria-busy="props.savingConfig ? 'true' : 'false'"
              @click="emit('saveConfig')"
            >
              {{ props.savingConfig ? t('common.saving', 'Saving…') : t('common.save', 'Save') }}
            </Button>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
