import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { MonitorRouteNames } from '../routes'
import { useMonitorRuntimeConfig } from './useMonitorRuntimeConfig'

const MONITOR_ACTIVE_ROUTE_NAMES = new Set([
  MonitorRouteNames.monitor,
  MonitorRouteNames.site,
])

export function useMonitorViewActivity() {
  const route = useRoute()
  const { runtimeConfigMs } = useMonitorRuntimeConfig()
  const isDocumentVisible = ref(document.visibilityState === 'visible')

  const isMonitoringRoute = computed(() => (
    typeof route.name === 'string'
    && MONITOR_ACTIVE_ROUTE_NAMES.has(route.name)
  ))

  const isMonitoringViewActive = computed(() => isMonitoringRoute.value && isDocumentVisible.value)
  const monitorRefetchIntervalMs = computed(() => (
    isMonitoringViewActive.value
      ? runtimeConfigMs.value.activeRefetchIntervalMs
      : runtimeConfigMs.value.backgroundRefetchIntervalMs
  ))

  function onVisibilityChange() {
    isDocumentVisible.value = document.visibilityState === 'visible'
  }

  onMounted(() => {
    document.addEventListener('visibilitychange', onVisibilityChange)
  })

  onUnmounted(() => {
    document.removeEventListener('visibilitychange', onVisibilityChange)
  })

  return {
    isMonitoringRoute,
    isMonitoringViewActive,
    monitorHeartbeatIntervalMs: computed(() => runtimeConfigMs.value.heartbeatIntervalMs),
    monitorRefetchIntervalMs,
  }
}
