<template>
  <div class="space-y-6">
    <section class="space-y-2">
      <p class="text-xs font-medium uppercase tracking-[0.28em] text-slate-400">单据列表</p>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-2">
          <h1 class="text-3xl font-semibold tracking-tight text-slate-900">工装出入库单据</h1>
          <p class="max-w-2xl text-sm leading-6 text-slate-500">
            统一查看出库和入库申请，快速筛选并在列表中直接处理单据。
          </p>
        </div>
        <div class="grid gap-3 sm:grid-cols-3">
          <div
            v-for="metric in summaryMetrics"
            :key="metric.label"
            class="rounded-2xl border border-white/70 bg-white/80 px-4 py-3 shadow-[0_20px_45px_-30px_rgba(15,23,42,0.35)] backdrop-blur"
          >
            <p class="text-xs uppercase tracking-[0.2em] text-slate-400">{{ metric.label }}</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ metric.value }}</p>
            <p class="text-xs text-slate-500">{{ metric.hint }}</p>
          </div>
        </div>
      </div>
    </section>

    <Card v-debug-id="DEBUG_IDS.ORDER_LIST.FILTER_SECTION" class="overflow-hidden border-slate-200/80 bg-white/85 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.45)]">
      <CardHeader class="border-b border-slate-100 bg-[linear-gradient(180deg,rgba(248,250,252,0.95),rgba(255,255,255,0.78))]">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div class="space-y-1">
            <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">筛选</p>
            <CardTitle class="text-lg text-slate-900">搜索并收敛队列</CardTitle>
            <p class="text-sm text-slate-500">
              保持原有后端筛选能力，同时用更清晰的方式呈现。
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <Button v-debug-id="DEBUG_IDS.ORDER_LIST.RESET_BTN" variant="outline" @click="resetFilters">重置筛选</Button>
            <Button @click="loadOrders">刷新列表</Button>
          </div>
        </div>
      </CardHeader>
      <CardContent class="pt-6">
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">关键词</span>
            <input
              v-debug-id="DEBUG_IDS.ORDER_LIST.SEARCH_INPUT"
              v-model="filters.keyword"
              type="text"
              class="mist-input"
              placeholder="单号、项目代号或备注"
              @keyup.enter="searchFromFirstPage"
            />
          </label>
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">单据类型</span>
            <select v-debug-id="DEBUG_IDS.ORDER_LIST.TYPE_FILTER" v-model="filters.orderType" class="mist-input">
              <option value="">全部类型</option>
              <option value="outbound">出库</option>
              <option value="inbound">入库</option>
            </select>
          </label>
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">单据状态</span>
            <select v-debug-id="DEBUG_IDS.ORDER_LIST.STATUS_FILTER" v-model="filters.orderStatus" class="mist-input">
              <option value="">全部状态</option>
              <option v-for="(status, key) in statusOptions" :key="key" :value="key">
                {{ status.label }}
              </option>
            </select>
          </label>
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">发起人 ID</span>
            <input
              v-model="filters.initiatorId"
              type="text"
              class="mist-input"
              placeholder="发起人账号"
              @keyup.enter="searchFromFirstPage"
            />
          </label>
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">保管员 ID</span>
            <input
              v-model="filters.keeperId"
              type="text"
              class="mist-input"
              placeholder="保管员账号"
              @keyup.enter="searchFromFirstPage"
            />
          </label>
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">创建起始</span>
            <input v-debug-id="DEBUG_IDS.ORDER_LIST.DATE_RANGE_FILTER" v-model="filters.dateFrom" type="date" class="mist-input" />
          </label>
          <label class="space-y-2">
            <span class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">创建截止</span>
            <input v-model="filters.dateTo" type="date" class="mist-input" />
          </label>

          <div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 p-4 text-sm text-slate-500">
            当前页面仍然读取 <code>/api/tool-io-orders</code>，保留原有分页、状态和行操作行为。
          </div>
        </div>
      </CardContent>
    </Card>

    <Card v-debug-id="DEBUG_IDS.ORDER_LIST.ORDER_TABLE" class="overflow-hidden border-slate-200/80 bg-white/90 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.45)]">
      <CardHeader class="border-b border-slate-100">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div class="space-y-1">
            <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">结果</p>
            <CardTitle class="text-lg text-slate-900">业务队列</CardTitle>
            <p class="text-sm text-slate-500">
              共 {{ pagination.total }} 条单据。当前第 {{ pagination.pageNo }} 页，每页 {{ pagination.pageSize }} 条。
            </p>
          </div>
          <div class="flex flex-wrap gap-2 text-xs text-slate-500">
            <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1">中文界面</span>
            <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1">接口保持不变</span>
          </div>
        </div>
      </CardHeader>
      <CardContent class="pt-0">
        <div v-if="loading" class="divide-y divide-slate-100">
          <div
            v-for="index in 6"
            :key="index"
            class="grid gap-4 px-6 py-5 lg:grid-cols-[1.7fr_0.8fr_0.9fr_0.9fr_0.95fr_1.1fr_auto]"
          >
            <div class="space-y-2">
              <div class="h-4 w-44 animate-pulse rounded-full bg-slate-200/80" />
              <div class="h-3 w-64 animate-pulse rounded-full bg-slate-100" />
            </div>
            <div class="h-6 w-16 animate-pulse rounded-full bg-slate-100" />
            <div class="h-4 w-20 animate-pulse rounded-full bg-slate-100" />
            <div class="h-4 w-20 animate-pulse rounded-full bg-slate-100" />
            <div class="h-6 w-20 animate-pulse rounded-full bg-slate-100" />
            <div class="h-4 w-28 animate-pulse rounded-full bg-slate-100" />
            <div class="h-9 w-28 animate-pulse rounded-full bg-slate-100" />
          </div>
        </div>

        <div
          v-else-if="errorMessage"
          class="flex flex-col items-center justify-center gap-4 px-6 py-16 text-center"
        >
          <div class="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-medium text-rose-600">
            请求失败
          </div>
          <div class="space-y-2">
            <h3 class="text-lg font-semibold text-slate-900">单据列表加载失败</h3>
            <p class="max-w-md text-sm leading-6 text-slate-500">{{ errorMessage }}</p>
          </div>
          <Button @click="loadOrders">重试</Button>
        </div>

        <div
          v-else-if="!orders.length"
          class="flex flex-col items-center justify-center gap-4 px-6 py-16 text-center"
        >
          <div class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">
            空状态
          </div>
          <div class="space-y-2">
            <h3 class="text-lg font-semibold text-slate-900">
              {{ hasActiveFilters ? '没有匹配当前筛选条件的单据' : '暂时还没有单据' }}
            </h3>
            <p class="max-w-md text-sm leading-6 text-slate-500">
              {{
                hasActiveFilters
                  ? '可以调整或清空筛选条件后再试。'
                  : '创建新的出入库申请后，单据会显示在这里。'
              }}
            </p>
          </div>
          <Button :variant="hasActiveFilters ? 'outline' : 'default'" @click="handleEmptyAction">
            {{ hasActiveFilters ? '清空筛选' : '重新加载' }}
          </Button>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <article
            v-for="order in orders"
            :key="order.orderNo"
            class="grid gap-4 px-6 py-5 transition-colors hover:bg-slate-50/70 lg:grid-cols-[1.7fr_0.8fr_0.9fr_0.9fr_0.95fr_1.1fr_auto]"
          >
            <div class="min-w-0 space-y-2">
              <button
                v-debug-id="DEBUG_IDS.ORDER_LIST.ORDER_NO_COL"
                class="text-left text-sm font-semibold text-slate-900 transition-colors hover:text-slate-600"
                @click="viewOrder(order.orderNo)"
              >
                {{ order.orderNo }}
              </button>
              <div class="flex flex-wrap gap-2 text-xs text-slate-500">
                <span class="rounded-full bg-slate-100 px-2.5 py-1">项目 {{ order.projectCode || '-' }}</span>
                <span class="rounded-full bg-slate-100 px-2.5 py-1">工装 {{ order.toolCount || 0 }}</span>
                <span class="rounded-full bg-slate-100 px-2.5 py-1">
                  位置 {{ order.targetLocationText || '-' }}
                </span>
              </div>
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">类型</p>
              <p class="text-sm font-medium text-slate-700">{{ orderTypeLabel(order.orderType) }}</p>
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">发起人</p>
              <p class="text-sm font-medium text-slate-700">{{ order.initiatorName || '-' }}</p>
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">保管员</p>
              <p class="text-sm font-medium text-slate-700">{{ order.keeperName || '-' }}</p>
            </div>

            <div v-debug-id="DEBUG_IDS.ORDER_LIST.STATUS_COL" class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">状态</p>
              <OrderStatusTag :status="order.orderStatus" />
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">创建时间</p>
              <p class="text-sm font-medium text-slate-700">{{ formatDateTime(order.createdAt) }}</p>
            </div>

            <div class="flex flex-wrap items-start justify-start gap-2 lg:justify-end">
              <Button v-debug-id="DEBUG_IDS.ORDER_LIST.VIEW_ACTION" variant="outline" size="sm" @click="viewOrder(order.orderNo)">查看</Button>
              <Button
                v-if="canSubmit(order)"
                variant="ghost"
                size="sm"
                class="text-amber-700 hover:bg-amber-50 hover:text-amber-800"
                @click="submitCurrentOrder(order)"
              >
                提交
              </Button>
              <Button
                v-if="canCancel(order)"
                variant="ghost"
                size="sm"
                class="text-rose-700 hover:bg-rose-50 hover:text-rose-800"
                @click="cancelCurrentOrder(order)"
              >
                取消
              </Button>
              <Button
                v-if="canFinalConfirm(order)"
                variant="ghost"
                size="sm"
                class="text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800"
                @click="finalConfirmCurrentOrder(order)"
              >
                最终确认
              </Button>
            </div>
          </article>
        </div>


        <div class="flex flex-col gap-4 border-t border-slate-100 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-slate-500">
            显示第 {{ pageStart }} 到 {{ pageEnd }} 条，共 {{ pagination.total }} 条单据
          </p>
          <div class="flex items-center gap-2">
            <Button variant="outline" :disabled="pagination.pageNo <= 1 || loading" @click="changePage(-1)">
              上一页
            </Button>
            <div class="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-600">
              {{ pagination.pageNo }} / {{ totalPages }}
            </div>
            <Button
              variant="outline"
              :disabled="pagination.pageNo >= totalPages || loading || !pagination.total"
              @click="changePage(1)"
            >
              下一页
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { cancelOrder, finalConfirmOrder, getOrderList, submitOrder } from '@/api/orders'
import OrderStatusTag from '@/components/tool-io/OrderStatusTag.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import { formatDateTime, orderStatusMap } from '@/utils/toolIO'
import { useSessionStore } from '@/store/session'
import { DEBUG_IDS } from '@/debug/debugIds'

