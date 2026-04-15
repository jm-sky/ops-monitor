<script setup lang="ts">
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { Pencil, RefreshCw, Server, Trash2, Zap } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Button from '@/components/ui/button/Button.vue'
import {
  Dialog,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
} from '@/components/ui/dialog'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteStatus } from '../types'
import EditSiteDialog from '../components/EditSiteDialog.vue'
import SiteDetailConfigurationCard from '../components/SiteDetailConfigurationCard.vue'
import SiteDetailHealthCard from '../components/SiteDetailHealthCard.vue'
import SiteDetailSnapshotHistoryCard from '../components/SiteDetailSnapshotHistoryCard.vue'
import SiteDetailSystemCard from '../components/SiteDetailSystemCard.vue'
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
const savingConfig = ref(false)
const serverLabelDraft = ref('')
const environmentDraft = ref('')
const healthResponseDialogOpen = ref(false)
const systemResponseDialogOpen = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const togglingEnabled = ref(false)
const deleting = ref(false)

const formattedHealthResponse = computed(() => {
  const rawData = status.value?.healthSnapshot?.rawData
  if (!rawData) return ''
  return JSON.stringify(rawData, null, 2)
})

const formattedSystemResponse = computed(() => {
  const rawData = status.value?.systemSnapshot?.rawData
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

async function saveConfig() {
  if (!status.value) return
  savingConfig.value = true
  try {
    const updatedSite = await monitorService.updateSite(siteId.value, {
      serverLabel: serverLabelDraft.value.trim() || null,
      environment: environmentDraft.value.trim() || null,
    })
    updateSiteCache(updatedSite)
    serverLabelDraft.value = updatedSite.serverLabel ?? ''
    environmentDraft.value = updatedSite.environment ?? ''
    toast.success(t('common.saved', 'Saved'))
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.updateError', 'Failed to update site') })
  } finally {
    savingConfig.value = false
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
  environmentDraft.value = updatedSite.environment ?? ''
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

watch(status, (nextStatus) => {
  if (nextStatus) {
    serverLabelDraft.value = nextStatus.site.serverLabel ?? ''
    environmentDraft.value = nextStatus.site.environment ?? ''
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
    <div v-if="status">
      <CommonPageHeader
        :label="status.site.name"
        :icon="Server"
        with-back-button
        @back="router.back()"
      >
        <template #actions>
          <div class="flex w-full flex-wrap items-center justify-end gap-2 sm:w-auto">
            <div class="flex items-center gap-2 rounded-md border bg-muted/30 px-2.5 py-1.5">
              <Switch
                :id="`site-enabled-${siteId}`"
                :model-value="status.site.enabled"
                :disabled="togglingEnabled"
                @update:model-value="toggleEnabled"
              />
              <Label :for="`site-enabled-${siteId}`" class="cursor-pointer select-none text-sm">
                {{ status.site.enabled ? t('monitor.enabled', 'Enabled') : t('monitor.disabled', 'Disabled') }}
              </Label>
            </div>
            <div class="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                :disabled="isFetching || polling"
                :aria-busy="isFetching ? 'true' : 'false'"
                @click="load"
              >
                <RefreshCw :class="['size-4', isFetching && 'animate-spin']" />
                {{ t('common.refresh', 'Refresh') }}
              </Button>
              <Button
                size="sm"
                :disabled="polling || isFetching"
                :aria-busy="polling ? 'true' : 'false'"
                @click="pollNow"
              >
                <Zap :class="['size-4', polling && 'animate-pulse']" />
                {{ t('monitor.pollNow', 'Poll now') }}
              </Button>
            </div>
            <div class="flex items-center gap-2">
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
            </div>
          </div>
        </template>
      </CommonPageHeader>

      <div class="mt-6 grid grid-cols-1 gap-6" :aria-busy="isFetching ? 'true' : 'false'">
        <SiteDetailHealthCard
          :snapshot="status.healthSnapshot"
          @view-raw-response="healthResponseDialogOpen = true"
        />
        <SiteDetailSystemCard
          :snapshot="status.systemSnapshot"
          @view-raw-response="systemResponseDialogOpen = true"
        />
        <SiteDetailSnapshotHistoryCard :site="status.site" />
        <SiteDetailConfigurationCard
          v-model:server-label-draft="serverLabelDraft"
          v-model:environment-draft="environmentDraft"
          :saving-config="savingConfig"
          :site="status.site"
          @save-config="saveConfig"
        />
      </div>

      <Dialog v-model:open="healthResponseDialogOpen">
        <DialogScrollContent class="sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>{{ t('monitor.healthEndpointResponse', 'Health endpoint response') }}</DialogTitle>
          </DialogHeader>
          <pre class="rounded-md bg-muted p-4 text-xs leading-5 overflow-x-auto">{{ formattedHealthResponse }}</pre>
        </DialogScrollContent>
      </Dialog>

      <Dialog v-model:open="systemResponseDialogOpen">
        <DialogScrollContent class="sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>{{ t('monitor.systemEndpointResponse', 'System endpoint response') }}</DialogTitle>
          </DialogHeader>
          <pre class="rounded-md bg-muted p-4 text-xs leading-5 overflow-x-auto">{{ formattedSystemResponse }}</pre>
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
