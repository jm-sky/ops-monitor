import type { RouteRecordRaw } from 'vue-router'

export const MonitorRoutePaths = {
  monitor: '/monitor',
  site: '/monitor/:id',
}

export const MonitorRouteNames = {
  monitor: 'monitor',
  site: 'monitor-site',
}

export const monitorRoutes: RouteRecordRaw[] = [
  {
    path: MonitorRoutePaths.monitor,
    name: MonitorRouteNames.monitor,
    component: () => import('@/modules/monitor/pages/MonitorPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'monitor.title' },
  },
  {
    path: MonitorRoutePaths.site,
    name: MonitorRouteNames.site,
    component: () => import('@/modules/monitor/pages/SiteDetailPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'monitor.siteDetail' },
  },
]