const router = useRouter()

const session = useSessionStore()

const statusOptions = orderStatusMap
const orders = ref([])
const loading = ref(false)
const errorMessage = ref('')

const filters = reactive({
  keyword: '',
  orderType: '',
  orderStatus: '',
  initiatorId: '',
  keeperId: '',
  dateFrom: '',
  dateTo: ''
})

const pagination = reactive({
  pageNo: 1,
  pageSize: 20,
  total: 0
})

const totalPages = computed(() => Math.max(1, Math.ceil((pagination.total || 0) / pagination.pageSize)))
const pageStart = computed(() => (pagination.total ? (pagination.pageNo - 1) * pagination.pageSize + 1 : 0))
const pageEnd = computed(() => Math.min(pagination.total, pagination.pageNo * pagination.pageSize))
const hasActiveFilters = computed(() => Object.values(filters).some((value) => Boolean(value)))

const summaryMetrics = computed(() => [
  {
    label: '当前总数',
    value: pagination.total,
    hint: '按当前筛选条件返回的全部单据。'
  },
  {
    label: '本页草稿',
    value: orders.value.filter((order) => order.orderStatus === 'draft').length,
    hint: '仍可由发起人提交的单据。'
  },
  {
    label: '待处理',
    value: orders.value.filter((order) => ['submitted', 'partially_confirmed'].includes(order.orderStatus)).length,
    hint: '仍处于保管或后续处理过程中的单据。'
  }
])

