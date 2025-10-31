<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import Alert from '@/components/ui/alert/Alert.vue'
import AlertDescription from '@/components/ui/alert/AlertDescription.vue'
import GuestLayoutCentered from '@/layouts/GuestLayoutCentered.vue'
import LoginForm from '@/modules/auth/components/LoginForm.vue'

const { t } = useI18n()
const route = useRoute()
const message: string | null = route.meta.message as string | null
</script>

<template>
  <GuestLayoutCentered>
    <template #actions>
      <slot name="actions" />
    </template>

    <div class="max-w-md w-full space-y-8">
      <div class="space-y-4 bg-card/60 py-8 px-6 shadow-lg rounded-lg">
        <h2 class="text-center text-2xl font-bold text-card-foreground">
          {{ t('auth.sign_in_to_account') }}
        </h2>
        <LoginForm />
      </div>

      <Alert v-if="message" variant="info">
        <AlertDescription>{{ message }}</AlertDescription>
      </Alert>
    </div>
  </GuestLayoutCentered>
</template>
