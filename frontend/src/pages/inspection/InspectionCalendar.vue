<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
            可视化调度
          </Badge>
          <h1 class="page-header-title">定检日历</h1>
          <p class="page-header-desc">
            以日历形式直观展示定检任务分布，支持通过拖拽灵活调整计划时间。
          </p>
        </div>
        <div class="page-header-actions">
          <div class="flex bg-muted/50 p-1 rounded-xl border border-border/50">
            <button
              v-for="view in views"
              :key="view.id"
              :class="[
                'px-4 py-1.5 text-xs font-bold rounded-lg transition-all',
                currentView === view.id ? 'bg-primary text-primary-foreground shadow-md' : 'text-muted-foreground hover:text-foreground'
              ]"
              @click="changeView(view.id)"
            >
              {{ view.label }}
            </button>
          </div>
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <div class="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-8">
      <!-- 日历主区域 -->
      <Card class="border-border bg-card shadow-xl overflow-hidden">
        <CardContent class="p-6 calendar-container">
          <FullCalendar
            ref="calendarRef"
            :options="calendarOptions"
          />
        </CardContent>
      </Card>

      <!-- 侧边栏：图例与待处理 -->
      <div class="space-y-6">
        <Card class="border-border bg-card shadow-lg">
          <CardHeader class="card-header py-3">
            <CardTitle class="text-sm font-bold">图例说明</CardTitle>
          </CardHeader>
          <CardContent class="p-4 space-y-3">
            <div v-for="item in legend" :key="item.label" class="flex items-center gap-3">
              <div :class="['h-3 w-3 rounded-full', item.colorClass]" />
              <span class="text-xs font-medium">{{ item.label }}</span>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border bg-card shadow-lg">
          <CardHeader class="card-header py-3">
            <CardTitle class="text-sm font-bold">未排程任务</CardTitle>
          </CardHeader>
          <CardContent class="p-4">
            <div v-if="unscheduledTasks.length" class="space-y-3">
              <div
                v-for="task in unscheduledTasks"
                :key="task.task_no"
                class="p-3 rounded-xl border border-border bg-muted/30 hover:border-primary transition-colors cursor-move"
              >
                <p class="text-[10px] font-bold text-muted-foreground">{{ task.task_no }}</p>
                <p class="text-xs font-semibold truncate">{{ task.tool_name }}</p>
              </div>
            </div>
            <div v-else class="text-center py-8">
              <p class="text-xs text-muted-foreground">暂无待排程任务</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- 任务详情 Popover 样式由 CSS 控制 -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import zhCnLocale from '@fullcalendar/core/locales/zh-cn'
import { getCalendarData, rescheduleTask } from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import { ElMessage, ElMessageBox } from 'element-plus'
import Badge from '@/components/ui/Badge.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const session = useSessionStore()
const calendarRef = ref(null)
const currentView = ref('dayGridMonth')

const views = [
  { id: 'dayGridMonth', label: '月视图' },
  { id: 'timeGridWeek', label: '周视图' }
]

const legend = [
  { label: '待领取', colorClass: 'bg-gray-400' },
  { label: '进行中', colorClass: 'bg-blue-500' },
  { label: '待验收', colorClass: 'bg-orange-500' },
  { label: '已逾期', colorClass: 'bg-red-500' },
  { label: '已关闭', colorClass: 'bg-green-500' }
]

const unscheduledTasks = ref([
  { task_no: 'IT-20260402-001', tool_name: '定位销 A' },
  { task_no: 'IT-20260402-002', tool_name: '测量规 B' }
])

const calendarOptions = reactive({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: zhCnLocale,
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: ''
  },
  height: 'auto',
  weekNumbers: true,
  editable: session.hasPermission('inspection:create'),
  selectable: true,
  dayMaxEvents: true,
  events: [],
  eventClick: handleEventClick,
  eventDrop: handleEventDrop,
  datesSet: handleDatesSet
})

async function handleDatesSet(info) {
  loadEvents(info.startStr, info.endStr)
}

async function loadEvents(start, end) {
  try {
    // const res = await getCalendarData({
    //   org_id: session.orgId,
    //   start_date: start,
    //   end_date: end
    // })
    // if (res.success) { calendarOptions.events = res.data.map(...) }
    
    // Mock 数据
    calendarOptions.events = [
      {
        id: '1',
        title: '定检: 测试用工装',
        start: '2026-04-05',
        backgroundColor: '#3b82f6',
        borderColor: '#3b82f6',
        extendedProps: { task_no: 'IT-20260405-001', status: 'in_progress' }
      },
      {
        id: '2',
        title: '定检: 测量规 B',
        start: '2026-04-10',
        backgroundColor: '#ef4444',
        borderColor: '#ef4444',
        extendedProps: { task_no: 'IT-20260410-002', status: 'overdue' }
      }
    ]
  } catch (err) {
    console.error('加载日历数据失败:', err)
  }
}

function handleEventClick(info) {
  const taskNo = info.event.extendedProps.task_no
  ElMessageBox.alert(
    `任务编号: ${taskNo}<br>工装名称: ${info.event.title}<br>状态: ${info.event.extendedProps.status}`,
    '任务概览',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '查看详情',
      callback: (action) => {
        if (action === 'confirm') {
          window.location.hash = `/inspection/tasks/${taskNo}`
        }
      }
    }
  )
}

let debounceTimer = null
async function handleEventDrop(info) {
  if (debounceTimer) clearTimeout(debounceTimer)
  
  debounceTimer = setTimeout(async () => {
    const taskNo = info.event.extendedProps.task_no
    const newDate = info.event.start.toISOString().split('T')[0]
    
    try {
      const res = await rescheduleTask(taskNo, { deadline: newDate })
      if (res.success) {
        ElMessage.success('计划时间已更新')
      }
    } catch (err) {
      console.error('更新计划时间失败:', err)
      info.revert()
    }
  }, 300)
}

function changeView(viewId) {
  currentView.value = viewId
  const calendarApi = calendarRef.value.getApi()
  calendarApi.changeView(viewId)
}

onMounted(() => {
  // 初始加载
})
</script>

<style scoped>
@reference "../../assets/index.css";

.calendar-container :deep(.fc) {
  --fc-border-color: hsl(var(--border) / 0.5);
  --fc-today-bg-color: hsl(var(--primary) / 0.05);
  --fc-page-bg-color: transparent;
  font-family: inherit;
}

.calendar-container :deep(.fc-header-toolbar) {
  margin-bottom: 2rem !important;
}

.calendar-container :deep(.fc-toolbar-title) {
  font-size: 1.25rem !important;
  font-weight: 700 !important;
}

.calendar-container :deep(.fc-button) {
  @apply bg-muted text-foreground border-none shadow-none font-bold text-xs uppercase tracking-wider;
}

.calendar-container :deep(.fc-button-primary:not(:disabled).fc-button-active),
.calendar-container :deep(.fc-button-primary:not(:disabled):active) {
  @apply bg-primary text-primary-foreground;
}

.calendar-container :deep(.fc-daygrid-day-number) {
  @apply text-xs font-bold p-2;
}

.calendar-container :deep(.fc-event) {
  @apply rounded-lg border-none px-2 py-1 shadow-sm cursor-pointer transition-transform hover:scale-105;
}

.calendar-container :deep(.fc-event-title) {
  @apply text-[10px] font-bold;
}
</style>
