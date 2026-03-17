<template>
  <div class="space-y-6 text-foreground">
    <section class="space-y-2">
      <p class="text-xs font-medium uppercase tracking-[0.28em] text-muted-foreground">预知运输</p>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-2">
          <h1 class="text-3xl font-semibold tracking-tight text-foreground">预知运输任务</h1>
          <p class="max-w-2xl text-sm leading-6 text-muted-foreground">
            提前查看已提交但尚未审批，或已确认待运输的单据，以便做好运输准备。
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="outline" @click="loadOrders">
            <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': loading }" />
            刷新列表
          </Button>
        </div>
      </div>
    </section>

    <Card class="overflow-hidden border-border/80 bg-card/85 shadow-lg">
      <CardHeader class="border-b border-border bg-muted/30 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-xs font-medium uppercase tracking-wider text-muted-foreground">状态筛选</span>
            <div class="flex bg-muted/50 p-1 rounded-xl border border-border/50">
              <button
                v-for="opt in filterOptions"
                :key="opt.value"
                class="px-4 py-1.5 text-xs font-medium rounded-lg transition-all"
                :class="filterStatus === opt.value ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                @click="handleFilterChange(opt.value)"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
          <div class="text-xs text-muted-foreground">
            共 {{ orders.length }} 条单据
          </div>
        </div>
      </CardHeader>
      
      <CardContent class="p-0">
        <div v-if="loading" class="divide-y divide-border">
          <div v-for="i in 5" :key="i" class="p-6 space-y-3">
            <div class="h-4 w-48 bg-muted animate-pulse rounded-full" />
            <div class="h-3 w-72 bg-muted/50 animate-pulse rounded-full" />
          </div>
        </div>

        <div v-else-if="!orders.length" class="flex flex-col items-center justify-center py-20 text-center opacity-60">
          <div class="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Truck class="h-8 w-8 text-muted-foreground/40" />
          </div>
          <h3 class="text-lg font-medium text-foreground">暂无预知运输任务</h3>
          <p class="text-sm text-muted-foreground mt-1">当前没有符合筛选条件的待运输单据。</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left border-collapse">
            <thead class="bg-muted/30 border-b border-border text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              <tr>
                <th class="px-6 py-4">单据号</th>
                <th class="px-6 py-4">类型</th>
                <th class="px-6 py-4">目的地</th>
                <th class="px-6 py-4">状态</th>
                <th class="px-6 py-4">预计工装</th>
                <th class="px-6 py-4">时间节点</th>
                <th class="px-6 py-4 text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border">
              <tr v-for="order in filteredOrders" :key="order.order_no" class="group hover:bg-accent/30 transition-colors">
                <td class="px-6 py-5">
                  <router-link :to="`/inventory/${order.order_no}`" class="font-mono font-bold text-primary hover:underline">
                    {{ order.order_no }}
                  </router-link>
                  <p class="text-[10px] text-muted-foreground mt-1">提交人: {{ order.submitter_name }}</p>
                </td>
                <td class="px-6 py-5">
                  <Badge :variant="order.order_type === 'outbound' ? 'default' : 'secondary'">
                    {{ order.order_type === 'outbound' ? '出库' : '入库' }}
                  </Badge>
                </td>
                <td class="px-6 py-5 font-medium">
                  {{ order.destination || '-' }}
                </td>
                <td class="px-6 py-5">
                  <el-tag :type="getStatusType(order.status)" size="small" effect="light">
                    {{ order.status_text }}
                  </el-tag>
                </td>
                <td class="px-6 py-5 font-mono text-muted-foreground">
                  {{ order.expected_tools || 0 }} 件
                </td>
                <td class="px-6 py-5 space-y-1">
                  <div v-if="order.submit_time" class="flex items-center gap-2 text-[11px] text-muted-foreground">
                    <Clock class="h-3 w-3" /> 提交: {{ formatDate(order.submit_time) }}
                  </div>
                  <div v-if="order.keeper_confirmed_time" class="flex items-center gap-2 text-[11px] text-emerald-500/80">
                    <CheckCircle2 class="h-3 w-3" /> 确认: {{ formatDate(order.keeper_confirmed_time) }}
                  </div>
                  <div v-if="order.estimated_transport_time" class="flex items-center gap-2 text-[11px] text-amber-500/80">
                    <Truck class="h-3 w-3" /> 预计: {{ formatDate(order.estimated_transport_time) }}
                  </div>
                </td>
                <td class="px-6 py-5 text-right">
                  <Button variant="ghost" size="sm" asChild>
                    <router-link :to="`/inventory/${order.order_no}`">查看详情</router-link>
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RefreshCw, Truck, Clock, CheckCircle2 } from 'lucide-vue-next'
import { getPreTransportOrders } from '@/api/orders'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Badge from '@/components/ui/Badge.vue'

const loading = ref(false)
const orders = ref([])
const filterStatus = ref('all')

const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '已提交', value: 'submitted' },
  { label: '已确认待运输', value: 'ready' }
]

const filteredOrders = computed(() => {
  if (filterStatus.value === 'all') return orders.value
  if (filterStatus.value === 'submitted') {
    return orders.value.filter(o => o.status === 'submitted')
  }
  if (filterStatus.value === 'ready') {
    return orders.value.filter(o => ['keeper_confirmed', 'transport_notified'].includes(o.status))
  }
  return orders.value
})

async function loadOrders() {
  loading.value = true
  try {
    const result = await getPreTransportOrders()
    if (result.success) {
      orders.value = result.orders || []
    }
  } catch (error) {
    console.error('Failed to load pre-transport orders:', error)
  } finally {
    loading.value = false
  }
}

function handleFilterChange(val) {
  filterStatus.value = val
}

function getStatusType(status) {
  switch (status) {
    case 'submitted': return 'warning'
    case 'keeper_confirmed': return 'info'
    case 'transport_notified': return 'primary'
    default: return 'info'
  }
}

function formatDate(val) {
  if (!val) return '-'
  const date = new Date(val)
  return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadOrders()
})
</script>
