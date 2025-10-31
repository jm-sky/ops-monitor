export const dashboardRoutes = [
  {
    path: '/dashboard',
    name: 'dashboard',
    meta: { requiresAuth: true },
    component: () => import('@/modules/dashboard/pages/DashboardPage.vue'),
  },
]




