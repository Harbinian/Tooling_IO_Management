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
      <div v-debug-id="DEBUG_IDS.ORDER_CREATE.TOOL_SEARCH_DIALOG" class="flex items-center justify-between pr-8">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Search class="h-5 w-5" />
          </div>
          <div>
            <h3 class="text-lg font-bold leading-none text-slate-900">搜索工装</h3>
            <p class="mt-1.5 text-xs text-slate-500">按序列号、工作包、工装图号或工装名称检索工装主表。</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="rounded-full" @click="handleCancel">
          <X class="h-4 w-4 text-slate-400" />
        </Button>
      </div>
    </template>

    <div class="space-y-6">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_FILTER_SECTION">
        <div class="space-y-1.5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_TOOL_CODE_FILTER">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">序列号</label>
          <Input v-model="filters.toolCode" placeholder="输入序列号" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_TOOL_NAME_FILTER">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">工装名称</label>
          <Input v-model="filters.toolName" placeholder="输入工装名称" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_DRAWING_NO_FILTER">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">工装图号</label>
          <Input v-model="filters.drawingNo" placeholder="输入工装图号" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">工作包</label>
          <Input v-model="filters.workPackage" placeholder="输入工作包" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="flex items-end gap-2 pb-0.5">
          <Button variant="outline" size="sm" class="h-9 flex-1" @click="resetFilters" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_RESET_BTN">
            重置
          </Button>
          <Button
            variant="default"
            size="sm"
            class="h-9 flex-1 bg-slate-900"
            :loading="loading"
            @click="runSearch"
            v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_SEARCH_BTN"
          >
            搜索
          </Button>
        </div>
      </div>

      <div class="relative min-h-[400px] overflow-hidden rounded-xl border bg-white shadow-sm" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_RESULT_TABLE">
        <el-table
          ref="tableRef"
          :data="results"
          :row-key="getRowKey"
          height="440"
          class="tool-search-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="52" :selectable="isSelectable" reserve-selection />
          <el-table-column prop="toolCode" label="序列号" width="220">
            <template #default="{ row }">
              <span class="font-mono text-xs font-semibold text-slate-900">{{ row.toolCode }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="workPackage" label="工作包" width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="font-mono text-[11px] text-slate-500">{{ row.workPackage || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="drawingNo" label="工装图号" width="220" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="font-mono text-[11px] text-slate-500">{{ row.drawingNo || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="toolName" label="工装名称" min-width="260" show-overflow-tooltip />
        </el-table>

        <div v-if="loading" class="absolute inset-0 z-10 flex items-center justify-center bg-white/60 backdrop-blur-[1px]">
          <div class="flex flex-col items-center gap-3">
            <RefreshCw class="h-8 w-8 animate-spin text-slate-400" />
            <p class="text-xs font-medium text-slate-500">正在加载工装数据...</p>
          </div>
        </div>

        <div v-if="!loading && results.length === 0" class="absolute inset-0 flex flex-col items-center justify-center p-12 text-center opacity-40">
          <Inbox class="mb-3 h-12 w-12 text-slate-300" />
          <p class="text-sm font-medium text-slate-500">暂无匹配结果，请调整筛选条件后重试。</p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between px-2 py-1" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_FOOTER_ACTION_AREA">
        <div class="flex items-center gap-4 text-xs font-medium text-slate-500">
          <div class="flex items-center gap-1.5">
            <div class="h-2 w-2 rounded-full bg-primary" />
            <span>当前选中: <b class="text-slate-900">{{ selection.length }}</b> 项</span>
          </div>
          <div v-if="selectedToolCodes.length" class="flex items-center gap-1.5 border-l border-slate-200 pl-4">
            <div class="h-2 w-2 rounded-full bg-emerald-500" />
            <span>已加入明细: <b class="text-slate-900">{{ selectedToolCodes.length }}</b> 项</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Button variant="ghost" @click="handleCancel" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_CANCEL_BTN">取消</Button>
          <Button
            variant="default"
            class="bg-slate-900 px-8"
            :disabled="selection.length === 0"
            @click="emitSelection"
            v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_CONFIRM_BTN"
          >
            添加到明细
          </Button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Inbox, RefreshCw, Search, X } from 'lucide-vue-next'
import { searchTools } from '@/api/tools'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

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
  workPackage: ''
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
    filters.workPackage.trim()
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
      includesFilter(item.workPackage, filters.workPackage.trim())
    )
  })
}

async function runSearch() {
  loading.value = true
  selection.value = []

  try {
    const result = await searchTools({
      keyword: buildKeyword(),
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
  filters.workPackage = ''
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
