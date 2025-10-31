<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import GuestLayoutCentered from '@/layouts/GuestLayoutCentered.vue'
import { AuthRoutePaths } from '@/modules/auth/config/routes'

const { t } = useI18n()
</script>

<template>
  <GuestLayoutCentered>
    <div class="text-center">
      <h1 class="text-4xl font-bold mb-4">
        Welcome to Ops Monitor
      </h1>
      <p class="text-muted-foreground mb-6">
        Ops Monitor is a tool to monitor your system and applications.
      </p>
      <div class="flex gap-4 justify-center">
        <ButtonLink :to="AuthRoutePaths.login">
          {{ t('auth.login') }}
        </ButtonLink>
      </div>
    </div>
  </GuestLayoutCentered>
</template>
