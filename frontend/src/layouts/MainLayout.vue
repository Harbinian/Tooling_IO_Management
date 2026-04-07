<script setup>
import {
  Bell,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  PackageSearch,
  PlusCircle,
  Settings,
  ShieldCheck,
  User,
  Users
} from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { cn } from '@/lib/utils'
import { DEBUG_IDS } from '@/debug/debugIds'
import { useSessionStore } from '@/store/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const isCollapsed = ref(false)
const showSettingsDialog = ref(false)
const debugModeEnabled = ref(false)

const navigation = [
  {
    group: '工装管理系统',
    items: [
      {
        label: '出入库',
        icon: ClipboardList,
        children: [
          { name: '订单列表', href: '/inventory', permission: 'order:list' },
          { name: '创建申请', href: '/inventory/create', permission: 'order:create' },
          { name: '保管员工作台', href: '/inventory/keeper', permission: 'order:keeper_confirm' },
          { name: '预知运输', href: '/inventory/pre-transport', permission: 'order:transport_execute' },
          { name: 'MPL管理', href: '/mpl', permission: 'mpl:write' }
        ]
      },
      {
        label: '定检任务管理',
        icon: ShieldCheck,
        children: [
          { name: '计划列表', href: '/inspection/plans', permission: 'inspection:list' },
          { name: '任务列表', href: '/inspection/tasks', permission: 'inspection:list' },
          { name: '定检看板', href: '/inspection/dashboard', permission: 'inspection:list' },
          { name: '定检统计', href: '/inspection/stats', permission: 'inspection:list' },
          { name: '定检日历', href: '/inspection/calendar', permission: 'inspection:list' },
          { name: '工装定检状态', href: '/inspection/status', permission: 'inspection:list' }
        ]
      }
    ]
  },
  {
    group: '系统概览与管理',
    items: [
      {
        label: '概览',
        icon: LayoutDashboard,
        children: [
          { name: '仪表盘', href: '/dashboard', permission: 'dashboard:view' }
        ]
      },
      {
        label: '系统管理',
        icon: Settings,
        children: [
          { name: '账号管理', href: '/admin/users', permission: 'admin:user_manage' },
          { name: '角色管理', href: '/admin/roles', permission: 'admin:role_manage' },
          { name: '权限管理', href: '/admin/permissions', permission: 'admin:role_manage' },
          { name: '反馈管理', href: '/admin/feedback', permission: 'admin:user_manage' },
          { name: '个人设置', href: '/settings', permission: 'dashboard:view' }
        ]
      }
    ]
  }
]

const mplAllowedRoleCodes = new Set(['engineering', 'sys_admin'])
const inspectionAllowedRoleCodes = new Set(['sys_admin'])

const availableNavigation = computed(() => {
  return navigation
    .map((group) => {
      const filteredItems = group.items
        .map((item) => {
          const filteredChildren = item.children.filter((child) => {
            if (child.href === '/mpl') {
              const roleCodes = new Set((session.roles || []).map((role) => role.role_code))
              const canAccessMpl = [...mplAllowedRoleCodes].some((roleCode) => roleCodes.has(roleCode))
              return canAccessMpl && session.hasPermission(child.permission)
            }
            if (child.href.startsWith('/inspection/')) {
              const roleCodes = new Set((session.roles || []).map((role) => role.role_code))
              const canAccessInspection = [...inspectionAllowedRoleCodes].some((roleCode) => roleCodes.has(roleCode))
              return canAccessInspection && session.hasPermission(child.permission)
            }
            return !child.permission || session.hasPermission(child.permission)
          })

          return {
            ...item,
            children: filteredChildren
          }
        })
        .filter((item) => item.children.length > 0)

      return {
        ...group,
        items: filteredItems
      }
    })
    .filter((group) => group.items.length > 0)
})

const displayRole = computed(() => session.roleName || (session.role === 'keeper' ? '保管员' : '发起人'))

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const logout = async () => {
  session.clear()
  await router.replace('/login')
}

