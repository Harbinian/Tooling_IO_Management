<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
            管理管理
          </Badge>
          <h1 class="page-header-title">定检计划</h1>
          <p class="page-header-desc">
            制定和管理年度、月份定检计划，发布后将自动生成工装定检任务。
          </p>
        </div>
        <div class="page-header-actions" v-if="canCreatePlan">
          <router-link to="/inspection/plans/create">
            <Button class="btn-primary">
              <PlusCircle class="mr-2 h-4 w-4" />
              创建新计划
            </Button>
          </router-link>
        </div>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <Card class="border-border bg-card shadow-xl overflow-hidden">
      <CardHeader class="card-header">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div class="card-header-inner">
            <div class="card-header-accent" />
            <CardTitle class="card-title">计划列表</CardTitle>
          </div>
          <div class="flex items-center gap-2">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索计划名称或编号"
              class="!w-64"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <Search class="h-4 w-4 text-muted-foreground" />
              </template>
            </el-input>
            <el-select v-model="filters.status" placeholder="状态筛选" clearable class="!w-32">
              <el-option label="草稿" value="draft" />
              <el-option label="已发布" value="published" />
              <el-option label="已关闭" value="closed" />
            </el-select>
            <Button variant="outline" size="sm" @click="handleSearch">
              查询
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent class="p-0">
        <el-table
          v-loading="loading"
          :data="plans"
          stripe
          class="w-full"
          header-cell-class-name="table-header"
        >
          <el-table-column prop="plan_no" label="计划编号" min-width="140" fixed />
          <el-table-column prop="plan_name" label="计划名称" min-width="200" show-overflow-tooltip />
          <el-table-column label="定检周期" min-width="120">
            <template #default="{ row }">
              {{ row.year }}年 {{ row.month }}月
            </template>
          </el-table-column>
          <el-table-column prop="plan_type" label="计划类型" min-width="100">
            <template #default="{ row }">
              <span v-if="row.plan_type === 'regular'">常规</span>
              <span v-else-if="row.plan_type === 'annual'">年度</span>
              <span v-else-if="row.plan_type === 'special'">专项</span>
              <span v-else>{{ row.plan_type }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="100">
            <template #default="{ row }">
              <span :class="['status-badge', getStatusClass(row.status)]">
                {{ getStatusLabel(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="created_by_name" label="创建人" min-width="100" />
          <el-table-column prop="published_at" label="发布时间" min-width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.published_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="180" fixed="right">
            <template #default="{ row }">
              <div class="flex items-center gap-2">
                <router-link :to="`/inspection/plans/${row.plan_no}`">
                  <el-button link type="primary">查看</el-button>
                </router-link>
                <template v-if="row.status === 'draft'">
                  <el-button link type="primary" @click="handlePublish(row)">发布</el-button>
                  <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
                </template>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="p-4 flex justify-end border-t border-border">
          <el-pagination
            v-model:current-page="pagination.page_no"
            v-model:page-size="pagination.page_size"
            :total="pagination.total"
            layout="total, prev, pager, next"
            @current-change="loadPlans"
          />
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { PlusCircle, Search } from 'lucide-vue-next'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getPlanList, publishPlan } from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const session = useSessionStore()
const loading = ref(false)
const plans = ref([])
const filters = ref({
  keyword: '',
  status: ''
})
const pagination = ref({
  page_no: 1,
  page_size: 10,
  total: 0
})

const canCreatePlan = computed(() => session.hasPermission('inspection:create'))

async function loadPlans() {
  loading.value = true
  try {
    const res = await getPlanList({
      ...filters.value,
      page_no: pagination.value.page_no,
      page_size: pagination.value.page_size,
      org_id: session.orgId
    })
    if (res.success) {
      plans.value = res.data
      pagination.value.total = res.total || 0
    }
  } catch (err) {
    console.error('加载计划列表失败:', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.value.page_no = 1
  loadPlans()
}

async function handlePublish(row) {
  try {
    await ElMessageBox.confirm(
      `确认发布计划 ${row.plan_name} 吗？发布后将自动生成定检任务。`,
      '发布确认',
      {
        confirmButtonText: '发布',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const res = await publishPlan(row.plan_no)
    if (res.success) {
      ElMessage.success('计划发布成功')
      loadPlans()
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('发布计划失败:', err)
      ElMessage.error('发布计划失败')
    }
  }
}

async function handleDelete(row) {
  // 暂时未实现删除 API，后续补充
  ElMessage.info('删除功能暂未开放')
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

function formatDateTime(val) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

onMounted(() => {
  loadPlans()
})
</script>
