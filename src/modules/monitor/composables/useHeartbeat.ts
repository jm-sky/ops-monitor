import { onMounted, onUnmounted } from 'vue'
import { apiClient } from '@/shared/services/apiClient'

const HEARTBEAT_INTERVAL_MS = 30_000

export function useHeartbeat() {
  let timer: ReturnType<typeof setInterval> | null = null

  async function sendHeartbeat() {
    try {
      await apiClient.post('/monitor/heartbeat')
    } catch {
      // Silently ignore — heartbeat is best-effort
    }
  }

  onMounted(() => {
    void sendHeartbeat()
    timer = setInterval(() => void sendHeartbeat(), HEARTBEAT_INTERVAL_MS)
  })

  onUnmounted(() => {
    if (timer !== null) {
      clearInterval(timer)
      timer = null
    }
  })
}
