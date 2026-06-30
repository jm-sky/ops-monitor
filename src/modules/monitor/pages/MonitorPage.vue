<script setup lang="ts">
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { Activity, Plus, RefreshCw, Server } from 'lucide-vue-next'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Button from '@/components/ui/button/Button.vue'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { MonitorOverallStatus, Site, SiteStatus } from '../types'
import AddSiteDialog from '../components/AddSiteDialog.vue'
import MonitorFiltersBar from '../components/MonitorFiltersBar.vue'
import SiteGroupSection from '../components/SiteGroupSection.vue'
import { useHeartbeat } from '../composables/useHeartbeat'
import { useMonitorFiltersRouteSync } from '../composables/useMonitorFiltersRouteSync'
import { useMonitorViewActivity } from '../composables/useMonitorViewActivity'
import { fetchSiteStatuses, monitorQueryKeys } from '../services/monitorQueries'

const { t } = useI18n()
const router = useRouter()
const queryClient = useQueryClient()
const { handleError } = useHandleError()
const {
  isMonitoringViewActive,
  monitorHeartbeatIntervalMs,
  monitorRefetchIntervalMs,
} = useMonitorViewActivity()

useHeartbeat({
  enabled: isMonitoringViewActive,
  intervalMs: monitorHeartbeatIntervalMs,
})

const showAddDialog = ref(false)
const searchQuery = ref('')
const debouncedSearchQuery = ref('')
const quickFilter = ref<'all' | 'issues'>('all')
const selectedEnvironment = ref('__all__')

useMonitorFiltersRouteSync(searchQuery, quickFilter, selectedEnvironment)

const DENSE_MODE_STORAGE_KEY = 'monitor.denseMode'
const denseMode = ref(localStorage.getItem(DENSE_MODE_STORAGE_KEY) === 'true')
let searchDebounceTimeout: ReturnType<typeof setTimeout> | undefined
const {
  data: queryData,
  error,
  isError,
  isFetching,
  isLoading,
  isFetched,
} = useQuery<SiteStatus[]>({
  queryKey: monitorQueryKeys.siteStatuses(),
  queryFn: fetchSiteStatuses,
  placeholderData: previousData => previousData,
  refetchInterval: () => monitorRefetchIntervalMs.value,
})
const statuses = computed<SiteStatus[]>(() => queryData.value ?? [])

interface SiteGroup {
  key: string
  label: string
  items: SiteStatus[]
}

async function loadSites() {
  await queryClient.invalidateQueries({ queryKey: monitorQueryKeys.siteStatuses() })
}

function overallStatus(s: SiteStatus): MonitorOverallStatus {
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
  void loadSites()
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
    const key = label.length > 0 ? label : '__ungrouped__'
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

const normalizedSearchQuery = computed(() =>
  debouncedSearchQuery.value.trim().replace(/\s+/g, ' ').toLowerCase(),
)
const normalizedSearchTerms = computed(() =>
  normalizedSearchQuery.value.length > 0
    ? normalizedSearchQuery.value.split(' ').filter(Boolean)
    : [],
)

interface EnvironmentOption {
  count: number
  value: string
}

const environmentOptions = computed<EnvironmentOption[]>(() => {
  const counts = new Map<string, number>()

  for (const siteStatus of statuses.value) {
    const environment = siteStatus.site.environment?.trim()
    if (environment) {
      counts.set(environment, (counts.get(environment) ?? 0) + 1)
    }
  }

  return [...counts.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }))
})

function normalizeSearchValue(value: string): string {
  return value.trim().replace(/\s+/g, ' ').toLowerCase()
}

function matchesSearch(siteStatus: SiteStatus, searchTerms: string[]): boolean {
  if (searchTerms.length === 0) return true

  const tokens = [
    siteStatus.site.name,
    siteStatus.site.description ?? '',
    siteStatus.site.serverLabel ?? '',
    siteStatus.site.environment ?? '',
    siteStatus.site.healthUrl ?? '',
    siteStatus.site.systemUrl ?? '',
  ].map(normalizeSearchValue)

  return searchTerms.every(term => tokens.some(value => value.includes(term)))
}

const filteredGroupedStatuses = computed<SiteGroup[]>(() => {
  const searchTerms = normalizedSearchTerms.value
  const showIssuesOnly = quickFilter.value === 'issues'

  return groupedStatuses.value
    .map(group => {
      const items = group.items.filter(siteStatus => {
        if (showIssuesOnly && overallStatus(siteStatus) === 'ok') return false
        if (selectedEnvironment.value !== '__all__' && siteStatus.site.environment?.trim() !== selectedEnvironment.value) return false
        if (searchTerms.length > 0 && !matchesSearch(siteStatus, searchTerms)) return false
        return true
      })

      return {
        ...group,
        items,
      }
    })
    .filter(group => group.items.length > 0)
})

