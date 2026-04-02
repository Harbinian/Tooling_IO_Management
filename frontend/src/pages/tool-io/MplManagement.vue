<template>
  <div class="space-y-8 text-foreground">
    <header class="relative overflow-hidden rounded-3xl bg-primary px-8 py-10 text-primary-foreground shadow-2xl">
      <div class="relative z-10">
        <p class="text-[10px] font-bold uppercase tracking-[0.28em] text-primary-foreground/70">Detachable Components</p>
        <h1 class="mt-3 text-3xl font-bold tracking-tight">MPL 管理</h1>
        <p class="mt-3 max-w-2xl text-sm text-primary-foreground/80">
          维护工装可拆卸件清单，用于保管员确认时的完整性核对。
        </p>
      </div>
      <div class="absolute -right-12 -top-16 h-52 w-52 rounded-full bg-primary-foreground/10 blur-3xl"></div>
    </header>

    <Card class="border-border bg-card shadow-xl">
      <CardHeader class="border-b border-border">
        <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-semibold">工装图号</label>
              <Input v-model="filters.drawing_no" placeholder="按图号筛选" @keyup.enter="loadGroups" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-semibold">关键字</label>
              <Input v-model="filters.keyword" placeholder="图号 / 版次 / 组件" @keyup.enter="loadGroups" />
            </div>
          </div>
          <div class="flex gap-3">
            <Button variant="outline" @click="resetFilters">重置</Button>
            <Button variant="outline" @click="loadGroups" :disabled="loading">查询</Button>
            <Button class="bg-primary text-primary-foreground border-none hover:bg-primary/90" @click="openCreateDialog">
              新建 MPL
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent class="pt-6">
        <el-table :data="groups" v-loading="loading" border class="w-full">
          <el-table-column prop="mpl_no" label="MPL 编号" min-width="220" />
          <el-table-column prop="tool_drawing_no" label="工装图号" min-width="180" />
          <el-table-column prop="tool_revision" label="版次" width="120" />
          <el-table-column prop="component_count" label="组件数" width="100" />
          <el-table-column prop="updated_at" label="更新时间" min-width="180" />
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <div class="flex gap-2">
                <Button variant="outline" size="sm" @click="viewGroup(row.mpl_no)">查看</Button>
                <Button variant="outline" size="sm" @click="editGroup(row.mpl_no)">编辑</Button>
                <Button variant="destructive" size="sm" @click="removeGroup(row.mpl_no)">删除</Button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="mt-4 flex justify-end">
          <el-pagination
            layout="total, prev, pager, next"
            :total="total"
            :current-page="pageNo"
            :page-size="pageSize"
            @current-change="handlePageChange"
          />
        </div>
      </CardContent>
    </Card>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'view' ? 'MPL 详情' : dialogMode === 'edit' ? '编辑 MPL' : '新建 MPL'" width="980px" destroy-on-close>
      <div class="space-y-6">
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <label class="text-sm font-semibold">工装图号</label>
            <Input v-model="form.tool_drawing_no" :disabled="dialogMode === 'view'" />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold">工装版次</label>
            <Input v-model="form.tool_revision" :disabled="dialogMode === 'view'" />
          </div>
        </div>

        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold">组件明细</h3>
          <Button v-if="dialogMode !== 'view'" variant="outline" size="sm" @click="addItem">新增组件</Button>
        </div>

        <div class="space-y-4">
          <div v-for="(item, index) in form.items" :key="`${index}-${item.component_no}`" class="rounded-2xl border border-border bg-muted/20 p-4">
            <div class="mb-4 flex items-center justify-between">
              <p class="text-sm font-semibold">组件 {{ index + 1 }}</p>
              <Button v-if="dialogMode !== 'view'" variant="ghost" size="sm" @click="removeItem(index)">移除</Button>
            </div>

            <div class="grid gap-4 md:grid-cols-3">
              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted-foreground">组件号</label>
                <Input v-model="item.component_no" :disabled="dialogMode === 'view'" />
              </div>
              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted-foreground">组件名称</label>
                <Input v-model="item.component_name" :disabled="dialogMode === 'view'" />
              </div>
              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted-foreground">数量</label>
                <Input v-model="item.quantity" type="number" min="1" :disabled="dialogMode === 'view'" />
              </div>
            </div>

            <div class="mt-4 grid gap-4 md:grid-cols-[240px,1fr]">
              <div class="space-y-2">
                <label class="text-xs font-semibold text-muted-foreground">图片</label>
                <el-upload
                  v-if="dialogMode !== 'view'"
                  action="#"
                  :auto-upload="false"
                  :limit="1"
                  accept="image/*"
                  :show-file-list="false"
                  :on-change="(file) => handleFileChange(file, item)"
                >
                  <el-button>选择图片</el-button>
                </el-upload>
                <p v-else class="text-xs text-muted-foreground">只读模式</p>
              </div>
              <div class="rounded-xl border border-dashed border-border bg-background/70 p-3">
                <img v-if="item.photo_data" :src="item.photo_data" alt="MPL component" class="h-40 w-full rounded-lg object-contain bg-muted/20" />
                <p v-else class="flex h-40 items-center justify-center text-sm text-muted-foreground">暂无图片</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button variant="outline" @click="dialogVisible = false">关闭</Button>
          <Button
            v-if="dialogMode !== 'view'"
            class="bg-primary text-primary-foreground border-none hover:bg-primary/90"
            :disabled="saving"
            @click="submitForm"
          >
            {{ saving ? '保存中...' : '保存' }}
          </Button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createMpl, deleteMpl, getMplDetail, getMplList, updateMpl } from '@/api/mpl'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import Input from '@/components/ui/Input.vue'

