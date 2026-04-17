<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { ref } from 'vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import { normalizeTags, type SiteFormData } from '../composables/useSiteForm'

const props = withDefaults(defineProps<{
  idPrefix: string
  tokenPlaceholder?: string
}>(), {
  tokenPlaceholder: 'Optional',
})

const form = defineModel<SiteFormData>('form', { required: true })

const tagDraft = ref('')

function addTagsFromDraft() {
  const next = tagDraft.value.trim()
  if (!next) return

  const parts = next
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)

  form.value.tags = normalizeTags([...form.value.tags, ...parts])
  tagDraft.value = ''
}

function removeTag(tag: string) {
  form.value.tags = form.value.tags.filter((t) => t !== tag)
}

function onTagKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ',') {
    event.preventDefault()
    addTagsFromDraft()
  }
}
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
    <Label :for="`${props.idPrefix}-site-environment`">{{ $t('monitor.fields.environment', 'Environment (optional)') }}</Label>
    <Input
      :id="`${props.idPrefix}-site-environment`"
      v-model="form.environment"
      placeholder="production"
    />
  </div>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-ip`">{{ $t('monitor.fields.ip', 'IP address (optional)') }}</Label>
    <Input
      :id="`${props.idPrefix}-site-ip`"
      v-model="form.ip"
      placeholder="10.0.0.10"
    />
  </div>
  <div class="space-y-1.5">
    <Label :for="`${props.idPrefix}-site-tags`">{{ $t('monitor.fields.tags', 'Tags (optional)') }}</Label>
    <div class="flex flex-col gap-2">
      <Input
        :id="`${props.idPrefix}-site-tags`"
        v-model="tagDraft"
        :placeholder="$t('monitor.tagsPlaceholder', 'Type a tag and press Enter')"
        @keydown="onTagKeydown"
        @blur="addTagsFromDraft"
      />
      <div v-if="form.tags.length > 0" class="flex flex-wrap gap-2">
        <Badge
          v-for="tag in form.tags"
          :key="tag"
          variant="secondary"
          class="gap-1 pr-1"
        >
          <span class="truncate">{{ tag }}</span>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            class="h-5 w-5"
            :aria-label="$t('monitor.removeTag', 'Remove tag')"
            @click="removeTag(tag)"
          >
            <X class="size-3" />
          </Button>
        </Badge>
      </div>
    </div>
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
