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
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteUpdate } from '../types'
import { siteToForm, toNullableString } from '../composables/useSiteForm'
import { monitorService } from '../services/monitorService'
import SiteFormFields from './SiteFormFields.vue'

const open = defineModel<boolean>('open', { required: true })
const props = defineProps<{ site: Site }>()
const emit = defineEmits<{ updated: [site: Site] }>()

const { t } = useI18n()
const { handleError } = useHandleError()

const saving = ref(false)
const form = ref(siteToForm(props.site))

watch(open, (isOpen) => {
  if (isOpen) {
    form.value = siteToForm(props.site)
  }
})

async function submit() {
  if (!form.value.name) return
  saving.value = true
  try {
    const nextToken = toNullableString(form.value.token)
    const payload: SiteUpdate = {
      name: form.value.name.trim(),
      enabled: form.value.enabled,
      pollingHealth: form.value.pollingHealth,
      pollingSystem: form.value.pollingSystem,
      verifySSL: form.value.verifySSL,
      serverLabel: toNullableString(form.value.serverLabel),
      environment: toNullableString(form.value.environment),
      healthUrl: toNullableString(form.value.healthUrl),
      systemUrl: toNullableString(form.value.systemUrl),
    }
    if (nextToken !== null) payload.token = nextToken
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
        <SiteFormFields v-model:form="form" id-prefix="edit" token-placeholder="Leave blank to keep current" />

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
