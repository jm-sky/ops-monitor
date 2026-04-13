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
import type { AlertChannel, AlertChannelCreate, AlertChannelType } from '../types/alerts'
import { alertChannelService } from '../services/alertChannelService'

const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ created: [channel: AlertChannel] }>()

const { t } = useI18n()
const { handleError } = useHandleError()

const saving = ref(false)
const name = ref('')
const type = ref<AlertChannelType>('teams')
const enabled = ref(true)

// Type-specific fields
const teamsWebhook = ref('')
const emailTo = ref('')         // comma-separated
const emailPrefix = ref('[OpsMonitor]')
const telegramToken = ref('')
const telegramChatId = ref('')

const types: { value: AlertChannelType; label: string }[] = [
  { value: 'teams', label: 'MS Teams' },
  { value: 'email', label: 'Email' },
  { value: 'telegram', label: 'Telegram' },
]

const isValid = computed(() => {
  if (!name.value) return false
  if (type.value === 'teams') return !!teamsWebhook.value
  if (type.value === 'email') return !!emailTo.value
  if (type.value === 'telegram') return !!telegramToken.value && !!telegramChatId.value
  return false
})

function buildConfig(): Record<string, unknown> {
  if (type.value === 'teams') return { webhook_url: teamsWebhook.value }
  if (type.value === 'email') {
    const to = emailTo.value.split(',').map(s => s.trim()).filter(Boolean)
    return { to, subject_prefix: emailPrefix.value || '[OpsMonitor]' }
  }
  if (type.value === 'telegram') return { bot_token: telegramToken.value, chat_id: telegramChatId.value }
  return {}
}

function reset() {
  name.value = ''
  type.value = 'teams'
  enabled.value = true
  teamsWebhook.value = ''
  emailTo.value = ''
  emailPrefix.value = '[OpsMonitor]'
  telegramToken.value = ''
  telegramChatId.value = ''
}

watch(open, (v) => { if (!v) reset() })

async function submit() {
  saving.value = true
  try {
    const payload: AlertChannelCreate = {
      name: name.value,
      type: type.value,
      enabled: enabled.value,
      config: buildConfig(),
    }
    const channel = await alertChannelService.create(payload)
    emit('created', channel)
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.createError', 'Failed to create channel') })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('monitor.alerts.addChannel', 'Add alert channel') }}</DialogTitle>
      </DialogHeader>

      <form class="space-y-4" @submit.prevent="submit">
        <!-- Name -->
        <div class="space-y-1.5">
          <Label for="ch-name">{{ t('monitor.alerts.fields.name', 'Name') }} *</Label>
          <Input
            id="ch-name"
            v-model="name"
            placeholder="ops-teams"
            required
          />
        </div>

        <!-- Type -->
        <div class="space-y-1.5">
          <Label>{{ t('monitor.alerts.fields.type', 'Type') }} *</Label>
          <div class="flex gap-2">
            <Button
              v-for="opt in types"
              :key="opt.value"
              type="button"
              :variant="type === opt.value ? 'default' : 'outline'"
              size="sm"
              @click="type = opt.value"
            >
              {{ opt.label }}
            </Button>
          </div>
        </div>

        <!-- Teams config -->
        <template v-if="type === 'teams'">
          <div class="space-y-1.5">
            <Label for="teams-webhook">Webhook URL *</Label>
            <Input id="teams-webhook" v-model="teamsWebhook" placeholder="https://outlook.office.com/webhook/..." />
          </div>
        </template>

        <!-- Email config -->
        <template v-else-if="type === 'email'">
          <div class="space-y-1.5">
            <Label for="email-to">{{ t('monitor.alerts.fields.emailTo', 'Recipients (comma-separated)') }} *</Label>
            <Input id="email-to" v-model="emailTo" placeholder="ops@firma.pl, admin@firma.pl" />
          </div>
          <div class="space-y-1.5">
            <Label for="email-prefix">{{ t('monitor.alerts.fields.subjectPrefix', 'Subject prefix') }}</Label>
            <Input id="email-prefix" v-model="emailPrefix" placeholder="[OpsMonitor]" />
          </div>
        </template>

        <!-- Telegram config -->
        <template v-else-if="type === 'telegram'">
          <div class="space-y-1.5">
            <Label for="tg-token">Bot token *</Label>
            <Input
              id="tg-token"
              v-model="telegramToken"
              type="password"
              placeholder="123456:ABC-..."
            />
          </div>
          <div class="space-y-1.5">
            <Label for="tg-chat">Chat ID *</Label>
            <Input id="tg-chat" v-model="telegramChatId" placeholder="-1001234567890" />
          </div>
        </template>

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