const hasAnySites = computed(() => groupedStatuses.value.length > 0)
const hasSites = computed(() => filteredGroupedStatuses.value.length > 0)
const filteredSiteCount = computed(() =>
  filteredGroupedStatuses.value.reduce((sum, group) => sum + group.items.length, 0),
)
const activeFilterHints = computed<string[]>(() => {
  const hints: string[] = []

  if (normalizedSearchQuery.value) {
    hints.push(t('monitor.activeFilterQuery', { query: normalizedSearchQuery.value }))
  }
  if (quickFilter.value === 'issues') {
    hints.push(t('monitor.activeFilterIssues', 'Issues only'))
  }
  if (selectedEnvironment.value !== '__all__') {
    hints.push(t('monitor.activeFilterEnvironment', { environment: selectedEnvironment.value }))
  }

  return hints
})
const resultSummary = computed(() =>
  t('monitor.resultsSummary', {
    groups: filteredGroupedStatuses.value.length,
    sites: filteredSiteCount.value,
  }),
)
const hasActiveFilters = computed(() =>
  normalizedSearchQuery.value.length > 0
  || quickFilter.value === 'issues'
  || selectedEnvironment.value !== '__all__',
)
const isRefreshing = computed(() => isFetching.value && hasSites.value)
const showEmptyState = computed(() => isFetched.value && !isFetching.value && !hasAnySites.value && !isError.value)
const showNoResultsState = computed(() =>
  isFetched.value
  && !isFetching.value
  && hasAnySites.value
  && !hasSites.value
  && (normalizedSearchQuery.value.length > 0 || quickFilter.value === 'issues' || selectedEnvironment.value !== '__all__')
  && !isError.value,
)

watch(error, (queryError, previousError) => {
  if (queryError && queryError !== previousError) {
    handleError(queryError, { fallbackMessage: t('monitor.loadError', 'Failed to load sites') })
  }
})

watch(denseMode, value => {
  localStorage.setItem(DENSE_MODE_STORAGE_KEY, String(value))
})

watch(searchQuery, value => {
  if (searchDebounceTimeout) clearTimeout(searchDebounceTimeout)
  searchDebounceTimeout = setTimeout(() => {
    debouncedSearchQuery.value = value
  }, 200)
}, { immediate: true })

watch(environmentOptions, options => {
  if (selectedEnvironment.value === '__all__') return
  const stillExists = options.some(option => option.value === selectedEnvironment.value)
  if (!stillExists) {
    const staleEnvironment = selectedEnvironment.value
    selectedEnvironment.value = '__all__'
    toast.info(t('monitor.environmentResetInfo', { environment: staleEnvironment }))
  }
})

onBeforeUnmount(() => {
  if (searchDebounceTimeout) clearTimeout(searchDebounceTimeout)
})

function clearFilters() {
  searchQuery.value = ''
  quickFilter.value = 'all'
  selectedEnvironment.value = '__all__'
}
</script>

<template>
  <AuthenticatedLayout>
    <CommonPageHeader :label="t('monitor.title', 'Monitor')" :icon="Activity">
      <template #actions>
        <div v-if="isRefreshing" class="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw class="size-3 animate-spin" />
          {{ t('monitor.refreshing', 'Refreshing...') }}
        </div>
        <div class="flex items-center gap-2 mr-2">
          <Switch id="monitor-dense-mode" v-model="denseMode" />
          <Label for="monitor-dense-mode" class="cursor-pointer select-none text-sm">
            {{ t('monitor.denseMode', 'Dense mode') }}
          </Label>
        </div>
        <Button
          variant="outline"
          size="sm"
          :disabled="isFetching"
          @click="loadSites"
        >
          <RefreshCw :class="['size-4', isFetching && 'animate-spin']" />
          {{ t('common.refresh', 'Refresh') }}
        </Button>
        <Button size="sm" @click="showAddDialog = true">
          <Plus class="size-4" />
          {{ t('monitor.addSite', 'Add site') }}
        </Button>
      </template>
    </CommonPageHeader>
    <MonitorFiltersBar
      v-model:search-query="searchQuery"
      v-model:quick-filter="quickFilter"
      v-model:selected-environment="selectedEnvironment"
      :environment-options="environmentOptions"
      :has-active-filters="hasActiveFilters"
      :result-summary="resultSummary"
    />

    <!-- Grouped site grid -->
    <div
      v-if="hasSites"
      :class="[
        'mt-6',
        denseMode
          ? 'columns-1 gap-4 space-y-4 sm:columns-2 lg:columns-3 2xl:columns-4'
          : 'space-y-6',
      ]"
    >
      <SiteGroupSection
        v-for="group in filteredGroupedStatuses"
        :key="group.key"
        :group="group"
        :overall-status="overallStatus"
        :disabled-label="t('monitor.disabled', 'Polling disabled')"
        :dense-mode="denseMode"
        @select-site="goToSite"
      />
    </div>

    <div v-else-if="showNoResultsState" class="mt-12 flex flex-col items-center gap-4 text-center text-muted-foreground">
      <Server class="size-12 opacity-30" />
      <p class="text-lg font-medium">
        {{ t('monitor.noSearchResults', 'No matching sites') }}
      </p>
      <p class="text-sm">
        {{
          quickFilter === 'issues'
            ? t('monitor.noIssueResultsHint', 'No sites with issues for the current search/filter.')
            : t('monitor.noSearchResultsHint', 'Try a different search phrase.')
        }}
      </p>
      <p v-if="activeFilterHints.length > 0" class="text-xs">
        {{ t('monitor.activeFiltersSummary', { filters: activeFilterHints.join(' | ') }) }}
      </p>
      <Button
        variant="outline"
        @click="clearFilters"
      >
        {{ t('monitor.clearFilters', 'Clear filters') }}
      </Button>
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

    <div v-else-if="isLoading" class="mt-12 flex justify-center">
      <RefreshCw class="size-6 animate-spin text-muted-foreground" />
    </div>

    <AddSiteDialog v-model:open="showAddDialog" @created="onSiteAdded" />
  </AuthenticatedLayout>
</template>
