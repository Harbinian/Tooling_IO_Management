<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Box, Calendar, FileText, Settings as SettingsIcon, ChevronRight } from 'lucide-vue-next'
import { useSessionStore } from '@/store/session'

const router = useRouter()
const session = useSessionStore()

const currentTime = ref(new Date())
/** @type {any} */
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric', 
    weekday: 'long' 
  })
})

const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

const greeting = computed(() => {
  const hour = currentTime.value.getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

const allCards = [
  {
    key: 'tool-io',
    title: '工装出入库',
    icon: Box,
    href: '/inventory',
    permission: 'order:list',
    description: '出入库订单管理',
    colorClass: 'text-primary',
    bgClass: 'bg-primary/10'
  },
  {
    key: 'inspection',
    title: '定检管理',
    icon: Calendar,
    href: '/inspection/plans',
    permission: 'inspection:list',
    description: '工装定期检查任务',
    colorClass: 'text-warning',
    bgClass: 'bg-warning/10'
  },
  {
    key: 'mpl',
    title: 'MPL管理',
    icon: FileText,
    href: '/mpl',
    permission: 'mpl:write',
    description: '工装可拆卸件清单',
    colorClass: 'text-destructive',
    bgClass: 'bg-destructive/10'
  },
  {
    key: 'admin',
    title: '系统管理',
    icon: SettingsIcon,
    href: '/admin/users',
    permission: 'admin:user_manage',
    description: '用户、角色、权限管理',
    colorClass: 'text-foreground',
    bgClass: 'bg-muted'
  }
]

const visibleCards = computed(() => {
  return allCards.filter(card => {
    // Sys admin has access to everything
    if (session.isAdmin()) return true;
    
    // Check specific permission
    if (card.permission) {
      return session.hasPermission(card.permission)
    }
    return true
  })
})

const navigateTo = (/** @type {any} */ href) => {
  router.push(href)
}
</script>

<template>
  <div class="space-y-8">
    <!-- Portal Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card p-8 rounded-3xl border border-border shadow-sm">
      <div class="space-y-2">
        <h1 class="text-3xl font-black tracking-tight text-foreground">
          {{ greeting }}，{{ session.userName || session.loginName }}
        </h1>
        <p class="text-muted-foreground text-lg">欢迎使用工装管理系统</p>
      </div>
      <div class="text-right">
        <div class="text-4xl font-black tracking-tighter text-foreground">{{ formattedTime }}</div>
        <div class="text-sm font-medium text-muted-foreground mt-1">{{ formattedDate }}</div>
      </div>
    </div>

    <!-- Portal Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      <div
        v-for="card in visibleCards"
        :key="card.key"
        @click="navigateTo(card.href)"
        class="group relative overflow-hidden rounded-3xl bg-card border border-border p-6 shadow-sm transition-all hover:shadow-md hover:border-primary/50 cursor-pointer flex flex-col h-full"
      >
        <div class="flex items-start justify-between mb-8">
          <div :class="['h-14 w-14 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110', card.bgClass]">
            <component :is="card.icon" :class="['h-7 w-7', card.colorClass]" />
          </div>
          <div class="h-8 w-8 rounded-full bg-muted flex items-center justify-center transition-colors group-hover:bg-primary group-hover:text-primary-foreground text-muted-foreground">
            <ChevronRight class="h-4 w-4" />
          </div>
        </div>
        
        <div class="mt-auto space-y-2">
          <h3 class="text-xl font-bold text-foreground group-hover:text-primary transition-colors">
            {{ card.title }}
          </h3>
          <p class="text-sm text-muted-foreground line-clamp-2">
            {{ card.description }}
          </p>
        </div>
        
        <!-- Decorative background element -->
        <div :class="['absolute -right-12 -bottom-12 h-32 w-32 rounded-full blur-[40px] opacity-0 group-hover:opacity-50 transition-opacity', card.bgClass]"></div>
      </div>
    </div>
    
    <!-- Empty State if no cards are visible -->
    <div v-if="visibleCards.length === 0" class="flex flex-col items-center justify-center p-12 bg-card rounded-3xl border border-border shadow-sm">
      <div class="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-4">
        <Box class="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-bold text-foreground mb-2">暂无可用业务</h3>
      <p class="text-sm text-muted-foreground">您当前没有任何业务模块的访问权限，请联系管理员。</p>
    </div>
  </div>
</template>
