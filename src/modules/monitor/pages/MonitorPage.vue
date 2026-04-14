<script setup lang="ts">
import { Activity, Plus, RefreshCw, Server } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Button from '@/components/ui/button/Button.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteStatus } from '../types'
import AddSiteDialog from '../components/AddSiteDialog.vue'
import SiteGroupSection from '../components/SiteGroupSection.vue'
import { monitorService } from '../services/monitorService'

let cachedStatuses: SiteStatus[] = []
let hasCachedResult = false

const { t } = useI18n()
const router = useRouter()
const { handleError } = useHandleError()

const statuses = ref<SiteStatus[]>([...cachedStatuses])
const loading = ref(false)
const showAddDialog = ref(false)
const hasLoadedOnce = ref(hasCachedResult)

interface SiteGroup {
  key: string
  label: string
  items: SiteStatus[]
}

async function loadSites() {
  loading.value = true
  try {
    const sites = await monitorService.listSites()
    // Fetch status for each site in parallel
    const freshStatuses = await Promise.all(sites.map(site => monitorService.getSite(site.id)))
    statuses.value = freshStatuses
    cachedStatuses = [...freshStatuses]
    hasCachedResult = true
    hasLoadedOnce.value = true
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

function compareSiteInGroup(a: SiteStatus, b: SiteStatus): number {
  const aHasHealth = Boolean(a.site.healthUrl)
  const bHasHealth = Boolean(b.site.healthUrl)
  if (aHasHealth !== bHasHealth) return aHasHealth ? -1 : 1
  return a.site.name.localeCompare(b.site.name)
}

function compareSiteInServerGroup(a: SiteStatus, b: SiteStatus, serverLabel: string): number {
  const aIsServerSite = a.site.name === serverLabel
  const bIsServerSite = b.site.name === serverLabel
  if (aIsServerSite !== bIsServerSite) return aIsServerSite ? -1 : 1
  return compareSiteInGroup(a, b)
}

const groupedStatuses = computed<SiteGroup[]>(() => {
  const groupsMap = new Map<string, SiteStatus[]>()

  for (const status of statuses.value) {
    const label = status.site.serverLabel?.trim() ?? ''
    const key = label ?? '__ungrouped__'
    const existing = groupsMap.get(key)
    if (existing) {
      existing.push(status)
    } else {
      groupsMap.set(key, [status])
    }
  }

  const groups: SiteGroup[] = Array.from(groupsMap.entries()).map(([key, items]) => {
    const sortedItems = [...items].sort((a, b) => {
      if (key === '__ungrouped__') return compareSiteInGroup(a, b)
      return compareSiteInServerGroup(a, b, key)
    })

    return {
      key,
      label: key === '__ungrouped__' ? t('monitor.ungrouped', 'Ungrouped') : key,
      items: sortedItems,
    }
  })

  return groups.sort((a, b) => {
    if (a.key === '__ungrouped__') return 1
    if (b.key === '__ungrouped__') return -1
    return a.label.localeCompare(b.label)
  })
})

const hasSites = computed(() => groupedStatuses.value.length > 0)
const isRefreshing = computed(() => loading.value && hasSites.value)
const showEmptyState = computed(() => hasLoadedOnce.value && !loading.value && !hasSites.value)

onMounted(loadSites)
</script>

<template>
  <AuthenticatedLayout>
    <CommonPageHeader :label="t('monitor.title', 'Monitor')" :icon="Activity">
      <template #actions>
        <div v-if="isRefreshing" class="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw class="size-3 animate-spin" />
          {{ t('monitor.refreshing', 'Refreshing...') }}
        </div>
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

    <!-- Grouped site grid -->
    <div v-if="hasSites" class="mt-6 space-y-6">
      <SiteGroupSection
        v-for="group in groupedStatuses"
        :key="group.key"
        :group="group"
        :overall-status="overallStatus"
        :disabled-label="t('monitor.disabled', 'Polling disabled')"
        @select-site="goToSite"
      />
    </div>

    <!-- Empty state -->
    <div v-else-if="showEmptyState" class="mt-12 flex flex-col items-center gap-4 text-center text-muted-foreground">
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