function isActive(href) {
  if (href === '/inventory') return route.path === '/inventory'
  if (href === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(href)
}

function isGroupActive(item) {
  return item.children.some(child => isActive(child.href))
}

const isAdmin = computed(() => session.isAdmin())

const toggleSettings = () => {
  showSettingsDialog.value = true
}

const toggleDebugMode = (value) => {
  if (value) {
    sessionStorage.setItem('debugUI', '1')
    if (!window.location.search.includes('debugUI=')) {
      const newUrl = window.location.pathname + '?debugUI=1' + window.location.hash
      window.history.replaceState({}, '', newUrl)
    }
  } else {
    sessionStorage.removeItem('debugUI')
    const url = new URL(window.location.href)
    url.searchParams.delete('debugUI')
    window.history.replaceState({}, '', url.toString())
  }
  debugModeEnabled.value = value
}

// Initialize debug mode from sessionStorage or URL
const initDebugMode = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const urlDebug = urlParams.get('debugUI')
  const storageDebug = sessionStorage.getItem('debugUI')
  debugModeEnabled.value = !!(urlDebug || storageDebug)
}

initDebugMode()
</script>

<template>
  <div class="flex h-screen bg-background font-sans text-foreground">
    <aside
      v-debug-id="DEBUG_IDS.MAIN_LAYOUT.SIDEBAR"
      :class="cn(
        'relative z-30 flex flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-72'
      )"
    >
      <div class="flex h-16 items-center border-b border-sidebar-border px-6">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary font-bold text-primary-foreground shadow-lg shadow-primary/20">
            <ShieldCheck class="h-5 w-5" />
          </div>
          <span v-if="!isCollapsed" class="text-lg font-bold tracking-tight text-foreground">工装管理系统</span>
        </div>
      </div>

      <nav class="flex-1 space-y-6 overflow-y-auto p-4 custom-scrollbar">
        <div v-for="group in availableNavigation" :key="group.group" class="space-y-2">
          <p v-if="!isCollapsed" class="px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground/60">
            {{ group.group }}
          </p>
          <div class="space-y-1">
            <template v-for="item in group.items" :key="item.label">
              <!-- Expanded Sidebar Item -->
              <div v-if="!isCollapsed" class="space-y-1">
                <div
                  :class="cn(
                    'flex items-center gap-3 px-3 py-2 text-xs font-bold uppercase tracking-wider transition-colors',
                    isGroupActive(item) ? 'text-primary' : 'text-muted-foreground'
                  )"
                >
                  <component :is="item.icon" class="h-4 w-4" />
                  <span>{{ item.label }}</span>
                </div>
                <div class="ml-4 space-y-1 border-l border-sidebar-border pl-4">
                  <router-link
                    v-for="child in item.children"
                    :key="child.name"
                    :to="child.href"
                    :class="cn(
                      'block rounded-lg px-3 py-2 text-sm font-medium transition-all',
                      isActive(child.href)
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )"
                  >
                    {{ child.name }}
                  </router-link>
                </div>
              </div>

              <!-- Collapsed Sidebar Item (Popover) -->
              <el-popover
                v-else
                placement="right"
                :width="200"
                trigger="hover"
                popper-class="sidebar-popover"
              >
                <template #reference>
                  <div
                    :class="cn(
                      'flex h-10 w-10 items-center justify-center rounded-xl transition-all cursor-pointer',
                      isGroupActive(item)
                        ? 'bg-primary text-primary-foreground shadow-md'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )"
                  >
                    <component :is="item.icon" class="h-5 w-5" />
                  </div>
                </template>
                <div class="space-y-1 p-1">
                  <p class="mb-2 px-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    {{ item.label }}
                  </p>
                  <router-link
                    v-for="child in item.children"
                    :key="child.name"
                    :to="child.href"
                    :class="cn(
                      'block rounded-md px-3 py-2 text-sm font-medium transition-all',
                      isActive(child.href)
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )"
                  >
                    {{ child.name }}
                  </router-link>
                </div>
              </el-popover>
            </template>
          </div>
        </div>
      </nav>

      <div class="space-y-4 border-t border-sidebar-border bg-sidebar p-4">
        <div v-if="!isCollapsed" class="space-y-3 rounded-2xl border border-sidebar-border bg-card p-4 shadow-sm">
          <p class="text-[10px] font-bold uppercase tracking-[0.28em] text-muted-foreground">当前用户</p>
          <div>
            <p class="text-lg font-bold text-foreground">{{ session.userName || '未登录' }}</p>
            <p class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              {{ session.loginName || 'anonymous' }}
            </p>
          </div>
          <div class="rounded-xl bg-muted px-3 py-2">
            <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-muted-foreground">工号</p>
            <p class="mt-1 truncate text-sm font-semibold text-foreground">{{ session.employeeNo || '-' }}</p>
          </div>
        </div>

        <div :class="cn('flex items-center gap-3 px-2', isCollapsed ? 'justify-center' : '')">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-sidebar-border bg-card shadow-sm">
            <User class="h-5 w-5 text-muted-foreground" />
          </div>
          <div v-if="!isCollapsed" class="flex-1 overflow-hidden">
            <p class="truncate text-sm font-bold text-foreground">{{ session.userName || '未登录' }}</p>
            <p class="truncate text-[10px] font-bold uppercase tracking-tight text-muted-foreground">
              {{ displayRole }}
            </p>
          </div>
          <button v-if="!isCollapsed" class="text-muted-foreground transition-colors hover:text-destructive" @click="logout">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>

      <button
        @click="toggleSidebar"
        class="absolute -right-3 top-20 z-40 flex h-6 w-6 items-center justify-center rounded-full border border-sidebar-border bg-sidebar text-muted-foreground shadow-sm transition-all hover:scale-110 hover:text-foreground"
      >
        <ChevronLeft v-if="!isCollapsed" class="h-4 w-4" />
        <ChevronRight v-else class="h-4 w-4" />
      </button>
    </aside>

    <main class="flex flex-1 flex-col overflow-hidden">
      <header class="flex h-16 shrink-0 items-center justify-between border-b border-header-border bg-header px-8">
        <div class="flex items-center gap-4">
          <h2 class="text-sm font-bold uppercase tracking-[0.2em] text-muted-foreground">
            {{ route.meta.title || 'Overview' }}
          </h2>
        </div>
        <div class="flex items-center gap-3">
          <button class="relative rounded-xl p-2 text-muted-foreground transition-all hover:bg-accent hover:text-accent-foreground">
            <Bell class="h-5 w-5" />
            <span class="absolute right-2.5 top-2.5 h-2 w-2 rounded-full border-2 border-header bg-rose-500"></span>
          </button>
          <button class="rounded-xl p-2 text-muted-foreground transition-all hover:bg-accent hover:text-accent-foreground" @click="toggleSettings">
            <Settings class="h-5 w-5" />
          </button>
        </div>
      </header>

      <div class="custom-scrollbar flex-1 overflow-y-auto bg-background p-8">
        <div class="mx-auto max-w-7xl">
          <router-view />
        </div>
      </div>
    </main>
  </div>

  <!-- Settings Dialog -->
  <el-dialog v-model="showSettingsDialog" title="系统设置" width="400px">
    <div class="space-y-4">
      <div v-if="isAdmin" class="flex items-center justify-between rounded-lg border border-border p-4">
        <div>
          <p class="font-semibold text-foreground">Debug 模式</p>
          <p class="text-sm text-muted-foreground">显示调试信息和内部 ID</p>
        </div>
        <el-switch v-model="debugModeEnabled" @change="toggleDebugMode" />
      </div>
      <div v-else class="rounded-lg border border-border p-4">
        <p class="text-sm text-muted-foreground">仅管理员可修改系统设置</p>
      </div>
    </div>
    <template #footer>
      <el-button @click="showSettingsDialog = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.3);
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 0.5);
}
</style>
