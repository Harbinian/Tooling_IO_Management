<script setup>
import {
  Bell,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  PackageSearch,
  PlusCircle,
  Settings,
  ShieldCheck,
  User,
  Users
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { cn } from '@/lib/utils'
import { useSessionStore } from '@/store/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const isCollapsed = ref(false)

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, permission: 'dashboard:view' },
  { name: 'Order List', href: '/inventory', icon: ClipboardList, permission: 'order:list' },
  { name: 'Create Request', href: '/inventory/create', icon: PlusCircle, permission: 'order:create' },
  { name: 'Keeper Workspace', href: '/inventory/keeper', icon: PackageSearch, permission: 'order:keeper_confirm' },
  { name: 'Account Management', href: '/admin/users', icon: Users, permission: 'admin:user_manage' }
]

const availableNavigation = computed(() =>
  navigation.filter((item) => !item.permission || session.hasPermission(item.permission))
)

const displayRole = computed(() => session.roleName || (session.role === 'keeper' ? 'Keeper' : 'Initiator'))

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const logout = async () => {
  session.clear()
  await router.replace('/login')
}

function isActive(href) {
  return href === '/inventory' ? route.path === '/inventory' : route.path.startsWith(href)
}
</script>

<template>
  <div class="flex h-screen bg-slate-50/30 font-sans">
    <aside
      :class="cn(
        'relative z-30 flex flex-col border-r border-slate-200 bg-white transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-72'
      )"
    >
      <div class="flex h-16 items-center border-b border-slate-100 px-6">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 font-bold text-white shadow-lg shadow-slate-200">
            <ShieldCheck class="h-5 w-5" />
          </div>
          <span v-if="!isCollapsed" class="text-lg font-bold tracking-tight text-slate-900">Tooling IO</span>
        </div>
      </div>

      <nav class="flex-1 space-y-1.5 p-4">
        <router-link
          v-for="item in availableNavigation"
          :key="item.name"
          :to="item.href"
          :class="cn(
            'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-all',
            isActive(item.href)
              ? 'bg-slate-900 text-white shadow-md shadow-slate-200'
              : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
          )"
        >
          <component
            :is="item.icon"
            :class="cn('h-5 w-5 shrink-0', isActive(item.href) ? 'text-white' : 'text-slate-400 group-hover:text-slate-900')"
          />
          <span v-if="!isCollapsed">{{ item.name }}</span>
        </router-link>
      </nav>

      <div class="space-y-4 border-t border-slate-100 bg-slate-50/50 p-4">
        <div v-if="!isCollapsed" class="space-y-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p class="text-[10px] font-bold uppercase tracking-[0.28em] text-slate-400">Current User</p>
          <div>
            <p class="text-lg font-bold text-slate-900">{{ session.userName || 'Not Signed In' }}</p>
            <p class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              {{ session.loginName || 'anonymous' }}
            </p>
          </div>
          <div class="grid gap-3 sm:grid-cols-2">
            <div class="rounded-xl bg-slate-50 px-3 py-2">
              <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">User ID</p>
              <p class="mt-1 truncate text-sm font-semibold text-slate-700">{{ session.userId || '-' }}</p>
            </div>
            <div class="rounded-xl bg-slate-50 px-3 py-2">
              <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Primary Role</p>
              <p class="mt-1 truncate text-sm font-semibold text-slate-700">{{ displayRole }}</p>
            </div>
          </div>
        </div>

        <div :class="cn('flex items-center gap-3 px-2', isCollapsed ? 'justify-center' : '')">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white shadow-sm">
            <User class="h-5 w-5 text-slate-400" />
          </div>
          <div v-if="!isCollapsed" class="flex-1 overflow-hidden">
            <p class="truncate text-sm font-bold text-slate-900">{{ session.userName || 'Not Signed In' }}</p>
            <p class="truncate text-[10px] font-bold uppercase tracking-tight text-slate-400">
              {{ displayRole }}
            </p>
          </div>
          <button v-if="!isCollapsed" class="text-slate-300 transition-colors hover:text-rose-500" @click="logout">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>

      <button
        @click="toggleSidebar"
        class="absolute -right-3 top-20 z-40 flex h-6 w-6 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 shadow-sm transition-all hover:scale-110 hover:text-slate-900"
      >
        <ChevronLeft v-if="!isCollapsed" class="h-4 w-4" />
        <ChevronRight v-else class="h-4 w-4" />
      </button>
    </aside>

    <main class="flex flex-1 flex-col overflow-hidden">
      <header class="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-8">
        <div class="flex items-center gap-4">
          <h2 class="text-sm font-bold uppercase tracking-[0.2em] text-slate-400">
            {{ route.meta.title || 'Overview' }}
          </h2>
        </div>
        <div class="flex items-center gap-3">
          <button class="relative rounded-xl p-2 text-slate-400 transition-all hover:bg-slate-50 hover:text-slate-900">
            <Bell class="h-5 w-5" />
            <span class="absolute right-2.5 top-2.5 h-2 w-2 rounded-full border-2 border-white bg-rose-500"></span>
          </button>
          <button class="rounded-xl p-2 text-slate-400 transition-all hover:bg-slate-50 hover:text-slate-900">
            <Settings class="h-5 w-5" />
          </button>
        </div>
      </header>

      <div class="custom-scrollbar flex-1 overflow-y-auto bg-slate-50/50 p-8">
        <div class="mx-auto max-w-7xl">
          <router-view />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