const MAX_SIZE = 2 * 1024 * 1024

const loading = ref(false)
const saving = ref(false)
const groups = ref([])
const total = ref(0)
const pageNo = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const dialogMode = ref('create')

const filters = reactive({
  drawing_no: '',
  keyword: ''
})

const form = reactive({
  mpl_no: '',
  tool_drawing_no: '',
  tool_revision: '',
  items: []
})

function buildEmptyItem() {
  return {
    component_no: '',
    component_name: '',
    quantity: 1,
    photo_data: ''
  }
}

function resetForm() {
  form.mpl_no = ''
  form.tool_drawing_no = ''
  form.tool_revision = ''
  form.items = [buildEmptyItem()]
}

async function loadGroups() {
  loading.value = true
  try {
    const result = await getMplList({
      page_no: pageNo.value,
      page_size: pageSize.value,
      drawing_no: filters.drawing_no,
      keyword: filters.keyword
    })
    groups.value = result.data || []
    total.value = result.total || 0
  } finally {
    loading.value = false
  }
}

function handlePageChange(nextPage) {
  pageNo.value = nextPage
  loadGroups()
}

function resetFilters() {
  filters.drawing_no = ''
  filters.keyword = ''
  pageNo.value = 1
  loadGroups()
}

function openCreateDialog() {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

async function fillForm(mplNo, mode) {
  const result = await getMplDetail(mplNo)
  if (!result.success) return
  dialogMode.value = mode
  form.mpl_no = result.data.mpl_no
  form.tool_drawing_no = result.data.tool_drawing_no
  form.tool_revision = result.data.tool_revision
  form.items = (result.data.items || []).map((item) => ({
    component_no: item.component_no,
    component_name: item.component_name,
    quantity: item.quantity,
    photo_data: item.photo_data || ''
  }))
  dialogVisible.value = true
}

function viewGroup(mplNo) {
  fillForm(mplNo, 'view')
}

function editGroup(mplNo) {
  fillForm(mplNo, 'edit')
}

async function removeGroup(mplNo) {
  await ElMessageBox.confirm(`确认删除 ${mplNo} 吗？`, '删除 MPL', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  const result = await deleteMpl(mplNo)
  if (result.success) {
    ElMessage.success('MPL 已删除')
    loadGroups()
  }
}

function addItem() {
  form.items.push(buildEmptyItem())
}

function removeItem(index) {
  if (form.items.length === 1) {
    ElMessage.warning('至少保留一个组件')
    return
  }
  form.items.splice(index, 1)
}

function handleFileChange(file, item) {
  if (file.size > MAX_SIZE) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (event) => {
    item.photo_data = event.target?.result || ''
  }
  reader.readAsDataURL(file.raw)
}

function buildPayload() {
  return {
    tool_drawing_no: form.tool_drawing_no.trim(),
    tool_revision: form.tool_revision.trim(),
    items: form.items.map((item) => ({
      component_no: String(item.component_no || '').trim(),
      component_name: String(item.component_name || '').trim(),
      quantity: Number(item.quantity || 1),
      photo_data: item.photo_data || ''
    }))
  }
}

async function submitForm() {
  const payload = buildPayload()
  if (!payload.tool_drawing_no || !payload.tool_revision) {
    ElMessage.warning('请填写工装图号和版次')
    return
  }
  if (payload.items.some((item) => !item.component_no || !item.component_name || item.quantity <= 0)) {
    ElMessage.warning('请完整填写组件号、组件名称和数量')
    return
  }

  saving.value = true
  try {
    const result = dialogMode.value === 'edit'
      ? await updateMpl(form.mpl_no, payload)
      : await createMpl(payload)
    if (result.success) {
      ElMessage.success(dialogMode.value === 'edit' ? 'MPL 已更新' : 'MPL 已创建')
      dialogVisible.value = false
      loadGroups()
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  resetForm()
  loadGroups()
})
</script>
