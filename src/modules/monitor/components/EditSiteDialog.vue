<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteUpdate } from '../types'
import { monitorService } from '../services/monitorService'

const open = defineModel<boolean>('open', { required: true })
const props = defineProps<{ site: Site }>()
const emit = defineEmits<{ updated: [site: Site] }>()

const { t } = useI18n()
const { handleError } = useHandleError()

const saving = ref(false)

interface FormData {
  name: string
  serverLabel: string
  healthUrl: string
  systemUrl: string
  token: string
  enabled: boolean
  pollingHealth: number
  pollingSystem: number
  verifySSL: boolean
}

const form = ref<FormData>(siteToForm(props.site))

function siteToForm(site: Site): FormData {
  return {
    name: site.name,
    serverLabel: site.serverLabel ?? '',
    healthUrl: site.healthUrl ?? '',
    systemUrl: site.systemUrl ?? '',
    token: site.token ?? '',
    enabled: site.enabled,
    pollingHealth: site.pollingHealth,
    pollingSystem: site.pollingSystem,
    verifySSL: site.verifySSL,
  }
}

watch(open, (isOpen) => {
  if (isOpen) {
    form.value = siteToForm(props.site)
  }
})

async function submit() {
  if (!form.value.name) return
  saving.value = true
  try {
    const payload: SiteUpdate = {
      ...form.value,
      serverLabel: form.value.serverLabel.trim() || null,
      healthUrl: form.value.healthUrl || null,
      systemUrl: form.value.systemUrl || null,
      token: form.value.token || null,
    }
    const updated = await monitorService.updateSite(props.site.id, payload)
    emit('updated', updated)
    open.value = false
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.updateError', 'Failed to update site') })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('monitor.editSite', 'Edit site') }}</DialogTitle>
      </DialogHeader>

      <form class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1.5">
          <Label for="edit-site-name">{{ t('monitor.fields.name', 'Name') }} *</Label>
          <Input
            id="edit-site-name"
            v-model="form.name"
            placeholder="app-prod-1"
            required
          />
        </div>
        <div class="space-y-1.5">
          <Label for="edit-site-server">{{ t('monitor.fields.serverLabel', 'Server (optional)') }}</Label>
          <Input
            id="edit-site-server"
            v-model="form.serverLabel"
            placeholder="srv-prod-1"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="edit-site-health">{{ t('monitor.fields.healthUrl', 'Health URL') }}</Label>
          <Input
            id="edit-site-health"
            v-model="form.healthUrl"
            placeholder="https://app.example.com/health"
            type="url"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="edit-site-system">{{ t('monitor.fields.systemUrl', 'System URL') }}</Label>
          <Input
            id="edit-site-system"
            v-model="form.systemUrl"
            placeholder="https://app.example.com:9100/system"
            type="url"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="edit-site-token">{{ t('monitor.fields.token', 'Bearer token') }}</Label>
          <Input
            id="edit-site-token"
            v-model="form.token"
            type="password"
            placeholder="Leave blank to keep current"
          />
        </div>
        <div class="flex items-center gap-3">
          <Switch id="edit-verify-ssl" v-model="form.verifySSL" />
          <Label for="edit-verify-ssl">{{ t('monitor.fields.verifySSL', 'Verify SSL certificate') }}</Label>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <Label for="edit-poll-health">{{ t('monitor.fields.pollingHealth', 'Health interval (s)') }}</Label>
            <Input
              id="edit-poll-health"
              v-model.number="form.pollingHealth"
              type="number"
              min="30"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="edit-poll-system">{{ t('monitor.fields.pollingSystem', 'System interval (s)') }}</Label>
            <Input
              id="edit-poll-system"
              v-model.number="form.pollingSystem"
              type="number"
              min="30"
            />
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" @click="open = false">
            {{ t('common.cancel', 'Cancel') }}
          </Button>
          <Button type="submit" :disabled="saving || !form.name">
            {{ saving ? t('common.saving', 'Saving…') : t('common.save', 'Save') }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
