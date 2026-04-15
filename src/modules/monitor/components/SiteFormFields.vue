<script setup lang="ts">
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import type { SiteFormData } from '../composables/useSiteForm'

const props = withDefaults(defineProps<{
  idPrefix: string
  tokenPlaceholder?: string
}>(), {
  tokenPlaceholder: 'Optional',
})

const form = defineModel<SiteFormData>('form', { required: true })
</script>

<template>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-name`">{{ $t('monitor.fields.name', 'Name') }} *</Label>
    <Input
      :id="`${props.idPrefix}-site-name`"
      v-model="form.name"
      placeholder="app-prod-1"
      required
    />
  </div>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-server`">{{ $t('monitor.fields.serverLabel', 'Server (optional)') }}</Label>
    <Input
      :id="`${props.idPrefix}-site-server`"
      v-model="form.serverLabel"
      placeholder="srv-prod-1"
    />
  </div>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-health`">{{ $t('monitor.fields.healthUrl', 'Health URL') }}</Label>
    <Input
      :id="`${props.idPrefix}-site-health`"
      v-model="form.healthUrl"
      placeholder="https://app.example.com/health"
      type="url"
    />
  </div>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-system`">{{ $t('monitor.fields.systemUrl', 'System URL') }}</Label>
    <Input
      :id="`${props.idPrefix}-site-system`"
      v-model="form.systemUrl"
      placeholder="https://app.example.com:9100/system"
      type="url"
    />
  </div>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-token`">{{ $t('monitor.fields.token', 'Bearer token') }}</Label>
    <Input
      :id="`${props.idPrefix}-site-token`"
      v-model="form.token"
      type="password"
      :placeholder="props.tokenPlaceholder"
    />
  </div>
  <div class="flex items-center gap-3">
    <Switch :id="`${props.idPrefix}-verify-ssl`" v-model="form.verifySSL" />
    <Label :for="`${props.idPrefix}-verify-ssl`">{{ $t('monitor.fields.verifySSL', 'Verify SSL certificate') }}</Label>
  </div>
  <div class="grid grid-cols-2 gap-4">
    <div class="space-y-1.5">
      <Label :for="`${props.idPrefix}-poll-health`">{{ $t('monitor.fields.pollingHealth', 'Health interval (s)') }}</Label>
      <Input
        :id="`${props.idPrefix}-poll-health`"
        v-model.number="form.pollingHealth"
        type="number"
        min="30"
      />
    </div>
    <div class="space-y-1.5">
      <Label :for="`${props.idPrefix}-poll-system`">{{ $t('monitor.fields.pollingSystem', 'System interval (s)') }}</Label>
      <Input
        :id="`${props.idPrefix}-poll-system`"
        v-model.number="form.pollingSystem"
        type="number"
        min="30"
      />
    </div>
  </div>
</template>
