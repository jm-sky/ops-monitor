import type { RouteRecordRaw } from 'vue-router'

export const MonitorRoutePaths = {
  monitor: '/monitor',
  site: '/monitor/:id',
  alertChannels: '/monitor/alerts',
}

export const MonitorRouteNames = {
  monitor: 'monitor',
  site: 'monitor-site',
  alertChannels: 'monitor-alert-channels',
}

export const monitorRoutes: RouteRecordRaw[] = [
  {
    path: MonitorRoutePaths.monitor,
    name: MonitorRouteNames.monitor,
    component: () => import('@/modules/monitor/pages/MonitorPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'monitor.title' },
  },
  {
    path: MonitorRoutePaths.alertChannels,
    name: MonitorRouteNames.alertChannels,
    component: () => import('@/modules/monitor/pages/AlertChannelsPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'monitor.alerts.title' },
  },
  {
    path: MonitorRoutePaths.site,
    name: MonitorRouteNames.site,
    component: () => import('@/modules/monitor/pages/SiteDetailPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'monitor.siteDetail' },
  },
]
