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
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteCreate } from '../types'
import { createDefaultSiteForm, toNullableString } from '../composables/useSiteForm'
import { monitorService } from '../services/monitorService'
import SiteFormFields from './SiteFormFields.vue'

const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ created: [site: Site] }>()

const { t } = useI18n()
const { handleError } = useHandleError()

const saving = ref(false)
const form = ref(createDefaultSiteForm())

function reset() {
  form.value = createDefaultSiteForm()
}

async function submit() {
  if (!form.value.name) return
  saving.value = true
  try {
    const payload: SiteCreate = {
      name: form.value.name.trim(),
      enabled: form.value.enabled,
      pollingHealth: form.value.pollingHealth,
      pollingSystem: form.value.pollingSystem,
      verifySSL: form.value.verifySSL,
      serverLabel: toNullableString(form.value.serverLabel),
      healthUrl: toNullableString(form.value.healthUrl),
      systemUrl: toNullableString(form.value.systemUrl),
      token: toNullableString(form.value.token),
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
        <SiteFormFields v-model:form="form" id-prefix="add" />

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
