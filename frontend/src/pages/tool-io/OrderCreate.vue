<template>
  <div class="space-y-10 animate-in fade-in duration-500 pb-20">
    <!-- Page Header Section -->
    <header class="relative overflow-hidden rounded-3xl bg-slate-900 px-8 py-12 text-white shadow-2xl">
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <Badge variant="outline" class="mb-4 border-slate-700 text-slate-400 bg-slate-800/50 backdrop-blur-sm">
            Workflow Step 01
          </Badge>
          <h1 class="text-3xl font-bold tracking-tight md:text-4xl">新建申请单</h1>
          <p class="mt-2 text-slate-400 max-w-lg">
            填写基础信息并搜索添加工装明细。提交后，单据将自动流转至保管员进行实物确认。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <Button variant="outline" class="border-slate-700 text-white hover:bg-slate-800" @click="resetForm">
            <RefreshCw class="mr-2 h-4 w-4" /> 重置表单
          </Button>
          <Button class="bg-white text-slate-900 hover:bg-slate-100 font-bold shadow-lg" @click="searchDialogVisible = true">
            <Search class="mr-2 h-4 w-4" /> 搜索并添加工装
          </Button>
        </div>
      </div>
      
      <!-- Abstract background elements -->
      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl"></div>
      <div class="absolute left-1/2 bottom-0 h-32 w-32 rounded-full bg-emerald-500/10 blur-2xl"></div>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-10 items-start">
      <div class="space-y-8">
        <!-- Main Form Card -->
        <Card class="border-slate-200/80 bg-white shadow-sm overflow-hidden">
          <CardHeader class="border-b border-slate-100 bg-slate-50/30 py-4">
            <div class="flex items-center gap-2">
              <div class="h-8 w-1 bg-primary rounded-full" />
              <CardTitle class="text-base font-bold">基础信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
              <!-- Order Type -->
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-700">申请类型</label>
                <TabsList v-model="form.orderType" class="w-full md:w-auto">
                  <TabsTrigger value="outbound" :model-value="form.orderType" @update:model-value="v => form.orderType = v" class="px-8">
                    出库申请
                  </TabsTrigger>
                  <TabsTrigger value="inbound" :model-value="form.orderType" @update:model-value="v => form.orderType = v" class="px-8">
                    入库申请
                  </TabsTrigger>
                </TabsList>
              </div>

              <!-- Project Code -->
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">项目代号</label>
                <Input v-model="form.projectCode" placeholder="如：P-2024-001" />
              </div>

              <!-- Usage Purpose -->
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">用途</label>
                <Input v-model="form.usagePurpose" placeholder="如：生产装配 / 维护保养" />
              </div>

              <!-- Target Location -->
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">目标位置</label>
                <Input v-model="form.targetLocationText" placeholder="请输入车间或库位编号" />
              </div>

              <!-- Planned Use Time -->
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">计划使用时间</label>
                <el-date-picker
                  v-model="form.plannedUseTime"
                  type="datetime"
                  placeholder="选择日期时间"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  class="!w-full !h-10"
                />
              </div>

              <!-- Remark -->
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-700">备注</label>
                <Textarea v-model="form.remark" placeholder="如有其他特殊要求请在此注明..." />
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Selected Tools Card -->
        <Card class="border-slate-200/80 bg-white shadow-sm overflow-hidden">
          <CardHeader class="border-b border-slate-100 bg-slate-50/30 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="h-8 w-1 bg-emerald-500 rounded-full" />
                <CardTitle class="text-base font-bold">已选工装明细</CardTitle>
              </div>
              <Badge variant="secondary" class="bg-emerald-50 text-emerald-700 border-emerald-100">
                {{ selectedTools.length }} 项已选
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div v-if="selectedTools.length > 0" class="overflow-x-auto">
              <table class="w-full text-sm text-left border-collapse">
                <thead class="bg-slate-50/50 border-b border-slate-100 text-slate-500 text-[11px] font-bold uppercase tracking-wider">
                  <tr>
                    <th class="px-6 py-3">工装信息</th>
                    <th class="px-6 py-3">图号 / 机型</th>
                    <th class="px-6 py-3">当前库位</th>
                    <th class="px-6 py-3 w-32">申请数量</th>
                    <th class="px-6 py-3 text-right">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  <tr v-for="(item, index) in selectedTools" :key="item.toolCode" class="group hover:bg-slate-50/50 transition-colors">
                    <td class="px-6 py-4">
                      <div class="font-semibold text-slate-900">{{ item.toolCode }}</div>
                      <div class="text-xs text-slate-500 mt-0.5 truncate max-w-[200px]">{{ item.toolName }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-slate-600 font-mono text-[13px]">{{ item.drawingNo || '-' }}</div>
                      <div class="text-[11px] text-slate-400 mt-0.5">{{ item.specModel || '-' }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <span class="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600">
                        {{ item.currentLocationText || '未知' }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <Input 
                        type="number" 
                        v-model.number="item.applyQty" 
                        class="h-8 text-xs w-20 text-center border-slate-200"
                        :min="1"
                      />
                    </td>
                    <td class="px-6 py-4 text-right">
                      <Button variant="ghost" size="sm" class="text-slate-400 hover:text-rose-600 hover:bg-rose-50" @click="removeTool(index)">
                        <Trash2 class="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Empty State -->
            <div v-else class="p-12 flex flex-col items-center justify-center text-center">
              <div class="h-16 w-16 rounded-full bg-slate-50 flex items-center justify-center mb-4">
                <Box class="h-8 w-8 text-slate-300" />
              </div>
              <h3 class="text-sm font-semibold text-slate-900">尚未选择工装</h3>
              <p class="text-xs text-slate-500 mt-1 max-w-[240px]">
                点击右上角的“搜索并添加工装”按钮，从工装主表中选择您需要的项目。
              </p>
              <Button variant="outline" size="sm" class="mt-4" @click="searchDialogVisible = true">
                立即去搜索
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column: Previews & Actions -->
      <div class="space-y-6">
        <!-- Text Preview Card -->
        <Card class="border-slate-200/80 bg-white shadow-sm overflow-hidden sticky top-8">
          <CardHeader class="border-b border-slate-100 bg-slate-50/30 py-4">
            <div class="flex items-center justify-between">
              <CardTitle class="text-base font-bold">文本预览</CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                :disabled="!selectedTools.length" 
                class="text-xs text-primary h-7"
                @click="handlePreview"
              >
                生成预览
              </Button>
            </div>
          </CardHeader>
          <CardContent class="p-4">
            <NotificationPreview 
              type="keeper" 
              :content="keeperText" 
              empty-text="生成预览后，此处将显示发送给保管员的结构化申请文本。"
              class="border-none shadow-none bg-slate-50/50"
            />
          </CardContent>
          <CardFooter class="flex flex-col gap-3 pt-0 border-t border-slate-50 bg-slate-50/30 p-6">
            <Button 
              class="w-full bg-slate-900 text-white" 
              :disabled="!selectedTools.length" 
              :loading="submittingOrder"
              @click="submitCreatedOrder"
            >
              提交单据
            </Button>
            <Button 
              variant="outline" 
              class="w-full bg-white" 
              :disabled="!selectedTools.length" 
              :loading="savingDraft"
              @click="saveDraft"
            >
              保存草稿
            </Button>
            <p class="text-[10px] text-center text-slate-400 mt-1">
              提交后单据将流转至“已提交”状态，等待保管员确认。
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>

    <!-- Search Dialog -->
    <ToolSearchDialog
      v-model:visible="searchDialogVisible"
      :selected-tool-codes="selectedToolCodes"
      @confirm="appendTools"
    />
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { 
  Search, 
  Plus, 
  Trash2, 
  Box, 
  FileText, 
  ArrowRight,
  Info,
  RefreshCw
} from 'lucide-vue-next'
import { createOrder, generateKeeperText, submitOrder } from '@/api/toolIO'
import { useSessionStore } from '@/store/session'
import ToolSearchDialog from '@/components/tool-io/ToolSearchDialog.vue'
import NotificationPreview from '@/components/tool-io/NotificationPreview.vue'

// UI Components
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardFooter from '@/components/ui/CardFooter.vue'
import CardDescription from '@/components/ui/CardDescription.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import TabsList from '@/components/ui/TabsList.vue'
import TabsTrigger from '@/components/ui/TabsTrigger.vue'

const router = useRouter()
const session = useSessionStore()

const form = reactive({
  orderType: 'outbound',
  projectCode: '',
  usagePurpose: '',
  targetLocationText: '',
  plannedUseTime: '',
  plannedReturnTime: '',
  remark: ''
})

const selectedTools = ref([])
const keeperText = ref('')
const searchDialogVisible = ref(false)
const savingDraft = ref(false)
const submittingOrder = ref(false)

const selectedToolCodes = computed(() =>
  selectedTools.value.map((tool) => tool.toolCode).filter(Boolean)
)

function appendTools(tools) {
  const nextTools = [...selectedTools.value]
  const selectedCodeSet = new Set(selectedToolCodes.value)
  let addedCount = 0
  let duplicateCount = 0

  for (const tool of tools) {
    if (!tool?.toolCode) continue
    if (selectedCodeSet.has(tool.toolCode)) {
      duplicateCount += 1
      continue
    }

    // Default apply quantity to 1
    nextTools.push({
      ...tool,
      applyQty: 1
    })
    selectedCodeSet.add(tool.toolCode)
    addedCount += 1
  }

  selectedTools.value = nextTools
  keeperText.value = ''

  if (addedCount) {
    ElMessage.success(`已添加 ${addedCount} 项工装`)
  }
  if (duplicateCount) {
    ElMessage.warning(`${duplicateCount} 项重复工装已忽略`)
  }
}

function removeTool(index) {
  selectedTools.value.splice(index, 1)
  keeperText.value = ''
}

function validateBeforeSubmit() {
  if (!selectedTools.value.length) {
    ElMessage.warning('请先选择工装')
    return false
  }
  if (!form.targetLocationText.trim()) {
    ElMessage.warning('请输入目标位置')
    return false
  }
  return true
}

function buildPayload() {
  return {
    order_type: form.orderType,
    initiator_id: session.userId || 'anonymous',
    initiator_name: session.userName || 'anonymous',
    initiator_role: session.role || 'team_leader',
    department: '',
    project_code: form.projectCode,
    usage_purpose: form.usagePurpose,
    planned_use_time: form.plannedUseTime,
    planned_return_time: form.plannedReturnTime,
    target_location_text: form.targetLocationText,
    remark: form.remark,
    items: selectedTools.value.map((item) => ({
      tool_id: item.toolId,
      tool_code: item.toolCode,
      tool_name: item.toolName,
      drawing_no: item.drawingNo,
      spec_model: item.specModel,
      apply_qty: item.applyQty || 1
    }))
  }
}

async function handlePreview() {
  if (!validateBeforeSubmit()) return

  const created = await createOrder(buildPayload())
  if (!created.success) {
    ElMessage.error(created.error || '生成预览失败')
    return
  }

  const preview = await generateKeeperText(created.order_no)
  if (preview.success) {
    keeperText.value = preview.text
    ElMessage.success(`已生成预览，单号：${created.order_no}`)
  } else {
    ElMessage.error(preview.error || '生成预览失败')
  }
}

async function saveDraft() {
  if (!validateBeforeSubmit()) return
  savingDraft.value = true

  try {
    const result = await createOrder(buildPayload())
    if (!result.success) {
      ElMessage.error(result.error || '保存草稿失败')
      return
    }

    ElMessage.success(`草稿已创建：${result.order_no}`)
    router.push(`/inventory/${result.order_no}`)
  } finally {
    savingDraft.value = false
  }
}

async function submitCreatedOrder() {
  if (!validateBeforeSubmit()) return
  submittingOrder.value = true

  try {
    const created = await createOrder(buildPayload())
    if (!created.success) {
      ElMessage.error(created.error || '创建单据失败')
      return
    }

    const result = await submitOrder(created.order_no, {
      operator_id: session.userId || 'anonymous',
      operator_name: session.userName || 'anonymous',
      operator_role: session.role || 'team_leader'
    })
    if (!result.success) {
      ElMessage.error(result.error || '提交单据失败')
      return
    }

    ElMessage.success(`单据已提交：${created.order_no}`)
    router.push(`/inventory/${created.order_no}`)
  } finally {
    submittingOrder.value = false
  }
}

function resetForm() {
  form.orderType = 'outbound'
  form.projectCode = ''
  form.usagePurpose = ''
  form.targetLocationText = ''
  form.plannedUseTime = ''
  form.plannedReturnTime = ''
  form.remark = ''
  selectedTools.value = []
  keeperText.value = ''
}
</script>

<style scoped>
/* el-date-picker global override for tailwind sync */
:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
  border-radius: 0.375rem !important;
  padding: 0 12px !important;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #0f172a inset !important;
}
</style>
