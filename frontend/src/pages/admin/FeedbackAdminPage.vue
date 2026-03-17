<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  getAllFeedbackAdmin,
  updateFeedbackStatus,
  addFeedbackReply,
  getFeedbackReplies,
  FeedbackCategory,
  FeedbackCategoryLabels,
  FeedbackStatus,
  FeedbackStatusLabels
} from '@/api/feedback'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Input from '@/components/ui/Input.vue'
import NativeSelect from '@/components/ui/NativeSelect.vue'
import Badge from '@/components/ui/Badge.vue'
import Textarea from '@/components/ui/Textarea.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshCw, MessageSquare, CheckCircle2, Eye } from 'lucide-vue-next'

const loading = ref(false)
const feedbackList = ref([])
const total = ref(0)
const drawerVisible = ref(false)
const selectedFeedback = ref(null)
const replies = ref([])
const repliesLoading = ref(false)
const newReply = ref('')
const submittingReply = ref(false)

const filters = reactive({
  status: '',
  category: '',
  keyword: '',
  limit: 20,
  offset: 0
})

const categoryOptions = [
  { value: '', label: '全部分类' },
  ...Object.entries(FeedbackCategoryLabels).map(([value, label]) => ({ value, label }))
]

const statusOptions = [
  { value: '', label: '全部状态' },
  ...Object.entries(FeedbackStatusLabels).map(([value, label]) => ({ value, label }))
]

const statusUpdateOptions = Object.entries(FeedbackStatusLabels).map(([value, label]) => ({ value, label }))

const getCategoryBadgeVariant = (category) => {
  switch (category) {
    case FeedbackCategory.BUG: return 'destructive'
    case FeedbackCategory.FEATURE: return 'default'
    case FeedbackCategory.UX: return 'secondary'
    default: return 'outline'
  }
}

const getStatusBadgeVariant = (status) => {
  switch (status) {
    case FeedbackStatus.PENDING: return 'outline'
    case FeedbackStatus.REVIEWED: return 'secondary'
    case FeedbackStatus.RESOLVED: return 'default'
    default: return 'outline'
  }
}

async function fetchFeedback() {
  loading.value = true
  const result = await getAllFeedbackAdmin(filters)
  if (result.success) {
    feedbackList.value = result.data
    total.value = result.total
  } else {
    ElMessage.error('获取反馈列表失败')
  }
  loading.value = false
}

function handleFilter() {
  filters.offset = 0
  fetchFeedback()
}

async function handleViewDetails(feedback) {
  selectedFeedback.value = feedback
  drawerVisible.value = true
  fetchReplies(feedback.id)
}

async function fetchReplies(feedbackId) {
  repliesLoading.value = true
  replies.value = await getFeedbackReplies(feedbackId)
  repliesLoading.value = false
}

