import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import type { MonitorRuntimeConfig } from '../types'
import {
  DEFAULT_MONITOR_ACTIVE_REFETCH_INTERVAL_MS,
  DEFAULT_MONITOR_BACKGROUND_REFETCH_INTERVAL_MS,
  DEFAULT_MONITOR_HEARTBEAT_INTERVAL_MS,
} from '../constants/polling'
import { fetchMonitorConfig, monitorQueryKeys } from '../services/monitorQueries'

interface MonitorRuntimeConfigMs {
  activeRefetchIntervalMs: number
  backgroundRefetchIntervalMs: number
  heartbeatIntervalMs: number
}

function secondsToMs(seconds: number): number {
  return Math.max(1, Math.floor(seconds * 1000))
}

function toRuntimeConfigMs(config: MonitorRuntimeConfig): MonitorRuntimeConfigMs {
  return {
    activeRefetchIntervalMs: secondsToMs(config.uiActiveRefetchSeconds),
    backgroundRefetchIntervalMs: secondsToMs(config.uiBackgroundRefetchSeconds),
    heartbeatIntervalMs: secondsToMs(config.heartbeatIntervalSeconds),
  }
}

const DEFAULT_RUNTIME_CONFIG_MS: MonitorRuntimeConfigMs = {
  activeRefetchIntervalMs: DEFAULT_MONITOR_ACTIVE_REFETCH_INTERVAL_MS,
  backgroundRefetchIntervalMs: DEFAULT_MONITOR_BACKGROUND_REFETCH_INTERVAL_MS,
  heartbeatIntervalMs: DEFAULT_MONITOR_HEARTBEAT_INTERVAL_MS,
}

export function useMonitorRuntimeConfig() {
  const { data } = useQuery<MonitorRuntimeConfig>({
    queryKey: monitorQueryKeys.config(),
    queryFn: fetchMonitorConfig,
    staleTime: 10 * 60 * 1000,
  })

  const runtimeConfigMs = computed(() => {
    if (!data.value) return DEFAULT_RUNTIME_CONFIG_MS
    return toRuntimeConfigMs(data.value)
  })

  return {
    runtimeConfigMs,
  }
}
