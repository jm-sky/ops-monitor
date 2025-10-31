import { authRoutes } from '@/modules/auth/config/routes'
import { dashboardRoutes } from '@/modules/dashboard/routes'
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
  },
  ...dashboardRoutes,
  ...authRoutes,
]
