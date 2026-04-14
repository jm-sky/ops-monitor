<script setup lang="ts">
import { ArrowLeft, RefreshCw, Server, Zap } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Input from '@/components/ui/input/Input.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { SiteStatus } from '../types'
import SiteStatusBadge from '../components/SiteStatusBadge.vue'
import { monitorService } from '../services/monitorService'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { handleError } = useHandleError()

const siteId = computed(() => route.params.id as string)
const status = ref<SiteStatus | null>(null)
const loading = ref(false)
const polling = ref(false)
const savingServerLabel = ref(false)
const serverLabelDraft = ref('')

async function load() {
  loading.value = true
  try {
    status.value = await monitorService.getSite(siteId.value)
    serverLabelDraft.value = status.value.site.serverLabel ?? ''
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.loadError', 'Failed to load site') })
  } finally {
    loading.value = false
  }
}

async function pollNow() {
  polling.value = true
  try {
    await monitorService.pollNow(siteId.value)
    toast.success(t('monitor.pollComplete', 'Poll complete'))
    await load()
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
    status.value = { ...status.value, site: updatedSite }
    serverLabelDraft.value = updatedSite.serverLabel ?? ''
    toast.success(t('common.saved', 'Saved'))
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.updateError', 'Failed to update site') })
  } finally {
    savingServerLabel.value = false
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

onMounted(load)
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
          <Button
            variant="outline"
            size="sm"
            :disabled="loading"
            @click="load"
          >
            <RefreshCw :class="['size-4', loading && 'animate-spin']" />
            {{ t('common.refresh', 'Refresh') }}
          </Button>
          <Button size="sm" :disabled="polling" @click="pollNow">
            <Zap :class="['size-4', polling && 'animate-pulse']" />
            {{ t('monitor.pollNow', 'Poll now') }}
          </Button>
        </template>
      </CommonPageHeader>

      <div class="mt-6 grid gap-6 md:grid-cols-2">
        <!-- Health -->
        <Card>
          <CardHeader class="flex flex-row items-center justify-between">
            <CardTitle>{{ t('monitor.health', 'Health') }}</CardTitle>
            <SiteStatusBadge :status="status.healthSnapshot?.status ?? null" />
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
              <div class="flex justify-between">
                <span class="text-muted-foreground">CPU</span>
                <span>{{ status.systemSnapshot.rawData.cpu_percent }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">RAM</span>
                <span>
                  {{ (status.systemSnapshot.rawData.memory as Record<string, number>)?.percent }}%
                  ({{ (status.systemSnapshot.rawData.memory as Record<string, number>)?.used_mb?.toFixed(0) }} /
                  {{ (status.systemSnapshot.rawData.memory as Record<string, number>)?.total_mb?.toFixed(0) }} MB)
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Disk</span>
                <span>
                  {{ (status.systemSnapshot.rawData.disk as Record<string, number>)?.percent }}%
                  ({{ (status.systemSnapshot.rawData.disk as Record<string, number>)?.used_gb?.toFixed(1) }} /
                  {{ (status.systemSnapshot.rawData.disk as Record<string, number>)?.total_gb?.toFixed(1) }} GB)
                </span>
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
              <span class="truncate max-w-xs">{{ status.site.healthUrl ?? '—' }}</span>
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
    </div>

    <div v-else-if="loading" class="flex justify-center py-12">
      <RefreshCw class="size-6 animate-spin text-muted-foreground" />
    </div>
  </AuthenticatedLayout>
</template>
