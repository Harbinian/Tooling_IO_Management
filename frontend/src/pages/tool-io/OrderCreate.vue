<template>
  <div class="animate-in fade-in space-y-10 pb-20 duration-500">
    <header class="relative overflow-hidden rounded-3xl bg-slate-900 px-8 py-12 text-white shadow-2xl">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="mb-4 border-slate-700 bg-slate-800/50 text-slate-400 backdrop-blur-sm">
            创建单据
          </Badge>
          <h1 class="text-3xl font-bold tracking-tight md:text-4xl">工装出入库申请</h1>
          <p class="mt-2 max-w-lg text-slate-400">
            先从工装主表选择工装，再填写用途、目标位置和计划时间，最后生成并提交出入库单。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <Button
            v-debug-id="DEBUG_IDS.ORDER_CREATE.CANCEL_BTN"
            variant="outline"
            class="border-slate-700 text-white hover:bg-slate-800"
            @click="resetForm"
          >
            <RefreshCw class="mr-2 h-4 w-4" />
            重置表单
          </Button>
          <Button
            v-debug-id="DEBUG_IDS.ORDER_CREATE.TOOL_SEARCH_FIELD"
            class="bg-white font-bold text-slate-900 shadow-lg hover:bg-slate-100"
            @click="searchDialogVisible = true"
          >
            <Search class="mr-2 h-4 w-4" />
            搜索并添加工装
          </Button>
        </div>
      </div>

      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/2 h-32 w-32 rounded-full bg-emerald-500/10 blur-2xl"></div>
    </header>

    <div class="grid grid-cols-1 items-start gap-10 lg:grid-cols-[1fr_400px]">
      <div class="space-y-8">
        <Card v-debug-id="DEBUG_IDS.ORDER_CREATE.FORM" class="overflow-hidden border-slate-200/80 bg-white shadow-sm">
          <CardHeader class="border-b border-slate-100 bg-slate-50/30 py-4">
            <div class="flex items-center gap-2">
              <div class="h-8 w-1 rounded-full bg-primary" />
              <CardTitle class="text-base font-bold">基本信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6">
            <div class="grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2">
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-700">单据类型</label>
                <TabsList v-debug-id="DEBUG_IDS.ORDER_CREATE.ORDER_TYPE_FIELD" v-model="form.orderType" class="w-full md:w-auto">
                  <TabsTrigger value="outbound" :model-value="form.orderType" @update:model-value="(v) => (form.orderType = v)" class="px-8">
                    出库
                  </TabsTrigger>
                  <TabsTrigger value="inbound" :model-value="form.orderType" @update:model-value="(v) => (form.orderType = v)" class="px-8">
                    入库
                  </TabsTrigger>
                </TabsList>
              </div>

              <div v-if="form.orderType === 'outbound'" class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">用途</label>
                <Select v-model="form.usagePurpose" placeholder="请选择用途">
                  <option value="" disabled>请选择用途</option>
                  <option v-for="opt in usagePurposeOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </Select>
              </div>

              <div v-if="form.orderType === 'outbound'" class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">目标位置</label>
                <Input v-model="form.targetLocationText" placeholder="输入目标位置" />
              </div>

              <div class="space-y-2" v-debug-id="DEBUG_IDS.ORDER_CREATE.RETURN_TIME_FIELD">
                <label class="text-sm font-semibold text-slate-700">
                  {{ form.orderType === 'outbound' ? '计划使用时间' : '计划归还时间' }}
                </label>
                <el-date-picker
                  v-model="form.plannedUseTime"
                  type="datetime"
                  placeholder="请选择时间"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  class="!h-10 !w-full"
                />
              </div>

              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-slate-700">备注</label>
                <Textarea
                  v-debug-id="DEBUG_IDS.ORDER_CREATE.REMARK_FIELD"
                  v-model="form.remark"
                  placeholder="补充说明保管、运输或归还要求"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card v-debug-id="DEBUG_IDS.ORDER_CREATE.TOOL_TABLE" class="overflow-hidden border-slate-200/80 bg-white shadow-sm">
          <CardHeader class="border-b border-slate-100 bg-slate-50/30 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="h-8 w-1 rounded-full bg-emerald-500" />
                <CardTitle class="text-base font-bold">已选工装明细</CardTitle>
              </div>
              <Badge variant="secondary" class="border-emerald-100 bg-emerald-50 text-emerald-700">
                已选 {{ selectedTools.length }} 项
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div v-if="selectedTools.length > 0" class="overflow-x-auto">
              <table class="w-full border-collapse text-left text-sm">
                <thead class="border-b border-slate-100 bg-slate-50/50 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  <tr>
                    <th class="px-6 py-3">序列号</th>
                    <th class="px-6 py-3">工装名称</th>
                    <th class="px-6 py-3">工装图号</th>
                    <th class="px-6 py-3">工作包</th>
                    <th class="w-32 px-6 py-3">申请数量</th>
                    <th class="px-6 py-3 text-right">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  <tr v-for="(item, index) in selectedTools" :key="item.toolCode" class="group transition-colors hover:bg-slate-50/50">
                    <td class="px-6 py-4">
                      <div class="font-mono text-xs font-semibold text-slate-900">{{ item.toolCode }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="max-w-[240px] truncate font-semibold text-slate-900">{{ item.toolName || '-' }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="font-mono text-[13px] text-slate-600">{{ item.drawingNo || '-' }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <span class="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600">
                        {{ item.workPackage || '-' }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <Input
                        type="number"
                        v-model.number="item.applyQty"
                        class="h-8 w-20 border-slate-200 text-center text-xs"
                        :min="1"
                      />
                    </td>
                    <td class="px-6 py-4 text-right">
                      <Button variant="ghost" size="sm" class="text-slate-400 hover:bg-rose-50 hover:text-rose-600" @click="removeTool(index)">
                        <Trash2 class="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-else class="flex flex-col items-center justify-center p-12 text-center">
              <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-50">
                <Box class="h-8 w-8 text-slate-300" />
              </div>
              <h3 class="text-sm font-semibold text-slate-900">尚未选择工装</h3>
              <p class="mt-1 max-w-[260px] text-xs text-slate-500">
                点击右上角搜索并添加工装按钮，从工装主表中选择需要的工装。
              </p>
              <Button variant="outline" size="sm" class="mt-4" @click="searchDialogVisible = true">
                打开搜索弹窗
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="space-y-6">
        <Card class="sticky top-8 overflow-hidden border-slate-200/80 bg-white shadow-sm">
          <CardHeader class="border-b border-slate-100 bg-slate-50/30 py-4">
            <div class="flex items-center justify-between">
              <CardTitle class="text-base font-bold">通知预览</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                :disabled="!selectedTools.length"
                class="h-7 text-xs text-primary"
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
              empty-text="创建单据后可在这里预览保管员通知文本。"
              class="border-none bg-slate-50/50 shadow-none"
            />
          </CardContent>
          <CardFooter class="flex flex-col gap-3 border-t border-slate-50 bg-slate-50/30 p-6 pt-0">
            <Button
              v-debug-id="DEBUG_IDS.ORDER_CREATE.SUBMIT_BTN"
              v-permission="'order:submit'"
              class="w-full bg-slate-900 text-white"
              :disabled="!selectedTools.length"
              :loading="submittingOrder"
              @click="submitCreatedOrder"
            >
              提交单据
            </Button>
            <Button
              v-permission="'order:create'"
              variant="outline"
              class="w-full bg-white"
              :disabled="!selectedTools.length"
              :loading="savingDraft"
              @click="saveDraft"
            >
              保存草稿
            </Button>

            <p class="mt-1 text-center text-[10px] text-slate-400">
              提交后会进入保管员确认流程，单据号将在详情页中生成。
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>

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
import { Box, RefreshCw, Search, Trash2 } from 'lucide-vue-next'
import { createOrder, generateKeeperText, submitOrder } from '@/api/orders'
import { DEBUG_IDS } from '@/debug/debugIds'
import ToolSearchDialog from '@/components/tool-io/ToolSearchDialog.vue'
import NotificationPreview from '@/components/tool-io/NotificationPreview.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardFooter from '@/components/ui/CardFooter.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import TabsList from '@/components/ui/TabsList.vue'
import TabsTrigger from '@/components/ui/TabsTrigger.vue'
import Textarea from '@/components/ui/Textarea.vue'
import { useSessionStore } from '@/store/session'

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

const usagePurposeOptions = [
  { label: '现场使用', value: '现场使用' },
  { label: '返修', value: '返修' },
  { label: '定检', value: '定检' }
]

const selectedTools = ref([])
const keeperText = ref('')
const searchDialogVisible = ref(false)
const savingDraft = ref(false)
const submittingOrder = ref(false)

const selectedToolCodes = computed(() => selectedTools.value.map((tool) => tool.toolCode).filter(Boolean))

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
    ElMessage.success(`已新增 ${addedCount} 项工装`)
  }
  if (duplicateCount) {
    ElMessage.warning(`${duplicateCount} 项工装已在明细中，未重复添加`)
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

  if (form.orderType === 'outbound') {
    if (!form.usagePurpose) {
      ElMessage.warning('请选择用途')
      return false
    }
    if (!form.targetLocationText.trim()) {
      ElMessage.warning('请输入目标位置')
      return false
    }
  }

  if (!form.plannedUseTime) {
    ElMessage.warning(form.orderType === 'outbound' ? '请选择计划使用时间' : '请选择计划归还时间')
    return false
  }

  return true
}

function buildPayload() {
  const sanitizedItems = selectedTools.value.filter((item) => item && typeof item === 'object')
  const isOutbound = form.orderType === 'outbound'

  return {
    order_type: form.orderType,
    initiator_id: session.userId || 'anonymous',
    initiator_name: session.userName || 'anonymous',
    initiator_role: session.role || 'team_leader',
    department: '',
    project_code: isOutbound ? form.projectCode : '',
    usage_purpose: isOutbound ? form.usagePurpose : '',
    planned_use_time: form.plannedUseTime,
    planned_return_time: form.plannedReturnTime,
    target_location_text: isOutbound ? form.targetLocationText : '',
    remark: form.remark,
    items: sanitizedItems.map((item) => ({
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
    ElMessage.success(`已生成保管员通知预览：${created.order_no}`)
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

    ElMessage.success(`草稿已保存：${result.order_no}`)
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
:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
  border-radius: 0.375rem !important;
  padding: 0 12px !important;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #0f172a inset !important;
}
</style>
