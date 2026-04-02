<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Badge variant="outline" class="badge-outline uppercase tracking-widest text-[10px]">
              任务详情
            </Badge>
            <span :class="['status-badge', getStatusClass(task.status)]">
              {{ getStatusLabel(task.status) }}
            </span>
          </div>
          <h1 class="page-header-title">{{ task.tool_name || '任务加载中...' }}</h1>
          <p class="page-header-desc">
            任务编号：{{ taskNo }} | 序列号：{{ task.serial_no }}
          </p>
        </div>
        <div class="page-header-actions">
          <Button variant="ghost" class="btn-ghost" @click="goBack">
            返回列表
          </Button>
          
          <!-- 动态操作按钮 -->
          <template v-if="task.status === 'pending'">
            <Button class="btn-primary" @click="handleReceive">
              领取任务
            </Button>
          </template>

          <template v-if="task.status === 'received'">
            <Button variant="outline" class="btn-ghost" @click="handleCreateOutbound">
              创建出库单
            </Button>
            <Button class="btn-primary" @click="handleStartInspection">
              开始检验
            </Button>
          </template>

          <template v-if="task.status === 'in_progress'">
            <Button class="btn-primary" @click="showReportDialog = true">
              提交测量报告
            </Button>
          </template>

          <template v-if="task.status === 'report_submitted' && canAudit">
            <Button variant="outline" class="btn-ghost" @click="handleRejectReport">
              驳回报告
            </Button>
            <Button class="btn-primary" @click="handleAcceptReport">
              验收通过
            </Button>
          </template>

          <template v-if="task.status === 'accepted'">
            <Button class="btn-primary" @click="handleCreateInbound">
              创建入库单
            </Button>
          </template>

          <template v-if="task.status === 'inbound_completed' && canClose">
            <Button class="btn-primary" @click="handleCloseTask">
              关闭任务
            </Button>
          </template>
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <div class="lg:col-span-2 space-y-8">
        <!-- 工作流进度 -->
        <Card class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <div class="card-header-accent bg-blue-500" />
              <CardTitle class="card-title">作业进度</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6">
            <WorkflowStepper
              :current-status="task.status"
              workflow-type="inspection"
              :show-header="false"
            />
          </CardContent>
        </Card>

        <!-- 基本信息 -->
        <Card class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <div class="card-header-accent" />
              <CardTitle class="card-title">基本信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">工装图号</p>
              <p class="text-sm font-semibold">{{ task.drawing_no || '-' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">关联计划</p>
              <p class="text-sm font-semibold">{{ task.plan_name || '-' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">截止时间</p>
              <p class="text-sm font-semibold">{{ formatDateTime(task.due_date) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">执行人</p>
              <p class="text-sm font-semibold">{{ task.executor_name || '待领取' }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">领取时间</p>
              <p class="text-sm font-semibold">{{ formatDateTime(task.received_at) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">最后更新</p>
              <p class="text-sm font-semibold">{{ formatDateTime(task.updated_at) }}</p>
            </div>
          </CardContent>
        </Card>

        <!-- 关联单据 -->
        <Card class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <div class="card-header-accent bg-emerald-500" />
              <CardTitle class="card-title">关联流转单据</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <el-table :data="linkedOrders" stripe class="w-full" header-cell-class-name="table-header">
              <el-table-column prop="order_no" label="单据编号" min-width="140" />
              <el-table-column prop="order_type" label="类型" min-width="100">
                <template #default="{ row }">
                  {{ row.order_type === 'outbound' ? '出库' : '入库' }}
                </template>
              </el-table-column>
              <el-table-column prop="order_status" label="状态" min-width="120" />
              <el-table-column prop="created_at" label="创建时间" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" min-width="100" fixed="right">
                <template #default="{ row }">
                  <router-link :to="`/inventory/${row.order_no}`">
                    <el-button link type="primary">查看详情</el-button>
                  </router-link>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="!linkedOrders.length" class="empty-state">
              <h3 class="empty-state-title">暂无关联单据</h3>
              <p class="empty-state-desc">在作业过程中发起的出入库申请将显示在此处。</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="space-y-6">
        <!-- 测量报告摘要 -->
        <Card v-if="task.report_id" class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <CardTitle class="card-title">测量报告</CardTitle>
          </CardHeader>
          <CardContent class="p-6 space-y-4">
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">检验结论</p>
              <p :class="['text-sm font-bold', task.inspection_result === 'pass' ? 'text-green-500' : 'text-red-500']">
                {{ task.inspection_result === 'pass' ? '合格' : '不合格' }}
              </p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">检验日期</p>
              <p class="text-sm font-semibold">{{ formatDateTime(task.inspection_date) }}</p>
            </div>
            <div v-if="task.attachment_path" class="space-y-2 pt-2">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">报告附件</p>
              <!-- 简单的附件链接，后续可优化为预览 -->
              <el-button link type="primary" size="small">查看原始附件</el-button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- 报告提交对话框 -->
    <ReportSubmit
      v-if="showReportDialog"
      :task-no="taskNo"
      @close="showReportDialog = false"
      @success="handleReportSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getTaskDetail, receiveTask, startInspection, 
  acceptReport, rejectReport, closeTask, getLinkedOrders 
} from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import WorkflowStepper from '@/components/inspection/WorkflowStepper.vue'
import ReportSubmit from './ReportSubmit.vue'

const props = defineProps({
  taskNo: {
    type: String,
    required: true
  }
})

const router = useRouter()
const session = useSessionStore()
const task = ref({})
const linkedOrders = ref([])
const loading = ref(false)
const showReportDialog = ref(false)

const canAudit = computed(() => session.hasPermission('inspection:audit'))
const canClose = computed(() => session.hasPermission('order:keeper_confirm'))

async function loadDetail() {
  loading.value = true
  try {
    const res = await getTaskDetail(props.taskNo)
    if (res.success) {
      task.value = res.data
      await loadLinkedOrders()
    }
  } catch (err) {
    console.error('加载任务详情失败:', err)
    ElMessage.error('加载任务详情失败')
  } finally {
    loading.value = false
  }
}

async function loadLinkedOrders() {
  try {
    const res = await getLinkedOrders(props.taskNo)
    if (res.success) {
      linkedOrders.value = res.data || []
    }
  } catch (err) {
    console.error('加载关联单据失败:', err)
  }
}

async function handleReceive() {
  try {
    const res = await receiveTask(props.taskNo)
    if (res.success) {
      ElMessage.success('已领取任务')
      loadDetail()
    }
  } catch (err) {
    console.error('领取任务失败:', err)
  }
}

async function handleStartInspection() {
  try {
    const res = await startInspection(props.taskNo)
    if (res.success) {
      ElMessage.success('已开始定检作业')
      loadDetail()
    }
  } catch (err) {
    console.error('开始定检失败:', err)
  }
}

function handleCreateOutbound() {
  router.push({
    path: '/inventory/create',
    query: { task_no: props.taskNo, type: 'outbound', serial_no: task.value.serial_no }
  })
}

function handleCreateInbound() {
  router.push({
    path: '/inventory/create',
    query: { task_no: props.taskNo, type: 'inbound', serial_no: task.value.serial_no }
  })
}

async function handleAcceptReport() {
  try {
    await ElMessageBox.confirm('确认定检结果合格并验收通过吗？', '验收确认')
    const res = await acceptReport(props.taskNo)
    if (res.success) {
      ElMessage.success('验收已通过')
      loadDetail()
    }
  } catch (err) {
    if (err !== 'cancel') console.error('验收失败:', err)
  }
}

async function handleRejectReport() {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入驳回原因', '报告驳回', {
      inputPattern: /\S+/,
      inputErrorMessage: '原因不能为空'
    })
    const res = await rejectReport(props.taskNo, { reason })
    if (res.success) {
      ElMessage.warning('报告已驳回')
      loadDetail()
    }
  } catch (err) {
    if (err !== 'cancel') console.error('驳回失败:', err)
  }
}

async function handleCloseTask() {
  try {
    await ElMessageBox.confirm('确认定检全流程已结束并关闭任务吗？', '关闭确认')
    const res = await closeTask(props.taskNo)
    if (res.success) {
      ElMessage.success('任务已关闭')
      loadDetail()
    }
  } catch (err) {
    if (err !== 'cancel') console.error('关闭失败:', err)
  }
}

function handleReportSuccess() {
  showReportDialog.value = false
  loadDetail()
}

function getStatusLabel(status) {
  const map = {
    pending: '待领取',
    received: '已接收',
    outbound_created: '出库中',
    outbound_completed: '出库完成',
    in_progress: '定检中',
    report_submitted: '待验收',
    accepted: '已验收',
    rejected: '已驳回',
    inbound_created: '入库中',
    inbound_completed: '入库完成',
    closed: '已关闭'
  }
  return map[status] || status
}

function getStatusClass(status) {
  const map = {
    pending: 'status-pending',
    closed: 'status-completed',
    rejected: 'status-overdue'
  }
  return map[status] || 'status-active'
}

function formatDateTime(val) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

function goBack() {
  router.push('/inspection/tasks')
}

onMounted(() => {
  loadDetail()
})
</script>
