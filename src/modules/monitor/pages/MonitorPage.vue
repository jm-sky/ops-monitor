<script setup lang="ts">
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { Activity, Plus, RefreshCw, Server } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Button from '@/components/ui/button/Button.vue'
import SearchInput from '@/components/ui/input/SearchInput.vue'
import Label from '@/components/ui/label/Label.vue'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site, SiteStatus } from '../types'
import AddSiteDialog from '../components/AddSiteDialog.vue'
import SiteGroupSection from '../components/SiteGroupSection.vue'
import { useHeartbeat } from '../composables/useHeartbeat'
import { fetchSiteStatuses, monitorQueryKeys } from '../services/monitorQueries'

const { t } = useI18n()
const router = useRouter()
const queryClient = useQueryClient()
const { handleError } = useHandleError()

useHeartbeat()

const showAddDialog = ref(false)
const searchQuery = ref('')
const quickFilter = ref<'all' | 'issues'>('all')
const selectedEnvironment = ref('__all__')
const DENSE_MODE_STORAGE_KEY = 'monitor.denseMode'
const denseMode = ref(localStorage.getItem(DENSE_MODE_STORAGE_KEY) === 'true')
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

const normalizedSearchQuery = computed(() => searchQuery.value.trim().toLowerCase())

const availableEnvironments = computed<string[]>(() => {
  const values = new Set<string>()

  for (const siteStatus of statuses.value) {
    const environment = siteStatus.site.environment?.trim()
    if (environment) {
      values.add(environment)
    }
  }

  return [...values].sort((a, b) => a.localeCompare(b))
})

function matchesSearch(siteStatus: SiteStatus, query: string): boolean {
  if (!query) return true

  const tokens = [
    siteStatus.site.name,
    siteStatus.site.description ?? '',
    siteStatus.site.serverLabel ?? '',
    siteStatus.site.environment ?? '',
    siteStatus.site.healthUrl ?? '',
    siteStatus.site.systemUrl ?? '',
  ]

  return tokens.some(value => value.toLowerCase().includes(query))
}

const filteredGroupedStatuses = computed<SiteGroup[]>(() => {
  const query = normalizedSearchQuery.value
  const showIssuesOnly = quickFilter.value === 'issues'

  return groupedStatuses.value
    .map(group => {
      const items = group.items.filter(siteStatus => {
        if (showIssuesOnly && overallStatus(siteStatus) === 'ok') return false
        if (selectedEnvironment.value !== '__all__' && siteStatus.site.environment !== selectedEnvironment.value) return false
        if (query && !matchesSearch(siteStatus, query)) return false
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
    <div class="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div class="w-full md:max-w-md">
        <SearchInput
          v-model="searchQuery"
          name="monitor-site-search"
          :placeholder="t('monitor.searchPlaceholder', 'Search sites...')"
        />
      </div>
      <div class="flex items-center gap-2 self-end">
        <Select v-model="selectedEnvironment">
          <SelectTrigger class="h-8 w-44">
            <SelectValue :placeholder="t('monitor.filterEnvironmentAll', 'All environments')" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">
              {{ t('monitor.filterEnvironmentAll', 'All environments') }}
            </SelectItem>
            <SelectItem
              v-for="environment in availableEnvironments"
              :key="environment"
              :value="environment"
            >
              {{ environment }}
            </SelectItem>
          </SelectContent>
        </Select>
        <span class="text-xs text-muted-foreground">
          {{ t('monitor.quickFilters', 'Quick filters') }}
        </span>
        <Button
          size="sm"
          :variant="quickFilter === 'all' ? 'default' : 'outline'"
          @click="quickFilter = 'all'"
        >
          {{ t('monitor.filterAll', 'All') }}
        </Button>
        <Button
          size="sm"
          :variant="quickFilter === 'issues' ? 'default' : 'outline'"
          @click="quickFilter = 'issues'"
        >
          {{ t('monitor.filterIssues', 'Issues') }}
        </Button>
      </div>
    </div>

    <!-- Grouped site grid -->
    <div
      v-if="hasSites"
      :class="[
        'mt-6',
        denseMode ? 'flex flex-wrap items-start gap-4' : 'space-y-6',
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
      <Button
        variant="outline"
        @click="
          searchQuery = '';
          quickFilter = 'all';
          selectedEnvironment = '__all__'
        "
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
