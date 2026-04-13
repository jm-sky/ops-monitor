<script setup lang="ts">
import { Activity, Bell, Info, LayoutDashboard, Settings } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
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
} from '@/components/ui/sidebar'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { MonitorRoutePaths } from '@/modules/monitor/routes'
import { PublicRoutePaths } from '@/router/publicRoutes'

const { t } = useI18n()

const mainLinks = [
  {
    to: AuthRoutePaths.dashboard,
    label: t('navigation.dashboard', 'Dashboard'),
    icon: LayoutDashboard,
  },
  {
    to: MonitorRoutePaths.monitor,
    label: t('navigation.monitor', 'Monitor'),
    icon: Activity,
  },
  {
    to: MonitorRoutePaths.alertChannels,
    label: t('navigation.alertChannels', 'Alert channels'),
    icon: Bell,
  },
  {
    to: '/settings',
    label: t('navigation.settings', 'Settings'),
    icon: Settings,
  },
]
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent class="overflow-x-hidden">
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.main', 'Navigation') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in mainLinks" :key="link.to">
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
