<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Pagination from '@/components/data-table/Pagination.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import { monitorQueryKeys } from '../services/monitorQueries'
import { monitorService } from '../services/monitorService'
import PackageUpdateEventRow from './PackageUpdateEventRow.vue'

const { siteId } = defineProps<{
  siteId: string
}>()

const { t } = useI18n()

const PAGE_SIZE_OPTIONS = [10, 20, 50]

const includeAutomatic = ref(true)
const page = ref(1)
const pageSize = ref(10)
const offset = computed(() => (page.value - 1) * pageSize.value)

const { data, error, isLoading } = useQuery({
  queryKey: computed(() => monitorQueryKeys.packageUpdates(siteId, includeAutomatic.value, pageSize.value, offset.value)),
  queryFn: () => monitorService.getPackageUpdates(siteId, {
    includeAutomatic: includeAutomatic.value,
    limit: pageSize.value,
    offset: offset.value,
  }),
  placeholderData: previousData => previousData,
})

const events = computed(() => data.value?.items ?? [])
const total = computed(() => data.value?.total ?? 0)

watch(includeAutomatic, () => {
  page.value = 1
})

watch(error, (queryError) => {
  if (queryError) toast.error(t('monitor.packageUpdates.loadError', 'Failed to load update history'))
})

function setPageSize(size: number) {
  pageSize.value = size
  page.value = 1
}
</script>

<template>
  <Card>
    <CardHeader class="pb-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <CardTitle>{{ t('monitor.packageUpdates.title', 'Update history') }}</CardTitle>
        <div class="flex items-center gap-2">
          <Switch :id="`package-updates-automatic-${siteId}`" v-model="includeAutomatic" />
          <Label :for="`package-updates-automatic-${siteId}`" class="cursor-pointer select-none text-sm">
            {{ t('monitor.packageUpdates.showAutomatic', 'Include automatic runs') }}
          </Label>
        </div>
      </div>
    </CardHeader>
    <CardContent>
      <div v-if="isLoading" class="py-6 text-center text-sm text-muted-foreground">
        {{ t('common.loading', 'Loading...') }}
      </div>
      <div v-else-if="!events.length" class="py-6 text-center text-sm text-muted-foreground">
        {{ t('monitor.packageUpdates.empty', 'No package updates recorded yet') }}
      </div>
      <div v-else class="space-y-4">
        <ul>
          <PackageUpdateEventRow v-for="event in events" :key="event.id" :event />
        </ul>
        <Pagination
          v-model:page="page"
          :page-size
          :total
          :page-size-options="PAGE_SIZE_OPTIONS"
          @update:page-size="setPageSize"
        />
      </div>
    </CardContent>
  </Card>
</template>
