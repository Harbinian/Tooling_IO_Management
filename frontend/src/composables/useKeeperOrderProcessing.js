/**
 * useKeeperOrderProcessing - Composable for keeper order processing workflow.
 *
 * This composable handles the core keeper order processing logic including:
 * - Loading pending orders
 * - Selecting and viewing order details
 * - Approving/rejecting orders
 * - Final confirmation
 * - Transport notification preview
 */

import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getOrderDetail,
  getPendingKeeperOrders,
  keeperConfirmOrder,
  rejectOrder,
  finalConfirmOrder,
  generateTransportText,
  notifyTransport,
  getFinalConfirmAvailability
} from '@/api/orders'

export function useKeeperOrderProcessing(session) {
  // State
  const pendingOrders = ref([])
  const selectedOrder = ref({})
  const confirmItems = ref([])
  const transportPreview = ref('')
  const wechatPreview = ref('')
  const loading = ref(false)
  const finalConfirmState = ref({ available: false, reason: '' })
  const mplWarnings = ref([])

  const confirmForm = reactive({
    transportType: '叉车',
    transportAssigneeId: '',
    transportAssigneeName: '',
    keeperRemark: ''
  })

  // Computed
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

  const summaryFields = computed(() => {
    if (!selectedOrder.value.orderNo) return []
    return [
      { label: '单据类型', value: selectedOrder.value.orderType === 'outbound' ? '出库' : '入库' },
      { label: '发起人', value: selectedOrder.value.initiatorName || '-' },
      { label: '用途', value: selectedOrder.value.usagePurpose || '-' },
      { label: '目标位置', value: selectedOrder.value.targetLocationText || '-' }
    ]
  })

  // Helpers
  function resetPreview() {
    transportPreview.value = ''
    wechatPreview.value = ''
  }

  function resolveItemLocationText(item) {
    return item.keeperConfirmLocationText || item.currentLocationText || item.locationText || ''
  }

  function buildEditableItems(order) {
    return (order.items || []).map((item) => {
      return {
        ...item,
        // 显式保留 item_id，确保 API 调用时必填字段明确可见
        item_id: item.id,
        serial_no: item.serialNo || '',
        drawing_no: item.drawingNo || '',
        tool_name: item.toolName || '',
        locationText: resolveItemLocationText(item),
        status: item.itemStatus === 'rejected' ? 'rejected' : 'approved',
        checkRemark: item.checkRemark || '',
        mplExists: false
      }
    })
  }

  // Actions
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

  async function selectOrder(row, loadMplStatusesFn = null, loadProductionPrepUsersFn = null) {
    const result = await getOrderDetail(row.orderNo)
    if (!result.success) return

    selectedOrder.value = result.data
    confirmItems.value = buildEditableItems(result.data)
    confirmForm.transportType = result.data.transportType || '叉车'
    confirmForm.transportAssigneeId = result.data.transportOperatorId || ''
    confirmForm.transportAssigneeName = result.data.transportOperatorName || ''
    confirmForm.keeperRemark = ''
    mplWarnings.value = []
    const availability = await getFinalConfirmAvailability(row.orderNo, {
      operator_id: session.userId,
      operator_role: session.role
    }).catch(() => ({ success: false, available: false }))
    finalConfirmState.value = availability.success ? availability : { available: false, reason: '' }
    if (loadMplStatusesFn) {
      await loadMplStatusesFn(confirmItems.value)
    }
    if (loadProductionPrepUsersFn) {
      await loadProductionPrepUsersFn()
    }
    resetPreview()
  }

  async function previewTransport() {
    const result = await generateTransportText(selectedOrder.value.orderNo)
    if (!result.success) return
    transportPreview.value = result.text || ''
    wechatPreview.value = result.wechat_text || ''
  }

  async function approveOrder() {
    // 防御性校验：确保所有 items 都有 item_id
    const invalidItems = confirmItems.value.filter(item => !item.item_id)
    if (invalidItems.length > 0) {
      ElMessage.error(`工装明细缺少关键标识，请刷新页面后重试。缺失项: ${invalidItems.map(i => i.serialNo || i.serial_no).join(', ')}`)
      return
    }

    const payload = {
      keeper_id: session.userId,
      keeper_name: session.userName,
      transport_type: confirmForm.transportType,
      transport_assignee_id: confirmForm.transportAssigneeId,
      transport_assignee_name: confirmForm.transportAssigneeName,
      keeper_remark: confirmForm.keeperRemark,
      items: confirmItems.value.map((item) => ({
        // 显式使用 item_id 和 serial_no（由 buildEditableItems 明确保留）
        item_id: item.item_id,
        serial_no: item.serial_no || item.serialNo || '',
        location_id: null,
        location_text: resolveItemLocationText(item),
        check_result: item.status,
        check_remark: item.checkRemark || confirmForm.keeperRemark,
        approved_qty: item.status === 'approved' ? (item.split_quantity ?? item.applyQty ?? 1) : 0,
        status: item.status
      })),
      operator_id: session.userId,
      operator_name: session.userName,
      operator_role: session.role
    }

    const result = await keeperConfirmOrder(selectedOrder.value.orderNo, payload)
    if (!result.success) return

    if (Array.isArray(result.mpl_warnings) && result.mpl_warnings.length) {
      mplWarnings.value = result.mpl_warnings
      ElMessage.warning('MPL 缺失，已按警告模式继续确认')
    }
    ElMessage.success('保管确认已提交')
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
    pendingOrders.value = pendingOrders.value.filter(o => o.orderNo !== selectedOrder.value.orderNo)
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
  }

  async function finalizeCurrentOrder() {
    const result = await finalConfirmOrder(selectedOrder.value.orderNo, {
      operator_id: session.userId,
      operator_name: session.userName,
      operator_role: session.role
    })
    if (!result.success) return

    ElMessage.success('单据已完成最终确认')
  }

  return {
    // State
    pendingOrders,
    selectedOrder,
    confirmItems,
    confirmForm,
    transportPreview,
    wechatPreview,
    loading,
    finalConfirmState,
    mplWarnings,
    // Computed
    canReview,
    canNotify,
    canFinalConfirm,
    summaryFields,
    // Actions
    loadPendingOrders,
    selectOrder,
    previewTransport,
    approveOrder,
    rejectCurrentOrder,
    sendTransportNotify,
    finalizeCurrentOrder,
    // Helpers
    resetPreview
  }
}
