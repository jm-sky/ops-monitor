<script setup lang="ts">
import { Activity, Plus, RefreshCw, Server } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteStatus } from '../types'
import AddSiteDialog from '../components/AddSiteDialog.vue'
import SiteStatusBadge from '../components/SiteStatusBadge.vue'
import { monitorService } from '../services/monitorService'

const { t } = useI18n()
const router = useRouter()
const { handleError } = useHandleError()

const statuses = ref<SiteStatus[]>([])
const loading = ref(false)
const showAddDialog = ref(false)

async function loadSites() {
  loading.value = true
  try {
    const sites = await monitorService.listSites()
    // Fetch status for each site in parallel
    statuses.value = await Promise.all(sites.map(site => monitorService.getSite(site.id)))
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.loadError', 'Failed to load sites') })
  } finally {
    loading.value = false
  }
}

function overallStatus(s: SiteStatus): string {
  const h = s.healthSnapshot?.status
  const sys = s.systemSnapshot?.status
  if (h === 'failed' || sys === 'failed') return 'failed'
  if (h === 'degraded') return 'degraded'
  if (sys === 'reboot_required') return 'reboot_required'
  if (sys === 'outdated') return 'outdated'
  if (h === 'ok' || sys === 'up_to_date') return 'ok'
  return 'unknown'
}

function goToSite(id: string) {
  router.push({ name: 'monitor-site', params: { id } })
}

function onSiteAdded(_site: Site) {
  showAddDialog.value = false
  toast.success(t('monitor.siteAdded', 'Site added'))
  loadSites()
}

onMounted(loadSites)
</script>

<template>
  <AuthenticatedLayout>
    <CommonPageHeader :label="t('monitor.title', 'Monitor')" :icon="Activity">
      <template #actions>
        <Button
          variant="outline"
          size="sm"
          :disabled="loading"
          @click="loadSites"
        >
          <RefreshCw :class="['size-4', loading && 'animate-spin']" />
          {{ t('common.refresh', 'Refresh') }}
        </Button>
        <Button size="sm" @click="showAddDialog = true">
          <Plus class="size-4" />
          {{ t('monitor.addSite', 'Add site') }}
        </Button>
      </template>
    </CommonPageHeader>

    <!-- Site grid -->
    <div v-if="statuses.length > 0" class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card
        v-for="s in statuses"
        :key="s.site.id"
        class="cursor-pointer transition-shadow hover:shadow-md"
        @click="goToSite(s.site.id)"
      >
        <CardHeader class="flex flex-row items-start justify-between gap-2 pb-2">
          <div class="flex items-center gap-2 min-w-0">
            <Server class="size-4 shrink-0 text-muted-foreground" />
            <CardTitle class="truncate text-base">
              {{ s.site.name }}
            </CardTitle>
          </div>
          <SiteStatusBadge :status="overallStatus(s)" />
        </CardHeader>
        <CardContent class="space-y-1 text-sm text-muted-foreground">
          <div v-if="s.site.description" class="truncate">
            {{ s.site.description }}
          </div>
          <div class="flex flex-wrap gap-2 pt-1">
            <span v-if="s.healthSnapshot" class="flex items-center gap-1">
              <span class="font-medium text-foreground">Health:</span>
              <SiteStatusBadge :status="s.healthSnapshot.status ?? 'unknown'" size="sm" />
            </span>
            <span v-if="s.systemSnapshot" class="flex items-center gap-1">
              <span class="font-medium text-foreground">System:</span>
              <SiteStatusBadge :status="s.systemSnapshot.status ?? 'unknown'" size="sm" />
            </span>
          </div>
          <div v-if="!s.site.enabled" class="text-xs text-muted-foreground italic">
            {{ t('monitor.disabled', 'Polling disabled') }}
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="mt-12 flex flex-col items-center gap-4 text-center text-muted-foreground">
      <Server class="size-12 opacity-30" />
      <p class="text-lg font-medium">
        {{ t('monitor.noSites', 'No sites configured') }}
      </p>
      <p class="text-sm">
        {{ t('monitor.noSitesHint', 'Add a site to start monitoring.') }}
      </p>
      <Button @click="showAddDialog = true">
        <Plus class="size-4" />
        {{ t('monitor.addSite', 'Add site') }}
      </Button>
    </div>

    <AddSiteDialog v-model:open="showAddDialog" @created="onSiteAdded" />
  </AuthenticatedLayout>
</template>
