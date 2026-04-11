<script setup lang="ts">
import { LogIn, UserPlus } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import LandingPageContainerCard from '@/components/layout/LandingPageContainerCard.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { GearRoutePath } from '@/modules/gear/routes'
import { hasLocalData } from '@/modules/gear/services/dataMigrationService'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import { READINESS_EXCELLENT_THRESHOLD } from '@/modules/gear/utils/constants'

const { t } = useI18n()
const authStore = useAuthStore()
const gearStore = useGearStore()
const { isAuthenticated } = useAuth()

// Check if user is not logged in but has containers in localStorage
const hasLocalContainers = computed(() => {
  if (authStore.isAuthenticated) return false
  return hasLocalData()
})

// Load containers from localStorage if not authenticated
onMounted(() => {
  if (!authStore.isAuthenticated) {
    gearStore.loadFromStorage()
  }
})

// Get containers for stats
const localContainers = computed(() => {
  if (!hasLocalContainers.value) return []
  return gearStore.getAllContainers
})

// Calculate stats similar to HomePage
const containersCount = computed(() => localContainers.value.length)

const itemsCount = computed(() => {
  return localContainers.value.reduce((sum, c) => sum + c.items.length, 0)
})

const readyContainersCount = computed(() => {
  return localContainers.value.filter(c => {
    const ownedItems = c.items.filter(i => i.status === 'owned').length
    const totalItems = c.items.length
    if (totalItems === 0) return false
    return (ownedItems / totalItems) * 100 >= READINESS_EXCELLENT_THRESHOLD
  }).length
})
</script>

<template>
  <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 space-y-4">
    <div class="text-center space-y-2">
      <h2 class="text-2xl font-semibold">
        {{ t('landing.localData.title', 'Masz kontenery w przeglądarce') }}
      </h2>
      <p class="text-muted-foreground">
        {{ t('landing.localData.description', 'Zaloguj się lub zarejestruj, aby zsynchronizować swoje dane') }}
      </p>
    </div>

    <!-- Container Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <LandingPageContainerCard
        :to="GearRoutePath.Containers"
        :label="t('gear.page.containers', 'Containers')"
        :containers-count="containersCount"
      />
      <LandingPageContainerCard
        :to="GearRoutePath.AllItems"
        :label="t('gear.page.items', 'Items')"
        :containers-count="itemsCount"
      />
      <LandingPageContainerCard
        :to="GearRoutePath.Containers"
        :label="t('gear.page.readyContainers', 'Ready Containers')"
        :containers-count="readyContainersCount"
      />
    </div>

    <!-- Login/Register CTA -->
    <div v-if="!isAuthenticated" class="flex flex-col gap-6 justify-center items-center pt-4">
      <ButtonLink size="lg" class="w-full sm:w-auto" :to="AuthRoutePaths.login">
        <LogIn class="size-5" />
        {{ t('landing.login', 'Log In') }}
      </ButtonLink>
      <ButtonLink
        size="lg"
        variant="outline"
        class="w-full sm:w-auto"
        :to="AuthRoutePaths.register"
      >
        <UserPlus class="size-5" />
        {{ t('landing.register', 'Sign Up') }}
      </ButtonLink>
    </div>
  </div>
</template>

