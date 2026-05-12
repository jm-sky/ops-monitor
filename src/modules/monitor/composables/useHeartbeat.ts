import { computed, type ComputedRef, onMounted, onUnmounted, watch } from 'vue'
import { apiClient } from '@/shared/services/apiClient'
import { DEFAULT_MONITOR_HEARTBEAT_INTERVAL_MS } from '../constants/polling'

interface UseHeartbeatOptions {
  enabled?: ComputedRef<boolean>
  intervalMs?: ComputedRef<number>
}

export function useHeartbeat(options: UseHeartbeatOptions = {}) {
  const enabled = computed(() => options.enabled?.value ?? true)
  const intervalMs = computed(() => options.intervalMs?.value ?? DEFAULT_MONITOR_HEARTBEAT_INTERVAL_MS)
  let timer: ReturnType<typeof setInterval> | null = null

  async function sendHeartbeat() {
    try {
      await apiClient.post('/monitor/heartbeat')
    } catch {
      // Silently ignore — heartbeat is best-effort
    }
  }

  function stopHeartbeat() {
    if (timer === null) return
    clearInterval(timer)
    timer = null
  }

  onMounted(() => {
    watch([enabled, intervalMs], ([isEnabled, currentIntervalMs], previousValues) => {
      if (!isEnabled) {
        stopHeartbeat()
        return
      }

      const previousEnabled = previousValues?.[0] ?? false
      const previousIntervalMs = previousValues?.[1]
      if (previousEnabled && previousIntervalMs !== currentIntervalMs) {
        stopHeartbeat()
      }

      void sendHeartbeat()
      if (timer === null) {
        timer = setInterval(() => void sendHeartbeat(), currentIntervalMs)
      }
    }, { immediate: true })
  })

  onUnmounted(() => {
    stopHeartbeat()
  })
}
