<template>
  <el-dialog
    :model-value="visible"
    width="1280px"
    destroy-on-close
    :show-close="false"
    class="tool-search-dialog-custom"
    @close="handleCancel"
  >
    <template #header>
      <div class="flex items-center justify-between pr-8">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Search class="h-5 w-5" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900 leading-none">工装库搜索</h3>
            <p class="text-xs text-slate-500 mt-1.5">检索基于工装身份卡主表：序列号、名称、图号、机型、库位等。</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="rounded-full" @click="handleCancel">
          <X class="h-4 w-4 text-slate-400" />
        </Button>
      </div>
    </template>

    <div class="space-y-6">
      <!-- Search Filters -->
      <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-wider text-slate-400 ml-1">工装编码</label>
          <Input v-model="filters.toolCode" placeholder="输入序列号" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-wider text-slate-400 ml-1">工装名称</label>
          <Input v-model="filters.toolName" placeholder="模糊匹配" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-wider text-slate-400 ml-1">图号</label>
          <Input v-model="filters.drawingNo" placeholder="输入图号" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-wider text-slate-400 ml-1">机型</label>
          <Input v-model="filters.specModel" placeholder="输入机型" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5">
          <label class="text-[11px] font-bold uppercase tracking-wider text-slate-400 ml-1">库位</label>
          <Input v-model="filters.location" placeholder="输入库位" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="flex items-end gap-2 pb-0.5">
          <Button variant="outline" size="sm" class="flex-1 h-9" @click="resetFilters">重置</Button>
          <Button variant="default" size="sm" class="flex-1 h-9 bg-slate-900" :loading="loading" @click="runSearch">
            搜索
          </Button>
        </div>
      </div>

      <!-- Results Table -->
      <div class="border rounded-xl overflow-hidden bg-white shadow-sm min-h-[400px] relative">
        <el-table
          ref="tableRef"
          :data="results"
          :row-key="getRowKey"
          height="440"
          class="tool-search-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="52" :selectable="isSelectable" reserve-selection />
          <el-table-column prop="toolCode" label="编码" width="140">
            <template #default="{ row }">
              <span class="font-mono text-xs font-semibold text-slate-900">{{ row.toolCode }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="toolName" label="工装名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="drawingNo" label="图号" width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="font-mono text-[11px] text-slate-500">{{ row.drawingNo || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="specModel" label="机型" width="100" />
          <el-table-column prop="currentVersion" label="版次" width="80" align="center" />
          <el-table-column prop="currentLocationText" label="库位" width="120" show-overflow-tooltip>
            <template #default="{ row }">
              <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-none font-normal">
                {{ row.currentLocationText || '-' }}
              </Badge>
            </template>
          </el-table-column>
          <el-table-column prop="statusText" label="当前状态" min-width="140" show-overflow-tooltip />
        </el-table>

        <!-- Loading Overlay -->
        <div v-if="loading" class="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center z-10">
          <div class="flex flex-col items-center gap-3">
            <RefreshCw class="h-8 w-8 text-slate-400 animate-spin" />
            <p class="text-xs font-medium text-slate-500">正在检索工装数据...</p>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!loading && results.length === 0" class="absolute inset-0 flex flex-col items-center justify-center text-center p-12 opacity-40">
          <Inbox class="h-12 w-12 text-slate-300 mb-3" />
          <p class="text-sm font-medium text-slate-500">请输入搜索条件后查询工装</p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between px-2 py-1">
        <div class="flex items-center gap-4 text-xs text-slate-500 font-medium">
          <div class="flex items-center gap-1.5">
            <div class="h-2 w-2 rounded-full bg-primary" />
            <span>本次选择: <b class="text-slate-900">{{ selection.length }}</b> 项</span>
          </div>
          <div v-if="selectedToolCodes.length" class="flex items-center gap-1.5 border-l border-slate-200 pl-4">
            <div class="h-2 w-2 rounded-full bg-emerald-500" />
            <span>当前单据已选: <b class="text-slate-900">{{ selectedToolCodes.length }}</b> 项</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Button variant="ghost" @click="handleCancel">取消</Button>
          <Button variant="default" class="bg-slate-900 px-8" :disabled="selection.length === 0" @click="emitSelection">
            确认加入单据
          </Button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, X, RefreshCw, Inbox } from 'lucide-vue-next'
import { searchTools } from '@/api/toolIO'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedToolCodes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'confirm'])

const filters = reactive({
  toolCode: '',
  toolName: '',
  drawingNo: '',
  specModel: '',
  location: '',
  status: ''
})

const loading = ref(false)
const results = ref([])
const selection = ref([])
const tableRef = ref(null)

const selectedToolCodeSet = computed(() => new Set(props.selectedToolCodes.filter(Boolean)))

function getRowKey(row) {
  return row.toolCode
}

function isSelectable(row) {
  return !selectedToolCodeSet.value.has(row.toolCode)
}

function handleSelectionChange(rows) {
  selection.value = rows
}

function buildKeyword() {
  return [
    filters.toolCode.trim(),
    filters.toolName.trim(),
    filters.drawingNo.trim(),
    filters.specModel.trim()
  ].find(Boolean) || ''
}

function includesFilter(source, keyword) {
  if (!keyword) return true
  return String(source || '').toLowerCase().includes(keyword.toLowerCase())
}

function applyClientFilters(items) {
  return items.filter((item) => {
    return (
      includesFilter(item.toolCode, filters.toolCode.trim()) &&
      includesFilter(item.toolName, filters.toolName.trim()) &&
      includesFilter(item.drawingNo, filters.drawingNo.trim()) &&
      includesFilter(item.specModel, filters.specModel.trim()) &&
      includesFilter(item.currentLocationText, filters.location.trim()) &&
      includesFilter(item.statusText, filters.status.trim())
    )
  })
}

async function runSearch() {
  loading.value = true
  selection.value = []

  try {
    const result = await searchTools({
      keyword: buildKeyword(),
      location: filters.location.trim(),
      status: filters.status.trim(),
      page_no: 1,
      page_size: 200
    })

    if (!result.success) {
      ElMessage.error(result.error || '工装搜索失败')
      results.value = []
      return
    }

    results.value = applyClientFilters(result.data || [])
    await nextTick()
    tableRef.value?.clearSelection()
  } catch (error) {
    results.value = []
    ElMessage.error(error?.message || '工装搜索失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.toolCode = ''
  filters.toolName = ''
  filters.drawingNo = ''
  filters.specModel = ''
  filters.location = ''
  filters.status = ''
  results.value = []
  selection.value = []
  tableRef.value?.clearSelection()
}

function emitSelection() {
  if (!selection.value.length) {
    ElMessage.warning('请先选择工装')
    return
  }

  emit('confirm', selection.value)
  emit('update:visible', false)
}

function handleCancel() {
  emit('update:visible', false)
}
</script>

<style>
.tool-search-dialog-custom .el-dialog__header {
  padding: 24px 24px 16px;
  margin-right: 0;
  border-bottom: 1px solid #f1f5f9;
}
.tool-search-dialog-custom .el-dialog__body {
  padding: 24px;
}
.tool-search-dialog-custom .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
}
.tool-search-table .el-table__header th {
  background-color: #f8fafc;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  height: 44px;
}
</style>
