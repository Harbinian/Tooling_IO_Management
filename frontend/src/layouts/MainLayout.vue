<script setup>
import { 
  LayoutDashboard, 
  ClipboardList, 
  PlusCircle, 
  PackageSearch, 
  Bell, 
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User
} from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { cn } from '@/lib/utils'
import Button from '@/components/ui/Button.vue'
import { useSessionStore } from '@/store/session'

const route = useRoute()
const session = useSessionStore()
const isCollapsed = ref(false)

const navigation = [
  { name: '仪表盘', href: '/dashboard', icon: LayoutDashboard },
  { name: '订单列表', href: '/inventory', icon: ClipboardList },
  { name: '新建订单', href: '/inventory/create', icon: PlusCircle },
  { name: '保管员工作台', href: '/inventory/keeper', icon: PackageSearch },
]

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

watch(
  () => ({ ...session }),
  () => session.persist(),
  { deep: true }
)
</script>

<template>
  <div class="flex h-screen bg-slate-50/30 font-sans">
    <!-- Sidebar -->
    <aside
      :class="cn(
        'relative flex flex-col border-r border-slate-200 bg-white transition-all duration-300 z-30',
        isCollapsed ? 'w-16' : 'w-72'
      )"
    >
      <!-- Logo Area -->
      <div class="flex h-16 items-center border-b border-slate-100 px-6">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white font-bold shadow-lg shadow-slate-200">
            T
          </div>
          <span v-if="!isCollapsed" class="text-lg font-bold tracking-tight text-slate-900">Tooling IO</span>
        </div>
      </div>

      <!-- Nav Items -->
      <nav class="flex-1 space-y-1.5 p-4">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          :class="cn(
            'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-all group',
            (item.href === '/inventory' ? route.path === '/inventory' : route.path.startsWith(item.href))
              ? 'bg-slate-900 text-white shadow-md shadow-slate-200' 
              : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
          )"
        >
          <component :is="item.icon" :class="cn('h-5 w-5 shrink-0', (item.href === '/inventory' ? route.path === '/inventory' : route.path.startsWith(item.href)) ? 'text-white' : 'text-slate-400 group-hover:text-slate-900')" />
          <span v-if="!isCollapsed">{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- Session / User Area -->
      <div class="border-t border-slate-100 p-4 space-y-4 bg-slate-50/50">
        <div v-if="!isCollapsed" class="space-y-3">
          <div class="space-y-1">
            <label class="text-[10px] font-bold uppercase tracking-wider text-slate-400 ml-1">用户姓名</label>
            <el-input v-model="session.userName" size="small" placeholder="姓名" class="mist-el-input" />
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold uppercase tracking-wider text-slate-400 ml-1">用户 ID</label>
            <el-input v-model="session.userId" size="small" placeholder="ID" class="mist-el-input" />
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold uppercase tracking-wider text-slate-400 ml-1">当前角色</label>
            <el-select v-model="session.role" size="small" placeholder="角色" class="w-full">
              <el-option label="班组长" value="initiator" />
              <el-option label="保管员" value="keeper" />
            </el-select>
          </div>
        </div>

        <div :class="cn('flex items-center gap-3 px-2', isCollapsed ? 'justify-center' : '')">
          <div class="h-9 w-9 rounded-xl bg-white border border-slate-200 shadow-sm flex items-center justify-center shrink-0">
            <User class="h-5 w-5 text-slate-400" />
          </div>
          <div v-if="!isCollapsed" class="flex-1 overflow-hidden">
            <p class="text-sm font-bold text-slate-900 truncate">{{ session.userName || '未登录' }}</p>
            <p class="text-[10px] font-bold uppercase tracking-tight text-slate-400 truncate">
              {{ session.role === 'keeper' ? '保管员' : '班组长' }}
            </p>
          </div>
          <button v-if="!isCollapsed" class="text-slate-300 hover:text-rose-500 transition-colors">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- Toggle Button -->
      <button
        @click="toggleSidebar"
        class="absolute -right-3 top-20 flex h-6 w-6 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 hover:text-slate-900 shadow-sm transition-all hover:scale-110 z-40"
      >
        <ChevronLeft v-if="!isCollapsed" class="h-4 w-4" />
        <ChevronRight v-else class="h-4 w-4" />
      </button>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- Top Header -->
      <header class="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-8 shrink-0">
        <div class="flex items-center gap-4">
          <h2 class="text-sm font-bold text-slate-400 uppercase tracking-[0.2em]">
            {{ route.meta.title || 'Overview' }}
          </h2>
        </div>
        <div class="flex items-center gap-3">
          <button class="relative rounded-xl p-2 text-slate-400 hover:bg-slate-50 hover:text-slate-900 transition-all">
            <Bell class="h-5 w-5" />
            <span class="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-rose-500 border-2 border-white"></span>
          </button>
          <button class="rounded-xl p-2 text-slate-400 hover:bg-slate-50 hover:text-slate-900 transition-all">
            <Settings class="h-5 w-5" />
          </button>
        </div>
      </header>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto bg-slate-50/50 p-8 custom-scrollbar">
        <div class="mx-auto max-w-7xl">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.mist-el-input :deep(.el-input__wrapper) {
  background-color: white !important;
  box-shadow: none !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px !important;
}

.mist-el-input :deep(.el-input__wrapper.is-focus) {
  border-color: #0f172a !important;
}

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
