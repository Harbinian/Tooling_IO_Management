<template>
  <div class="space-y-10 animate-in fade-in duration-500 pb-20">
    <!-- Page Header Section -->
    <header class="relative overflow-hidden rounded-3xl bg-slate-900 px-8 py-12 text-white shadow-2xl">
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Badge variant="outline" class="border-slate-700 text-slate-400 bg-slate-800/50 backdrop-blur-sm uppercase tracking-widest text-[10px]">
              单据详情
            </Badge>
            <OrderStatusTag v-if="order.orderStatus" :status="order.orderStatus" class="border-slate-700" />
          </div>
          <h1 class="text-3xl font-bold tracking-tight md:text-4xl font-mono">
            {{ order.orderNo || orderNo }}
          </h1>
          <p class="mt-3 text-slate-400 max-w-2xl text-sm leading-relaxed">
            实时查看单据上下文、工装明细状态、工作流追踪以及通知记录。
          </p>
        </div>
        <div v-debug-id="DEBUG_IDS.ORDER_DETAIL.ACTION_SECTION" class="flex flex-wrap items-center gap-3">
          <Button variant="outline" class="border-slate-700 text-white hover:bg-slate-800" @click="goBack">
            返回列表
          </Button>
          <Button v-if="canSubmit" class="bg-amber-500 text-slate-950 hover:bg-amber-400 font-bold" @click="submitCurrentOrder">
            提交单据
          </Button>
          <Button v-if="canCancel" class="bg-rose-500 text-white hover:bg-rose-400 font-bold" @click="cancelCurrentOrder">
            取消单据
          </Button>
          <Button
            v-if="canFinalConfirm"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.FINAL_CONFIRM_BTN"
            class="bg-emerald-500 text-slate-950 hover:bg-emerald-400 font-bold shadow-lg"
            @click="finalConfirmCurrentOrder"
          >
            最终确认
          </Button>
        </div>
      </div>

      
      <!-- Abstract background elements -->
      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl"></div>
      <div class="absolute left-1/4 bottom-0 h-32 w-32 rounded-full bg-blue-500/10 blur-2xl"></div>
    </header>

    <div v-if="loading" class="space-y-10">
      <Card class="bg-white shadow-shimmer">
        <CardContent class="grid gap-8 pt-8 md:grid-cols-2 xl:grid-cols-4">
          <div v-for="index in 8" :key="index" class="space-y-3">
            <div class="h-3 w-20 animate-pulse rounded-full bg-slate-100" />
            <div class="h-5 w-32 animate-pulse rounded-full bg-slate-200/60" />
          </div>
        </CardContent>
      </Card>
      <Card class="bg-white shadow-shimmer">
        <CardContent class="space-y-6 pt-8">
          <div v-for="index in 3" :key="index" class="h-24 animate-pulse rounded-2xl bg-slate-50" />
        </CardContent>
      </Card>
    </div>

    <div
      v-else-if="errorMessage"
      class="rounded-3xl border border-rose-200 bg-white/90 px-6 py-12 text-center shadow-[0_24px_70px_-50px_rgba(244,63,94,0.4)]"
    >
      <p class="text-xs font-medium uppercase tracking-[0.24em] text-rose-500">请求失败</p>
      <h2 class="mt-3 text-2xl font-semibold text-slate-900">单据详情加载失败</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500">{{ errorMessage }}</p>
      <div class="mt-6 flex justify-center gap-3">
        <Button variant="outline" @click="goBack">返回</Button>
        <Button @click="loadOrder">重试</Button>
      </div>
    </div>

    <div
      v-else-if="!hasOrder"
      class="rounded-3xl border border-slate-200 bg-white/90 px-6 py-12 text-center shadow-[0_24px_70px_-55px_rgba(15,23,42,0.35)]"
    >
      <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">缺少数据</p>
      <h2 class="mt-3 text-2xl font-semibold text-slate-900">当前单据暂无详情</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500">
        当前接口没有返回这张单据的详情。请检查路由参数，或返回单据列表重新进入。
      </p>
      <div class="mt-6 flex justify-center">
        <Button @click="goBack">返回列表</Button>
      </div>
    </div>

    <template v-else>
      <div class="grid gap-6 xl:grid-cols-[1.35fr_0.95fr]">
        <Card v-debug-id="DEBUG_IDS.ORDER_DETAIL.INFO_PANEL" class="border-slate-200/80 bg-white/90 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.4)]">
          <CardHeader class="border-b border-slate-100">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">概览</p>
              <CardTitle class="text-lg text-slate-900">单据信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="grid gap-4 pt-6 md:grid-cols-2 xl:grid-cols-3">
            <div v-for="field in overviewFields" :key="field.label" class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">{{ field.label }}</p>
              <p class="text-sm font-medium leading-6 text-slate-800">{{ field.value }}</p>
            </div>
          </CardContent>
        </Card>


        <Card class="border-slate-200/80 bg-white/90 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.4)]">
          <CardHeader class="border-b border-slate-100">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">流程</p>
              <CardTitle class="text-lg text-slate-900">进度跟踪</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="space-y-4 pt-6">
            <div
              v-for="step in workflowSteps"
              :key="step.key"
              class="flex items-start gap-4 rounded-2xl border px-4 py-4"
              :class="stepClass(step.state)"
            >
              <div
                class="mt-0.5 flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold"
                :class="stepDotClass(step.state)"
              >
                {{ step.index }}
              </div>
              <div class="space-y-1">
                <p class="text-sm font-semibold text-slate-900">{{ step.label }}</p>
                <p class="text-sm leading-6 text-slate-500">{{ step.description }}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card v-debug-id="DEBUG_IDS.ORDER_DETAIL.TOOL_LIST_PANEL" class="border-slate-200/80 bg-white/90 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.4)]">
        <CardHeader class="border-b border-slate-100">
          <div class="space-y-1">
            <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">工装</p>
            <CardTitle class="text-lg text-slate-900">工装明细</CardTitle>
          </div>
        </CardHeader>
        <CardContent class="pt-0">
          <div v-if="order.items?.length" class="divide-y divide-slate-100">
            <article
              v-for="(item, index) in order.items"
              :key="item.toolCode || item.toolId || index"
              class="grid gap-4 px-6 py-5 lg:grid-cols-[1.6fr_0.9fr_0.9fr_0.9fr_0.9fr_0.9fr]"
            >
              <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-sm font-semibold text-slate-900">{{ item.toolCode || item.toolId || '-' }}</p>
                  <OrderStatusTag v-if="item.itemStatus" :status="item.itemStatus" item />
                </div>
                <p class="text-sm text-slate-600">{{ item.toolName || '-' }}</p>
                <div class="flex flex-wrap gap-2 text-xs text-slate-500">
                  <span class="rounded-full bg-slate-100 px-2.5 py-1">Drawing {{ item.drawingNo || '-' }}</span>
                  <span class="rounded-full bg-slate-100 px-2.5 py-1">Spec {{ item.specModel || '-' }}</span>
                </div>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">申请数量</p>
                <p class="text-sm font-medium text-slate-700">{{ item.applyQty ?? '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">确认数量</p>
                <p class="text-sm font-medium text-slate-700">{{ item.approvedQty ?? '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">当前位置</p>
                <p class="text-sm font-medium text-slate-700">{{ item.currentLocationText || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">确认位置</p>
                <p class="text-sm font-medium text-slate-700">{{ item.keeperConfirmLocationText || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">检查结果</p>
                <p class="text-sm font-medium text-slate-700">{{ item.checkResult || '-' }}</p>
              </div>
            </article>
          </div>
          <div
            v-else
            class="flex min-h-44 items-center justify-center px-6 py-10 text-center text-sm text-slate-500"
          >
            当前单据暂无工装明细。
          </div>
        </CardContent>
      </Card>

      <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card v-debug-id="DEBUG_IDS.ORDER_DETAIL.LOG_TIMELINE" class="border-slate-200/80 bg-white/90 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.4)]">

          <CardHeader class="border-b border-slate-100">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">Audit trail</p>
              <CardTitle class="text-lg text-slate-900">Operation logs</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <LogTimeline :logs="logs" />
          </CardContent>
        </Card>

        <Card class="border-slate-200/80 bg-white/90 shadow-[0_30px_80px_-55px_rgba(15,23,42,0.4)]">
          <CardHeader class="border-b border-slate-100">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">通知</p>
              <CardTitle class="text-lg text-slate-900">通知记录</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <div v-if="order.notificationRecords?.length" class="space-y-3">
              <article
                v-for="(record, index) in order.notificationRecords"
                :key="`${record.notifyType}-${record.sendTime}-${index}`"
                class="rounded-2xl border border-slate-200 bg-white/80 p-4"
              >
                <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-slate-900">
                      {{ record.title || record.notifyType || '通知记录' }}
                    </p>
                    <p class="text-sm text-slate-600">
                      {{ record.receiver || '-' }} 路 {{ record.notifyChannel || '-' }}
                    </p>
                  </div>
                  <p class="text-xs text-slate-500">{{ formatDateTime(record.sendTime) }}</p>
                </div>
                <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                  <span class="rounded-full bg-slate-100 px-2.5 py-1">类型 {{ record.notifyType || '-' }}</span>
                  <span class="rounded-full bg-slate-100 px-2.5 py-1">状态 {{ record.sendStatus || '-' }}</span>
                </div>
                <p class="mt-3 text-sm leading-6 text-slate-600">{{ record.sendResult || record.content || '-' }}</p>
              </article>
            </div>
            <div
              v-else
              class="flex min-h-40 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 px-6 py-10 text-center text-sm text-slate-500"
            >
              当前单据还没有通知记录。
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="grid gap-6 xl:grid-cols-3">
        <div class="relative">
          <NotificationPreview
            type="keeper"
            :content="keeperText"
            empty-text="暂无保管员通知预览"
          />
          <Button
            v-if="keeperText && canNotifyKeeper"
            size="sm"
            class="absolute bottom-4 right-4 z-10"
            :disabled="loading"
            @click="sendKeeperNotification"
          >
            <Send class="mr-1 h-3 w-3" />
            发送飞书
          </Button>
        </div>
        <div class="relative">
          <NotificationPreview
            type="transport"
            :content="transportText"
            empty-text="暂无运输通知预览"
          />
          <Button
            v-if="transportText && canNotifyTransport"
            size="sm"
            class="absolute bottom-4 right-4 z-10"
            :disabled="loading"
            @click="sendTransportNotification"
          >
            <Send class="mr-1 h-3 w-3" />
            发送飞书
          </Button>
        </div>
        <NotificationPreview
          type="wechat"
          :content="wechatText"
          empty-text="暂无复制文本"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  cancelOrder,
  finalConfirmOrder,
  getFinalConfirmAvailability,
  getNotificationRecords,
  generateKeeperText,
  generateTransportText,
  getOrderDetail,
  getOrderLogs,
  notifyKeeper,
  notifyTransport,
  submitOrder
} from '@/api/orders'
import LogTimeline from '@/components/tool-io/LogTimeline.vue'
import NotificationPreview from '@/components/tool-io/NotificationPreview.vue'
import OrderStatusTag from '@/components/tool-io/OrderStatusTag.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import { Send } from 'lucide-vue-next'
import { formatDateTime } from '@/utils/toolIO'
import { useSessionStore } from '@/store/session'
import { DEBUG_IDS } from '@/debug/debugIds'

const props = defineProps({

  orderNo: {
    type: String,
    required: true
  }
})

const router = useRouter()
const session = useSessionStore()

const loading = ref(false)
const errorMessage = ref('')
const finalConfirmState = ref({ available: false, reason: '', expected_role: '' })
const order = ref({
  items: [],
  notificationRecords: []
})
const logs = ref([])
const keeperText = ref('')
const transportText = ref('')
const wechatText = ref('')

const hasOrder = computed(() => Boolean(order.value?.orderNo))

const overviewFields = computed(() => [
  { label: '单据类型', value: orderTypeLabel(order.value.orderType) },
  { label: '发起人', value: order.value.initiatorName || '-' },
  { label: '保管员', value: order.value.keeperName || '-' },
  { label: '项目代号', value: order.value.projectCode || '-' },
  { label: '用途', value: order.value.usagePurpose || '-' },
  { label: '目标位置', value: order.value.targetLocationText || '-' },
  { label: '创建时间', value: formatDateTime(order.value.createdAt) },
  { label: '运输类型', value: order.value.transportType || '-' },
  { label: '工装数量', value: order.value.toolCount ?? 0 },
  { label: '已确认数量', value: order.value.approvedCount ?? 0 },
  { label: '部门', value: order.value.department || '-' },
  { label: '备注', value: order.value.remark || '-' }
])

const workflowOrder = ['draft', 'submitted', 'keeper_confirmed', 'transport_in_progress', 'transport_completed', 'completed']

const workflowSteps = computed(() => {
  const activeStatus = order.value.orderStatus
  const activeIndex = workflowOrder.indexOf(activeStatus)
  const partialIndex = workflowOrder.indexOf('keeper_confirmed')

  return [
    {
      key: 'draft',
      index: '01',
      label: '草稿',
      description: '发起人已填写申请，但还未正式提交流程。',
      state: stepState(activeIndex, 0, activeStatus)
    },
    {
      key: 'submitted',
      index: '02',
      label: '已提交',
      description: '单据已进入保管员审核阶段。',
      state: stepState(activeIndex, 1, activeStatus)
    },
    {
      key: 'keeper_confirmed',
      index: '03',
      label: activeStatus === 'partially_confirmed' ? '部分确认' : '保管员已确认',
      description:
        activeStatus === 'partially_confirmed'
          ? '当前只有部分申请工装完成了确认。'
          : '保管员审核和数量确认已完成。',
      state:
        activeStatus === 'partially_confirmed'
          ? 'current'
          : stepState(activeIndex, partialIndex, activeStatus)
    },
    {
      key: 'transport_in_progress',
      index: '04',
      label: activeStatus === 'transport_notified' ? '待运输' : '运输中',
      description:
        activeStatus === 'transport_notified'
          ? '运输已指派或已通知，等待开始执行。'
          : '工装正在由运输人员执行转运。',
      state:
        activeStatus === 'transport_notified'
          ? 'current'
          : stepState(activeIndex, 3, activeStatus)
    },
    {
      key: 'transport_completed',
      index: '05',
      label: '运输已完成',
      description: '实物转运已结束，单据可以进入最终确认。',
      state:
        activeStatus === 'final_confirmation_pending'
          ? 'current'
          : stepState(activeIndex, 4, activeStatus)
    },
    {
      key: 'completed',
      index: '06',
      label: activeStatus === 'rejected' ? '已驳回' : activeStatus === 'cancelled' ? '已取消' : '已完成',
      description:
        activeStatus === 'rejected'
          ? '单据在流程处理中被驳回。'
          : activeStatus === 'cancelled'
            ? '单据在完成前被取消。'
            : '流程已到达最终完成状态。',
      state:
        activeStatus === 'completed'
          ? 'current'
          : ['rejected', 'cancelled'].includes(activeStatus)
            ? 'blocked'
            : stepState(activeIndex, 5, activeStatus)
    }
  ]
})

const canSubmit = computed(() => session.role === 'initiator' && order.value.orderStatus === 'draft')
const canCancel = computed(
  () => session.role === 'initiator' && ['draft', 'rejected'].includes(order.value.orderStatus)
)
const canFinalConfirm = computed(() => {
  return Boolean(finalConfirmState.value.available)
})
const canNotifyKeeper = computed(() => {
  return ['submitted', 'keeper_confirmed'].includes(order.value.orderStatus)
})
const canNotifyTransport = computed(() => {
  return ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'transport_in_progress'].includes(order.value.orderStatus)
})

function stepState(activeIndex, index, activeStatus) {
  if (['rejected', 'cancelled'].includes(activeStatus)) {
    return index < Math.max(activeIndex, 0) ? 'complete' : 'upcoming'
  }
  if (activeIndex === -1) return 'upcoming'
  if (index < activeIndex) return 'complete'
  if (index === activeIndex) return 'current'
  return 'upcoming'
}

function stepClass(state) {
  if (state === 'complete') return 'border-emerald-200 bg-emerald-50/60'
  if (state === 'current') return 'border-sky-200 bg-sky-50/70'
  if (state === 'blocked') return 'border-rose-200 bg-rose-50/70'
  return 'border-slate-200 bg-slate-50/80'
}

function stepDotClass(state) {
  if (state === 'complete') return 'bg-emerald-600 text-white'
  if (state === 'current') return 'bg-sky-600 text-white'
  if (state === 'blocked') return 'bg-rose-600 text-white'
  return 'bg-slate-200 text-slate-600'
}

function orderTypeLabel(orderType) {
  return orderType === 'outbound' ? '出库' : orderType === 'inbound' ? '入库' : '-'
}

function canGenerateTransportPreview(currentOrder) {
  if (!currentOrder?.orderNo) return false
  if ((currentOrder.approvedCount || 0) > 0) return true
  return ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'transport_in_progress'].includes(currentOrder.orderStatus)
}

function operatorPayload() {
  return {
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  }
}

async function loadOrder() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [detailResult, logResult, notificationResult] = await Promise.all([
      getOrderDetail(props.orderNo),
      getOrderLogs(props.orderNo),
      getNotificationRecords(props.orderNo)
    ])

    order.value = detailResult.success
      ? detailResult.data
      : {
          items: [],
          notificationRecords: []
        }
    logs.value = logResult.success ? logResult.data : []
    if (detailResult.success) {
      order.value.notificationRecords = notificationResult.success ? notificationResult.data : order.value.notificationRecords || []
    }

    if (!detailResult.success) {
      errorMessage.value = detailResult.error || '单据详情加载失败。'
      finalConfirmState.value = { available: false, reason: '', expected_role: '' }
      keeperText.value = ''
      transportText.value = ''
      wechatText.value = ''
      return
    }

    const availability = await getFinalConfirmAvailability(props.orderNo, {
      operator_id: session.userId,
      operator_role: session.role
    }).catch(() => ({ success: false, available: false }))
    finalConfirmState.value = availability.success
      ? availability
      : { available: false, reason: '', expected_role: '' }

    keeperText.value = ''
    transportText.value = ''
    wechatText.value = ''

    const keeperResult = await generateKeeperText(props.orderNo).catch(() => ({ success: false }))
    if (keeperResult.success) keeperText.value = keeperResult.text

    if (!canGenerateTransportPreview(order.value)) return

    const transportResult = await generateTransportText(props.orderNo).catch(() => ({ success: false }))
    if (transportResult.success) {
      transportText.value = transportResult.text
      wechatText.value = transportResult.wechat_text
    }
  } catch (error) {
    order.value = { items: [], notificationRecords: [] }
    logs.value = []
    finalConfirmState.value = { available: false, reason: '', expected_role: '' }
    keeperText.value = ''
    transportText.value = ''
    wechatText.value = ''
    errorMessage.value = error?.response?.data?.error || error?.message || '单据详情加载失败。'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/inventory')
}

async function submitCurrentOrder() {
  const result = await submitOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}

async function cancelCurrentOrder() {
  await ElMessageBox.confirm(`确认取消单据 ${props.orderNo} 吗？`, '取消单据', { type: 'warning' })
  const result = await cancelOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}

async function finalConfirmCurrentOrder() {
  await ElMessageBox.confirm(`确认完成单据 ${props.orderNo} 的最终确认吗？`, '最终确认', { type: 'warning' })
  const result = await finalConfirmOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}

async function sendKeeperNotification() {
  loading.value = true
  try {
    const result = await notifyKeeper(props.orderNo, operatorPayload())
    if (result.success) {
      ElMessage.success(result.send_status === 'sent' ? '保管员飞书通知已发送' : `发送失败：${result.send_result}`)
      loadOrder()
    } else {
      ElMessage.error(result.error || '发送通知失败')
    }
  } catch (e) {
    ElMessage.error('发送保管员通知失败')
  } finally {
    loading.value = false
  }
}

async function sendTransportNotification() {
  loading.value = true
  try {
    const result = await notifyTransport(props.orderNo, operatorPayload())
    if (result.success) {
      ElMessage.success(result.send_status === 'sent' ? '运输飞书通知已发送' : `发送失败：${result.send_result}`)
      loadOrder()
    } else {
      ElMessage.error(result.error || '发送通知失败')
    }
  } catch (e) {
    ElMessage.error('发送运输通知失败')
  } finally {
    loading.value = false
  }
}

loadOrder()
</script>

