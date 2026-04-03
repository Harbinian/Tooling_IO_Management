<template>
  <div v-debug-id="DEBUG_IDS.INSPECTION.DASHBOARD.PAGE_HEADER" class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
            全局视图
          </Badge>
          <h1 class="page-header-title">定检看板</h1>
          <p class="page-header-desc">
            实时监控工装定检状态，查看待检、逾期及进行中的任务概览。
          </p>
        </div>
        <div class="page-header-actions">
          <Button class="btn-primary" @click="handleExport" :loading="exporting">
            <Download class="mr-2 h-4 w-4" />
            导出数据
          </Button>
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <!-- 四宫格统计卡片 -->
    <div v-debug-id="DEBUG_IDS.INSPECTION.DASHBOARD.STATS_CARD" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card v-for="stat in stats" :key="stat.label" class="border-border bg-card shadow-lg hover:shadow-xl transition-all overflow-hidden group">
        <CardContent class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-muted-foreground">{{ stat.label }}</p>
              <p :class="['text-3xl font-bold mt-2', stat.colorClass]">{{ stat.value }}</p>
            </div>
            <div :class="['p-3 rounded-2xl bg-muted group-hover:scale-110 transition-transform', stat.iconBg]">
              <component :is="stat.icon" :class="['h-6 w-6', stat.iconColor]" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 筛选与表格 -->
    <Card v-debug-id="DEBUG_IDS.INSPECTION.DASHBOARD.RECENT_TASKS_TABLE" class="border-border bg-card shadow-xl overflow-hidden">
      <CardHeader class="card-header">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div class="card-header-inner">
            <div class="card-header-accent" />
            <CardTitle class="card-title">工装定检清单</CardTitle>
          </div>
          <div class="flex flex-wrap items-center gap-3">
            <el-select v-model="filters.status" placeholder="状态" clearable class="!w-32">
              <el-option label="全部" value="" />
              <el-option label="正常" value="normal" />
              <el-option label="已逾期" value="overdue" />
              <el-option label="待定检" value="pending" />
            </el-select>
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="到期开始"
              end-placeholder="到期结束"
              value-format="YYYY-MM-DD"
              class="!w-64"
            />
            <el-input
              v-model="filters.keyword"
              placeholder="搜索序列号/名称"
              class="!w-48"
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
          :data="toolList"
          stripe
          class="w-full"
          header-cell-class-name="table-header"
        >
          <el-table-column prop="serial_no" label="序列号" min-width="120" fixed />
          <el-table-column prop="tool_name" label="工装名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="drawing_no" label="图号" min-width="140" />
          <el-table-column prop="last_inspection_date" label="最近定检" min-width="120">
            <template #default="{ row }">
              {{ formatDate(row.last_inspection_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="next_inspection_date" label="下次定检" min-width="120">
            <template #default="{ row }">
              {{ formatDate(row.next_inspection_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="inspection_cycle" label="周期(天)" min-width="100" align="center" />
          <el-table-column label="状态" min-width="100">
            <template #default="{ row }">
              <span :class="['status-badge', getStatusClass(row.status)]">
                {{ getStatusLabel(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="100" fixed="right">
            <template #default="{ row }">
              <router-link :to="`/inspection/status?serial_no=${row.serial_no}`">
                <el-button link type="primary">详情</el-button>
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
            @current-change="loadData"
          />
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import {
  Download, Search, AlertCircle, Clock, CheckCircle2, PlayCircle
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { getStatsSummary, getPlanList, exportInspectionStatus } from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import { DEBUG_IDS } from '@/debug/debugIds'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const session = useSessionStore()
const loading = ref(false)
const exporting = ref(false)
const toolList = ref([])
const statsSummary = reactive({
  pending_count: 0,
  in_progress_count: 0,
  overdue_count: 0,
  completed_count: 0
})

const stats = ref([
  { 
    label: '待定检工装', 
    value: 0, 
    icon: Clock, 
    colorClass: 'text-yellow-500', 
    iconBg: 'bg-yellow-500/10', 
    iconColor: 'text-yellow-500' 
  },
  { 
    label: '进行中任务', 
    value: 0, 
    icon: PlayCircle, 
    colorClass: 'text-blue-500', 
    iconBg: 'bg-blue-500/10', 
    iconColor: 'text-blue-500' 
  },
  { 
    label: '已逾期工装', 
    value: 0, 
    icon: AlertCircle, 
    colorClass: 'text-red-500', 
    iconBg: 'bg-red-500/10', 
    iconColor: 'text-red-500' 
  },
  { 
    label: '本月已完成', 
    value: 0, 
    icon: CheckCircle2, 
    colorClass: 'text-green-500', 
    iconBg: 'bg-green-500/10', 
    iconColor: 'text-green-500' 
  }
])

const filters = ref({
  status: '',
  dateRange: [],
  keyword: ''
})

const pagination = ref({
  page_no: 1,
  page_size: 10,
  total: 0
})

async function loadStats() {
  try {
    const res = await getStatsSummary({ org_id: session.orgId })
    if (res.success) {
      stats.value[0].value = res.data.pending_count || 0
      stats.value[1].value = res.data.in_progress_count || 0
      stats.value[2].value = res.data.overdue_count || 0
      stats.value[3].value = res.data.completed_count || 0
    }
  } catch (err) {
    console.error('加载统计数据失败:', err)
  }
}

async function loadData() {
  loading.value = true
  try {
    // 借用 getPlanList 或补充一个新的 getInspectionStatusList API
    // 暂时借用，实际开发中可能需要专用 API
    const params = {
      ...filters.value,
      page_no: pagination.value.page_no,
      page_size: pagination.value.page_size,
      org_id: session.orgId,
      start_date: filters.value.dateRange?.[0],
      end_date: filters.value.dateRange?.[1]
    }
    // 这里应该是获取工装定检状态列表的接口
    // const res = await getInspectionStatusList(params)
    // if (res.success) { ... }
    
    // Mock 数据用于演示布局
    toolList.value = [
      { serial_no: 'T000001', tool_name: '测试用工装', drawing_no: 'Tooling_IO_TEST', last_inspection_date: '2026-01-01', next_inspection_date: '2026-04-01', inspection_cycle: 90, status: 'overdue' },
      { serial_no: 'T000002', tool_name: '定位销 A', drawing_no: 'DW-001', last_inspection_date: '2026-02-15', next_inspection_date: '2026-05-15', inspection_cycle: 90, status: 'normal' },
      { serial_no: 'T000003', tool_name: '测量规 B', drawing_no: 'MG-002', last_inspection_date: '2026-03-10', next_inspection_date: '2026-04-10', inspection_cycle: 30, status: 'pending' }
    ]
    pagination.value.total = 3
  } catch (err) {
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.value.page_no = 1
  loadData()
}

async function handleExport() {
  if (pagination.value.total > 10000) {
    ElMessage.warning('导出数据量超过 10000 条，请缩小筛选范围。')
    return
  }
  exporting.value = true
  try {
    const res = await exportInspectionStatus({
      ...filters.value,
      org_id: session.orgId
    })
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `定检状态导出_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    console.error('导出失败:', err)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

function getStatusLabel(status) {
  const map = {
    normal: '正常',
    overdue: '已逾期',
    pending: '待定检'
  }
  return map[status] || status
}

function getStatusClass(status) {
  const map = {
    normal: 'status-completed',
    overdue: 'status-overdue',
    pending: 'status-warning'
  }
  return map[status] || ''
}

function formatDate(val) {
  if (!val) return '-'
  return new Date(val).toLocaleDateString()
}

onMounted(() => {
  loadStats()
  loadData()
})
</script>
