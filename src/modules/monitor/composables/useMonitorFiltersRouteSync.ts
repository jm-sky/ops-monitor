import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MonitorRouteNames } from '../routes'
import type { Ref } from 'vue'
import type { LocationQuery } from 'vue-router'

const QUERY_KEYS = {
  search: 'q',
  filter: 'filter',
  environment: 'env',
} as const

interface MonitorFiltersFromQuery {
  searchQuery: string
  quickFilter: 'all' | 'issues'
  selectedEnvironment: string
}

function parseMonitorFiltersFromQuery(query: LocationQuery): MonitorFiltersFromQuery {
  const q = query[QUERY_KEYS.search]
  const filter = query[QUERY_KEYS.filter]
  const env = query[QUERY_KEYS.environment]

  return {
    searchQuery: typeof q === 'string' ? q : '',
    quickFilter: filter === 'issues' ? 'issues' : 'all',
    selectedEnvironment: typeof env === 'string' && env.length > 0 ? env : '__all__',
  }
}

function buildMonitorFiltersQuery(
  searchQuery: string,
  quickFilter: 'all' | 'issues',
  selectedEnvironment: string,
): LocationQuery {
  const query: LocationQuery = {}
  const trimmedSearch = searchQuery.trim()

  if (trimmedSearch.length > 0) {
    query[QUERY_KEYS.search] = trimmedSearch
  }
  if (quickFilter === 'issues') {
    query[QUERY_KEYS.filter] = 'issues'
  }
  if (selectedEnvironment !== '__all__') {
    query[QUERY_KEYS.environment] = selectedEnvironment
  }

  return query
}

function normalizeQueryValue(
  value: LocationQuery[string] | undefined,
): string | undefined {
  if (value === undefined || value === null) return undefined
  return String(value)
}

function monitorFilterQueriesEqual(routeQuery: LocationQuery, filtersQuery: LocationQuery): boolean {
  for (const key of Object.values(QUERY_KEYS)) {
    if (normalizeQueryValue(routeQuery[key]) !== normalizeQueryValue(filtersQuery[key])) {
      return false
    }
  }
  return true
}

export function useMonitorFiltersRouteSync(
  searchQuery: Ref<string>,
  quickFilter: Ref<'all' | 'issues'>,
  selectedEnvironment: Ref<string>,
) {
  const route = useRoute()
  const router = useRouter()
  let syncingFromRoute = false

  function applyQueryToFilters() {
    const parsed = parseMonitorFiltersFromQuery(route.query)

    syncingFromRoute = true
    try {
      if (searchQuery.value !== parsed.searchQuery) searchQuery.value = parsed.searchQuery
      if (quickFilter.value !== parsed.quickFilter) quickFilter.value = parsed.quickFilter
      if (selectedEnvironment.value !== parsed.selectedEnvironment) selectedEnvironment.value = parsed.selectedEnvironment
    } finally {
      syncingFromRoute = false
    }
  }

  function syncFiltersToRoute() {
    if (route.name !== MonitorRouteNames.monitor) return
    if (syncingFromRoute) return

    const nextQuery = buildMonitorFiltersQuery(
      searchQuery.value,
      quickFilter.value,
      selectedEnvironment.value,
    )

    if (monitorFilterQueriesEqual(route.query, nextQuery)) return

    void router.replace({ name: MonitorRouteNames.monitor, query: nextQuery })
  }

  if (route.name === MonitorRouteNames.monitor) {
    applyQueryToFilters()
  }

  watch([searchQuery, quickFilter, selectedEnvironment], () => {
    if (syncingFromRoute) return
    syncFiltersToRoute()
  })

  watch(() => route.query, () => {
    if (route.name !== MonitorRouteNames.monitor) return
    applyQueryToFilters()
  })
}
