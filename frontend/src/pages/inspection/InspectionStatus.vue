<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10">
        <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
          状态查询
        </Badge>
        <h1 class="page-header-title">工装定检状态</h1>
        <p class="page-header-desc">
          输入工装序列号，快速查询其当前的定检周期、最近检验日期及下次预定时间。
        </p>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <Card class="border-border bg-card shadow-xl overflow-hidden">
      <CardHeader class="card-header">
        <div class="card-header-inner">
          <div class="card-header-accent" />
          <CardTitle class="card-title">快速查询</CardTitle>
        </div>
      </CardHeader>
      <CardContent class="p-6">
        <div class="flex items-center gap-4 max-w-xl">
          <el-input
            v-model="serialNo"
            placeholder="请输入工装序列号（如 T000001）"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <Search class="h-4 w-4 text-muted-foreground" />
            </template>
          </el-input>
          <Button :loading="loading" @click="handleSearch">
            查询状态
          </Button>
        </div>

        <div v-if="result" class="mt-10 animate-in slide-in-from-top-4 duration-500">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="rounded-2xl border border-border bg-muted/30 p-6 space-y-2">
              <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">定检状态</p>
              <p :class="['text-2xl font-bold', getStatusColor(result.status)]">
                {{ getStatusLabel(result.status) }}
              </p>
            </div>
            <div class="rounded-2xl border border-border bg-muted/30 p-6 space-y-2">
              <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">工装名称</p>
              <p class="text-lg font-semibold truncate">{{ result.tool_name }}</p>
            </div>
            <div class="rounded-2xl border border-border bg-muted/30 p-6 space-y-2">
              <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">最近定检</p>
              <p class="text-lg font-semibold">{{ formatDate(result.last_inspection_date) }}</p>
            </div>
            <div class="rounded-2xl border border-border bg-muted/30 p-6 space-y-2">
              <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">下次定检</p>
              <p class="text-lg font-semibold">{{ formatDate(result.next_inspection_date) }}</p>
            </div>
          </div>

          <div class="mt-8 rounded-2xl border border-border bg-card p-6">
            <h3 class="text-sm font-bold mb-4">详情参数</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-y-4">
              <div class="space-y-1">
                <p class="text-xs text-muted-foreground">定检周期</p>
                <p class="text-sm font-medium">{{ result.inspection_cycle || '-' }} 天</p>
              </div>
              <div class="space-y-1">
                <p class="text-xs text-muted-foreground">工装图号</p>
                <p class="text-sm font-medium">{{ result.drawing_no || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-xs text-muted-foreground">所属部门</p>
                <p class="text-sm font-medium">{{ result.dept_name || '-' }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="searched && !loading" class="mt-10 py-12 text-center">
          <Box class="h-12 w-12 text-muted-foreground/30 mx-auto" />
          <h3 class="mt-4 text-sm font-semibold text-foreground">未找到相关数据</h3>
          <p class="mt-1 text-xs text-muted-foreground">请确认序列号是否正确，或该工装尚未纳入定检管理。</p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, Box } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { getInspectionStatus } from '@/api/inspection'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const serialNo = ref('')
const loading = ref(false)
const searched = ref(false)
const result = ref(null)

async function handleSearch() {
  if (!serialNo.value) {
    ElMessage.warning('请输入序列号')
    return
  }

  loading.value = true
  searched.value = true
  try {
    const res = await getInspectionStatus(serialNo.value)
    if (res.success && res.data) {
      result.value = res.data
    } else {
      result.value = null
    }
  } catch (err) {
    console.error('查询定检状态失败:', err)
    result.value = null
  } finally {
    loading.value = false
  }
}

function getStatusLabel(status) {
  const map = {
    normal: '状态正常',
    overdue: '已逾期',
    pending: '待定检'
  }
  return map[status] || status
}

function getStatusColor(status) {
  const map = {
    normal: 'text-green-500',
    overdue: 'text-red-500',
    pending: 'text-yellow-500'
  }
  return map[status] || ''
}

function formatDate(val) {
  if (!val) return '-'
  return new Date(val).toLocaleDateString()
}
</script>
