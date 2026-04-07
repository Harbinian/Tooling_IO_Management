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
        meta: { title: '仪表盘', permission: 'dashboard:view', group: 'tooling' }
      },
      {
        path: 'inventory',
        name: 'tool-io-list',
        component: () => import('@/pages/tool-io/OrderList.vue'),
        meta: { title: '订单列表', permission: 'order:list', group: 'tooling', subgroup: 'io' }
      },
      {
        path: 'inventory/create',
        name: 'tool-io-create',
        component: () => import('@/pages/tool-io/OrderCreate.vue'),
        meta: { title: '创建申请', permission: 'order:create', group: 'tooling', subgroup: 'io' }
      },
      {
        path: 'inventory/keeper',
        name: 'tool-io-keeper',
        component: () => import('@/pages/tool-io/KeeperProcess.vue'),
        meta: { title: '保管员工作台', permission: 'order:keeper_confirm', group: 'tooling', subgroup: 'io' }
      },
      {
        path: 'inventory/pre-transport',
        name: 'tool-io-pre-transport',
        component: () => import('@/pages/tool-io/PreTransportList.vue'),
        meta: { title: '预知运输任务', permission: 'order:transport_execute', group: 'tooling', subgroup: 'io' }
      },
      {
        path: 'mpl',
        name: 'mpl-management',
        component: () => import('@/pages/tool-io/MplManagement.vue'),
        meta: { title: 'MPL管理', permission: 'mpl:write', group: 'tooling', subgroup: 'io' }
      },
      {
        path: 'inventory/:orderNo',
        name: 'tool-io-detail',
        component: () => import('@/pages/tool-io/OrderDetail.vue'),
        props: true,
        meta: { title: '订单详情', permission: 'order:list', group: 'tooling', subgroup: 'io' }
      },
      {
        path: 'inspection/plans',
        name: 'inspection-plans',
        component: () => import('@/pages/inspection/PlanList.vue'),
        meta: { title: '定检任务管理', permission: 'inspection:list', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/plans/create',
        name: 'inspection-plan-create',
        component: () => import('@/pages/inspection/PlanCreate.vue'),
        meta: { title: '创建定检任务管理', permission: 'inspection:create', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/plans/:planNo',
        name: 'inspection-plan-detail',
        component: () => import('@/pages/inspection/PlanDetail.vue'),
        props: true,
        meta: { title: '计划详情', permission: 'inspection:view', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/dashboard',
        name: 'inspection-dashboard',
        component: () => import('@/pages/inspection/InspectionDashboard.vue'),
        meta: { title: '定检看板', permission: 'inspection:list', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/stats',
        name: 'inspection-stats',
        component: () => import('@/pages/inspection/InspectionStats.vue'),
        meta: { title: '定检统计', permission: 'inspection:list', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/calendar',
        name: 'inspection-calendar',
        component: () => import('@/pages/inspection/InspectionCalendar.vue'),
        meta: { title: '定检日历', permission: 'inspection:list', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/tasks',
        name: 'inspection-tasks',
        component: () => import('@/pages/inspection/TaskList.vue'),
        meta: { title: '定检任务', permission: 'inspection:list', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/tasks/:taskNo',
        name: 'inspection-task-detail',
        component: () => import('@/pages/inspection/TaskDetail.vue'),
        props: true,
        meta: { title: '任务详情', permission: 'inspection:view', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'inspection/status',
        name: 'inspection-status',
        component: () => import('@/pages/inspection/InspectionStatus.vue'),
        meta: { title: '工装定检状态', permission: 'inspection:list', group: 'tooling', subgroup: 'inspection' }
      },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: () => import('@/pages/admin/UserAdminPage.vue'),
        meta: { title: '账号管理', permission: 'admin:user_manage', group: 'system' }
      },
      {
        path: 'admin/roles',
        name: 'admin-roles',
        component: () => import('@/pages/admin/RoleManagementPage.vue'),
        meta: { title: '角色管理', permission: 'admin:role_manage', group: 'system' }
      },
      {
        path: 'admin/roles/:roleId/permissions',
        name: 'admin-role-permissions',
        component: () => import('@/pages/admin/RolePermissionAssignment.vue'),
        meta: { title: '权限分配', permission: 'admin:role_manage', group: 'system' }
      },
      {
        path: 'admin/permissions',
        name: 'admin-permissions',
        component: () => import('@/pages/admin/PermissionManagementPage.vue'),
        meta: { title: '权限管理', permission: 'admin:role_manage', group: 'system' }
      },
      {
        path: 'admin/feedback',
        name: 'admin-feedback',
        component: () => import('@/pages/admin/FeedbackAdminPage.vue'),
        meta: { title: '反馈管理', permission: 'admin:user_manage', group: 'system' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/pages/settings/SettingsPage.vue'),
        meta: { title: '个人设置', permission: 'dashboard:view', group: 'personal' }
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
  const canAccessMplManagement = roleCodes.has('engineering') || roleCodes.has('sys_admin')

  // /keeper route (keeper workspace) - only KEEPER role can access
  // Short paths: /keeper, /inventory/keeper
  // DENY: PRODUCTION_PREP, AUDITOR
  // NOTE: SYS_ADMIN and TEAM_LEADER can access keeper workspace for oversight
  // RBAC violations always redirect to login with denied=1 (NOT dashboard) for proper deny detection
  const canAccessKeeper = isKeeper || roleCodes.has('sys_admin') || roleCodes.has('team_leader') || roleCodes.has('planner')
  if ((to.path === '/inventory/keeper' || to.path === '/keeper') && !canAccessKeeper) {
    return { name: 'login', query: { redirect: to.fullPath, denied: '1' } }
  }

  // /create route (order creation) - only TEAM_LEADER, PLANNER, SYS_ADMIN can access
  // Short paths: /create, /inventory/create
  // DENY: KEEPER, PRODUCTION_PREP, AUDITOR
  // RBAC violations always redirect to login with denied=1 (NOT dashboard) for proper deny detection
  if ((to.path === '/inventory/create' || to.path === '/create') && !isTeamLeader) {
    return { name: 'login', query: { redirect: to.fullPath, denied: '1' } }
  }

  // /tool-io route (order list) - requires order:list permission
  // Short paths: /tool-io, /inventory
  // DENY: PRODUCTION_PREP (has transport_execute but not list permission)
  // RBAC violations always redirect to login with denied=1 (NOT dashboard) for proper deny detection
  if ((to.path === '/tool-io' || to.path === '/inventory') && isProductionPrep) {
    return { name: 'login', query: { redirect: to.fullPath, denied: '1' } }
  }

  if (to.path === '/mpl' && !canAccessMplManagement) {
    return { name: 'login', query: { redirect: to.fullPath, denied: '1' } }
  }

  if (to.meta.permission && !session.hasPermission(to.meta.permission)) {
    // User lacks required permission - show access denied instead of redirect loop
    // This prevents infinite redirect when user doesn't have dashboard:view
    return { name: 'login', query: { redirect: to.fullPath, denied: '1' } }
  }

  return true
})

export default router
