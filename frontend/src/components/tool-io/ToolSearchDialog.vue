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
      <div v-debug-id="DEBUG_IDS.ORDER_CREATE.TOOL_SEARCH_DIALOG" class="flex items-center justify-between pr-8 text-foreground">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg shadow-primary/20">
            <Search class="h-5 w-5" />
          </div>
          <div>
            <h3 class="text-lg font-bold leading-none text-foreground">搜索工装</h3>
            <p class="mt-1.5 text-xs text-muted-foreground">按序列号、工作包、工装图号或工装名称检索工装主表。</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="rounded-full hover:bg-accent" @click="handleCancel">
          <X class="h-4 w-4 text-muted-foreground" />
        </Button>
      </div>
    </template>

    <div class="space-y-6 text-foreground">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_FILTER_SECTION">
        <div class="space-y-1.5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_TOOL_CODE_FILTER">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">序列号</label>
          <Input v-model="filters.serialNo" placeholder="输入序列号" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_TOOL_NAME_FILTER">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">工装名称</label>
          <Input v-model="filters.toolName" placeholder="输入工装名称" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_DRAWING_NO_FILTER">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">工装图号</label>
          <Input v-model="filters.drawingNo" placeholder="输入工装图号" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="space-y-1.5">
          <label class="ml-1 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">工作包</label>
          <Input v-model="filters.workPackage" placeholder="输入工作包" @keyup.enter="runSearch" class="h-9 text-xs" />
        </div>
        <div class="flex items-end gap-2 pb-0.5">
          <Button variant="outline" size="sm" class="h-9 flex-1 border-border" @click="resetFilters" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_RESET_BTN">
            重置
          </Button>
          <Button
            variant="default"
            size="sm"
            class="h-9 flex-1 bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 border-none"
            :loading="loading"
            @click="runSearch"
            v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_SEARCH_BTN"
          >
            搜索
          </Button>
        </div>
      </div>

      <div class="relative min-h-[400px] overflow-hidden rounded-xl border border-border bg-card shadow-sm" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_RESULT_TABLE">
        <el-table
          ref="tableRef"
          :data="results"
          :row-key="getRowKey"
          :row-class-name="tableRowClassName"
          height="440"
          class="tool-search-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="52" :selectable="isSelectable" reserve-selection />
          <el-table-column prop="serialNo" label="序列号" width="220">
            <template #default="{ row }">
              <div class="flex items-center gap-2">
                <span class="font-mono text-xs font-semibold text-foreground">{{ row.serialNo }}</span>
                <el-tooltip
                  v-if="row.disabled"
                  :content="row.disabled_reason"
                  placement="top"
                >
                  <AlertCircle class="h-3.5 w-3.5 text-warning cursor-help" />
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="workPackage" label="工作包" width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="font-mono text-[11px] text-muted-foreground">{{ row.workPackage || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="drawingNo" label="工装图号" width="220" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="font-mono text-[11px] text-muted-foreground">{{ row.drawingNo || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="toolName" label="工装名称" min-width="260" show-overflow-tooltip />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.disabled" type="warning" size="small" effect="plain" class="border-warning/30 bg-warning/5 text-warning">
                {{ row.status_text }}
              </el-tag>
              <el-tag v-else type="success" size="small" effect="light">
                {{ row.status_text || '在库' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="loading" class="absolute inset-0 z-10 flex items-center justify-center bg-background/60 backdrop-blur-[1px]">
          <div class="flex flex-col items-center gap-3">
            <RefreshCw class="h-8 w-8 animate-spin text-muted-foreground" />
            <p class="text-xs font-medium text-muted-foreground">正在加载工装数据...</p>
          </div>
        </div>

        <div v-if="!loading && results.length === 0" class="absolute inset-0 flex flex-col items-center justify-center p-12 text-center opacity-40">
          <Inbox class="mb-3 h-12 w-12 text-muted-foreground" />
          <p class="text-sm font-medium text-muted-foreground">暂无匹配结果，请调整筛选条件后重试。</p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between px-2 py-1 text-foreground" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_FOOTER_ACTION_AREA">
        <div class="flex items-center gap-4 text-xs font-medium text-muted-foreground">
          <div class="flex items-center gap-1.5">
            <div class="h-2 w-2 rounded-full bg-primary" />
            <span>当前选中: <b class="text-foreground">{{ selection.length }}</b> 项</span>
          </div>
          <div v-if="selectedSerialNos.length" class="flex items-center gap-1.5 border-l border-border pl-4">
            <div class="h-2 w-2 rounded-full bg-emerald-500" />
            <span>已加入明细: <b class="text-foreground">{{ selectedSerialNos.length }}</b> 项</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Button variant="ghost" @click="handleCancel" v-debug-id="DEBUG_IDS.ORDER_CREATE.TS_CANCEL_BTN">取消</Button>
          <Button
            variant="default"
            class="bg-primary text-primary-foreground px-8 border-none hover:bg-primary/90"
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
import { Inbox, RefreshCw, Search, X, AlertCircle } from 'lucide-vue-next'
import { searchTools } from '@/api/tools'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedSerialNos: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'confirm'])

const filters = reactive({
  serialNo: '',
  toolName: '',
  drawingNo: '',
  workPackage: ''
})

const loading = ref(false)
const results = ref([])
const selection = ref([])
const tableRef = ref(null)

const selectedSerialNoSet = computed(() => new Set(props.selectedSerialNos.filter(Boolean)))

function getRowKey(row) {
  return row.serialNo
}

function isSelectable(row) {
  return !row.disabled && !selectedSerialNoSet.value.has(row.serialNo)
}

function tableRowClassName({ row }) {
  return row.disabled ? 'tool-item-disabled' : ''
}

function handleSelectionChange(rows) {
  selection.value = rows
}

function buildKeyword() {
  return [
    filters.serialNo.trim(),
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
      includesFilter(item.serialNo, filters.serialNo.trim()) &&
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
  filters.serialNo = ''
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
  border-bottom: 1px solid hsl(var(--border));
}

.tool-search-dialog-custom .el-dialog__body {
  padding: 24px;
}

.tool-search-dialog-custom .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid hsl(var(--border));
}

.tool-search-table .el-table__header th {
  background-color: hsl(var(--muted));
  color: hsl(var(--muted-foreground));
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  height: 44px;
}

.tool-item-disabled {
  opacity: 0.5;
  background-color: hsl(var(--muted)) !important;
  cursor: not-allowed;
}

.tool-item-disabled td {
  background-color: transparent !important;
}
</style>
