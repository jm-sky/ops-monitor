<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import SearchInput from '@/components/ui/input/SearchInput.vue'

interface EnvironmentOption {
  count: number
  value: string
}

const props = defineProps<{
  environmentOptions: EnvironmentOption[]
  hasActiveFilters: boolean
  resultSummary: string
}>()

const searchQuery = defineModel<string>('searchQuery', { required: true })
const quickFilter = defineModel<'all' | 'issues'>('quickFilter', { required: true })
const selectedEnvironment = defineModel<string>('selectedEnvironment', { required: true })

const { t } = useI18n()

function clearSearchQuery() {
  searchQuery.value = ''
}

function clearFilters() {
  clearSearchQuery()
  quickFilter.value = 'all'
  selectedEnvironment.value = '__all__'
}

function removeFilter(filter: 'search' | 'issues' | 'environment') {
  if (filter === 'search') {
    clearSearchQuery()
    return
  }
  if (filter === 'issues') {
    quickFilter.value = 'all'
    return
  }
  selectedEnvironment.value = '__all__'
}
</script>

<template>
  <div class="mt-4 space-y-3">
    <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
      <div class="w-full space-y-1 md:max-w-md">
        <SearchInput
          v-model="searchQuery"
          name="monitor-site-search"
          :placeholder="t('monitor.searchPlaceholder', 'Search sites...')"
          @keydown.esc="clearSearchQuery"
        />
        <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <span>{{ t('monitor.searchShortcutHint', 'Press Esc to clear search') }}</span>
          <span>•</span>
          <span>{{ props.resultSummary }}</span>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-2 md:self-start">
        <div class="flex flex-wrap items-center rounded-md border border-border/90 bg-background p-0.5">
          <Button
            size="sm"
            :variant="selectedEnvironment === '__all__' ? 'default' : 'ghost'"
            @click="selectedEnvironment = '__all__'"
          >
            {{ t('monitor.filterEnvironmentAll', 'All environments') }}
          </Button>
          <Button
            v-for="environmentOption in props.environmentOptions"
            :key="environmentOption.value"
            size="sm"
            :variant="selectedEnvironment === environmentOption.value ? 'default' : 'ghost'"
            @click="selectedEnvironment = environmentOption.value"
          >
            {{
              t('monitor.environmentOptionWithCount', {
                count: environmentOption.count,
                environment: environmentOption.value,
              })
            }}
          </Button>
        </div>
        <div class="flex items-center rounded-md border border-border/90 bg-background p-0.5">
          <Button
            size="sm"
            :variant="quickFilter === 'all' ? 'default' : 'ghost'"
            @click="quickFilter = 'all'"
          >
            {{ t('monitor.filterAll', 'All') }}
          </Button>
          <Button
            size="sm"
            :variant="quickFilter === 'issues' ? 'default' : 'ghost'"
            @click="quickFilter = 'issues'"
          >
            {{ t('monitor.filterIssues', 'Issues') }}
          </Button>
        </div>
        <Button
          variant="outline"
          size="sm"
          :disabled="!props.hasActiveFilters"
          @click="clearFilters"
        >
          {{ t('monitor.clearFilters', 'Clear filters') }}
        </Button>
      </div>
    </div>

    <div v-if="props.hasActiveFilters" class="flex flex-wrap items-center gap-2 text-xs">
      <span class="text-muted-foreground">
        {{ t('monitor.activeFilters', 'Active filters') }}
      </span>
      <Button
        v-if="searchQuery.trim().length > 0"
        size="xs"
        variant="secondary"
        @click="removeFilter('search')"
      >
        {{ t('monitor.activeFilterQuery', { query: searchQuery.trim().replace(/\s+/g, ' ') }) }}
        <X class="size-3" />
      </Button>
      <Button
        v-if="quickFilter === 'issues'"
        size="xs"
        variant="secondary"
        @click="removeFilter('issues')"
      >
        {{ t('monitor.activeFilterIssues', 'Issues only') }}
        <X class="size-3" />
      </Button>
      <Button
        v-if="selectedEnvironment !== '__all__'"
        size="xs"
        variant="secondary"
        @click="removeFilter('environment')"
      >
        {{ t('monitor.activeFilterEnvironment', { environment: selectedEnvironment }) }}
        <X class="size-3" />
      </Button>
    </div>
  </div>
</template>
