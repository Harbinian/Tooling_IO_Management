<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ClipboardList,
  ShieldCheck,
  LayoutDashboard,
  Settings,
  ArrowRight
} from 'lucide-vue-next'

import { useSessionStore } from '@/store/session'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Badge from '@/components/ui/Badge.vue'
import { DEBUG_IDS } from '@/debug/debugIds'

const session = useSessionStore()
const router = useRouter()

// Module definitions
const moduleGroups = [
  {
    group: '工装管理系统',
    modules: [
      {
        id: 'tool-io',
        title: '工装出入库管理',
        description: '处理工装借出、归还、入库等全流程管理，支持批量操作和实时状态追踪。',
        icon: ClipboardList,
        permission: 'order:list',
        defaultRoute: '/inventory',
        debugId: 'H-CARD-TOOL-IO',
        subRoutes: [
          { path: '/inventory', permission: 'order:list' },
          { path: '/inventory/create', permission: 'order:create' },
          { path: '/inventory/keeper', permission: 'order:keeper_confirm' },
          { path: '/inventory/pre-transport', permission: 'order:transport_execute' }
        ]
      },
      {
        id: 'inspection',
        title: '定检任务管理',
        description: '管理工装定期检验计划、任务分配、执行记录和统计分析。',
        icon: ShieldCheck,
        permission: 'inspection:list',
        defaultRoute: '/inspection/plans',
        debugId: 'H-CARD-INSPECTION',
        subRoutes: [
          { path: '/inspection/plans', permission: 'inspection:list' },
          { path: '/inspection/tasks', permission: 'inspection:list' },
          { path: '/inspection/dashboard', permission: 'inspection:list' }
        ]
      }
    ]
  },
  {
    group: '系统概览与管理',
    modules: [
      {
        id: 'dashboard',
        title: '系统概览',
        description: '查看工装库存动态、待处理任务和团队工作负载概览。',
        icon: LayoutDashboard,
        permission: 'dashboard:view',
        defaultRoute: '/dashboard',
        debugId: 'H-CARD-DASHBOARD',
        subRoutes: [
          { path: '/dashboard', permission: 'dashboard:view' }
        ]
      },
      {
        id: 'admin',
        title: '系统管理',
        description: '用户账号、角色权限、组织架构和系统配置管理。',
        icon: Settings,
        permission: 'admin:user_manage',
        defaultRoute: '/admin/users',
        debugId: 'H-CARD-ADMIN',
        subRoutes: [
          { path: '/admin/users', permission: 'admin:user_manage' },
          { path: '/admin/roles', permission: 'admin:role_manage' },
          { path: '/admin/permissions', permission: 'admin:role_manage' },
          { path: '/admin/feedback', permission: 'admin:user_manage' }
        ]
      }
    ]
  }
]

// Compute accessible modules based on user permissions
const computedModuleGroups = computed(() => {
  return moduleGroups
    .map(group => ({
      ...group,
      modules: group.modules.map(module => {
        const accessibleRoute = module.subRoutes.find(route =>
          session.hasPermission(route.permission)
        )
        const hasAccessibleRoute = !!accessibleRoute
        const hasPermission = !module.permission || session.hasPermission(module.permission)

        return {
          ...module,
          isAccessible: hasPermission && hasAccessibleRoute,
          computedDefaultRoute: accessibleRoute?.path || module.defaultRoute
        }
      }).filter(module => module.isAccessible)
    }))
    .filter(group => group.modules.length > 0)
})

const navigateToModule = (module) => {
  router.push(module.computedDefaultRoute)
}
</script>

<template>
  <div class="space-y-10" v-debug-id="DEBUG_IDS.HOME.PAGE">
    <!-- Page Header -->
    <section class="relative overflow-hidden rounded-3xl bg-primary px-8 py-12 text-primary-foreground shadow-2xl">
      <div class="relative z-10 max-w-2xl">
        <Badge variant="outline" class="mb-4 border-primary-foreground/20 text-primary-foreground bg-primary-foreground/10">
          模块入口
        </Badge>
        <h1 class="text-3xl font-bold tracking-tight md:text-4xl text-primary-foreground">
          欢迎回来，<span class="text-emerald-400">{{ session.userName || '用户' }}</span>
        </h1>
        <p class="mt-4 text-lg text-primary-foreground/80">
          选择您需要访问的功能模块，开始工作。
        </p>
      </div>
      <div class="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl"></div>
    </section>

    <!-- Module Cards -->
    <div v-for="group in computedModuleGroups" :key="group.group" class="space-y-6">
      <h3 class="text-[11px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
        {{ group.group }}
      </h3>

      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
        <Card
          v-for="module in group.modules"
          :key="module.id"
          :class="[
            'group relative overflow-hidden cursor-pointer transition-all hover:scale-[1.02] hover:shadow-xl',
            'bg-card/80 backdrop-blur-sm border-border/50',
            module.isAccessible ? 'hover:border-primary/30' : 'opacity-50 cursor-not-allowed'
          ]"
          v-debug-id="module.debugId"
          @click="navigateToModule(module)"
        >
          <CardHeader class="flex flex-row items-start justify-between space-y-0 pb-4">
            <div class="flex items-center gap-4">
              <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary shadow-lg shadow-primary/10 group-hover:bg-primary group-hover:text-primary-foreground transition-all">
                <component :is="module.icon" class="h-7 w-7" />
              </div>
              <div>
                <CardTitle class="text-xl font-bold text-foreground">
                  {{ module.title }}
                </CardTitle>
              </div>
            </div>
            <ArrowRight class="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
          </CardHeader>

          <CardContent>
            <p class="text-[13px] leading-relaxed text-muted-foreground">
              {{ module.description }}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
