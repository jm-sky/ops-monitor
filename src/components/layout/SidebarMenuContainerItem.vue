<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import {
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import ContainerIcon from '@/modules/gear/components/ContainerIcon.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import type { IGearContainer } from '@/modules/gear/types/gear.types'

defineProps<{
  container: IGearContainer
}>()

const route = useRoute()

// Sprawdzanie czy kontener jest aktywny
const isActive = (containerId: string): boolean => {
  return route.params.id === containerId || route.params.containerId === containerId
}
</script>

<template>
  <SidebarMenuItem>
    <SidebarMenuButton :is-active="isActive(container.id)" as-child>
      <RouterLink :to="GearRoutePath.ContainerDetailById(container.id)">
        <ContainerIcon :type="container.type" :color="container.color" :size="4" />
        <span>{{ container.name }}</span>
      </RouterLink>
    </SidebarMenuButton>
  </SidebarMenuItem>
</template>