async function handleUpdateStatus(newStatus) {
  if (!selectedFeedback.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要将反馈状态更新为 "${FeedbackStatusLabels[newStatus]}" 吗？`,
      '更新状态',
      { type: 'info' }
    )
    
    const result = await updateFeedbackStatus(selectedFeedback.value.id, newStatus)
    if (result.success) {
      ElMessage.success('状态更新成功')
      selectedFeedback.value.status = newStatus
      fetchFeedback()
    } else {
      ElMessage.error(result.error || '状态更新失败')
    }
  } catch (e) {
    // Cancelled
  }
}

async function handleSubmitReply() {
  if (!newReply.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  submittingReply.value = true
  const result = await addFeedbackReply(selectedFeedback.value.id, newReply.value)
  if (result.success) {
    ElMessage.success('回复发送成功')
    newReply.value = ''
    fetchReplies(selectedFeedback.value.id)
    // If it was pending, it might have moved to reviewed
    fetchFeedback()
    // Update local status if needed
    if (selectedFeedback.value.status === FeedbackStatus.PENDING) {
      selectedFeedback.value.status = FeedbackStatus.REVIEWED
    }
  } else {
    ElMessage.error(result.error || '回复发送失败')
  }
  submittingReply.value = false
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  fetchFeedback()
})
</script>

<template>
  <div class="space-y-6 animate-in fade-in duration-500 text-foreground">
    <!-- Header -->
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">反馈管理</h1>
        <p class="text-muted-foreground">查看并处理用户提交的系统反馈与建议</p>
      </div>
      <Button variant="outline" @click="fetchFeedback" :disabled="loading">
        <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': loading }" />
        刷新
      </Button>
    </header>

    <!-- Filters -->
    <Card class="border-border/50 bg-card/50">
      <CardContent class="p-4">
        <div class="flex flex-wrap items-end gap-4">
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-muted-foreground">状态</label>
            <NativeSelect
              v-model="filters.status"
              :options="statusOptions"
              class="w-40"
              @change="handleFilter"
            />
          </div>
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-muted-foreground">分类</label>
            <NativeSelect
              v-model="filters.category"
              :options="categoryOptions"
              class="w-40"
              @change="handleFilter"
            />
          </div>
          <div class="flex-1 min-w-[200px] space-y-1.5">
            <label class="text-xs font-medium text-muted-foreground">搜索关键词</label>
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                v-model="filters.keyword"
                placeholder="搜索主题、内容、用户名..."
                class="pl-9"
                @keyup.enter="handleFilter"
              />
            </div>
          </div>
          <Button @click="handleFilter">查询</Button>
        </div>
      </CardContent>
    </Card>

    <!-- Feedback Table -->
    <Card class="border-border/50 bg-card/50">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="text-xs text-muted-foreground uppercase border-b border-border/50 bg-muted/30">
            <tr>
              <th class="px-6 py-4 font-semibold">提交者</th>
              <th class="px-6 py-4 font-semibold">分类</th>
              <th class="px-6 py-4 font-semibold">主题</th>
              <th class="px-6 py-4 font-semibold">状态</th>
              <th class="px-6 py-4 font-semibold">时间</th>
              <th class="px-6 py-4 font-semibold text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50">
            <tr v-for="item in feedbackList" :key="item.id" class="hover:bg-muted/20 transition-colors">
              <td class="px-6 py-4">
                <div class="font-medium text-foreground">{{ item.userName }}</div>
                <div class="text-xs text-muted-foreground">{{ item.loginName }}</div>
              </td>
              <td class="px-6 py-4">
                <Badge :variant="getCategoryBadgeVariant(item.category)">
                  {{ FeedbackCategoryLabels[item.category] }}
                </Badge>
              </td>
              <td class="px-6 py-4">
                <div class="max-w-md truncate font-medium text-foreground" :title="item.subject">
                  {{ item.subject }}
                </div>
              </td>
              <td class="px-6 py-4">
                <Badge :variant="getStatusBadgeVariant(item.status)">
                  {{ FeedbackStatusLabels[item.status] }}
                </Badge>
              </td>
              <td class="px-6 py-4 text-muted-foreground whitespace-nowrap">
                {{ formatDate(item.createdAt) }}
              </td>
              <td class="px-6 py-4 text-right">
                <Button variant="ghost" size="sm" @click="handleViewDetails(item)">
                  <Eye class="mr-2 h-4 w-4" />
                  处理
                </Button>
              </td>
            </tr>
            <tr v-if="feedbackList.length === 0 && !loading">
              <td colspan="6" class="px-6 py-12 text-center text-muted-foreground italic">
                未发现相关反馈记录
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Detail Drawer -->
    <el-drawer
      v-model="drawerVisible"
      title="反馈详情"
      direction="rtl"
      size="500px"
      custom-class="feedback-drawer"
    >
      <div v-if="selectedFeedback" class="space-y-6">
        <!-- Content Section -->
        <section class="space-y-4">
          <div class="flex items-center justify-between">
            <Badge :variant="getCategoryBadgeVariant(selectedFeedback.category)">
              {{ FeedbackCategoryLabels[selectedFeedback.category] }}
            </Badge>
            <div class="flex items-center gap-2">
              <span class="text-sm text-muted-foreground">当前状态:</span>
              <NativeSelect
                v-model="selectedFeedback.status"
                :options="statusUpdateOptions"
                class="w-32 h-8"
                @change="handleUpdateStatus"
              />
            </div>
          </div>
          
          <div class="space-y-1">
            <h2 class="text-xl font-bold text-foreground">{{ selectedFeedback.subject }}</h2>
            <div class="flex items-center text-sm text-muted-foreground gap-2">
              <span>{{ selectedFeedback.userName }}</span>
              <span>•</span>
              <span>{{ formatDate(selectedFeedback.createdAt) }}</span>
            </div>
          </div>

          <div class="p-4 rounded-lg bg-muted/30 border border-border/50 text-sm leading-relaxed whitespace-pre-wrap">
            {{ selectedFeedback.content }}
          </div>
        </section>

        <!-- Replies Section -->
        <section class="space-y-4 border-t border-border pt-6">
          <h3 class="font-bold flex items-center gap-2">
            <MessageSquare class="h-4 w-4" />
            处理回复
          </h3>
          
          <div class="space-y-4">
            <div v-if="repliesLoading" class="flex justify-center py-4">
              <RefreshCw class="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
            <div v-else-if="replies.length === 0" class="text-center py-4 text-sm text-muted-foreground italic">
              暂无回复记录
            </div>
            <div v-for="reply in replies" :key="reply.id" class="p-3 rounded-lg bg-secondary/10 border border-border/30 space-y-2">
              <div class="flex justify-between items-center text-xs">
                <span class="font-bold text-primary">{{ reply.replier_user_name }}</span>
                <span class="text-muted-foreground">{{ formatDate(reply.created_at) }}</span>
              </div>
              <p class="text-sm">{{ reply.reply_content }}</p>
            </div>
          </div>

          <!-- Add Reply Form -->
          <div class="space-y-3 pt-4">
            <Textarea
              v-model="newReply"
              placeholder="输入回复内容..."
              class="min-h-[100px]"
            />
            <div class="flex justify-end">
              <Button @click="handleSubmitReply" :disabled="submittingReply">
                <RefreshCw v-if="submittingReply" class="mr-2 h-4 w-4 animate-spin" />
                发送回复
              </Button>
            </div>
          </div>
        </section>
      </div>
    </el-drawer>
  </div>
</template>

<style>
.feedback-drawer {
  background-color: hsl(var(--background)) !important;
  color: hsl(var(--foreground)) !important;
}
.feedback-drawer .el-drawer__header {
  margin-bottom: 0;
  padding-bottom: 20px;
  border-bottom: 1px solid hsl(var(--border));
  color: hsl(var(--foreground));
}
.feedback-drawer .el-drawer__body {
  padding: 24px;
}
</style>
