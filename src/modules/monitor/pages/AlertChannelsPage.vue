<script setup lang="ts">
import { Bell, Mail, MessageSquare, Plus, Send, Trash2, Tv } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { AlertChannel, AlertChannelType } from '../types/alerts'
import AddChannelDialog from '../components/AddChannelDialog.vue'
import { alertChannelService } from '../services/alertChannelService'

const { t } = useI18n()
const { handleError } = useHandleError()

const channels = ref<AlertChannel[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const testingId = ref<string | null>(null)
const deletingId = ref<string | null>(null)

async function load() {
  loading.value = true
  try {
    channels.value = await alertChannelService.list()
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.loadError', 'Failed to load channels') })
  } finally {
    loading.value = false
  }
}

async function toggleEnabled(channel: AlertChannel) {
  try {
    const updated = await alertChannelService.update(channel.id, { enabled: !channel.enabled })
    const idx = channels.value.findIndex(c => c.id === channel.id)
    if (idx !== -1) channels.value[idx] = updated
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.updateError', 'Failed to update channel') })
  }
}

async function testChannel(channel: AlertChannel) {
  testingId.value = channel.id
  try {
    const result = await alertChannelService.test(channel.id)
    if (result.success) {
      toast.success(result.message)
    } else {
      toast.error(result.message)
    }
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.testError', 'Test failed') })
  } finally {
    testingId.value = null
  }
}

async function deleteChannel(channel: AlertChannel) {
  if (!confirm(t('monitor.alerts.deleteConfirm', `Delete channel "${channel.name}"?`))) return
  deletingId.value = channel.id
  try {
    await alertChannelService.delete(channel.id)
    channels.value = channels.value.filter(c => c.id !== channel.id)
    toast.success(t('monitor.alerts.deleted', 'Channel deleted'))
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.deleteError', 'Failed to delete channel') })
  } finally {
    deletingId.value = null
  }
}

function onCreated(channel: AlertChannel) {
  channels.value.push(channel)
  showAddDialog.value = false
  toast.success(t('monitor.alerts.created', 'Channel added'))
}

function channelIcon(type: AlertChannelType) {
  return { teams: Tv, email: Mail, telegram: MessageSquare }[type] ?? Bell
}

function channelLabel(type: AlertChannelType) {
  return { teams: 'MS Teams', email: 'Email', telegram: 'Telegram' }[type] ?? type
}

onMounted(load)
</script>

<template>
  <AuthenticatedLayout>
    <CommonPageHeader :label="t('monitor.alerts.title', 'Alert channels')" :icon="Bell">
      <template #actions>
        <Button size="sm" @click="showAddDialog = true">
          <Plus class="size-4" />
          {{ t('monitor.alerts.addChannel', 'Add channel') }}
        </Button>
      </template>
    </CommonPageHeader>

    <div v-if="channels.length > 0" class="mt-6 space-y-3">
      <Card v-for="ch in channels" :key="ch.id">
        <CardHeader class="flex flex-row items-center justify-between gap-4 py-3">
          <div class="flex items-center gap-3 min-w-0">
            <component :is="channelIcon(ch.type)" class="size-5 shrink-0 text-muted-foreground" />
            <div class="min-w-0">
              <CardTitle class="text-base">
                {{ ch.name }}
              </CardTitle>
              <p class="text-xs text-muted-foreground">
                {{ channelLabel(ch.type) }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <Badge :variant="ch.enabled ? 'success' : 'secondary'">
              {{ ch.enabled ? t('monitor.enabled', 'Enabled') : t('monitor.disabled', 'Disabled') }}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              :disabled="testingId === ch.id"
              @click="testChannel(ch)"
            >
              <Send class="size-4" />
              {{ t('monitor.alerts.test', 'Test') }}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              @click="toggleEnabled(ch)"
            >
              {{ ch.enabled ? t('common.disable', 'Disable') : t('common.enable', 'Enable') }}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              :disabled="deletingId === ch.id"
              @click="deleteChannel(ch)"
            >
              <Trash2 class="size-4 text-destructive" />
            </Button>
          </div>
        </CardHeader>
      </Card>
    </div>

    <div v-else-if="!loading" class="mt-12 flex flex-col items-center gap-4 text-center text-muted-foreground">
      <Bell class="size-12 opacity-30" />
      <p class="text-lg font-medium">
        {{ t('monitor.alerts.noChannels', 'No alert channels configured') }}
      </p>
      <p class="text-sm">
        {{ t('monitor.alerts.noChannelsHint', 'Add a channel to receive alerts when site status changes.') }}
      </p>
      <Button @click="showAddDialog = true">
        <Plus class="size-4" />
        {{ t('monitor.alerts.addChannel', 'Add channel') }}
      </Button>
    </div>

    <AddChannelDialog v-model:open="showAddDialog" @created="onCreated" />
  </AuthenticatedLayout>
</template>
