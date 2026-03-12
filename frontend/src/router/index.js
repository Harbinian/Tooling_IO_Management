import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'
import { useSessionStore } from '@/store/session'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: { public: true, title: 'Login' }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/pages/dashboard/DashboardOverview.vue'),
        meta: { title: 'Dashboard', permission: 'dashboard:view' }
      },
      {
        path: 'inventory',
        name: 'tool-io-list',
        component: () => import('@/pages/tool-io/OrderList.vue'),
        meta: { title: 'Order List', permission: 'order:list' }
      },
      {
        path: 'inventory/create',
        name: 'tool-io-create',
        component: () => import('@/pages/tool-io/OrderCreate.vue'),
        meta: { title: 'Create Request', permission: 'order:create' }
      },
      {
        path: 'inventory/keeper',
        name: 'tool-io-keeper',
        component: () => import('@/pages/tool-io/KeeperProcess.vue'),
        meta: { title: 'Keeper Workspace', permission: 'order:keeper_confirm' }
      },
      {
        path: 'inventory/:orderNo',
        name: 'tool-io-detail',
        component: () => import('@/pages/tool-io/OrderDetail.vue'),
        props: true,
        meta: { title: 'Order Detail', permission: 'order:view' }
      },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: () => import('@/pages/admin/UserAdminPage.vue'),
        meta: { title: 'Account Management', permission: 'admin:user_manage' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const session = useSessionStore()

  const debugUI = to.query.debugUI
  if (debugUI === '0' || debugUI === 'off') {
    sessionStorage.removeItem('debugUI')
  } else if (!debugUI) {
    const savedDebugUI = sessionStorage.getItem('debugUI')
    if (savedDebugUI) {
      return { ...to, query: { ...to.query, debugUI: savedDebugUI } }
    }
  } else {
    sessionStorage.setItem('debugUI', debugUI)
  }

  if (to.meta.public) {
    if (to.name === 'login' && session.token) {
      return { name: 'dashboard' }
    }
    return true
  }

  if (!session.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (!session.initialized) {
    const restored = await session.hydrate()
    if (!restored) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  if (to.meta.permission && !session.hasPermission(to.meta.permission)) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