function buildOperator() {
  return {
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  }
}

async function loadOrders() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await getOrderList({
      keyword: filters.keyword,
      order_type: filters.orderType,
      order_status: filters.orderStatus,
      initiator_id: filters.initiatorId,
      keeper_id: filters.keeperId,
      date_from: filters.dateFrom,
      date_to: filters.dateTo,
      page_no: pagination.pageNo,
      page_size: pagination.pageSize
    })

    if (!result.success) {
      errorMessage.value = result.error || '单据列表加载失败。'
      orders.value = []
      pagination.total = 0
      return
    }

    orders.value = result.data
    pagination.total = result.total || 0
  } catch (error) {
    orders.value = []
    pagination.total = 0
    errorMessage.value = error?.response?.data?.error || error?.message || '单据列表加载失败。'
  } finally {
    loading.value = false
  }
}

function searchFromFirstPage() {
  pagination.pageNo = 1
  loadOrders()
}

function resetFilters() {
  filters.keyword = ''
  filters.orderType = ''
  filters.orderStatus = ''
  filters.initiatorId = ''
  filters.keeperId = ''
  filters.dateFrom = ''
  filters.dateTo = ''
  pagination.pageNo = 1
  loadOrders()
}

function handleEmptyAction() {
  if (hasActiveFilters.value) {
    resetFilters()
    return
  }
  loadOrders()
}

