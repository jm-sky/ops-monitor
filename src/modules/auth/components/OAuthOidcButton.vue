<script setup lang="ts">
import { KeyRound } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { useOAuth } from '@/shared/composables/useOAuth'
import { config } from '@/shared/config/config'

const { t } = useI18n()
const { initiateOidcLogin, isOidcPending } = useOAuth()
</script>

<template>
  <Button
    type="button"
    variant="outline"
    size="lg"
    class="w-full"
    :disabled="isOidcPending"
    @click="initiateOidcLogin"
  >
    <KeyRound class="size-5" />
    {{ isOidcPending ? t('auth.oauth.button.redirecting') : config.oauth.oidc.label }}
  </Button>
</template>
