<template>
  <div class="animate-in fade-in space-y-10 pb-20 duration-500 text-foreground">
    <!-- Page Header Section -->
    <header class="relative overflow-hidden rounded-3xl bg-primary px-8 py-12 text-primary-foreground shadow-2xl">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <div class="mb-4 flex items-center gap-3">
            <Badge variant="outline" class="border-primary-foreground/20 bg-primary-foreground/10 text-[10px] uppercase tracking-widest text-primary-foreground backdrop-blur-sm">
              单据详情
            </Badge>
            <OrderStatusTag v-if="order.orderStatus" :status="order.orderStatus" class="border-primary-foreground/20" />
          </div>
          <h1 class="font-mono text-3xl font-bold tracking-tight text-primary-foreground md:text-4xl">
            {{ order.orderNo || orderNo }}
          </h1>
          <p class="mt-3 max-w-2xl text-sm leading-relaxed text-primary-foreground/80">
            实时查看单据上下文、工装明细状态、工作流追踪以及通知记录。
          </p>
        </div>
        <div v-debug-id="DEBUG_IDS.ORDER_DETAIL.ACTION_SECTION" class="flex flex-wrap items-center gap-3">
          <Button
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.BACK_TO_LIST_BTN"
            variant="ghost"
            class="border border-primary-foreground/20 text-primary-foreground hover:bg-white/10"
            @click="goBack"
          >
            返回列表
          </Button>
          <Button
            v-if="canSubmit"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.SUBMIT_ORDER_BTN"
            class="bg-warning font-bold text-primary-foreground hover:bg-warning/90 border-none"
            @click="submitCurrentOrder"
          >
            提交单据
          </Button>
          <Button
            v-if="canResetToDraft"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.RESET_TO_DRAFT_BTN"
            class="bg-warning font-bold text-primary-foreground hover:bg-warning/90 border-none"
            @click="resetToDraftCurrentOrder"
          >
            重置为草稿
          </Button>
          <Button
            v-if="canCancel"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.CANCEL_ORDER_BTN"
            class="bg-destructive font-bold text-primary-foreground hover:bg-destructive/90 border-none"
            @click="cancelCurrentOrder"
          >
            取消单据
          </Button>
          <Button
            v-if="canFinalConfirm"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.FINAL_CONFIRM_BTN"
            class="bg-primary font-bold text-primary-foreground shadow-lg hover:bg-primary/90 border-none"
            @click="finalConfirmCurrentOrder"
          >
            最终确认
          </Button>
          <Button
            v-if="canDelete"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.DELETE_BTN"
            variant="destructive"
            class="bg-destructive font-bold text-primary-foreground shadow-lg hover:bg-destructive/90 border-none"
            @click="deleteCurrentOrder"
          >
            删除订单
          </Button>
          <Button
            v-if="canReportIssue"
            v-debug-id="DEBUG_IDS.ORDER_DETAIL.REPORT_ISSUE_BTN"
            variant="default"
            class="bg-warning font-bold text-primary-foreground shadow-lg hover:bg-warning/90 border-none"
            @click="reportIssueVisible = true"
          >
            <AlertTriangle class="mr-2 h-4 w-4" />
            上报异常
          </Button>
        </div>
      </div>

      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary-foreground/10 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/4 h-32 w-32 rounded-full bg-blue-500/10 blur-2xl"></div>
    </header>

    <div v-if="loading" class="space-y-10">
      <Card class="bg-card shadow-shimmer border-border/50">
        <CardContent class="grid gap-8 pt-8 md:grid-cols-2 xl:grid-cols-4">
          <div v-for="index in 8" :key="index" class="space-y-3">
            <div class="h-3 w-20 animate-pulse rounded-full bg-muted" />
            <div class="h-5 w-32 animate-pulse rounded-full bg-muted/50" />
          </div>
        </CardContent>
      </Card>
      <Card class="bg-card shadow-shimmer border-border/50">
        <CardContent class="space-y-6 pt-8">
          <div v-for="index in 3" :key="index" class="h-24 animate-pulse rounded-2xl bg-muted/30" />
        </CardContent>
      </Card>
    </div>

    <div
      v-else-if="errorMessage"
      class="rounded-3xl border border-destructive/20 bg-card/90 px-6 py-12 text-center shadow-xl"
    >
      <p class="text-xs font-medium uppercase tracking-[0.24em] text-destructive">请求失败</p>
      <h2 class="mt-3 text-2xl font-semibold text-foreground">单据详情加载失败</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{{ errorMessage }}</p>
      <div class="mt-6 flex justify-center gap-3">
        <Button v-debug-id="DEBUG_IDS.ORDER_DETAIL.BACK_BTN" variant="outline" @click="goBack">返回</Button>
        <Button v-debug-id="DEBUG_IDS.ORDER_DETAIL.ERROR_RETRY_BTN" @click="loadOrder">重试</Button>
      </div>
    </div>

    <div
      v-else-if="!hasOrder"
      class="rounded-3xl border border-border bg-card/90 px-6 py-12 text-center shadow-xl"
    >
      <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">缺少数据</p>
      <h2 class="mt-3 text-2xl font-semibold text-foreground">当前单据暂无详情</h2>
      <p class="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground">
        当前接口没有返回这张单据的详情。请检查路由参数，或返回单据列表重新进入。
      </p>
      <div class="mt-6 flex justify-center">
        <Button @click="goBack">返回列表</Button>
      </div>
    </div>

    <template v-else>
      <div class="grid gap-6 xl:grid-cols-[1.35fr_0.95fr]">
        <Card v-debug-id="DEBUG_IDS.ORDER_DETAIL.INFO_PANEL" class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">概览</p>
              <CardTitle class="text-lg text-foreground">单据信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="grid gap-4 pt-6 md:grid-cols-2 xl:grid-cols-3">
            <div v-for="field in overviewFields" :key="field.label" class="space-y-1">
              <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">{{ field.label }}</p>
              <p class="text-sm font-medium leading-6 text-foreground/80">{{ field.value }}</p>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">流程</p>
              <CardTitle class="text-lg text-foreground">进度跟踪</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="space-y-4 pt-6">
            <WorkflowStepper
              :current-status="order.orderStatus"
              :order-type="order.orderType"
              :show-header="false"
              :custom-labels="workflowCustomLabels"
            />
          </CardContent>
        </Card>
      </div>

      <Card v-debug-id="DEBUG_IDS.ORDER_DETAIL.TOOL_LIST_PANEL" class="border-border bg-card shadow-xl">
        <CardHeader class="border-b border-border">
          <div class="space-y-1">
            <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">工装</p>
            <CardTitle class="text-lg text-foreground">工装明细</CardTitle>
          </div>
        </CardHeader>
        <CardContent class="pt-0">
          <div v-if="order.items?.length" class="divide-y divide-border">
            <article
              v-for="(item, index) in order.items"
              :key="item.toolCode || item.toolId || index"
              class="grid gap-4 px-6 py-5 lg:grid-cols-[1.6fr_0.9fr_0.9fr_0.9fr_0.9fr_0.9fr]"
            >
              <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-sm font-semibold text-foreground">{{ item.toolCode || item.toolId || '-' }}</p>
                  <OrderStatusTag v-if="item.itemStatus" :status="item.itemStatus" item />
                </div>
                <p class="text-sm text-muted-foreground">{{ item.toolName || '-' }}</p>
                <div class="flex flex-wrap gap-2 text-xs text-muted-foreground/60">
                  <span class="rounded-full bg-muted px-2.5 py-1">Drawing {{ item.drawingNo || '-' }}</span>
                  <span class="rounded-full bg-muted px-2.5 py-1">Spec {{ item.specModel || '-' }}</span>
                </div>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">申请数量</p>
                <p class="text-sm font-medium text-foreground/80">{{ item.applyQty ?? '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">分体数量</p>
                <p class="text-sm font-medium text-foreground/80">{{ item.split_quantity ?? '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">当前位置</p>
                <p class="text-sm font-medium text-foreground/80">{{ item.currentLocationText || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">确认位置</p>
                <p class="text-sm font-medium text-foreground/80">{{ item.keeperConfirmLocationText || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">检查结果</p>
                <p class="text-sm font-medium text-foreground/80">{{ item.checkResult || '-' }}</p>
              </div>
            </article>
          </div>
          <div
            v-else
            class="flex min-h-44 items-center justify-center px-6 py-10 text-center text-sm text-muted-foreground"
          >
            当前单据暂无工装明细。
          </div>
        </CardContent>
      </Card>

      <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card v-debug-id="DEBUG_IDS.ORDER_DETAIL.LOG_TIMELINE" class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">审计跟踪</p>
              <CardTitle class="text-lg text-foreground">操作日志</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <LogTimeline :logs="logs" />
          </CardContent>
        </Card>

        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">通知</p>
              <CardTitle class="text-lg text-foreground">通知记录</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <div v-if="order.notificationRecords?.length" class="space-y-3">
              <article
                v-for="(record, index) in order.notificationRecords"
                :key="`${record.notifyType}-${record.sendTime}-${index}`"
                class="rounded-2xl border border-border bg-muted/30 p-4 shadow-sm"
              >
                <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-foreground">
                      {{ record.title || record.notifyType || '通知记录' }}
                    </p>
                    <p class="text-sm text-muted-foreground">
                      {{ record.receiver || '-' }} · {{ record.notifyChannel || '-' }}
                    </p>
                  </div>
                  <p class="text-xs text-muted-foreground/60">{{ formatDateTime(record.sendTime) }}</p>
                </div>
                <div class="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground/60">
                  <span class="rounded-full bg-muted/50 px-2.5 py-1 border border-border/50">类型 {{ record.notifyType || '-' }}</span>
                  <span class="rounded-full bg-muted/50 px-2.5 py-1 border border-border/50">状态 {{ record.sendStatus || '-' }}</span>
                </div>
                <p class="mt-3 text-sm leading-6 text-foreground/70">{{ record.sendResult || record.content || '-' }}</p>
              </article>
            </div>
            <div
              v-else
              class="flex min-h-40 items-center justify-center rounded-2xl border border-dashed border-border bg-muted/20 px-6 py-10 text-center text-sm text-muted-foreground"
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
            class="absolute bottom-4 right-4 z-10 shadow-lg border-none"
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
            class="absolute bottom-4 right-4 z-10 shadow-lg border-none"
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

      <!-- Transport Issues Panel -->
      <Card v-if="issues.length || canReportIssue" class="border-border bg-card shadow-xl overflow-hidden">
        <CardHeader class="border-b border-border bg-muted/20">
          <div class="flex items-center justify-between">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">反馈</p>
              <CardTitle class="text-lg text-foreground flex items-center gap-2">
                <AlertTriangle class="h-5 w-5 text-amber-500" />
                运输异常记录
              </CardTitle>
            </div>
            <Badge v-if="issues.length" variant="outline" class="bg-amber-500/10 text-amber-500 border-amber-500/20">
              {{ issues.length }} 个异常
            </Badge>
          </div>
        </CardHeader>
        <CardContent class="p-0">
          <div v-if="issues.length" class="divide-y divide-border">
            <div v-for="issue in issues" :key="issue.id" class="p-6 transition-colors hover:bg-muted/10">
              <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div class="space-y-3 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <el-tag :type="issue.status === 'resolved' ? 'success' : 'danger'" size="small" effect="dark">
                      {{ issue.status === 'resolved' ? '已处理' : '待处理' }}
                    </el-tag>
                    <Badge variant="secondary" class="bg-amber-500/10 text-amber-500 border-amber-500/20">
                      {{ issue.issue_type }}
                    </Badge>
                    <span class="text-xs text-muted-foreground">
                      {{ issue.reporter_name }} 上报于 {{ issue.report_time }}
                    </span>
                  </div>
                  <p class="text-sm text-foreground/90 leading-relaxed">{{ issue.description }}</p>
                  
                  <!-- Resolution -->
                  <div v-if="issue.status === 'resolved'" class="mt-4 p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/10">
                    <div class="flex items-center gap-2 mb-2 text-emerald-500">
                      <CheckCircle class="h-4 w-4" />
                      <span class="text-xs font-bold uppercase tracking-wider">处理回复</span>
                      <span class="text-[10px] opacity-60">
                        {{ issue.resolver_name }} · {{ issue.resolve_time }}
                      </span>
                    </div>
                    <p class="text-sm text-foreground/80 italic">{{ issue.resolution }}</p>
                  </div>
                </div>
                
                <div v-if="canManageIssues && issue.status === 'pending'" class="shrink-0">
                  <Button size="sm" class="bg-primary hover:bg-primary/90 text-primary-foreground border-none" @click="handleResolveIssue(issue)">
                    处理异常
                  </Button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <div class="h-12 w-12 rounded-full bg-muted/50 flex items-center justify-center mb-4">
              <CheckCircle class="h-6 w-6 text-emerald-500/50" />
            </div>
            <p class="text-sm">当前暂无运输异常记录</p>
          </div>
        </CardContent>
      </Card>
    </template>

    <!-- Dialogs -->
    <ReportTransportIssueDialog
      v-model="reportIssueVisible"
      :order-no="orderNo"
      @success="loadOrder"
    />
    
    <ResolveIssueDialog
      v-model="resolveIssueVisible"
      :order-no="orderNo"
      :issue="selectedIssue"
      @success="loadOrder"
    />
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
  submitOrder,
  deleteOrder,
  getTransportIssues,
  resetOrderToDraft
} from '@/api/orders'
import LogTimeline from '@/components/tool-io/LogTimeline.vue'
import NotificationPreview from '@/components/tool-io/NotificationPreview.vue'
import OrderStatusTag from '@/components/tool-io/OrderStatusTag.vue'
import ReportTransportIssueDialog from '@/components/tool-io/ReportTransportIssueDialog.vue'
import ResolveIssueDialog from '@/components/tool-io/ResolveIssueDialog.vue'
import WorkflowStepper from '@/components/workflow/WorkflowStepper.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import { Send, AlertTriangle, CheckCircle2 as CheckCircle } from 'lucide-vue-next'
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

// Transport Exception Reporting State
const reportIssueVisible = ref(false)
const resolveIssueVisible = ref(false)
const issues = ref([])
const selectedIssue = ref(null)

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

const workflowCustomLabels = computed(() => ({
  partially_confirmed: {
    keeper_confirmed: {
      label: '部分确认',
      description: '当前只有部分申请工装完成了确认。'
    }
  },
  transport_notified: {
    transport_in_progress: {
      label: '待运输',
      description: '运输已指派或已通知，等待开始执行。'
    }
  }
}))

const canSubmit = computed(() => session.hasPermission('order:submit') && order.value.orderStatus === 'draft')
const canCancel = computed(
  () => session.hasPermission('order:cancel') && ['draft', 'rejected'].includes(order.value.orderStatus)
)
const canFinalConfirm = computed(() => {
  return Boolean(finalConfirmState.value.available)
})
const canDelete = computed(() => {
  return session.isAdmin() || session.hasPermission('order:delete')
})
const canNotifyKeeper = computed(() => {
  return ['submitted', 'keeper_confirmed'].includes(order.value.orderStatus)
})
const canNotifyTransport = computed(() => {
  return ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'transport_in_progress'].includes(order.value.orderStatus)
})

const canReportIssue = computed(() => {
  const isPrep = session.role === 'transport_operator' || session.permissions.includes('order:transport_execute')
  const validStatus = ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'transport_in_progress'].includes(order.value.orderStatus)
  return isPrep && validStatus
})

const canManageIssues = computed(() => {
  return session.role === 'keeper' || session.permissions.includes('order:keeper_confirm')
})

const canResetToDraft = computed(() => {
  return session.hasPermission('order:submit') && order.value.orderStatus === 'rejected'
})

function orderTypeLabel(orderType) {
  return orderType === 'outbound' ? '出库' : orderType === 'inbound' ? '入库' : '-'
}

function canGenerateTransportPreview(currentOrder) {
  if (!currentOrder?.orderNo) return false
  return (currentOrder.approvedCount || 0) > 0
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
    const [detailResult, logResult, notificationResult, issueResult] = await Promise.all([
      getOrderDetail(props.orderNo),
      getOrderLogs(props.orderNo),
      getNotificationRecords(props.orderNo),
      getTransportIssues(props.orderNo).catch(() => ({ success: false, data: [] }))
    ])

    order.value = detailResult.success
      ? detailResult.data
      : {
          items: [],
          notificationRecords: []
        }
    logs.value = logResult.success ? logResult.data : []
    issues.value = issueResult.success ? issueResult.data : []
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
  await ElMessageBox.confirm(
    `确认提交单据 ${props.orderNo} 吗？提交后将进入保管员审核流程。`,
    '提交单据',
    {
      confirmButtonText: '提交',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  const result = await submitOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}

async function cancelCurrentOrder() {
  await ElMessageBox.confirm(`确认取消单据 ${props.orderNo} 吗？`, '取消单据', { type: 'warning' })
  const result = await cancelOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}

async function resetToDraftCurrentOrder() {
  await ElMessageBox.confirm(
    `确认将单据 ${props.orderNo} 重置为草稿吗？重置后可重新编辑并提交。`,
    '重置为草稿',
    { confirmButtonText: '重置', cancelButtonText: '取消', type: 'warning' }
  )
  const result = await resetOrderToDraft(props.orderNo, operatorPayload())
  if (result.success) {
    ElMessage.success('单据已重置为草稿')
    loadOrder()
  } else {
    ElMessage.error(result.error || '重置失败')
  }
}

async function finalConfirmCurrentOrder() {
  await ElMessageBox.confirm(`确认完成单据 ${props.orderNo} 的最终确认吗？`, '最终确认', { type: 'warning' })
  const result = await finalConfirmOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}

async function deleteCurrentOrder() {
  try {
    await ElMessageBox.confirm(
      `确认删除单据 ${props.orderNo} 吗？删除后不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'bg-destructive border-destructive hover:bg-destructive/90'
      }
    )
    
    loading.value = true
    const result = await deleteOrder(props.orderNo, operatorPayload())
    if (result.success) {
      ElMessage.success('订单已成功删除')
      router.push('/inventory')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('操作异常')
    }
  } finally {
    loading.value = false
  }
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

function handleResolveIssue(issue) {
  selectedIssue.value = issue
  resolveIssueVisible.value = true
}

loadOrder()
</script>
