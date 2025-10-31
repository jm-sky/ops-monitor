<script setup lang="ts">
import { useRoute } from 'vue-router'
import HoverLinkExternal from '@/components/ui/hover-link/HoverLinkExternal.vue'
import LogoText from '@/components/ui/LogoText.vue'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

// Auth layout for login, register, forgot password pages
const route = useRoute()
const layoutActionsComponent = route.meta.layoutActionsComponent
</script>

<template>
  <div class="min-h-screen bg-linear-to-br from-blue-200 via-slate-100 to-purple-200 dark:from-gray-950 dark:via-gray-800 dark:to-gray-950 flex flex-col">
    <nav class="fixed top-2 right-2 flex gap-2 rounded-lg p-2 bg-card/50 backdrop-blur-sm">
      <slot name="actions">
        <component :is="layoutActionsComponent" v-if="layoutActionsComponent" />
      </slot>
      <LocaleToggle />
      <DarkModeToggle />
    </nav>

    <main class="flex-1 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="mx-auto text-center mb-8">
        <RouterLink to="/" class="block hover:opacity-80 hover:scale-105 transition-all">
          <LogoText class="text-3xl drop-shadow" />
        </RouterLink>
      </div>

      <slot />
    </main>

    <footer>
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <p class="text-center text-sm text-muted-foreground">
          &copy; 2025
          <HoverLinkExternal href="https://github.com/jm-sky/ops-monitor">
            Ops Monitor
          </HoverLinkExternal>
          by
          <HoverLinkExternal href="https://dev-made.it">
            DEV Made IT
          </HoverLinkExternal>.
        </p>
      </div>
    </footer>
  </div>
</template>
