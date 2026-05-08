<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Checkbox } from '@/components/ui/checkbox'
import Input from '@/components/ui/input/Input.vue'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { Site } from '../types'
import type { AlertChannelFilters, AlertType, HealthSeverity } from '../types/alerts'
import { monitorService } from '../services/monitorService'

const filters = defineModel<AlertChannelFilters>({ required: true })

const { t } = useI18n()
const { handleError } = useHandleError()

const sites = ref<Site[]>([])
const loadingSites = ref(false)

const ALERT_TYPES: AlertType[] = ['health', 'reboot', 'updates']

const TIMEZONES: string[] = [
  'Europe/Warsaw',
  'Europe/London',
  'Europe/Berlin',
  'UTC',
  'America/New_York',
  'Asia/Tokyo',
]

const allTags = computed<string[]>(() => {
  const set = new Set<string>()
  for (const s of sites.value) {
    for (const tag of s.tags ?? []) set.add(tag)
  }
  return [...set].sort()
})

const cooldownInput = ref<string>(
  filters.value.re_alert_after_minutes != null
    ? String(filters.value.re_alert_after_minutes)
    : '',
)

const healthSelected = computed(() =>
  filters.value.alert_types.length === 0
    || filters.value.alert_types.includes('health'),
)

function toggleAlertType(type: AlertType) {
  const current = new Set(filters.value.alert_types)
  if (current.has(type)) current.delete(type)
  else current.add(type)
  filters.value = { ...filters.value, alert_types: [...current] }
}

function isAlertTypeChecked(type: AlertType): boolean {
  return filters.value.alert_types.includes(type)
}

function setMinSeverity(value: string) {
  filters.value = { ...filters.value, min_health_severity: value as HealthSeverity }
}

function toggleSite(siteId: string) {
  const current = new Set(filters.value.site_ids)
  if (current.has(siteId)) current.delete(siteId)
  else current.add(siteId)
  filters.value = { ...filters.value, site_ids: [...current] }
}

function toggleTag(tag: string) {
  const current = new Set(filters.value.tags)
  if (current.has(tag)) current.delete(tag)
  else current.add(tag)
  filters.value = { ...filters.value, tags: [...current] }
}

function setQuietEnabled(value: boolean) {
  filters.value = {
    ...filters.value,
    quiet_hours: { ...filters.value.quiet_hours, enabled: value },
  }
}

function setQuietStart(value: string) {
  filters.value = {
    ...filters.value,
    quiet_hours: { ...filters.value.quiet_hours, start: value },
  }
}

function setQuietEnd(value: string) {
  filters.value = {
    ...filters.value,
    quiet_hours: { ...filters.value.quiet_hours, end: value },
  }
}

function setQuietTimezone(value: string) {
  filters.value = {
    ...filters.value,
    quiet_hours: { ...filters.value.quiet_hours, timezone: value },
  }
}

function onCooldownInput(value: string) {
  cooldownInput.value = value
  const trimmed = value.trim()
  if (!trimmed) {
    filters.value = { ...filters.value, re_alert_after_minutes: null }
    return
  }
  const parsed = Number.parseInt(trimmed, 10)
  if (Number.isFinite(parsed) && parsed >= 1) {
    filters.value = { ...filters.value, re_alert_after_minutes: parsed }
  }
}

async function loadSites() {
  loadingSites.value = true
  try {
    sites.value = await monitorService.listSites()
  } catch (error) {
    handleError(error, { fallbackMessage: t('monitor.loadError', 'Failed to load sites') })
  } finally {
    loadingSites.value = false
  }
}

onMounted(loadSites)
</script>

