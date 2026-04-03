<template>
  <div class="animate-in fade-in space-y-10 pb-20 duration-500 text-foreground">
    <header class="relative overflow-hidden rounded-3xl bg-primary px-8 py-12 text-primary-foreground shadow-2xl">
      <div class="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <Badge variant="outline" class="mb-4 border-primary-foreground/20 bg-primary-foreground/10 text-primary-foreground backdrop-blur-sm">
            创建单据
          </Badge>
          <h1 class="text-3xl font-bold tracking-tight md:text-4xl text-primary-foreground">工装出入库申请</h1>
          <p class="mt-2 max-w-lg text-primary-foreground/80">
            先从工装主表选择工装，再填写用途、目标位置和计划时间，最终生成并提交流出库单。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <Button
            v-debug-id="DEBUG_IDS.ORDER_CREATE.CANCEL_BTN"
            variant="ghost"
            class="border border-primary-foreground/20 text-primary-foreground hover:bg-white/10"
            @click="resetForm"
          >
            <RefreshCw class="mr-2 h-4 w-4" />
            重置表单
          </Button>
          <Button
            v-debug-id="DEBUG_IDS.ORDER_CREATE.TOOL_SEARCH_FIELD"
            class="bg-white font-bold text-slate-900 shadow-lg hover:bg-slate-100 border-none"
            @click="searchDialogVisible = true"
          >
            <Search class="mr-2 h-4 w-4" />
            搜索并添加工装
          </Button>
        </div>
      </div>

      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary-foreground/10 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/2 h-32 w-32 rounded-full bg-emerald-500/10 blur-2xl"></div>
    </header>

    <div class="grid grid-cols-1 items-start gap-10 lg:grid-cols-[1fr_400px]">
      <div class="space-y-8">
        <Card v-debug-id="DEBUG_IDS.ORDER_CREATE.FORM" class="overflow-hidden border-border bg-card shadow-sm">
          <CardHeader class="border-b border-border bg-muted/30 py-4">
            <div class="flex items-center gap-2">
              <div class="h-8 w-1 rounded-full bg-primary" />
              <CardTitle class="text-base font-bold text-foreground">基本信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6">
            <div class="grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2">
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-semibold text-foreground">单据类型</label>
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
                <label class="text-sm font-semibold text-foreground">用途</label>
                <Select v-debug-id="DEBUG_IDS.ORDER_CREATE.USAGE_PURPOSE_SELECT" v-model="form.usagePurpose" placeholder="请选择用途">
                  <option value="" disabled>请选择用途</option>
                  <option v-for="opt in usagePurposeOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </Select>
              </div>

              <div v-if="form.orderType === 'outbound'" class="space-y-2" v-debug-id="DEBUG_IDS.ORDER_CREATE.TARGET_LOCATION_FIELD">
                <label class="text-sm font-semibold text-foreground">目标位置</label>
                <el-select v-model="form.targetLocationText" placeholder="选择目标位置" class="!w-full">
                  <el-option label="A06" value="A06" />
                  <el-option label="A02" value="A02" />
                  <el-option label="A08" value="A08" />
                </el-select>
              </div>

              <div class="space-y-2" v-debug-id="DEBUG_IDS.ORDER_CREATE.RETURN_TIME_FIELD">
                <label class="text-sm font-semibold text-foreground">
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
                <label class="text-sm font-semibold text-foreground">备注</label>
                <Textarea
                  v-debug-id="DEBUG_IDS.ORDER_CREATE.REMARK_FIELD"
                  v-model="form.remark"
                  placeholder="补充说明保管、运输或归还要求"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card v-debug-id="DEBUG_IDS.ORDER_CREATE.TOOL_LIST" class="overflow-hidden border-border bg-card shadow-sm">
          <CardHeader class="border-b border-border bg-muted/30 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="h-8 w-1 rounded-full bg-emerald-500" />
                <CardTitle class="text-base font-bold text-foreground">已选工装明细</CardTitle>
              </div>
              <Badge variant="secondary" class="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
                {{ selectedTools.length }} 项已选
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div v-if="selectedTools.length > 0" class="overflow-x-auto">
              <table class="w-full border-collapse text-left text-sm">
                <thead class="border-b border-border bg-muted/50 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                  <tr>
                    <th class="px-6 py-3">工装信息</th>
                    <th class="px-6 py-3">图号 / 机型</th>
                    <th class="px-6 py-3">当前库位</th>
                    <th class="px-6 py-3 w-32">申请数量</th>
                    <th class="px-6 py-3 text-right">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border">
                  <tr v-for="(item, index) in selectedTools" :key="item.toolCode" class="group hover:bg-muted/30 transition-colors">
                    <td class="px-6 py-4">
                      <div class="font-semibold text-foreground">{{ item.toolCode }}</div>
                      <div class="mt-0.5 max-w-[200px] truncate text-xs text-muted-foreground">{{ item.toolName }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="font-mono text-[13px] text-muted-foreground">{{ item.drawingNo || '-' }}</div>
                      <div class="mt-0.5 text-[11px] text-muted-foreground/60">{{ item.specModel || '-' }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <span class="inline-flex items-center rounded-md bg-muted px-2 py-1 text-[11px] font-medium text-muted-foreground">
                        {{ item.currentLocationText || '未知' }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <Input
                        type="number"
                        v-model.number="item.applyQty"
                        class="h-8 w-20 border-border text-center text-xs"
                        :min="1"
                      />
                    </td>
                    <td class="px-6 py-4 text-right">
                      <Button variant="ghost" size="sm" class="text-muted-foreground hover:bg-destructive/10 hover:text-destructive" @click="removeTool(index)">
                        <Trash2 class="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-else class="flex flex-col items-center justify-center p-12 text-center">
              <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <Box class="h-8 w-8 text-muted-foreground/40" />
              </div>
              <h3 class="text-sm font-semibold text-foreground">尚未选择工装</h3>
              <p class="mt-1 max-w-[240px] text-xs text-muted-foreground">
                点击右上角的“搜索并添加工装”按钮，从工装主表中选择您需要的项目。
              </p>
              <Button variant="outline" size="sm" class="mt-4" @click="searchDialogVisible = true">
                立即去搜索
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="space-y-6">
        <Card class="sticky top-8 overflow-hidden border-border bg-card shadow-sm">
          <CardHeader class="border-b border-border bg-muted/30 py-4">
            <div class="flex items-center justify-between">
              <CardTitle class="text-base font-bold text-foreground">文本预览</CardTitle>
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
              empty-text="生成预览后，此处将显示发送给保管员的结构化申请文本。"
              class="border-none bg-muted/50 shadow-none"
            />
          </CardContent>
          <CardFooter class="flex flex-col gap-3 border-t border-border bg-muted/30 p-6 pt-0 mt-4">
            <Button
              v-permission="'order:submit'"
              class="w-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90"
              :disabled="!selectedTools.length"
              :loading="submittingOrder"
              @click="submitCreatedOrder"
            >
              提交单据
            </Button>
            <Button
              v-permission="'order:create'"
              variant="outline"
              class="w-full bg-card hover:bg-accent hover:text-accent-foreground"
              :disabled="!selectedTools.length"
              :loading="savingDraft"
              @click="saveDraft"
            >
              保存草稿
            </Button>
            <p class="mt-1 text-center text-[10px] text-muted-foreground">
              提交后单据将流转至“已提交”状态，等待保管员确认。
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
import { createOrder, previewKeeperText, submitOrder, updateOrder } from '@/api/orders'
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
const createdOrderNo = ref('')

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

  const preview = await previewKeeperText(buildPayload())
  if (!preview.success) {
    ElMessage.error(preview.error || '生成预览失败')
    return
  }
  if (preview.warning) {
    ElMessage.warning(preview.warning)
  }
  keeperText.value = preview.text
  ElMessage.success('已生成保管员通知预览')
}

async function saveDraft() {
  if (savingDraft.value || submittingOrder.value || !validateBeforeSubmit()) return
  savingDraft.value = true

  try {
    const payload = buildPayload()
    const result = createdOrderNo.value
      ? await updateOrder(createdOrderNo.value, payload)
      : await createOrder(payload)
    if (!result.success) {
      ElMessage.error(result.error || '提交单据失败')
      return
    }

    const orderNo = result.order_no || createdOrderNo.value
    createdOrderNo.value = orderNo || ''
    ElMessage.success(`草稿已保存：${orderNo}`)
    router.push(`/inventory/${orderNo}`)
  } finally {
    savingDraft.value = false
  }
}

async function persistCurrentDraft() {
  const payload = buildPayload()
  if (!createdOrderNo.value) {
    const created = await createOrder(payload)
    if (!created.success) {
      return created
    }
    createdOrderNo.value = created.order_no || ''
    return created
  }

  const updated = await updateOrder(createdOrderNo.value, payload)
  if (updated.success) {
    updated.order_no = updated.order_no || createdOrderNo.value
  }
  return updated
}

async function submitCreatedOrder() {
  if (submittingOrder.value || savingDraft.value || !validateBeforeSubmit()) return
  submittingOrder.value = true

  try {
    const draftResult = await persistCurrentDraft()
    if (!draftResult.success) {
      ElMessage.error(draftResult.error || '创建单据失败')
      return
    }
    if (draftResult.warning) {
      ElMessage.warning(draftResult.warning)
    }
    const orderNo = draftResult.order_no || createdOrderNo.value

    const result = await submitOrder(orderNo, {
      operator_id: session.userId || 'anonymous',
      operator_name: session.userName || 'anonymous',
      operator_role: session.role || 'team_leader'
    })

    if (!result.success) {
      ElMessage.error(result.error || '保存草稿失败')
      return
    }
    if (result.warning) {
      ElMessage.warning(result.warning)
    }

    ElMessage.success(`单据已提交：${orderNo}`)
    router.push(`/inventory/${orderNo}`)
  } catch (error) {
    console.error('[OrderCreate] submitCreatedOrder failed:', error)
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
  createdOrderNo.value = ''
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
