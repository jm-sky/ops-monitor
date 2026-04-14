<script setup lang="ts">
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { ArrowLeft, Braces, Pencil, RefreshCw, Server, Trash2, Zap } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
} from '@/components/ui/dialog'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import { ToClipboard } from '@/components/ui/to-clipboard'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteStatus } from '../types'
import EditSiteDialog from '../components/EditSiteDialog.vue'
import SiteStatusBadge from '../components/SiteStatusBadge.vue'
import { metricBarClass, metricLevel, metricValueClass } from '../composables/useMetricLevel'
import { monitorQueryKeys } from '../services/monitorQueries'
import { monitorService } from '../services/monitorService'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()
const { handleError } = useHandleError()

const siteId = computed(() => route.params.id as string)
const {
  data: queryData,
  error,
  isError,
  isFetching,
  isLoading,
  isFetched,
} = useQuery<SiteStatus>({
  queryKey: computed(() => monitorQueryKeys.site(siteId.value)),
  queryFn: () => monitorService.getSite(siteId.value),
  placeholderData: previousData => previousData,
})
const status = computed<SiteStatus | null>(() => queryData.value ?? null)
const polling = ref(false)
const savingServerLabel = ref(false)
const serverLabelDraft = ref('')
const healthResponseDialogOpen = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const togglingEnabled = ref(false)
const deleting = ref(false)

const formattedHealthResponse = computed(() => {
  const rawData = status.value?.healthSnapshot?.rawData
  if (!rawData) return ''
  return JSON.stringify(rawData, null, 2)
})

async function load() {
  await queryClient.invalidateQueries({ queryKey: monitorQueryKeys.site(siteId.value) })
}

async function pollNow() {
  polling.value = true
  try {
    await monitorService.pollNow(siteId.value)
    toast.success(t('monitor.pollComplete', 'Poll complete'))
    await load()
    await queryClient.invalidateQueries({ queryKey: monitorQueryKeys.siteStatuses() })
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.pollError', 'Poll failed') })
  } finally {
    polling.value = false
  }
}

async function saveServerLabel() {
  if (!status.value) return
  savingServerLabel.value = true
  try {
    const updatedSite = await monitorService.updateSite(siteId.value, {
      serverLabel: serverLabelDraft.value.trim() || null,
    })
    updateSiteCache(updatedSite)
    serverLabelDraft.value = updatedSite.serverLabel ?? ''
    toast.success(t('common.saved', 'Saved'))
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.updateError', 'Failed to update site') })
  } finally {
    savingServerLabel.value = false
  }
}

function updateSiteCache(updatedSite: Site) {
  queryClient.setQueryData(monitorQueryKeys.site(siteId.value), (cached: SiteStatus | undefined) => {
    if (!cached) return cached
    return { ...cached, site: updatedSite }
  })
  queryClient.setQueryData(monitorQueryKeys.siteStatuses(), (cached: SiteStatus[] | undefined) => {
    if (!cached) return cached
    return cached.map(s => s.site.id === updatedSite.id ? { ...s, site: updatedSite } : s)
  })
}

function onSiteUpdated(updatedSite: Site) {
  updateSiteCache(updatedSite)
  serverLabelDraft.value = updatedSite.serverLabel ?? ''
}

async function toggleEnabled() {
  if (!status.value) return
  togglingEnabled.value = true
  try {
    const updatedSite = await monitorService.updateSite(siteId.value, {
      enabled: !status.value.site.enabled,
    })
    updateSiteCache(updatedSite)
    toast.success(updatedSite.enabled ? t('monitor.siteEnabled', 'Site enabled') : t('monitor.siteDisabled', 'Site disabled'))
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.updateError', 'Failed to update site') })
  } finally {
    togglingEnabled.value = false
  }
}

async function deleteSite() {
  deleting.value = true
  try {
    await monitorService.deleteSite(siteId.value)
    await queryClient.invalidateQueries({ queryKey: monitorQueryKeys.siteStatuses() })
    toast.success(t('monitor.deleted', 'Site deleted'))
    router.back()
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.deleteError', 'Failed to delete site') })
    deleting.value = false
  }
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'short',
    timeStyle: 'medium',
  }).format(new Date(iso))
}

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return d > 0 ? `${d}d ${h}h ${m}m` : `${h}h ${m}m`
}

watch(status, (nextStatus) => {
  if (nextStatus) {
    serverLabelDraft.value = nextStatus.site.serverLabel ?? ''
  }
}, { immediate: true })

