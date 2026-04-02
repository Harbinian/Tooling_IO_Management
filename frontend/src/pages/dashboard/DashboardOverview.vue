<script setup>
import { ref, onMounted, computed } from 'vue'
import { ArrowUpRight, Clock, Truck, CheckCircle2, PlusCircle, History, Search, Users } from 'lucide-vue-next'
import MistStats from '@/components/mist/MistStats.vue'
import MistFeatures from '@/components/mist/MistFeatures.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { useSessionStore } from '@/store/session'
import { getDashboardMetrics } from '@/api/dashboard'
import { DEBUG_IDS } from '@/debug/debugIds'

const session = useSessionStore()

const stats = ref([
  { title: '今日出库', value: '0', description: '今日累计发起', icon: ArrowUpRight, debugId: DEBUG_IDS.DASHBOARD.PENDING_KEEPER_METRIC },
  { title: '今日入库', value: '0', description: '今日累计发起', icon: ArrowUpRight, debugId: DEBUG_IDS.DASHBOARD.PENDING_TRANSPORT_METRIC },
  { title: '待确认单据', value: '0', description: '等待保管员确认', icon: Clock, debugId: DEBUG_IDS.DASHBOARD.PENDING_CONFIRM_METRIC },
  { title: '运输中', value: '0', description: '正在运输或待运输', icon: Truck, debugId: DEBUG_IDS.DASHBOARD.IN_TRANSIT_METRIC },
  { title: '待最终确认', value: '0', description: '等待流程结束', icon: CheckCircle2, debugId: DEBUG_IDS.DASHBOARD.PENDING_FINAL_CONFIRM_METRIC },
  { title: '活跃单据', value: '0', description: '进行中的总单数', icon: History, debugId: DEBUG_IDS.DASHBOARD.ACTIVE_ORDERS_METRIC }
])


const loading = ref(true)

async function fetchStats() {
  try {
    loading.value = true
    const result = await getDashboardMetrics()
    if (result.success && result.data) {
      const data = result.data
      stats.value[0].value = (data.today_outbound_orders || 0).toString()
      stats.value[1].value = (data.today_inbound_orders || 0).toString()
      stats.value[2].value = (data.orders_pending_keeper_confirmation || 0).toString()
      stats.value[3].value = (data.orders_in_transport || 0).toString()
      stats.value[4].value = (data.orders_pending_final_confirmation || 0).toString()
      stats.value[5].value = (data.active_orders_total || 0).toString()
    }
  } catch (error) {
    console.error('获取仪表盘指标失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})

const quickActions = [
  {
    title: '新建出库申请',
    description: '快速发起工装借出申请，包含工装搜索和批量选择。',
    icon: PlusCircle,
    link: '/inventory/create',
    actionText: '立即发起'
  },
  {
    title: '查看历史单据',
    description: '检索和过滤所有已发起的出入库记录，查看详细进度。',
    icon: History,
    link: '/inventory',
    actionText: '进入列表'
  },
  {
    title: '库存工装查询',
    description: '实时查询工装状态、位置信息和图号详情。',
    icon: Search,
    link: '/inventory/create',
    actionText: '搜索库存'
  },
  {
    title: '保管确认',
    description: '处理待确认的出入库申请，更新工装状态与确认结果。',
    icon: Users,
    link: '/inventory/keeper',
    actionText: '进入工作台',
    permission: 'order:keeper_confirm'
  }
]

const availableQuickActions = computed(() =>
  quickActions.filter((action) => !action.permission || session.hasPermission(action.permission))
)
</script>

<template>
  <div class="space-y-12">
    <section v-debug-id="DEBUG_IDS.DASHBOARD.SUMMARY_CARD" class="relative overflow-hidden rounded-3xl bg-primary px-8 py-16 text-primary-foreground shadow-2xl">

      <div class="relative z-10 max-w-2xl">
        <Badge variant="outline" class="mb-4 border-primary-foreground/20 text-primary-foreground bg-primary-foreground/10 backdrop-blur-sm">
          智能工装管理系统 v2.0
        </Badge>
        <h1 class="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl text-primary-foreground">
          下午好，<span class="text-emerald-400">{{ session.userName || '测试用户' }}</span>
        </h1>
        <p class="mt-6 text-lg text-primary-foreground/80 leading-relaxed">
          高效管理工装库存。通过实时追踪、自动通知和结构化流程，让出入库过程更简单、更透明。
        </p>
        <div class="mt-10 flex flex-wrap gap-4">
          <Button v-debug-id="DEBUG_IDS.DASHBOARD.CREATE_OUTBOUND_BTN" v-if="session.hasPermission('order:create')" size="lg" class="bg-background text-foreground hover:bg-muted font-bold border-none" asChild>
            <router-link to="/inventory/create">
              <PlusCircle class="mr-2 h-5 w-5" /> 发起申请
            </router-link>
          </Button>
          <Button v-debug-id="DEBUG_IDS.DASHBOARD.VIEW_HISTORY_BTN" v-if="session.hasPermission('order:list')" size="lg" variant="ghost" class="border border-primary-foreground/20 text-primary-foreground hover:bg-white/10 font-bold" asChild>
            <router-link to="/inventory">
              <History class="mr-2 h-5 w-5" /> 查看历史
            </router-link>
          </Button>
        </div>
      </div>

      <div class="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-emerald-500/10 blur-3xl"></div>
      <div class="absolute right-20 bottom-0 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl"></div>
    </section>

    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h3 class="text-[11px] font-bold uppercase tracking-[0.2em] text-muted-foreground">核心指标</h3>
      </div>
      <MistStats :stats="stats" />
    </div>

    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h3 class="text-[11px] font-bold uppercase tracking-[0.2em] text-muted-foreground">快捷操作</h3>
      </div>
      <MistFeatures :features="availableQuickActions" />
    </div>

    <section class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <Card class="p-8 border-dashed border-border bg-muted/50">
        <div class="flex flex-col items-center justify-center text-center py-4">
          <div class="h-12 w-12 rounded-2xl bg-background shadow-sm flex items-center justify-center mb-4">
            <Clock class="h-6 w-6 text-muted-foreground" />
          </div>
          <h4 class="text-base font-bold text-foreground">最近动态</h4>
          <p class="text-sm text-muted-foreground mt-2">实时追踪工装流转状态，更多模块持续完善中。</p>
        </div>
      </Card>
      <Card class="p-8 border-dashed border-border bg-muted/50">
        <div class="flex flex-col items-center justify-center text-center py-4">
          <div class="h-12 w-12 rounded-2xl bg-background shadow-sm flex items-center justify-center mb-4">
            <Users class="h-6 w-6 text-muted-foreground" />
          </div>
          <h4 class="text-base font-bold text-foreground">团队协作</h4>
          <p class="text-sm text-muted-foreground mt-2">支持多角色协同确认，后续能力持续补齐。</p>
        </div>
      </Card>
    </section>
  </div>
</template>
