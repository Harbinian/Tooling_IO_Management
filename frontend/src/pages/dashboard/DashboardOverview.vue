<script setup>
import MistStats from '@/components/mist/MistStats.vue'
import MistFeatures from '@/components/mist/MistFeatures.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { 
  ArrowUpRight, 
  Clock, 
  Truck, 
  CheckCircle2,
  PlusCircle,
  History,
  Search,
  Users
} from 'lucide-vue-next'
import { ref, onMounted } from 'vue'

const stats = ref([
  { 
    title: '今日出库单', 
    value: '12', 
    description: '较昨日', 
    trend: '+20%', 
    icon: ArrowUpRight 
  },
  { 
    title: '待确认单据', 
    value: '5', 
    description: '当前积压', 
    trend: '-1', 
    icon: Clock 
  },
  { 
    title: '运输中', 
    value: '8', 
    description: '正在流转', 
    trend: '+3', 
    icon: Truck 
  },
  { 
    title: '已完成单据', 
    value: '142', 
    description: '本月累计', 
    trend: '+12%', 
    icon: CheckCircle2 
  },
])

const quickActions = [
  { 
    title: '新建出库申请', 
    description: '快速发起工装借出申请，包含工装搜索和批量选择。', 
    icon: PlusCircle, 
    link: '/inventory/create', 
    actionText: '立即发起' 
  },
  { 
    title: '查看历史订单', 
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
    title: '保管员确认', 
    description: '处理待确认的出入库申请，更新工装状态。', 
    icon: Users, 
    link: '/inventory/keeper', 
    actionText: '进入工作台' 
  },
]
</script>

<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <section class="relative overflow-hidden rounded-3xl bg-slate-900 px-8 py-16 text-white shadow-2xl">
        <div class="relative z-10 max-w-2xl">
          <Badge variant="outline" class="mb-4 border-slate-700 text-slate-400 bg-slate-800/50 backdrop-blur-sm">
            智能工装管理系统 v2.0
          </Badge>
          <h1 class="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
            下午好，<span class="text-emerald-400">测试用户</span>
          </h1>
          <p class="mt-6 text-lg text-slate-400 leading-relaxed">
            高效管理您的工装库存。通过实时追踪、自动通知和结构化工作流，让出入库流程更加简单透明。
          </p>
          <div class="mt-10 flex flex-wrap gap-4">
            <Button size="lg" class="bg-white text-slate-900 hover:bg-slate-100 font-bold" asChild>
              <router-link to="/inventory/create">
                <PlusCircle class="mr-2 h-5 w-5" /> 发起申请
              </router-link>
            </Button>
            <Button size="lg" variant="outline" class="border-slate-700 text-white hover:bg-slate-800" asChild>
              <router-link to="/inventory">
                <History class="mr-2 h-5 w-5" /> 查看历史
              </router-link>
            </Button>
          </div>
        </div>
        
        <!-- Abstract background elements -->
        <div class="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-emerald-500/10 blur-3xl"></div>
        <div class="absolute right-20 bottom-0 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl"></div>
      </section>

      <!-- Stats Grid -->
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400">核心指标</h3>
        </div>
        <MistStats :stats="stats" />
      </div>

      <!-- Quick Actions Grid -->
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400">快捷操作</h3>
        </div>
        <MistFeatures :features="quickActions" />
      </div>

      <!-- Development Info -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card class="p-8 border-dashed border-slate-200 bg-slate-50/50">
          <div class="flex flex-col items-center justify-center text-center py-4">
            <div class="h-12 w-12 rounded-2xl bg-white shadow-sm flex items-center justify-center mb-4">
              <Clock class="h-6 w-6 text-slate-400" />
            </div>
            <h4 class="text-base font-bold text-slate-900">最近动态</h4>
            <p class="text-sm text-slate-500 mt-2">实时追踪工装流转状态，模块正在开发中。</p>
          </div>
        </Card>
        <Card class="p-8 border-dashed border-slate-200 bg-slate-50/50">
          <div class="flex flex-col items-center justify-center text-center py-4">
            <div class="h-12 w-12 rounded-2xl bg-white shadow-sm flex items-center justify-center mb-4">
              <Users class="h-6 w-6 text-slate-400" />
            </div>
            <h4 class="text-base font-bold text-slate-900">团队协作</h4>
            <p class="text-sm text-slate-500 mt-2">支持多部门协同确认，模块正在开发中。</p>
          </div>
        </Card>
      </section>
    </div>
</template>
