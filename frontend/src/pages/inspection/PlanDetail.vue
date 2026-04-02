<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Badge variant="outline" class="badge-outline uppercase tracking-widest text-[10px]">
              计划详情
            </Badge>
            <span :class="['status-badge', getStatusClass(plan.status)]">
              {{ getStatusLabel(plan.status) }}
            </span>
          </div>
          <h1 class="page-header-title">{{ plan.plan_name || '计划加载中...' }}</h1>
          <p class="page-header-desc">
            计划编号：{{ planNo }}
          </p>
        </div>
        <div class="page-header-actions">
          <Button variant="ghost" class="btn-ghost" @click="goBack">
            返回列表
          </Button>
          <Button v-if="plan.status === 'draft'" class="btn-primary" @click="handlePublish">
            发布计划
          </Button>
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <div class="lg:col-span-2 space-y-8">
        <Card class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <div class="card-header-accent" />
              <CardTitle class="card-title">基本信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">计划年度/月份</p>
              <p class="text-sm font-semibold">{{ plan.year }}年 {{ plan.month }}月</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">计划类型</p>
              <p class="text-sm font-semibold">{{ getPlanTypeLabel(plan.plan_type) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">创建人</p>
              <p class="text-sm font-semibold">{{ plan.created_by_name }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">发布时间</p>
              <p class="text-sm font-semibold">{{ formatDateTime(plan.published_at) }}</p>
            </div>
            <div class="space-y-1 md:col-span-2">
              <p class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">备注</p>
              <p class="text-sm">{{ plan.remark || '无' }}</p>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <div class="card-header-accent bg-blue-500" />
              <CardTitle class="card-title">关联定检任务</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <el-table :data="tasks" stripe class="w-full" header-cell-class-name="table-header">
              <el-table-column prop="task_no" label="任务编号" min-width="140" />
              <el-table-column prop="serial_no" label="序列号" min-width="120" />
              <el-table-column prop="tool_name" label="工装名称" min-width="180" show-overflow-tooltip />
              <el-table-column label="状态" min-width="120">
                <template #default="{ row }">
                  <span :class="['status-badge', getTaskStatusClass(row.status)]">
                    {{ row.status }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="executor_name" label="执行人" min-width="100" />
              <el-table-column label="操作" min-width="100" fixed="right">
                <template #default="{ row }">
                  <router-link :to="`/inspection/tasks/${row.task_no}`">
                    <el-button link type="primary">查看详情</el-button>
                  </router-link>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="!tasks.length" class="empty-state">
              <Box class="empty-state-icon" />
              <h3 class="empty-state-title">暂无关联任务</h3>
              <p class="empty-state-desc">发布计划后将自动生成定检任务。</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="space-y-6">
        <!-- 侧边辅助信息或统计 -->
        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="card-header">
            <CardTitle class="card-title">任务统计</CardTitle>
          </CardHeader>
          <CardContent class="p-6 space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-muted-foreground">总任务数</span>
              <span class="text-lg font-bold">{{ tasks.length }}</span>
            </div>
            <!-- 可以增加更多维度的统计 -->
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Box } from 'lucide-vue-next'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPlanDetail, publishPlan } from '@/api/inspection'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const props = defineProps({
  planNo: {
    type: String,
    required: true
  }
})

const router = useRouter()
const plan = ref({})
const tasks = ref([])
const loading = ref(false)

async function loadDetail() {
  loading.value = true
  try {
    const res = await getPlanDetail(props.planNo)
    if (res.success) {
      plan.value = res.data.plan
      tasks.value = res.data.tasks || []
    }
  } catch (err) {
    console.error('加载计划详情失败:', err)
    ElMessage.error('加载计划详情失败')
  } finally {
    loading.value = false
  }
}

async function handlePublish() {
  try {
    await ElMessageBox.confirm(
      '确认发布该计划吗？发布后将不可更改并立即生成定检任务。',
      '发布确认',
      {
        confirmButtonText: '确认发布',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const res = await publishPlan(props.planNo)
    if (res.success) {
      ElMessage.success('计划已发布')
      loadDetail()
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('发布计划失败:', err)
      ElMessage.error('发布计划失败')
    }
  }
}

function getStatusLabel(status) {
  const map = {
    draft: '草稿',
    published: '已发布',
    closed: '已关闭'
  }
  return map[status] || status
}

function getStatusClass(status) {
  const map = {
    draft: 'status-pending',
    published: 'status-active',
    closed: 'status-completed'
  }
  return map[status] || ''
}

function getPlanTypeLabel(type) {
  const map = {
    regular: '常规',
    annual: '年度',
    special: '专项'
  }
  return map[type] || type
}

function getTaskStatusClass(status) {
  const map = {
    pending: 'status-pending',
    closed: 'status-completed'
  }
  return map[status] || 'status-active'
}

function formatDateTime(val) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

function goBack() {
  router.push('/inspection/plans')
}

onMounted(() => {
  loadDetail()
})
</script>
