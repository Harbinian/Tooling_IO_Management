import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'
import { useSessionStore } from '@/store/session'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: { public: true, title: '登录' }
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
        meta: { title: '仪表盘', permission: 'dashboard:view' }
      },
      {
        path: 'inventory',
        name: 'tool-io-list',
        component: () => import('@/pages/tool-io/OrderList.vue'),
        meta: { title: '订单列表', permission: 'order:list' }
      },
      {
        path: 'inventory/create',
        name: 'tool-io-create',
        component: () => import('@/pages/tool-io/OrderCreate.vue'),
        meta: { title: '创建申请', permission: 'order:create' }
      },
      {
        path: 'inventory/keeper',
        name: 'tool-io-keeper',
        component: () => import('@/pages/tool-io/KeeperProcess.vue'),
        meta: { title: '保管员工作台', permission: 'order:keeper_confirm' }
      },
      {
        path: 'inventory/pre-transport',
        name: 'tool-io-pre-transport',
        component: () => import('@/pages/tool-io/PreTransportList.vue'),
        meta: { title: '预知运输任务', permission: 'order:transport_execute' }
      },
      {
        path: 'inventory/:orderNo',
        name: 'tool-io-detail',
        component: () => import('@/pages/tool-io/OrderDetail.vue'),
        props: true,
        meta: { title: '订单详情', permission: 'order:list' }
      },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: () => import('@/pages/admin/UserAdminPage.vue'),
        meta: { title: '账号管理', permission: 'admin:user_manage' }
      },
      {
        path: 'admin/feedback',
        name: 'admin-feedback',
        component: () => import('@/pages/admin/FeedbackAdminPage.vue'),
        meta: { title: '反馈管理', permission: 'admin:user_manage' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/pages/settings/SettingsPage.vue'),
        meta: { title: '个人设置', permission: 'dashboard:view' }
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
    // Don't auto-redirect to dashboard if user was denied access (permission check failed)
    // This prevents infinite redirect loop when user lacks required permissions
    if (to.name === 'login' && session.token && !to.query.denied) {
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

  // RBAC: Explicit role-based route access control
  // This provides a secondary check to ensure role-based access control is enforced
  const roleCodes = new Set((session.roles || []).map((role) => role.role_code))
  const isKeeper = roleCodes.has('keeper')
  const isTeamLeader = roleCodes.has('team_leader') || roleCodes.has('planner') || roleCodes.has('sys_admin')
  const isProductionPrep = roleCodes.has('production_prep')

  // /keeper route (keeper workspace) - only KEEPER role can access
  // Short paths: /keeper, /inventory/keeper
  // DENY: TEAM_LEADER, PLANNER, PRODUCTION_PREP, AUDITOR
  if ((to.path === '/inventory/keeper' || to.path === '/keeper') && !isKeeper) {
    if (session.hasPermission('dashboard:view')) {
      return { name: 'dashboard' }
    }
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // /create route (order creation) - only TEAM_LEADER, PLANNER, SYS_ADMIN can access
  // Short paths: /create, /inventory/create
  // DENY: KEEPER, PRODUCTION_PREP, AUDITOR
  if ((to.path === '/inventory/create' || to.path === '/create') && !isTeamLeader) {
    if (session.hasPermission('dashboard:view')) {
      return { name: 'dashboard' }
    }
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // /tool-io route (order list) - requires order:list permission
  // Short paths: /tool-io, /inventory
  // DENY: PRODUCTION_PREP (has transport_execute but not list permission)
  if ((to.path === '/tool-io' || to.path === '/inventory') && isProductionPrep) {
    if (session.hasPermission('dashboard:view')) {
      return { name: 'dashboard' }
    }
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.permission && !session.hasPermission(to.meta.permission)) {
    // User lacks required permission - show access denied instead of redirect loop
    // This prevents infinite redirect when user doesn't have dashboard:view
    return { name: 'login', query: { redirect: to.fullPath, denied: '1' } }
  }

  return true
})

export default router