<template>
  <div class="space-y-5 rounded-md border p-4">
    <div class="space-y-1">
      <h3 class="text-sm font-semibold">
        {{ t('monitor.alerts.filters.title', 'Filters') }}
      </h3>
      <p class="text-xs text-muted-foreground">
        {{ t('monitor.alerts.filters.hint', 'Empty selections mean no restriction.') }}
      </p>
    </div>

    <div class="space-y-2">
      <Label>{{ t('monitor.alerts.filters.alertTypes', 'Alert types') }}</Label>
      <div class="flex flex-wrap gap-3">
        <label
          v-for="type in ALERT_TYPES"
          :key="type"
          class="flex cursor-pointer items-center gap-2 text-sm"
        >
          <Checkbox
            :model-value="isAlertTypeChecked(type)"
            @update:model-value="toggleAlertType(type)"
          />
          <span>{{ t(`monitor.alerts.type.${type}`, type) }}</span>
        </label>
      </div>
      <p class="text-xs text-muted-foreground">
        {{ t('monitor.alerts.filters.alertTypesHint', 'No selection = all types.') }}
      </p>
    </div>

    <div v-if="healthSelected" class="space-y-2">
      <Label>{{ t('monitor.alerts.filters.minSeverity', 'Health severity') }}</Label>
      <RadioGroup
        :model-value="filters.min_health_severity"
        class="flex gap-4"
        @update:model-value="setMinSeverity"
      >
        <div class="flex items-center gap-2">
          <RadioGroupItem id="sev-degraded" value="degraded" />
          <Label for="sev-degraded" class="cursor-pointer text-sm font-normal">
            {{ t('monitor.alerts.filters.severity.degraded', 'Degraded + Failed') }}
          </Label>
        </div>
        <div class="flex items-center gap-2">
          <RadioGroupItem id="sev-failed" value="failed" />
          <Label for="sev-failed" class="cursor-pointer text-sm font-normal">
            {{ t('monitor.alerts.filters.severity.failed', 'Failed only') }}
          </Label>
        </div>
      </RadioGroup>
    </div>

    <div class="space-y-2">
      <Label>{{ t('monitor.alerts.filters.sites', 'Sites') }}</Label>
      <div
        v-if="sites.length > 0"
        class="max-h-40 overflow-y-auto rounded-md border p-2 space-y-1.5"
      >
        <label
          v-for="site in sites"
          :key="site.id"
          class="flex cursor-pointer items-center gap-2 text-sm"
        >
          <Checkbox
            :model-value="filters.site_ids.includes(site.id)"
            @update:model-value="toggleSite(site.id)"
          />
          <span>{{ site.name }}</span>
        </label>
      </div>
      <p v-else-if="!loadingSites" class="text-xs text-muted-foreground">
        {{ t('monitor.alerts.filters.noSites', 'No sites configured yet.') }}
      </p>
      <p class="text-xs text-muted-foreground">
        {{ t('monitor.alerts.filters.sitesHint', 'No selection = all sites (combined with tags as OR).') }}
      </p>
    </div>

    <div class="space-y-2">
      <Label>{{ t('monitor.alerts.filters.tags', 'Tags') }}</Label>
      <div
        v-if="allTags.length > 0"
        class="flex flex-wrap gap-2"
      >
        <button
          v-for="tag in allTags"
          :key="tag"
          type="button"
          class="rounded-full border px-2.5 py-0.5 text-xs transition-colors"
          :class="filters.tags.includes(tag)
            ? 'bg-primary text-primary-foreground border-primary'
            : 'bg-background hover:bg-accent'"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
      <p v-else class="text-xs text-muted-foreground">
        {{ t('monitor.alerts.filters.noTags', 'No tags found across sites.') }}
      </p>
    </div>

    <div class="space-y-2">
      <div class="flex items-center justify-between gap-3">
        <Label class="cursor-pointer" for="qh-enabled">
          {{ t('monitor.alerts.filters.quietHours', 'Quiet hours') }}
        </Label>
        <Switch
          id="qh-enabled"
          :model-value="filters.quiet_hours.enabled"
          @update:model-value="setQuietEnabled"
        />
      </div>
      <div v-if="filters.quiet_hours.enabled" class="grid grid-cols-3 gap-2">
        <div class="space-y-1">
          <Label for="qh-start" class="text-xs">
            {{ t('monitor.alerts.filters.quietStart', 'Start') }}
          </Label>
          <Input
            id="qh-start"
            type="time"
            :model-value="filters.quiet_hours.start"
            @update:model-value="value => setQuietStart(String(value))"
          />
        </div>
        <div class="space-y-1">
          <Label for="qh-end" class="text-xs">
            {{ t('monitor.alerts.filters.quietEnd', 'End') }}
          </Label>
          <Input
            id="qh-end"
            type="time"
            :model-value="filters.quiet_hours.end"
            @update:model-value="value => setQuietEnd(String(value))"
          />
        </div>
        <div class="space-y-1">
          <Label class="text-xs">
            {{ t('monitor.alerts.filters.timezone', 'Timezone') }}
          </Label>
          <Select
            :model-value="filters.quiet_hours.timezone"
            @update:model-value="value => setQuietTimezone(String(value))"
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="tz in TIMEZONES" :key="tz" :value="tz">
                {{ tz }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>

    <div class="space-y-1.5">
      <Label for="ch-cooldown">
        {{ t('monitor.alerts.filters.cooldown', 'Re-alert cooldown (minutes)') }}
      </Label>
      <Input
        id="ch-cooldown"
        type="number"
        min="1"
        :model-value="cooldownInput"
        :placeholder="t('monitor.alerts.filters.cooldownPlaceholder', 'leave empty = off')"
        @update:model-value="value => onCooldownInput(String(value))"
      />
      <p class="text-xs text-muted-foreground">
        {{ t('monitor.alerts.filters.cooldownHint', 'If status stays bad, re-send after N minutes. Empty = no repeats.') }}
      </p>
    </div>
  </div>
</template>