watch(error, (queryError, previousError) => {
  if (queryError && queryError !== previousError) {
    handleError(queryError, { fallbackMessage: t('monitor.loadError', 'Failed to load site') })
  }
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="flex items-center gap-2 mb-4">
      <Button variant="ghost" size="sm" @click="router.back()">
        <ArrowLeft class="size-4" />
        {{ t('common.back', 'Back') }}
      </Button>
    </div>

    <div v-if="status">
      <CommonPageHeader :label="status.site.name" :icon="Server">
        <template #actions>
          <div class="flex items-center gap-2 mr-2">
            <Switch
              :id="`site-enabled-${siteId}`"
              :model-value="status.site.enabled"
              :disabled="togglingEnabled"
              @update:model-value="toggleEnabled"
            />
            <Label :for="`site-enabled-${siteId}`" class="cursor-pointer select-none">
              {{ status.site.enabled ? t('monitor.enabled', 'Enabled') : t('monitor.disabled', 'Disabled') }}
            </Label>
          </div>
          <Button
            variant="outline"
            size="sm"
            :disabled="isFetching"
            @click="load"
          >
            <RefreshCw :class="['size-4', isFetching && 'animate-spin']" />
            {{ t('common.refresh', 'Refresh') }}
          </Button>
          <Button size="sm" :disabled="polling" @click="pollNow">
            <Zap :class="['size-4', polling && 'animate-pulse']" />
            {{ t('monitor.pollNow', 'Poll now') }}
          </Button>
          <Button variant="outline" size="sm" @click="showEditDialog = true">
            <Pencil class="size-4" />
            {{ t('monitor.editSite', 'Edit') }}
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="text-destructive hover:text-destructive"
            @click="showDeleteDialog = true"
          >
            <Trash2 class="size-4" />
            {{ t('monitor.deleteSite', 'Delete') }}
          </Button>
        </template>
      </CommonPageHeader>

      <div class="mt-6 grid gap-6 md:grid-cols-2">
        <!-- Health -->
        <Card>
          <CardHeader class="flex flex-row items-center justify-between">
            <CardTitle>{{ t('monitor.health', 'Health') }}</CardTitle>
            <div class="flex items-center gap-2">
              <Button
                v-if="status.healthSnapshot?.rawData"
                variant="outline"
                size="xs"
                :aria-label="t('monitor.viewRawResponse', 'View full response')"
                :title="t('monitor.viewRawResponse', 'View full response')"
                class="h-6"
                @click="healthResponseDialogOpen = true"
              >
                <Braces class="size-3" /> Full response
              </Button>
              <SiteStatusBadge :status="status.healthSnapshot?.status ?? null" />
            </div>
          </CardHeader>
          <CardContent class="space-y-2 text-sm">
            <template v-if="status.healthSnapshot">
              <div class="flex justify-between">
                <span class="text-muted-foreground">{{ t('monitor.lastPolled', 'Last polled') }}</span>
                <span>{{ formatDate(status.healthSnapshot.polledAt) }}</span>
              </div>
              <div v-if="status.healthSnapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
                {{ status.healthSnapshot.error }}
              </div>
              <template v-if="status.healthSnapshot.rawData">
                <div
                  v-for="(comp, key) in (status.healthSnapshot.rawData.components as Record<string, unknown> | undefined)"
                  :key="key"
                  class="flex justify-between"
                >
                  <span class="text-muted-foreground capitalize">{{ key }}</span>
                  <SiteStatusBadge :status="(comp as Record<string, unknown>)?.status as string ?? null" />
                </div>
              </template>
            </template>
            <p v-else class="text-muted-foreground">
              {{ t('monitor.noData', 'No data yet') }}
            </p>
          </CardContent>
        </Card>

        <!-- System -->
        <Card>
          <CardHeader class="flex flex-row items-center justify-between">
            <CardTitle>{{ t('monitor.system', 'System') }}</CardTitle>
            <SiteStatusBadge :status="status.systemSnapshot?.status ?? null" />
          </CardHeader>
          <CardContent class="space-y-2 text-sm">
            <template v-if="status.systemSnapshot">
              <div class="flex justify-between">
                <span class="text-muted-foreground">{{ t('monitor.lastPolled', 'Last polled') }}</span>
                <span>{{ formatDate(status.systemSnapshot.polledAt) }}</span>
              </div>
              <div v-if="status.systemSnapshot.error" class="rounded bg-destructive/10 px-3 py-2 text-destructive">
                {{ status.systemSnapshot.error }}
              </div>
            </template>
            <template v-if="status.systemSnapshot?.rawData">
              <div class="space-y-0.5">
                <div class="flex justify-between">
                  <span class="text-muted-foreground">CPU</span>
                  <span :class="metricValueClass(metricLevel(status.systemSnapshot.rawData.cpu_percent as number))">
                    {{ status.systemSnapshot.rawData.cpu_percent }}%
                  </span>
                </div>
                <div class="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    :class="['h-full rounded-full transition-all', metricBarClass(metricLevel(status.systemSnapshot.rawData.cpu_percent as number))]"
                    :style="{ width: `${status.systemSnapshot.rawData.cpu_percent}%` }"
                  />
                </div>
              </div>
              <div class="space-y-0.5">
                <div class="flex justify-between">
                  <span class="text-muted-foreground">RAM</span>
                  <span :class="metricValueClass(metricLevel((status.systemSnapshot.rawData.memory as Record<string, number>)?.percent))">
                    {{ (status.systemSnapshot.rawData.memory as Record<string, number>)?.percent }}%
                    ({{ (status.systemSnapshot.rawData.memory as Record<string, number>)?.used_mb?.toFixed(0) }} /
                    {{ (status.systemSnapshot.rawData.memory as Record<string, number>)?.total_mb?.toFixed(0) }} MB)
                  </span>
                </div>
                <div class="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    :class="['h-full rounded-full transition-all', metricBarClass(metricLevel((status.systemSnapshot.rawData.memory as Record<string, number>)?.percent))]"
                    :style="{ width: `${(status.systemSnapshot.rawData.memory as Record<string, number>)?.percent}%` }"
                  />
                </div>
              </div>
              <div class="space-y-0.5">
                <div class="flex justify-between">
                  <span class="text-muted-foreground">Disk</span>
                  <span :class="metricValueClass(metricLevel((status.systemSnapshot.rawData.disk as Record<string, number>)?.percent))">
                    {{ (status.systemSnapshot.rawData.disk as Record<string, number>)?.percent }}%
                    ({{ (status.systemSnapshot.rawData.disk as Record<string, number>)?.used_gb?.toFixed(1) }} /
                    {{ (status.systemSnapshot.rawData.disk as Record<string, number>)?.total_gb?.toFixed(1) }} GB)
                  </span>
                </div>
                <div class="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    :class="['h-full rounded-full transition-all', metricBarClass(metricLevel((status.systemSnapshot.rawData.disk as Record<string, number>)?.percent))]"
                    :style="{ width: `${(status.systemSnapshot.rawData.disk as Record<string, number>)?.percent}%` }"
                  />
                </div>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">{{ t('monitor.uptime', 'Uptime') }}</span>
                <span>{{ formatUptime(status.systemSnapshot.rawData.uptime_seconds as number) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">{{ t('monitor.updates', 'Updates') }}</span>
                <span>{{ status.systemSnapshot.rawData.updates_available ?? 0 }}</span>
              </div>
              <div v-if="status.systemSnapshot.rawData.reboot_required" class="rounded bg-amber-50 dark:bg-amber-950 px-3 py-2 text-amber-700 dark:text-amber-300 text-xs">
                {{ t('monitor.rebootRequired', 'Reboot required') }}:
                {{ status.systemSnapshot.rawData.reboot_reason }}
              </div>
            </template>
            <p v-if="!status.systemSnapshot" class="text-muted-foreground">
              {{ t('monitor.noData', 'No data yet') }}
            </p>
          </CardContent>
        </Card>

        <!-- Site config -->
        <Card class="md:col-span-2">
          <CardHeader>
            <CardTitle>{{ t('monitor.configuration', 'Configuration') }}</CardTitle>
          </CardHeader>
          <CardContent class="grid gap-y-2 gap-x-8 text-sm sm:grid-cols-2">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Health URL</span>
              <ToClipboard :value="status.site.healthUrl" />
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">System URL</span>
              <span class="truncate max-w-xs">{{ status.site.systemUrl ?? '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">{{ t('monitor.fields.pollingHealth', 'Health interval') }}</span>
              <span>{{ status.site.pollingHealth }}s</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">{{ t('monitor.fields.pollingSystem', 'System interval') }}</span>
              <span>{{ status.site.pollingSystem }}s</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Status</span>
              <Badge :variant="status.site.enabled ? 'success' : 'secondary'">
                {{ status.site.enabled ? t('monitor.enabled', 'Enabled') : t('monitor.disabled', 'Disabled') }}
              </Badge>
            </div>
            <div class="sm:col-span-2 space-y-2">
              <div class="text-muted-foreground">
                {{ t('monitor.fields.serverLabel', 'Server (optional)') }}
              </div>
              <div class="flex gap-2">
                <Input
                  v-model="serverLabelDraft"
                  placeholder="srv-prod-1"
                />
                <Button
                  size="sm"
                  :disabled="savingServerLabel"
                  @click="saveServerLabel"
                >
                  {{ savingServerLabel ? t('common.saving', 'Saving…') : t('common.save', 'Save') }}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Dialog v-model:open="healthResponseDialogOpen">
        <DialogScrollContent class="sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>{{ t('monitor.healthEndpointResponse', 'Health endpoint response') }}</DialogTitle>
          </DialogHeader>
          <pre class="rounded-md bg-muted p-4 text-xs leading-5 overflow-x-auto">{{ formattedHealthResponse }}</pre>
        </DialogScrollContent>
      </Dialog>
    </div>

    <div v-else-if="isLoading || (isFetching && !isFetched && !isError)" class="flex justify-center py-12">
      <RefreshCw class="size-6 animate-spin text-muted-foreground" />
    </div>

    <EditSiteDialog
      v-if="status"
      v-model:open="showEditDialog"
      :site="status.site"
      @updated="onSiteUpdated"
    />
    <ConfirmDialog
      v-model:open="showDeleteDialog"
      :title="t('monitor.deleteSite', 'Delete site')"
      :description="t('monitor.deleteConfirmDescription', 'This will permanently delete the site and all its snapshots.')"
      :loading="deleting"
      @confirm="deleteSite"
    />
  </AuthenticatedLayout>
</template>
