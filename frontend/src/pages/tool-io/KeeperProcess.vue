<template>
  <div class="h-[calc(100vh-8rem)] flex flex-col gap-4">
    <el-tabs v-model="activeTab" class="custom-tabs">
      <el-tab-pane label="订单处理" name="orders">
        <div class="flex flex-col h-[calc(100vh-12rem)] lg:flex-row gap-8 overflow-hidden animate-in fade-in duration-500 pb-4 text-foreground">
          <!-- Left: Pending Orders List Sidebar -->
          <Card class="w-full lg:w-[440px] flex flex-col h-full bg-card/50 backdrop-blur-sm border-border/20 shadow-shimmer overflow-hidden">
            <CardHeader class="border-b border-border/50 bg-muted/30 py-5 shrink-0">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">待处理队列</p>
                  <CardTitle class="text-xl font-bold text-foreground mt-1">待处理单据</CardTitle>
                </div>
                <Button v-debug-id="DEBUG_IDS.KEEPER.REFRESH_BTN" variant="ghost" size="icon" class="rounded-full hover:bg-accent" @click="loadPendingOrders" :disabled="loading">
                  <RefreshCw class="h-4 w-4 text-muted-foreground" :class="{ 'animate-spin': loading }" />
                </Button>
              </div>
            </CardHeader>

            <CardContent v-debug-id="DEBUG_IDS.KEEPER.PENDING_LIST" class="flex-1 overflow-y-auto p-0 scrollbar-thin">
              <div v-if="pendingOrders.length" class="divide-y divide-border/50">
                <div
                  v-for="order in pendingOrders"
                  :key="order.orderNo"
                  v-debug-id="DEBUG_IDS.KEEPER.ORDER_CARD"
                  class="p-5 transition-all hover:bg-accent/50 cursor-pointer group relative border-l-4 border-transparent"
                  :class="{ 'bg-accent border-l-primary shadow-sm z-10': selectedOrder.orderNo === order.orderNo }"
                  @click="selectOrder(order)"
                >

                  <div class="flex items-start justify-between gap-3 mb-3">
                    <span class="text-sm font-bold text-foreground group-hover:text-primary transition-colors font-mono tracking-tight">
                      {{ order.orderNo }}
                    </span>
                    <OrderStatusTag :status="order.orderStatus" />
                  </div>

                  <div class="grid grid-cols-2 gap-y-2 text-[11px] font-medium text-muted-foreground">
                    <div class="flex items-center gap-2">
                      <div class="h-5 w-5 rounded-lg bg-muted flex items-center justify-center">
                        <User class="h-3 w-3 text-muted-foreground" />
                      </div>
                      <span class="text-foreground/80">{{ order.initiatorName }}</span>
                    </div>
                    <div class="flex items-center gap-2 justify-end">
                      <div class="h-5 w-5 rounded-lg bg-muted flex items-center justify-center">
                        <Package class="h-3 w-3 text-muted-foreground" />
                      </div>
                      <span class="text-foreground/80 font-bold">{{ order.toolCount }} 件</span>
                    </div>
                    <div class="flex items-center gap-2 col-span-2 mt-1">
                      <div class="h-5 w-5 rounded-lg bg-muted flex items-center justify-center">
                        <FileCode class="h-3 w-3 text-muted-foreground" />
                      </div>
                      <span class="truncate font-mono text-muted-foreground/60">{{ order.projectCode || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="loading" class="p-8 space-y-4">
                <div v-for="i in 4" :key="i" class="space-y-2">
                  <div class="h-4 w-2/3 bg-muted animate-pulse rounded" />
                  <div class="h-3 w-1/2 bg-muted/50 animate-pulse rounded" />
                </div>
              </div>

              <div v-else class="flex flex-col items-center justify-center h-full p-8 text-center opacity-60">
                <div class="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-3">
                  <Inbox class="h-6 w-6 text-muted-foreground/40" />
                </div>
                <p class="text-sm text-muted-foreground font-medium">暂无待处理单据</p>
              </div>
            </CardContent>
          </Card>

          <!-- Right: Selected Order Processing Workbench -->
          <Card class="flex-1 flex flex-col h-full bg-card shadow-2xl border-border/50 overflow-hidden">
            <CardHeader class="border-b border-border py-5 shrink-0">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div>
                    <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">处理工作台</p>
                    <CardTitle class="text-xl font-bold text-foreground mt-1">单据处理工作台</CardTitle>
                  </div>
                  <Badge v-if="selectedOrder.orderNo" variant="secondary" class="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 font-mono text-xs px-3 py-1">
                    {{ selectedOrder.orderNo }}
                  </Badge>
                </div>

                <div v-if="selectedOrder.orderNo" class="flex gap-3">
                  <Button
                    v-if="canFinalConfirm"
                    v-permission="'order:final_confirm'"
                    variant="default"
                    size="sm"
                    class="font-bold bg-emerald-500 text-primary-foreground hover:bg-emerald-400 shadow-lg border-none"
                    @click="finalizeCurrentOrder"
                  >
                    最终确认
                  </Button>
                  <Button v-debug-id="DEBUG_IDS.KEEPER.TRANSPORT_PREVIEW_BTN" variant="outline" size="sm" class="font-bold text-muted-foreground border-border hover:bg-accent" @click="previewTransport" :disabled="!selectedOrder.orderNo">
                    预览通知
                  </Button>
                  <Button
                    v-if="canDispatchTransport"
                    v-debug-id="DEBUG_IDS.KEEPER.DISPATCH_TRANSPORT_BTN"
                    variant="outline"
                    size="sm"
                    class="font-bold text-primary border-primary/50 hover:bg-primary/10"
                    @click="openDispatchTransportDialog"
                  >
                    <Truck class="h-4 w-4 mr-1" />
                    派遣运输
                  </Button>
                  <Button v-debug-id="DEBUG_IDS.KEEPER.REJECT_BTN" variant="destructive" size="sm" class="font-bold shadow-lg" :disabled="!canReview" @click="rejectCurrentOrder">
                    驳回
                  </Button>
                  <Button v-debug-id="DEBUG_IDS.KEEPER.APPROVE_BTN" variant="default" size="sm" class="font-bold bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 border-none" :disabled="!canReview" @click="approveOrder">
                    确认通过
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent class="flex-1 overflow-y-auto p-0 scrollbar-thin">
              <!-- Empty State -->
              <div v-if="!selectedOrder.orderNo" class="flex flex-col items-center justify-center h-full p-12 text-center">
                <div class="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
                  <MousePointer2 class="h-10 w-10 text-muted-foreground/30" />
                </div>
                <h3 class="text-lg font-semibold text-foreground mb-2">选择一个单据开始处理</h3>
                <p class="text-sm text-muted-foreground max-w-sm">
                  从左侧列表中点击任意待处理单据，即可在此处查看详情并进行保管员确认操作。
                </p>
              </div>

              <!-- Processing Form -->
              <div v-else class="p-6 space-y-8">
                <!-- Summary Info -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6 p-5 rounded-xl bg-muted/30 border border-border/50">
                  <div v-for="field in summaryFields" :key="field.label" class="space-y-1">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{{ field.label }}</p>
                    <p class="text-sm font-medium text-foreground">{{ field.value }}</p>
                  </div>
                </div>

                <!-- Transport Config -->
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-sm font-semibold text-foreground">运输类型</label>
                    <Input v-model="confirmForm.transportType" placeholder="如：人工 / 叉车 / 外协" />
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-semibold text-foreground">运输负责人</label>
                    <Input v-model="confirmForm.transportAssigneeName" placeholder="请输入姓名" />
                  </div>
                  <div class="space-y-2 md:col-span-2">
                    <label class="text-sm font-semibold text-foreground">保管员备注</label>
                    <Textarea v-model="confirmForm.keeperRemark" placeholder="请输入确认时的备注信息..." />
                  </div>
                </div>

                <!-- Item Verification List -->
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <h4 class="text-sm font-bold text-foreground flex items-center gap-2">
                      <Box class="h-4 w-4" /> 工装明细确认
                    </h4>
                    <span class="text-xs text-muted-foreground">共 {{ confirmItems.length }} 项</span>
                  </div>

                  <div class="border border-border rounded-xl overflow-hidden bg-card">
                    <table class="w-full text-sm text-left border-collapse">
                      <thead class="bg-muted/50 border-b border-border text-muted-foreground text-[11px] font-bold uppercase tracking-wider">
                        <tr>
                          <th class="px-4 py-3 font-bold">工装信息</th>
                          <th class="px-4 py-3 font-bold">建议位置</th>
                          <th class="px-4 py-3 font-bold w-[180px]">确认位置</th>
                          <th class="px-4 py-3 font-bold w-[120px]">状态</th>
                          <th class="px-4 py-3 font-bold w-[120px]">批准数量</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-border">
                        <tr v-for="item in confirmItems" :key="item.toolCode" class="group hover:bg-muted/20 transition-colors">
                          <td class="px-4 py-4">
                            <p class="font-semibold text-foreground mb-0.5">{{ item.toolCode }}</p>
                            <p class="text-xs text-muted-foreground">{{ item.toolName }}</p>
                          </td>
                          <td class="px-4 py-4 text-muted-foreground/80 italic">
                            {{ item.currentLocationText || '-' }}
                          </td>
                          <td class="px-4 py-4">
                            <Input v-model="item.locationText" placeholder="确认位置" class="h-8 text-xs border-border" />
                          </td>
                          <td class="px-4 py-4">
                            <Select v-model="item.status" class="h-8 text-xs border-border">
                              <option value="approved">通过</option>
                              <option value="rejected">拒绝</option>
                            </Select>
                          </td>
                          <td class="px-4 py-4">
                            <div class="flex items-center gap-2">
                              <Input
                                type="number"
                                v-model.number="item.approvedQty"
                                class="h-8 w-16 text-center border-border text-xs"
                                :max="item.applyQty"
                              />
                              <span class="text-[10px] text-muted-foreground">/ {{ item.applyQty }}</span>
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
                <div class="flex justify-end gap-3 pt-6 border-t border-border lg:hidden">
                  <Button variant="destructive" :disabled="!canReview" @click="rejectCurrentOrder">驳回</Button>
                  <Button variant="default" :disabled="!canReview" @click="approveOrder">确认通过</Button>
                </div>

                <!-- Notify Action -->
                <div v-if="canNotify" class="flex items-center justify-between p-4 rounded-xl bg-primary/10 border border-primary/20">
                  <div class="flex items-center gap-3 text-primary">
                    <div class="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center">
                      <div class="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center">
                        <Info class="h-3 w-3 text-primary" />
                      </div>
                    </div>
                    <p class="text-sm font-medium">保管员确认已完成，可点击右侧按钮发送飞书通知。</p>
                  </div>
                  <Button variant="default" size="sm" class="bg-primary hover:bg-primary/90 text-primary-foreground border-none" @click="sendTransportNotify">
                    发送飞书通知
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </el-tab-pane>

      <el-tab-pane v-if="showToolStatusTab" label="工装状态管理" name="tool-status">
        <div class="flex flex-col h-[calc(100vh-12rem)] lg:flex-row gap-8 overflow-hidden animate-in fade-in duration-500 pb-4 text-foreground">
          <!-- Left: Tool Selection Sidebar -->
          <Card class="w-full lg:w-[440px] flex flex-col h-full bg-card/50 backdrop-blur-sm border-border/20 shadow-shimmer overflow-hidden">
            <CardHeader class="border-b border-border/50 bg-muted/30 py-5 shrink-0">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">工装选择</p>
                  <CardTitle class="text-xl font-bold text-foreground mt-1">已选工装列表</CardTitle>
                </div>
                <Badge variant="outline" class="font-mono text-xs px-2 py-0.5">
                  {{ selectedTools.length }} 件
                </Badge>
              </div>
              <div class="mt-4">
                <div class="relative group">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-primary">
                    <Search class="h-4 w-4 text-muted-foreground" />
                  </div>
                  <Input
                    v-model="toolSearchKeyword"
                    placeholder="输入工装编码后按回车搜索"
                    class="pl-10 bg-background/50 border-border/50 focus:border-primary/50 transition-all"
                    @keyup.enter="handleSearchTools(toolSearchKeyword)"
                    :disabled="searchLoading"
                  />
                  <div v-if="searchLoading" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <RefreshCw class="h-4 w-4 text-muted-foreground animate-spin" />
                  </div>
                </div>
              </div>
            </CardHeader>

            <CardContent class="flex-1 overflow-y-auto p-0 scrollbar-thin">
              <div v-if="selectedTools.length" class="divide-y divide-border/50">
                <div
                  v-for="tool in selectedTools"
                  :key="tool.toolCode"
                  class="p-5 transition-all hover:bg-accent/50 group relative"
                >
                  <div class="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <p class="text-sm font-bold text-foreground font-mono">{{ tool.toolCode }}</p>
                      <p class="text-[11px] text-muted-foreground mt-0.5">{{ tool.toolName }}</p>
                    </div>
                    <Button variant="ghost" size="icon" class="h-8 w-8 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10" @click="removeTool(tool)">
                      <Trash2 class="h-4 w-4" />
                    </Button>
                  </div>
                  <div class="flex items-center justify-between mt-3">
                    <Badge variant="secondary" class="text-[10px] bg-muted/50 border-border/50">
                      {{ tool.statusText || tool.currentStatus || '未知状态' }}
                    </Badge>
                    <Button variant="link" size="sm" class="h-auto p-0 text-[10px] text-primary/70 hover:text-primary flex items-center gap-1" @click="loadToolHistory(tool.toolCode)">
                      <History class="h-3 w-3" /> 查看历史
                    </Button>
                  </div>
                </div>
              </div>
              <div v-else class="flex flex-col items-center justify-center h-full p-8 text-center opacity-60">
                <div class="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-3">
                  <Box class="h-6 w-6 text-muted-foreground/40" />
                </div>
                <p class="text-sm text-muted-foreground font-medium">请搜索并添加工装</p>
              </div>
            </CardContent>
          </Card>

          <!-- Right: Batch Action Workbench -->
          <Card class="flex-1 flex flex-col h-full bg-card shadow-2xl border-border/50 overflow-hidden">
            <CardHeader class="border-b border-border py-5 shrink-0">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">批量操作</p>
                  <CardTitle class="text-xl font-bold text-foreground mt-1">状态变更设置</CardTitle>
                </div>
                <Button
                  variant="default"
                  size="sm"
                  class="bg-primary hover:bg-primary/90 text-primary-foreground font-bold shadow-lg flex items-center gap-2"
                  :disabled="selectedTools.length === 0 || submittingStatus"
                  @click="applyStatusChange"
                >
                  <CheckCircle2 v-if="!submittingStatus" class="h-4 w-4" />
                  <RefreshCw v-else class="h-4 w-4 animate-spin" />
                  确认变更
                </Button>
              </div>
            </CardHeader>

            <CardContent class="flex-1 overflow-y-auto p-6 scrollbar-thin">
              <div class="grid md:grid-cols-2 gap-8">
                <!-- Status Selection -->
                <div class="space-y-6">
                  <div class="space-y-3">
                    <label class="text-sm font-bold text-foreground flex items-center gap-2">
                      <div class="h-1.5 w-1.5 rounded-full bg-primary"></div>
                      目标状态
                    </label>
                    <div class="grid grid-cols-2 gap-3">
                      <div
                        v-for="opt in toolStatusOptions"
                        :key="opt.value"
                        class="p-4 rounded-xl border-2 transition-all cursor-pointer flex flex-col items-center justify-center gap-2"
                        :class="newToolStatus === opt.value ? 'border-primary bg-primary/5 text-primary' : 'border-border/50 bg-muted/20 text-muted-foreground hover:border-border hover:bg-muted/40'"
                        @click="newToolStatus = opt.value"
                      >
                        <span class="text-sm font-bold">{{ opt.label }}</span>
                        <span class="text-[10px] opacity-60 font-mono">{{ opt.value }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="space-y-3">
                    <label class="text-sm font-bold text-foreground flex items-center gap-2">
                      <div class="h-1.5 w-1.5 rounded-full bg-primary"></div>
                      变更原因 / 备注
                    </label>
                    <Textarea
                      v-model="statusRemark"
                      placeholder="请详细说明状态变更的原因（如：年检、损坏送修、丢失报废等）"
                      class="min-h-[120px] bg-muted/20 border-border/50 focus:border-primary/50"
                    />
                  </div>
                </div>

                <!-- Status History -->
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <h4 class="text-sm font-bold text-foreground flex items-center gap-2">
                      <History class="h-4 w-4" /> 状态变更历史
                    </h4>
                    <span class="text-[10px] text-muted-foreground">最近 10 条记录</span>
                  </div>

                  <div class="border border-border/50 rounded-xl overflow-hidden bg-card/50">
                    <div v-if="historyLoading" class="p-8 flex justify-center">
                      <RefreshCw class="h-6 w-6 text-primary animate-spin" />
                    </div>
                    <div v-else-if="statusHistory.length === 0" class="p-12 text-center opacity-40">
                      <p class="text-xs">暂无历史记录</p>
                    </div>
                    <table v-else class="w-full text-xs text-left border-collapse">
                      <thead class="bg-muted/50 border-b border-border text-muted-foreground font-bold uppercase tracking-wider">
                        <tr>
                          <th class="px-4 py-3">工装编码</th>
                          <th class="px-4 py-3">变更轨迹</th>
                          <th class="px-4 py-3">操作信息</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-border/50">
                        <tr v-for="h in statusHistory" :key="h.id" class="hover:bg-muted/20 transition-colors">
                          <td class="px-4 py-4 align-top">
                            <span class="font-mono font-bold">{{ h.tool_code }}</span>
                          </td>
                          <td class="px-4 py-4">
                            <div class="flex items-center gap-2 mb-1">
                              <span class="text-muted-foreground">{{ getStatusLabel(h.old_status) }}</span>
                              <span class="text-primary">→</span>
                              <span class="font-bold text-foreground">{{ getStatusLabel(h.new_status) }}</span>
                            </div>
                            <p class="text-[10px] text-muted-foreground italic truncate max-w-[150px]" :title="h.remark">
                              {{ h.remark || '无备注' }}
                            </p>
                          </td>
                          <td class="px-4 py-4 align-top">
                            <p class="font-medium text-foreground">{{ h.operator_name }}</p>
                            <p class="text-[10px] text-muted-foreground">{{ h.change_time }}</p>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  RefreshCw,
  Inbox,
  User,
  Package,
  FileCode,
  MousePointer2,
  Box,
  Info,
  Search,
  History,
  Trash2,
  CheckCircle2,
  Truck
} from 'lucide-vue-next'
import {
  assignTransport,
  finalConfirmOrder,
  generateTransportText,
  getOrderDetail,
  getPendingKeeperOrders,
  keeperConfirmOrder,
  notifyTransport,
  rejectOrder
} from '@/api/orders'
import { getFinalConfirmAvailability } from '@/api/orders'
import { searchTools, batchUpdateToolStatus, getToolStatusHistory } from '@/api/tools'
import { useSessionStore } from '@/store/session'
import { DEBUG_IDS } from '@/debug/debugIds'
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
const activeTab = ref('orders')
const pendingOrders = ref([])
const selectedOrder = ref({})
const confirmItems = ref([])
const transportPreview = ref('')
const wechatPreview = ref('')
const loading = ref(false)
const finalConfirmState = ref({ available: false, reason: '' })

// Tool Status Management State
const toolSearchKeyword = ref('')
const selectedTools = ref([])
const newToolStatus = ref('in_storage')
const statusRemark = ref('')
const submittingStatus = ref(false)
const statusHistory = ref([])
const historyLoading = ref(false)
const searchLoading = ref(false)

const toolStatusOptions = [
  { label: '在库', value: 'in_storage' },
  { label: '已出库', value: 'outbounded' },
  { label: '维修中', value: 'maintain' },
  { label: '已报废', value: 'scrapped' }
]

const showToolStatusTab = computed(() => {
  return session.role === 'keeper' || session.role === 'admin'
})

async function handleSearchTools(query) {
  if (!query) return
  searchLoading.value = true
  try {
    const result = await searchTools({ keyword: query })
    if (result.success && result.data.length > 0) {
      // For now, let's just add the first one if it's not already there
      const tool = result.data[0]
      if (!selectedTools.value.some((t) => t.toolCode === tool.toolCode)) {
        selectedTools.value.push(tool)
        // Auto-load history for the newly added tool
        loadToolHistory(tool.toolCode)
      }
    } else {
      ElMessage.info('未找到匹配的工装')
    }
  } finally {
    searchLoading.value = false
    toolSearchKeyword.value = ''
  }
}

function removeTool(tool) {
  selectedTools.value = selectedTools.value.filter((t) => t.toolCode !== tool.toolCode)
}

async function applyStatusChange() {
  if (selectedTools.value.length === 0) {
    ElMessage.warning('请先选择工装')
    return
  }
  if (!newToolStatus.value) {
    ElMessage.warning('请选择新状态')
    return
  }

  submittingStatus.value = true
  try {
    const result = await batchUpdateToolStatus({
      tool_codes: selectedTools.value.map((t) => t.toolCode),
      new_status: newToolStatus.value,
      remark: statusRemark.value,
      operator_id: session.userId,
      operator_name: session.userName,
      operator_role: session.role
    })

    if (result.data.success) {
      ElMessage.success('状态更新成功')
      statusRemark.value = ''
      // Refresh history for the first selected tool as a sample
      if (selectedTools.value.length > 0) {
        loadToolHistory(selectedTools.value[0].toolCode)
      }
      // Update local status display
      selectedTools.value.forEach((t) => {
        t.currentStatus = newToolStatus.value
        t.statusText = toolStatusOptions.find(opt => opt.value === newToolStatus.value)?.label || newToolStatus.value
      })
    }
  } finally {
    submittingStatus.value = false
  }
}

async function loadToolHistory(toolCode) {
  historyLoading.value = true
  try {
    const result = await getToolStatusHistory(toolCode)
    if (result.data.success) {
      statusHistory.value = result.data.data
    }
  } finally {
    historyLoading.value = false
  }
}

function getStatusLabel(status) {
  return toolStatusOptions.find((opt) => opt.value === status)?.label || status
}

const confirmForm = reactive({
  transportType: '',
  transportAssigneeId: '',
  transportAssigneeName: '',
  keeperRemark: ''
})

const canDispatchTransport = computed(
  () =>
    session.hasPermission('order:keeper_confirm') &&
    ['keeper_confirmed', 'partially_confirmed'].includes(selectedOrder.value.orderStatus) &&
    !selectedOrder.value.transportOperatorId
)

const summaryFields = computed(() => {
  if (!selectedOrder.value.orderNo) return []
  return [
    { label: '单据类型', value: selectedOrder.value.orderType === 'outbound' ? '出库' : '入库' },
    { label: '发起人', value: selectedOrder.value.initiatorName || '-' },
    { label: '用途', value: selectedOrder.value.usagePurpose || '-' },
    { label: '目标位置', value: selectedOrder.value.targetLocationText || '-' }
  ]
})

const canReview = computed(
  () =>
    session.hasPermission('order:keeper_confirm') &&
    ['submitted', 'partially_confirmed'].includes(selectedOrder.value.orderStatus)
)

const canNotify = computed(
  () =>
    (session.hasPermission('notification:send_feishu') || session.hasPermission('order:keeper_confirm')) &&
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
  confirmForm.transportAssigneeId = result.data.transportOperatorId || ''
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

  ElMessage.success('保管确认已提交')
  await selectOrder(selectedOrder.value)
  await loadPendingOrders()
}

async function openDispatchTransportDialog() {
  const action = await ElMessageBox.confirm(
    `确认派遣运输任务给 ${confirmForm.transportAssigneeName || '指定运输负责人'} 吗？`,
    '派遣运输任务',
    {
      confirmButtonText: '确认派遣',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => 'confirm').catch(() => 'cancel')

  if (action !== 'confirm') return

  await dispatchTransport()
}

async function dispatchTransport() {
  const payload = {
    transport_type: confirmForm.transportType,
    transport_assignee_id: confirmForm.transportAssigneeId || confirmForm.transportAssigneeName,
    transport_assignee_name: confirmForm.transportAssigneeName,
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  }

  const result = await assignTransport(selectedOrder.value.orderNo, payload)
  if (!result.success) return

  ElMessage.success('运输任务已派遣')
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

  ElMessage.success('单据已完成最终确认')
  await selectOrder(selectedOrder.value)
  await loadPendingOrders()
}

loadPendingOrders()
</script>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 5px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.3);
  border-radius: 20px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 0.5);
}

:deep(.custom-tabs .el-tabs__header) {
  margin-bottom: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
}

:deep(.custom-tabs .el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.custom-tabs .el-tabs__item) {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  height: 3rem;
  line-height: 3rem;
  transition: all 0.2s;
}

:deep(.custom-tabs .el-tabs__item.is-active) {
  color: #fff;
}

:deep(.custom-tabs .el-tabs__active-bar) {
  background-color: #3b82f6;
  height: 2px;
}

:deep(.custom-tabs .el-tabs__content) {
  flex: 1;
  padding-top: 1rem;
}
</style>
