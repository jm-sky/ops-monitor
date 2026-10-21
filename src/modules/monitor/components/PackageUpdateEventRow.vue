<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import type { PackageAction, PackageChange, PackageUpdateEvent } from '../types'
import { formatDuration, formatMonitorDate } from '../composables/useMonitorFormatters'

const { event } = defineProps<{
  event: PackageUpdateEvent
}>()

const { t } = useI18n()

const ACTIONS: PackageAction[] = ['install', 'upgrade', 'remove', 'purge']

const groups = computed(() =>
  ACTIONS
    .map(action => ({ action, items: event.packages[action] ?? [] }))
    .filter(group => group.items.length > 0),
)
const packageCount = computed(() => groups.value.reduce((sum, group) => sum + group.items.length, 0))

function versionLabel(pkg: PackageChange): string {
  if (pkg.from_version && pkg.to_version) return `${pkg.from_version} → ${pkg.to_version}`
  return pkg.to_version ?? pkg.from_version ?? ''
}
</script>

<template>
  <li class="space-y-2 border-b py-3 last:border-0">
    <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
      <span class="text-sm font-medium whitespace-nowrap">{{ formatMonitorDate(event.startedAt) }}</span>
      <Badge
        :variant="event.automatic ? 'secondary' : 'outline'"
        class="h-5.5 rounded-md px-2 text-[11px] font-medium"
      >
        {{ event.automatic ? t('monitor.packageUpdates.automatic', 'Automatic') : t('monitor.packageUpdates.manual', 'Manual') }}
      </Badge>
      <span v-if="event.requestedBy" class="text-xs text-muted-foreground">
        {{ t('monitor.packageUpdates.by', { user: event.requestedBy }) }}
      </span>
      <span class="text-xs text-muted-foreground">
        {{ t('monitor.packageUpdates.duration', 'Duration') }}:
        <template v-if="event.finishedAt">{{ formatDuration(event.durationSeconds) }}</template>
        <template v-else>{{ t('monitor.packageUpdates.unfinished', 'no end time (interrupted?)') }}</template>
      </span>
    </div>

    <code v-if="event.commandline" class="block break-all rounded bg-muted px-2 py-1 text-xs">
      {{ event.commandline }}
    </code>

    <details v-if="packageCount > 0" class="text-xs">
      <summary class="cursor-pointer text-muted-foreground">
        {{ t('monitor.packageUpdates.packagesCount', { count: packageCount }) }}
        —
        {{ groups.map(g => `${t(`monitor.packageUpdates.${g.action}`)} ${g.items.length}`).join(', ') }}
      </summary>
      <div v-for="group in groups" :key="group.action" class="mt-2">
        <p class="font-medium">
          {{ t(`monitor.packageUpdates.${group.action}`) }}
        </p>
        <ul class="mt-1 grid gap-x-4 gap-y-0.5 sm:grid-cols-2">
          <li v-for="pkg in group.items" :key="`${pkg.name}:${pkg.arch}`" class="break-all">
            <span class="font-mono">{{ pkg.name }}</span>
            <span class="text-muted-foreground"> {{ versionLabel(pkg) }}</span>
            <span v-if="pkg.auto_installed" class="text-muted-foreground"> ({{ t('monitor.packageUpdates.dependency', 'dependency') }})</span>
          </li>
        </ul>
      </div>
    </details>
  </li>
</template>
