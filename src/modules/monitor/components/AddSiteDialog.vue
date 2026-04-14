<script setup lang="ts">
import { ref } from 'vue'
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
import type { Site, SiteCreate } from '../types'
import { monitorService } from '../services/monitorService'

const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ created: [site: Site] }>()

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

const form = ref<FormData>({
  name: '',
  serverLabel: '',
  healthUrl: '',
  systemUrl: '',
  token: '',
  enabled: true,
  pollingHealth: 300,
  pollingSystem: 300,
  verifySSL: true,
})

function reset() {
  form.value = {
    name: '',
    serverLabel: '',
    healthUrl: '',
    systemUrl: '',
    token: '',
    enabled: true,
    pollingHealth: 300,
    pollingSystem: 300,
    verifySSL: true,
  }
}


async function submit() {
  if (!form.value.name) return
  saving.value = true
  try {
    const payload: SiteCreate = {
      ...form.value,
      serverLabel: form.value.serverLabel.trim() || null,
      healthUrl: form.value.healthUrl || null,
      systemUrl: form.value.systemUrl || null,
      token: form.value.token || null,
      verifySSL: form.value.verifySSL,
    }
    const site = await monitorService.createSite(payload)
    reset()
    emit('created', site)
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.createError', 'Failed to create site') })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('monitor.addSite', 'Add site') }}</DialogTitle>
      </DialogHeader>

      <form class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1.5">
          <Label for="site-name">{{ t('monitor.fields.name', 'Name') }} *</Label>
          <Input
            id="site-name"
            v-model="form.name"
            placeholder="app-prod-1"
            required
          />
        </div>
        <div class="space-y-1.5">
          <Label for="site-server">{{ t('monitor.fields.serverLabel', 'Server (optional)') }}</Label>
          <Input
            id="site-server"
            v-model="form.serverLabel"
            placeholder="srv-prod-1"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="site-health">{{ t('monitor.fields.healthUrl', 'Health URL') }}</Label>
          <Input
            id="site-health"
            v-model="form.healthUrl"
            placeholder="https://app.example.com/health"
            type="url"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="site-system">{{ t('monitor.fields.systemUrl', 'System URL') }}</Label>
          <Input
            id="site-system"
            v-model="form.systemUrl"
            placeholder="https://app.example.com:9100/system"
            type="url"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="site-token">{{ t('monitor.fields.token', 'Bearer token') }}</Label>
          <Input
            id="site-token"
            v-model="form.token"
            type="password"
            placeholder="Optional"
          />
        </div>
        <div class="flex items-center gap-3">
          <Switch id="verify-ssl" v-model="form.verifySSL" />
          <Label for="verify-ssl">{{ t('monitor.fields.verifySSL', 'Verify SSL certificate') }}</Label>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <Label for="poll-health">{{ t('monitor.fields.pollingHealth', 'Health interval (s)') }}</Label>
            <Input
              id="poll-health"
              v-model.number="form.pollingHealth"
              type="number"
              min="30"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="poll-system">{{ t('monitor.fields.pollingSystem', 'System interval (s)') }}</Label>
            <Input
              id="poll-system"
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
