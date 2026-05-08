<script setup lang="ts">
import { Bell, Mail, MessageSquare, Pencil, Plus, Send, Trash2, Tv } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { AlertChannel, AlertChannelType, AlertEvent } from '../types/alerts'
import AddChannelDialog from '../components/AddChannelDialog.vue'
import ChannelFiltersSummary from '../components/ChannelFiltersSummary.vue'
import EditChannelDialog from '../components/EditChannelDialog.vue'
import SiteStatusBadge from '../components/SiteStatusBadge.vue'
import { alertChannelService } from '../services/alertChannelService'

const { t } = useI18n()
const { handleError } = useHandleError()

const channels = ref<AlertChannel[]>([])
const events = ref<AlertEvent[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const channelToEdit = ref<AlertChannel | null>(null)
const channelToDelete = ref<AlertChannel | null>(null)
const testingId = ref<string | null>(null)
const deletingId = ref<string | null>(null)

async function load() {
  loading.value = true
  try {
    [channels.value, events.value] = await Promise.all([
      alertChannelService.list(),
      alertChannelService.getAlertEvents({ limit: 100 }),
    ])
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.alerts.loadError', 'Failed to load channels') })
  } finally {
    loading.value = false
  }
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'short',
    timeStyle: 'medium',
  }).format(new Date(iso))
}

function alertTypeLabel(type: string): string {
  return {
    health: t('monitor.alerts.type.health', 'Health'),
    reboot: t('monitor.alerts.type.reboot', 'Reboot'),
    updates: t('monitor.alerts.type.updates', 'Updates'),
  }[type] ?? type
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

function deleteChannel(channel: AlertChannel) {
  channelToDelete.value = channel
  showDeleteDialog.value = true
}

function editChannel(channel: AlertChannel) {
  channelToEdit.value = channel
  showEditDialog.value = true
}

async function confirmDelete() {
  if (!channelToDelete.value) return
  const channel = channelToDelete.value
  deletingId.value = channel.id
  try {
    await alertChannelService.delete(channel.id)
    channels.value = channels.value.filter(c => c.id !== channel.id)
    toast.success(t('monitor.alerts.deleted', 'Channel deleted'))
    showDeleteDialog.value = false
    channelToDelete.value = null
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

function onUpdated(channel: AlertChannel) {
  const idx = channels.value.findIndex(c => c.id === channel.id)
  if (idx !== -1) channels.value[idx] = channel
  toast.success(t('monitor.alerts.updated', 'Channel updated'))
}

const deleteConfirmDescription = computed(() =>
  channelToDelete.value
    ? t('monitor.alerts.deleteConfirmDescription', `Delete channel "${channelToDelete.value.name}"? This cannot be undone.`)
    : '',
)

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
            <div class="min-w-0 space-y-1">
              <CardTitle class="text-base">
                {{ ch.name }}
              </CardTitle>
              <p class="text-xs text-muted-foreground">
                {{ channelLabel(ch.type) }}
              </p>
              <ChannelFiltersSummary :filters="ch.filters" />
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
              @click="editChannel(ch)"
            >
              <Pencil class="size-4" />
              {{ t('common.edit', 'Edit') }}
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

    <div class="mt-10">
      <h2 class="text-lg font-semibold mb-3">
        {{ t('monitor.alerts.log.title', 'Alert log') }}
      </h2>
      <Card v-if="events.length > 0">
        <CardContent class="p-0">
          <div class="divide-y">
            <div
              v-for="ev in events"
              :key="ev.id"
              class="flex items-center justify-between gap-4 px-4 py-2.5 text-sm"
            >
              <div class="flex items-center gap-3 min-w-0">
                <SiteStatusBadge :status="ev.status" />
                <span class="font-medium truncate">{{ ev.siteName }}</span>
                <span class="text-muted-foreground shrink-0">{{ alertTypeLabel(ev.alertType) }}</span>
              </div>
              <div class="flex items-center gap-4 shrink-0 text-xs text-muted-foreground">
                <span>{{ ev.channelName }}</span>
                <span>{{ formatDate(ev.sentAt) }}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      <p v-else-if="!loading" class="text-sm text-muted-foreground">
        {{ t('monitor.alerts.log.empty', 'No alerts have been sent yet.') }}
      </p>
    </div>

    <AddChannelDialog v-model:open="showAddDialog" @created="onCreated" />
    <EditChannelDialog
      v-if="channelToEdit"
      v-model:open="showEditDialog"
      :channel="channelToEdit"
      @updated="onUpdated"
    />
    <ConfirmDialog
      v-model:open="showDeleteDialog"
      :title="t('monitor.alerts.deleteConfirm', 'Delete channel?')"
      :description="deleteConfirmDescription"
      :loading="deletingId !== null"
      @confirm="confirmDelete"
    />
  </AuthenticatedLayout>
</template>
