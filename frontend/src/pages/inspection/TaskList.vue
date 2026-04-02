<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
            定检任务
          </Badge>
          <h1 class="page-header-title">定检作业队列</h1>
          <p class="page-header-desc">
            查看和处理分配给您的工装定检任务，跟踪从领用、出库到定检回库的全流程。
          </p>
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <div class="flex flex-col gap-6">
      <el-tabs v-model="filters.status" class="inspection-tabs" @tab-change="handleSearch">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="待领取" name="pending" />
        <el-tab-pane label="已接收" name="received" />
        <el-tab-pane label="定检中" name="in_progress" />
        <el-tab-pane label="报告已提交" name="report_submitted" />
        <el-tab-pane label="已验收" name="accepted" />
        <el-tab-pane label="已关闭" name="closed" />
      </el-tabs>

      <Card class="border-border bg-card shadow-xl overflow-hidden">
        <CardHeader class="card-header">
          <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
            <div class="card-header-inner">
              <div class="card-header-accent bg-blue-500" />
              <CardTitle class="card-title">任务列表</CardTitle>
            </div>
            <div class="flex items-center gap-2">
              <el-input
                v-model="filters.keyword"
                placeholder="搜索任务号/序列号/工装名称"
                class="!w-80"
                clearable
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <Search class="h-4 w-4 text-muted-foreground" />
                </template>
              </el-input>
              <Button variant="outline" size="sm" @click="handleSearch">
                查询
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-0">
          <el-table
            v-loading="loading"
            :data="tasks"
            stripe
            class="w-full"
            header-cell-class-name="table-header"
          >
            <el-table-column prop="task_no" label="任务编号" min-width="140" fixed />
            <el-table-column prop="plan_no" label="关联计划" min-width="180" show-overflow-tooltip />
            <el-table-column prop="serial_no" label="序列号" min-width="120" />
            <el-table-column prop="tool_name" label="工装名称" min-width="180" show-overflow-tooltip />
            <el-table-column label="状态" min-width="120">
              <template #default="{ row }">
                <span :class="['status-badge', getStatusClass(row.task_status)]">
                  {{ getStatusLabel(row.task_status) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="assigned_to_name" label="执行人" min-width="100" />
            <el-table-column prop="receive_time" label="领取时间" min-width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.receive_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="100" fixed="right">
              <template #default="{ row }">
                <router-link :to="`/inspection/tasks/${row.task_no}`">
                  <el-button link type="primary">查看详情</el-button>
                </router-link>
              </template>
            </el-table-column>
          </el-table>
          <div class="p-4 flex justify-end border-t border-border">
            <el-pagination
              v-model:current-page="pagination.page_no"
              v-model:page-size="pagination.page_size"
              :total="pagination.total"
              layout="total, prev, pager, next"
              @current-change="loadTasks"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from 'lucide-vue-next'
import { getTaskList } from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const session = useSessionStore()
const loading = ref(false)
const tasks = ref([])
const filters = ref({
  keyword: '',
  status: ''
})
const pagination = ref({
  page_no: 1,
  page_size: 10,
  total: 0
})

async function loadTasks() {
  loading.value = true
  try {
    const res = await getTaskList({
      ...filters.value,
      page_no: pagination.value.page_no,
      page_size: pagination.value.page_size,
      org_id: session.orgId
    })
    if (res.success) {
      tasks.value = res.data
      pagination.value.total = res.total || 0
    }
  } catch (err) {
    console.error('加载任务列表失败:', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.value.page_no = 1
  loadTasks()
}

function getStatusLabel(status) {
  const map = {
    pending: '待领取',
    received: '已接收',
    outbound_created: '出库申请已创建',
    outbound_completed: '出库已完成',
    in_progress: '定检中',
    report_submitted: '报告已提交',
    accepted: '审核通过',
    rejected: '已驳回',
    inbound_created: '入库申请已创建',
    inbound_completed: '入库已完成',
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

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
@reference "../../assets/index.css";

.inspection-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}
.inspection-tabs :deep(.el-tabs__active-bar) {
  @apply bg-primary;
}
.inspection-tabs :deep(.el-tabs__item) {
  @apply text-muted-foreground font-semibold;
}
.inspection-tabs :deep(.el-tabs__item.is-active) {
  @apply text-primary;
}
</style>
