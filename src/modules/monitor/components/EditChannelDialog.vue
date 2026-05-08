<script setup lang="ts">
import { computed, ref, watch } from 'vue'
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
import { useHandleError } from '@/shared/composables/useHandleError'
import type { AlertChannel, AlertChannelFilters, AlertChannelUpdate } from '../types/alerts'
import { alertChannelService } from '../services/alertChannelService'
import { DEFAULT_FILTERS } from '../types/alerts'
import ChannelFiltersForm from './ChannelFiltersForm.vue'

const open = defineModel<boolean>('open', { required: true })
const props = defineProps<{ channel: AlertChannel }>()
const emit = defineEmits<{ updated: [channel: AlertChannel] }>()

const { t } = useI18n()
const { handleError } = useHandleError()

const saving = ref(false)
const name = ref('')
const teamsWebhook = ref('')
const emailTo = ref('')
const emailPrefix = ref('[OpsMonitor]')
const telegramToken = ref('')
const telegramChatId = ref('')
const filters = ref<AlertChannelFilters>({
  ...DEFAULT_FILTERS,
  quiet_hours: { ...DEFAULT_FILTERS.quiet_hours },
})

const channelLabel = computed(() => ({
  teams: 'MS Teams',
  email: 'Email',
  telegram: 'Telegram',
}[props.channel.type]))

function loadFromChannel() {
  const c = props.channel
  name.value = c.name
  const cfg = c.config ?? {}
  teamsWebhook.value = String(cfg.webhook_url ?? '')
  const emailToVal = cfg.to
  emailTo.value = Array.isArray(emailToVal) ? emailToVal.join(', ') : ''
  emailPrefix.value = String(cfg.subject_prefix ?? '[OpsMonitor]')
  telegramToken.value = String(cfg.bot_token ?? '')
  telegramChatId.value = String(cfg.chat_id ?? '')

  filters.value = {
    ...DEFAULT_FILTERS,
    ...c.filters,
    quiet_hours: {
      ...DEFAULT_FILTERS.quiet_hours,
      ...(c.filters?.quiet_hours ?? {}),
    },
  }
}

watch(
  [open, () => props.channel],
  ([isOpen]) => {
    if (isOpen) loadFromChannel()
  },
  { immediate: true },
)

const isValid = computed(() => {
  if (!name.value) return false
  if (props.channel.type === 'teams') return !!teamsWebhook.value
  if (props.channel.type === 'email') return !!emailTo.value
  if (props.channel.type === 'telegram') return !!telegramToken.value && !!telegramChatId.value
  return false
})

function buildConfig(): Record<string, unknown> {
  const t = props.channel.type
  if (t === 'teams') return { webhook_url: teamsWebhook.value }
  if (t === 'email') {
    const to = emailTo.value.split(',').map(s => s.trim()).filter(Boolean)
    return { to, subject_prefix: emailPrefix.value || '[OpsMonitor]' }
  }
  if (t === 'telegram') return { bot_token: telegramToken.value, chat_id: telegramChatId.value }
  return {}
}

async function submit() {
  saving.value = true
  try {
    const payload: AlertChannelUpdate = {
      name: name.value,
      config: buildConfig(),
      filters: filters.value,
    }
    const updated = await alertChannelService.update(props.channel.id, payload)
    emit('updated', updated)
    open.value = false
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.updateError', 'Failed to update channel') })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-lg max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ t('monitor.alerts.editChannel', 'Edit alert channel') }}</DialogTitle>
      </DialogHeader>

      <form class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1.5">
          <Label for="edit-ch-name">{{ t('monitor.alerts.fields.name', 'Name') }} *</Label>
          <Input
            id="edit-ch-name"
            v-model="name"
            required
          />
        </div>

        <div class="space-y-1.5">
          <Label>{{ t('monitor.alerts.fields.type', 'Type') }}</Label>
          <p class="text-sm text-muted-foreground">
            {{ channelLabel }}
          </p>
        </div>

        <template v-if="props.channel.type === 'teams'">
          <div class="space-y-1.5">
            <Label for="edit-teams-webhook">Webhook URL *</Label>
            <Input id="edit-teams-webhook" v-model="teamsWebhook" />
          </div>
        </template>

        <template v-else-if="props.channel.type === 'email'">
          <div class="space-y-1.5">
            <Label for="edit-email-to">{{ t('monitor.alerts.fields.emailTo', 'Recipients (comma-separated)') }} *</Label>
            <Input id="edit-email-to" v-model="emailTo" />
          </div>
          <div class="space-y-1.5">
            <Label for="edit-email-prefix">{{ t('monitor.alerts.fields.subjectPrefix', 'Subject prefix') }}</Label>
            <Input id="edit-email-prefix" v-model="emailPrefix" />
          </div>
        </template>

        <template v-else-if="props.channel.type === 'telegram'">
          <div class="space-y-1.5">
            <Label for="edit-tg-token">Bot token *</Label>
            <Input
              id="edit-tg-token"
              v-model="telegramToken"
              type="password"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="edit-tg-chat">Chat ID *</Label>
            <Input id="edit-tg-chat" v-model="telegramChatId" />
          </div>
        </template>

        <ChannelFiltersForm v-model="filters" />

        <DialogFooter>
          <Button type="button" variant="outline" @click="open = false">
            {{ t('common.cancel', 'Cancel') }}
          </Button>
          <Button type="submit" :disabled="saving || !isValid">
            {{ saving ? t('common.saving', 'Saving…') : t('common.save', 'Save') }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