function changePage(direction) {
  const nextPage = pagination.pageNo + direction
  if (nextPage < 1 || nextPage > totalPages.value) return
  pagination.pageNo = nextPage
  loadOrders()
}

function viewOrder(orderNo) {
  router.push(`/inventory/${orderNo}`)
}

function orderTypeLabel(orderType) {
  return orderType === 'outbound' ? '出库' : orderType === 'inbound' ? '入库' : '-'
}

function canSubmit(order) {
  return session.hasPermission('order:submit') && order.orderStatus === 'draft'
}

function canCancel(order) {
  return session.hasPermission('order:cancel') && ['draft', 'rejected'].includes(order.orderStatus)
}

function canFinalConfirm(order) {
  if (!session.hasPermission('order:final_confirm')) return false
  
  if (order.orderType === 'outbound') {
    return ['transport_notified', 'transport_completed', 'final_confirmation_pending'].includes(order.orderStatus)
  }
  return ['transport_notified', 'transport_completed', 'final_confirmation_pending'].includes(order.orderStatus)
}

async function submitCurrentOrder(order) {
  const result = await submitOrder(order.orderNo, buildOperator())
  if (result.success) loadOrders()
}

async function cancelCurrentOrder(order) {
  await ElMessageBox.confirm(`确认取消单据 ${order.orderNo} 吗？`, '取消单据', { type: 'warning' })
  const result = await cancelOrder(order.orderNo, buildOperator())
  if (result.success) loadOrders()
}

async function finalConfirmCurrentOrder(order) {
  await ElMessageBox.confirm(`确认完成单据 ${order.orderNo} 的最终确认吗？`, '最终确认', { type: 'warning' })
  const result = await finalConfirmOrder(order.orderNo, buildOperator())
  if (result.success) loadOrders()
}

loadOrders()
</script>

<style scoped>
.mist-input {
  width: 100%;
  min-height: 2.75rem;
  border-radius: 1rem;
  border: 1px solid rgb(226 232 240);
  background: rgba(255, 255, 255, 0.92);
  padding: 0.75rem 0.95rem;
  font-size: 0.95rem;
  color: rgb(15 23 42);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease;
}

.mist-input:focus {
  outline: none;
  border-color: rgb(148 163 184);
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.18);
  background: rgb(255 255 255);
}

.mist-input::placeholder {
  color: rgb(148 163 184);
}
</style>
