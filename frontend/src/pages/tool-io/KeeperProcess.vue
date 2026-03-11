<template>
  <div class="flex flex-col h-[calc(100vh-8rem)] lg:flex-row gap-8 overflow-hidden animate-in fade-in duration-500 pb-4">
    <!-- Left: Pending Orders List Sidebar -->
    <Card class="w-full lg:w-[440px] flex flex-col h-full bg-white/50 backdrop-blur-sm border-white/20 shadow-shimmer overflow-hidden">
      <CardHeader class="border-b border-slate-100/50 bg-slate-50/30 py-5 shrink-0">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Inventory Queue</p>
            <CardTitle class="text-xl font-bold text-slate-900 mt-1">待处理单据</CardTitle>
          </div>
          <Button variant="ghost" size="icon" class="rounded-full hover:bg-slate-100" @click="loadPendingOrders" :disabled="loading">
            <RefreshCw class="h-4 w-4 text-slate-500" :class="{ 'animate-spin': loading }" />
          </Button>
        </div>
      </CardHeader>
      
      <CardContent class="flex-1 overflow-y-auto p-0 scrollbar-thin">
        <div v-if="pendingOrders.length" class="divide-y divide-slate-100/50">
          <div
            v-for="order in pendingOrders"
            :key="order.orderNo"
            class="p-5 transition-all hover:bg-white cursor-pointer group relative border-l-4 border-transparent"
            :class="{ 'bg-white border-l-slate-900 shadow-sm z-10': selectedOrder.orderNo === order.orderNo }"
            @click="selectOrder(order)"
          >
            <div class="flex items-start justify-between gap-3 mb-3">
              <span class="text-sm font-bold text-slate-900 group-hover:text-primary transition-colors font-mono tracking-tight">
                {{ order.orderNo }}
              </span>
              <OrderStatusTag :status="order.orderStatus" />
            </div>
            
            <div class="grid grid-cols-2 gap-y-2 text-[11px] font-medium text-slate-500">
              <div class="flex items-center gap-2">
                <div class="h-5 w-5 rounded-lg bg-slate-100 flex items-center justify-center">
                  <User class="h-3 w-3 text-slate-400" />
                </div>
                <span class="text-slate-700">{{ order.initiatorName }}</span>
              </div>
              <div class="flex items-center gap-2 justify-end">
                <div class="h-5 w-5 rounded-lg bg-slate-100 flex items-center justify-center">
                  <Package class="h-3 w-3 text-slate-400" />
                </div>
                <span class="text-slate-700 font-bold">{{ order.toolCount }} 件</span>
              </div>
              <div class="flex items-center gap-2 col-span-2 mt-1">
                <div class="h-5 w-5 rounded-lg bg-slate-100 flex items-center justify-center">
                  <FileCode class="h-3 w-3 text-slate-400" />
                </div>
                <span class="truncate font-mono text-slate-400">{{ order.projectCode || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="loading" class="p-8 space-y-4">
          <div v-for="i in 4" :key="i" class="space-y-2">
            <div class="h-4 w-2/3 bg-slate-100 animate-pulse rounded" />
            <div class="h-3 w-1/2 bg-slate-50 animate-pulse rounded" />
          </div>
        </div>
        
        <div v-else class="flex flex-col items-center justify-center h-full p-8 text-center opacity-60">
          <div class="h-12 w-12 rounded-full bg-slate-50 flex items-center justify-center mb-3">
            <Inbox class="h-6 w-6 text-slate-300" />
          </div>
          <p class="text-sm text-slate-500 font-medium">暂无待处理单据</p>
        </div>
      </CardContent>
    </Card>

    <!-- Right: Selected Order Processing Workbench -->
    <Card class="flex-1 flex flex-col h-full bg-white shadow-2xl border-border/50 overflow-hidden">
      <CardHeader class="border-b border-slate-100 py-5 shrink-0">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div>
              <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Process Workbench</p>
              <CardTitle class="text-xl font-bold text-slate-900 mt-1">单据处理工作台</CardTitle>
            </div>
            <Badge v-if="selectedOrder.orderNo" variant="secondary" class="bg-emerald-50 text-emerald-700 border-emerald-100 font-mono text-xs px-3 py-1">
              {{ selectedOrder.orderNo }}
            </Badge>
          </div>
          
          <div v-if="selectedOrder.orderNo" class="flex gap-3">
            <Button 
              v-if="canFinalConfirm" 
              variant="default" 
              size="sm" 
              class="font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 shadow-lg" 
              @click="finalizeCurrentOrder"
            >
              最终确认
            </Button>
            <Button variant="outline" size="sm" class="font-bold text-slate-600" @click="previewTransport" :disabled="!selectedOrder.orderNo">
              预览通知
            </Button>
            <Button variant="destructive" size="sm" class="font-bold" :disabled="!canReview" @click="rejectCurrentOrder">
              驳回
            </Button>
            <Button variant="default" size="sm" class="font-bold bg-slate-900 text-white shadow-lg" :disabled="!canReview" @click="approveOrder">
              确认通过
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent class="flex-1 overflow-y-auto p-0 scrollbar-thin">
        <!-- Empty State -->
        <div v-if="!selectedOrder.orderNo" class="flex flex-col items-center justify-center h-full p-12 text-center">
          <div class="h-20 w-20 rounded-full bg-slate-50 flex items-center justify-center mb-6">
            <MousePointer2 class="h-10 w-10 text-slate-300" />
          </div>
          <h3 class="text-lg font-semibold text-slate-900 mb-2">选择一个单据开始处理</h3>
          <p class="text-sm text-slate-500 max-w-sm">
            从左侧列表中点击任意待处理单据，即可在此处查看详情并进行保管员确认操作。
          </p>
        </div>

        <!-- Processing Form -->
        <div v-else class="p-6 space-y-8">
          <!-- Summary Info -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6 p-5 rounded-xl bg-slate-50/50 border border-slate-100">
            <div v-for="field in summaryFields" :key="field.label" class="space-y-1">
              <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">{{ field.label }}</p>
              <p class="text-sm font-medium text-slate-900">{{ field.value }}</p>
            </div>
          </div>

          <!-- Transport Config -->
          <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="text-sm font-semibold text-slate-700">运输类型</label>
              <Input v-model="confirmForm.transportType" placeholder="如：人工 / 叉车 / 外协" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-semibold text-slate-700">运输负责人</label>
              <Input v-model="confirmForm.transportAssigneeName" placeholder="请输入姓名" />
            </div>
            <div class="space-y-2 md:col-span-2">
              <label class="text-sm font-semibold text-slate-700">保管员备注</label>
              <Textarea v-model="confirmForm.keeperRemark" placeholder="请输入确认时的备注信息..." />
            </div>
          </div>

          <!-- Item Verification List -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Box class="h-4 w-4" /> 工装明细确认
              </h4>
              <span class="text-xs text-slate-400">共 {{ confirmItems.length }} 项</span>
            </div>
            
            <div class="border rounded-xl overflow-hidden bg-white">
              <table class="w-full text-sm text-left border-collapse">
                <thead class="bg-slate-50/80 border-b border-slate-100 text-slate-500 text-[11px] font-bold uppercase tracking-wider">
                  <tr>
                    <th class="px-4 py-3 font-bold">工装信息</th>
                    <th class="px-4 py-3 font-bold">建议位置</th>
                    <th class="px-4 py-3 font-bold w-[180px]">确认位置</th>
                    <th class="px-4 py-3 font-bold w-[120px]">状态</th>
                    <th class="px-4 py-3 font-bold w-[120px]">批准数量</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  <tr v-for="item in confirmItems" :key="item.toolCode" class="group">
                    <td class="px-4 py-4">
                      <p class="font-semibold text-slate-900 mb-0.5">{{ item.toolCode }}</p>
                      <p class="text-xs text-slate-500">{{ item.toolName }}</p>
                    </td>
                    <td class="px-4 py-4 text-slate-600 italic">
                      {{ item.currentLocationText || '-' }}
                    </td>
                    <td class="px-4 py-4">
                      <Input v-model="item.locationText" placeholder="确认位置" class="h-8 text-xs border-slate-200" />
                    </td>
                    <td class="px-4 py-4">
                      <Select v-model="item.status" class="h-8 text-xs border-slate-200">
                        <option value="approved">通过</option>
                        <option value="rejected">拒绝</option>
                      </Select>
                    </td>
                    <td class="px-4 py-4">
                      <div class="flex items-center gap-2">
                        <Input 
                          type="number" 
                          v-model.number="item.approvedQty" 
                          class="h-8 text-xs w-16 text-center border-slate-200"
                          :max="item.applyQty"
                        />
                        <span class="text-[10px] text-slate-400">/ {{ item.applyQty }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Notification Previews -->
          <div v-if="transportPreview || wechatPreview" class="grid md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-2">
            <NotificationPreview 
              type="transport" 
              :content="transportPreview" 
              empty-text="暂无运输通知预览"
            />
            <NotificationPreview 
              type="wechat" 
              :content="wechatPreview" 
              empty-text="暂无微信复制文本"
            />
          </div>

          <!-- Bottom Actions (Mobile) -->
          <div class="flex justify-end gap-3 pt-6 border-t border-slate-100 lg:hidden">
            <Button variant="destructive" :disabled="!canReview" @click="rejectCurrentOrder">驳回</Button>
            <Button variant="default" :disabled="!canReview" @click="approveOrder">确认通过</Button>
          </div>
          
          <!-- Notify Action -->
          <div v-if="canNotify" class="flex items-center justify-between p-4 rounded-xl bg-blue-50/50 border border-blue-100/50">
            <div class="flex items-center gap-3 text-blue-700">
              <Info class="h-5 w-5" />
              <p class="text-sm font-medium">保管员确认已完成，可点击右侧按钮发送飞书通知。</p>
            </div>
            <Button variant="default" size="sm" class="bg-blue-600 hover:bg-blue-700" @click="sendTransportNotify">
              发送飞书通知
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  RefreshCw,
  Inbox,
  User,
  Package,
  FileCode,
  MousePointer2,
  Box,
  Info
} from 'lucide-vue-next'
import {
  finalConfirmOrder,
  getFinalConfirmAvailability,
  generateTransportText,
  getOrderDetail,
  getPendingKeeperOrders,
  keeperConfirmOrder,
  notifyTransport,
  rejectOrder
} from '@/api/toolIO'
import { useSessionStore } from '@/store/session'
import NotificationPreview from '@/components/tool-io/NotificationPreview.vue'
import OrderStatusTag from '@/components/tool-io/OrderStatusTag.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Select from '@/components/ui/Select.vue'

const session = useSessionStore()
const pendingOrders = ref([])
const selectedOrder = ref({})
const confirmItems = ref([])
const transportPreview = ref('')
const wechatPreview = ref('')
const loading = ref(false)
const finalConfirmState = ref({ available: false, reason: '' })

const confirmForm = reactive({
  transportType: '',
  transportAssigneeName: '',
  keeperRemark: ''
})

const summaryFields = computed(() => {
  if (!selectedOrder.value.orderNo) return []
  return [
    { label: '单据类型', value: selectedOrder.value.orderType === 'outbound' ? '出库' : '入库' },
    { label: '发起人', value: selectedOrder.value.initiatorName || '-' },
    { label: '项目代号', value: selectedOrder.value.projectCode || '-' },
    { label: '目标位置', value: selectedOrder.value.targetLocationText || '-' }
  ]
})

const canReview = computed(
  () =>
    session.role === 'keeper' &&
    ['submitted', 'partially_confirmed'].includes(selectedOrder.value.orderStatus)
)

const canNotify = computed(
  () =>
    session.role === 'keeper' &&
    ['keeper_confirmed', 'partially_confirmed', 'transport_notified'].includes(selectedOrder.value.orderStatus)
)

const canFinalConfirm = computed(() => Boolean(finalConfirmState.value.available))

function resetPreview() {
  transportPreview.value = ''
  wechatPreview.value = ''
}

function buildEditableItems(order) {
  return (order.items || []).map((item) => {
    const defaultApprovedQty =
      item.itemStatus === 'approved'
        ? item.approvedQty || item.applyQty || 1
        : item.itemStatus === 'rejected'
          ? 0
          : item.applyQty || 1

    return {
      ...item,
      locationText: item.keeperConfirmLocationText || item.currentLocationText || '',
      status: item.itemStatus === 'rejected' ? 'rejected' : 'approved',
      approvedQty: defaultApprovedQty,
      checkRemark: item.checkRemark || ''
    }
  })
}

async function loadPendingOrders() {
  loading.value = true
  try {
    const result = await getPendingKeeperOrders(session.role === 'keeper' ? session.userId : undefined)
    if (result.success) {
      pendingOrders.value = result.data
    }
  } finally {
    loading.value = false
  }
}

async function selectOrder(row) {
  const result = await getOrderDetail(row.orderNo)
  if (!result.success) return

  selectedOrder.value = result.data
  confirmItems.value = buildEditableItems(result.data)
  confirmForm.transportType = result.data.transportType || ''
  confirmForm.transportAssigneeName = result.data.transportOperatorName || ''
  confirmForm.keeperRemark = ''
  const availability = await getFinalConfirmAvailability(row.orderNo, {
    operator_id: session.userId,
    operator_role: session.role
  }).catch(() => ({ success: false, available: false }))
  finalConfirmState.value = availability.success ? availability : { available: false, reason: '' }
  resetPreview()
}

async function previewTransport() {
  const result = await generateTransportText(selectedOrder.value.orderNo)
  if (!result.success) return
  transportPreview.value = result.text || ''
  wechatPreview.value = result.wechat_text || ''
}

async function approveOrder() {
  const invalidItem = confirmItems.value.find((item) => !item.locationText?.trim() && item.status === 'approved')
  if (invalidItem) {
    ElMessage.warning(`请填写工装 ${invalidItem.toolCode} 的确认位置`)
    return
  }

  const payload = {
    keeper_id: session.userId,
    keeper_name: session.userName,
    transport_type: confirmForm.transportType,
    transport_assignee_id: confirmForm.transportAssigneeName,
    transport_assignee_name: confirmForm.transportAssigneeName,
    keeper_remark: confirmForm.keeperRemark,
    items: confirmItems.value.map((item) => ({
      tool_code: item.toolCode,
      location_id: null,
      location_text: item.locationText,
      check_result: item.status,
      check_remark: item.checkRemark || confirmForm.keeperRemark,
      approved_qty: item.status === 'approved' ? item.approvedQty || item.applyQty || 1 : 0,
      status: item.status
    })),
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  }

  const result = await keeperConfirmOrder(selectedOrder.value.orderNo, payload)
  if (!result.success) return

  ElMessage.success('保管员确认已提交')
  await selectOrder(selectedOrder.value)
  await loadPendingOrders()
}

async function rejectCurrentOrder() {
  const rejectReason = await ElMessageBox.prompt('请输入驳回原因', '驳回单据', {
    confirmButtonText: '确认',
    cancelButtonText: '取消'
  }).then(({ value }) => value)

  if (!rejectReason) return

  const result = await rejectOrder(selectedOrder.value.orderNo, {
    reject_reason: rejectReason,
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  })
  if (!result.success) return

  ElMessage.success('单据已驳回')
  await loadPendingOrders()
  selectedOrder.value = {}
  confirmItems.value = []
  resetPreview()
}

async function sendTransportNotify() {
  const result = await notifyTransport(selectedOrder.value.orderNo, {
    notify_type: 'transport_notice',
    notify_channel: 'feishu',
    receiver: confirmForm.transportAssigneeName,
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  })
  if (!result.success) return

  wechatPreview.value = result.wechat_text || ''
  ElMessage.success('运输通知已处理')
  await selectOrder(selectedOrder.value)
  await loadPendingOrders()
}

async function finalizeCurrentOrder() {
  const result = await finalConfirmOrder(selectedOrder.value.orderNo, {
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  })
  if (!result.success) return

  ElMessage.success('Order final confirmation completed')
  await selectOrder(selectedOrder.value)
  await loadPendingOrders()
}

loadPendingOrders()
</script>

<style scoped>
/* Scrollbar customization for the list */
.scrollbar-thin::-webkit-scrollbar {
  width: 5px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 20px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
