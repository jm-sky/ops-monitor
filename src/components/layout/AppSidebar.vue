<script setup lang="ts">
import { BackpackIcon, BookIcon, Globe, Info, Package, ShoppingCart } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import SidebarMenuContainerItem from '@/components/layout/SidebarMenuContainerItem.vue'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from '@/components/ui/sidebar'
import { useGear } from '@/modules/gear/composables/useGear'
import { GearRoutePath } from '@/modules/gear/routes'
import { getRootContainers } from '@/modules/gear/utils/containerNesting'
import { PublicRoutePaths } from '@/router/publicRoutes'
import type { IGearContainer } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const { containers } = useGear()

// Linki: Mój sprzęt
const myGearLinks = computed(() => [
  {
    to: GearRoutePath.Containers,
    label: t('gear.page.title', 'Gear'),
    icon: BackpackIcon,
  },
  {
    to: GearRoutePath.AllItems,
    label: t('gear.allItems.navTitle', 'All Items'),
    icon: Package,
  },
  {
    to: GearRoutePath.ShoppingPlanning,
    label: t('gear.shopping.navTitle', 'Shopping'),
    icon: ShoppingCart,
  },
])

// Linki: Publiczne
const publicLinks = computed(() => [
  {
    to: GearRoutePath.PublicContainers,
    label: t('gear.publicContainers.navTitle', 'Public Browser'),
    icon: Globe,
  },
  {
    to: GearRoutePath.CatalogueBrowser,
    label: t('gear.catalogue.navTitle', 'Catalogue'),
    icon: BookIcon,
  },
])

// Root kontenery posortowane: ulubione + alfabetycznie
const rootContainers = computed<IGearContainer[]>(() => {
  const allContainers = containers.value
  const roots = getRootContainers(allContainers)

  // Sortowanie: najpierw ulubione, potem alfabetycznie
  return [...roots].sort((a, b) => {
    // Najpierw ulubione
    if (a.favorite && !b.favorite) return -1
    if (!a.favorite && b.favorite) return 1
    // Potem alfabetycznie
    return a.name.localeCompare(b.name)
  })
})
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent class="overflow-x-hidden max-h-[90vh] overflow-y-auto">
      <!-- Sekcja: Mój sprzęt -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.myGear', 'My Gear') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in myGearLinks" :key="link.to">
              <RouterLink v-slot="{ href, navigate, isActive }" :to="link.to" custom>
                <SidebarMenuButton
                  :is-active="isActive"
                  as="a"
                  :href="href"
                  @click="navigate"
                >
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </SidebarMenuButton>
              </RouterLink>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Publiczne -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.public', 'Public') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in publicLinks" :key="link.to">
              <RouterLink v-slot="{ href, navigate, isActive }" :to="link.to" custom>
                <SidebarMenuButton
                  :is-active="isActive"
                  as="a"
                  :href="href"
                  @click="navigate"
                >
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </SidebarMenuButton>
              </RouterLink>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Lista kontenerów -->
      <SidebarGroup class="max-h-[50vh] overflow-y-auto">
        <SidebarGroupLabel>{{ t('gear.page.containers', 'Containers') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu v-if="rootContainers.length > 0">
            <SidebarMenuContainerItem
              v-for="container in rootContainers"
              :key="container.id"
              :container="container"
            />
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <RouterLink v-slot="{ href, navigate, isActive }" :to="PublicRoutePaths.about" custom>
            <SidebarMenuButton
              :is-active="isActive"
              as="a"
              :href="href"
              @click="navigate"
            >
              <Info class="size-4" />
              <span>{{ t('common.pages.about', 'About') }}</span>
            </SidebarMenuButton>
          </RouterLink>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <SidebarRail />
  </Sidebar>
</template>

