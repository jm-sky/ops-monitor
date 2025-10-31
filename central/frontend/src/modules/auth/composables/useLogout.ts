import { useRouter } from 'vue-router'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { authService } from '@/modules/auth/services/authService'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'

export function useLogout() {
  const authStore = useAuthStore()
  const router = useRouter()

  async function logout() {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      authStore.logout()
      await router.push(AuthRoutePaths.login)
    }
  }

  return {
    logout,
  }
}
