<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
            统计面板
          </Badge>
          <h1 class="page-header-title">定检统计分析</h1>
          <p class="page-header-desc">
            分析定检任务的执行效率、逾期率及历史趋势对比。
          </p>
        </div>
        <div class="page-header-actions">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            class="!w-64"
            @change="loadData"
          />
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <!-- 核心指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card v-for="metric in coreMetrics" :key="metric.label" class="border-border bg-card shadow-lg">
        <CardContent class="p-6">
          <p class="text-xs font-bold uppercase tracking-wider text-muted-foreground">{{ metric.label }}</p>
          <div class="flex items-baseline gap-2 mt-2">
            <p class="text-3xl font-bold">{{ metric.value }}</p>
            <p v-if="metric.trend" :class="['text-xs font-semibold', metric.trend > 0 ? 'text-red-500' : 'text-green-500']">
              {{ metric.trend > 0 ? '↑' : '↓' }}{{ Math.abs(metric.trend) }}%
            </p>
          </div>
          <p class="text-xs text-muted-foreground mt-1">{{ metric.hint }}</p>
        </CardContent>
      </Card>
    </div>

    <!-- 图表区 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- 任务状态分布 -->
      <Card class="border-border bg-card shadow-xl overflow-hidden">
        <CardHeader class="card-header">
          <div class="card-header-inner">
            <div class="card-header-accent bg-blue-500" />
            <CardTitle class="card-title">任务状态分布</CardTitle>
          </div>
        </CardHeader>
        <CardContent class="p-6">
          <div ref="distributionChartRef" class="h-[350px] w-full" />
        </CardContent>
      </Card>

      <!-- 逾期趋势 -->
      <Card class="border-border bg-card shadow-xl overflow-hidden">
        <CardHeader class="card-header">
          <div class="card-header-inner">
            <div class="card-header-accent bg-red-500" />
            <CardTitle class="card-title">最近6个月逾期趋势</CardTitle>
          </div>
        </CardHeader>
        <CardContent class="p-6">
          <div ref="trendChartRef" class="h-[350px] w-full" />
        </CardContent>
      </Card>
    </div>

    <!-- 详情表格：排名 -->
    <Card class="border-border bg-card shadow-xl overflow-hidden">
      <CardHeader class="card-header">
        <div class="card-header-inner">
          <div class="card-header-accent bg-emerald-500" />
          <CardTitle class="card-title">各班组长任务完成率排名</CardTitle>
        </div>
      </CardHeader>
      <CardContent class="p-0">
        <el-table :data="rankingData" stripe class="w-full" header-cell-class-name="table-header">
          <el-table-column type="index" label="排名" width="80" align="center" />
          <el-table-column prop="team_leader" label="班组长" min-width="150" />
          <el-table-column prop="total_tasks" label="总任务数" min-width="120" align="center" />
          <el-table-column prop="completed_tasks" label="已完成" min-width="120" align="center" />
          <el-table-column label="完成率" min-width="200">
            <template #default="{ row }">
              <div class="flex items-center gap-3">
                <el-progress :percentage="row.completion_rate" :color="getProgressColor(row.completion_rate)" class="flex-1" />
                <span class="text-xs font-semibold w-12">{{ row.completion_rate }}%</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getTaskDistribution, getOverdueRate, getMonthlyComparison } from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import Badge from '@/components/ui/Badge.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const session = useSessionStore()
const dateRange = ref([])
const distributionChartRef = ref(null)
const trendChartRef = ref(null)
let distributionChart = null
let trendChart = null

const coreMetrics = ref([
  { label: '任务总数', value: '0', trend: 5, hint: '较上月同期' },
  { label: '平均逾期率', value: '0%', trend: -2, hint: '较上月同期' },
  { label: '平均处理时长', value: '0h', trend: 0, hint: '从领取到关闭' },
  { label: '本月完成数', value: '0', trend: 12, hint: '目标达成率 85%' }
])

const rankingData = ref([
  { team_leader: '张伟', total_tasks: 45, completed_tasks: 42, completion_rate: 93.3 },
  { team_leader: '李娜', total_tasks: 38, completed_tasks: 35, completion_rate: 92.1 },
  { team_leader: '王芳', total_tasks: 52, completed_tasks: 45, completion_rate: 86.5 },
  { team_leader: '赵刚', total_tasks: 30, completed_tasks: 25, completion_rate: 83.3 }
])

async function loadData() {
  const params = {
    org_id: session.orgId,
    start_date: dateRange.value?.[0],
    end_date: dateRange.value?.[1]
  }

  try {
    // 实际调用 API
    // const resSummary = await getMonthlyComparison(params)
    // if (resSummary.success) { ... }
    
    // Mock 数据用于演示
    coreMetrics.value[0].value = '165'
    coreMetrics.value[1].value = '4.2%'
    coreMetrics.value[2].value = '28.5h'
    coreMetrics.value[3].value = '142'

    updateCharts()
  } catch (err) {
    console.error('加载统计数据失败:', err)
  }
}

function initCharts() {
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
  }
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  window.addEventListener('resize', handleResize)
  updateCharts()
}

function updateCharts() {
  if (distributionChart) {
    distributionChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0', left: 'center' },
      series: [
        {
          name: '任务状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false, position: 'center' },
          emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
          labelLine: { show: false },
          data: [
            { value: 20, name: '待领取', itemStyle: { color: '#94a3b8' } },
            { value: 35, name: '进行中', itemStyle: { color: '#3b82f6' } },
            { value: 15, name: '待验收', itemStyle: { color: '#f59e0b' } },
            { value: 85, name: '已关闭', itemStyle: { color: '#10b981' } },
            { value: 10, name: '已逾期', itemStyle: { color: '#ef4444' } }
          ]
        }
      ]
    })
  }

  if (trendChart) {
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['10月', '11月', '12月', '1月', '2月', '3月'],
        axisLine: { lineStyle: { color: '#94a3b8' } }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#94a3b8' } },
        splitLine: { lineStyle: { type: 'dashed', opacity: 0.2 } }
      },
      series: [
        {
          data: [5.2, 4.8, 6.1, 3.9, 4.5, 4.2],
          type: 'line',
          smooth: true,
          symbolSize: 8,
          itemStyle: { color: '#ef4444' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
              { offset: 1, color: 'rgba(239, 68, 68, 0)' }
            ])
          }
        }
      ]
    })
  }
}

function handleResize() {
  distributionChart?.resize()
  trendChart?.resize()
}

function getProgressColor(rate) {
  if (rate >= 90) return '#10b981'
  if (rate >= 80) return '#3b82f6'
  return '#f59e0b'
}

onMounted(() => {
  const end = new Date()
  const start = new Date()
  start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
  dateRange.value = [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
  
  loadData()
  initCharts()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  distributionChart?.dispose()
  trendChart?.dispose()
})
</script>
