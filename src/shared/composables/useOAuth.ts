import { ref } from 'vue'
import { authService } from '@/modules/auth/services/authService'
import { config } from '@/shared/config/config'
import type { OAuthProviderName } from '@/modules/auth/types/user.type'

export function useOAuth() {
  const isPending = ref(false)
  const isGithubPending = ref(false)
  const isOidcPending = ref(false)
  const error = ref<Error | null>(null)

  const enabledMap: Record<OAuthProviderName, boolean> = {
    google: config.oauth.google.enabled,
    facebook: config.oauth.facebook.enabled,
    github: config.oauth.github.enabled,
    oidc: config.oauth.oidc.enabled,
  }

  const pendingFor = (provider: OAuthProviderName) => {
    if (provider === 'github') return isGithubPending
    if (provider === 'oidc') return isOidcPending
    return isPending
  }

  const initiateOAuthLogin = async (provider: OAuthProviderName) => {
    if (!enabledMap[provider]) {
      error.value = new Error(`${provider} OAuth not configured`)
      return
    }

    const pending = pendingFor(provider)
    pending.value = true
    error.value = null

    try {
      // CSRF `state` is persisted server-side (oauth_state_store) and verified
      // on callback — do not mirror it into sessionStorage (clear-text storage).
      const response = await authService.getOAuthAuthUrl(provider)
      window.location.href = response.authUrl
    }
    catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to initiate login')
      pending.value = false
    }
  }

  const initiateGoogleLogin = () => initiateOAuthLogin('google')
  const initiateFacebookLogin = () => initiateOAuthLogin('facebook')
  const initiateGithubLogin = () => initiateOAuthLogin('github')
  const initiateOidcLogin = () => initiateOAuthLogin('oidc')

  return {
    error,
    initiateFacebookLogin,
    initiateGithubLogin,
    initiateGoogleLogin,
    initiateOidcLogin,
    isEnabled: config.oauth.google.enabled,
    isFacebookEnabled: config.oauth.facebook.enabled,
    isGithubEnabled: config.oauth.github.enabled,
    isGithubPending,
    isOidcEnabled: config.oauth.oidc.enabled,
    isOidcPending,
    isPending,
  }
}
