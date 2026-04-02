import { ElMessage } from 'element-plus'

export const orderStatusMap = {
  draft: { label: '草稿', type: 'info' },
  submitted: { label: '已提交', type: 'warning' },
  keeper_confirmed: { label: '保管员已确认', type: 'success' },
  partially_confirmed: { label: '部分确认', type: 'warning' },
  transport_notified: { label: '已通知运输', type: 'primary' },
  transport_in_progress: { label: '运输中', type: 'primary' },
  transport_completed: { label: '运输已完成', type: 'success' },
  final_confirmation_pending: { label: '待最终确认', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' },
  cancelled: { label: '已取消', type: 'info' }
}

export const itemStatusMap = {
  pending_check: { label: '待确认', type: 'info' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  completed: { label: '已完成', type: 'success' }
}

export function pickValue(record, keys, fallback = '') {
  for (const key of keys) {
    if (record && record[key] !== undefined && record[key] !== null && record[key] !== '') {
      return record[key]
    }
  }
  return fallback
}

export function normalizeOrder(record = {}) {
  return {
    orderNo: pickValue(record, ['order_no', '出入库单号']),
    orderType: pickValue(record, ['order_type', '单据类型']),
    orderStatus: pickValue(record, ['order_status', '单据状态']),
    initiatorId: pickValue(record, ['initiator_id', '发起人ID']),
    initiatorName: pickValue(record, ['initiator_name', '发起人姓名']),
    initiatorRole: pickValue(record, ['initiator_role', '发起人角色']),
    department: pickValue(record, ['department', '部门']),
    projectCode: pickValue(record, ['project_code', '项目代号']),
    usagePurpose: pickValue(record, ['usage_purpose', '用途']),
    targetLocationText: pickValue(record, ['target_location_text', '目标位置文本']),
    keeperId: pickValue(record, ['keeper_id', '保管员ID']),
    keeperName: pickValue(record, ['keeper_name', '保管员姓名']),
    transportType: pickValue(record, ['transport_type', '运输类型']),
    transportOperatorId: pickValue(record, ['transport_operator_id', 'transport_assignee_id', '运输人ID']),
    transportOperatorName: pickValue(
      record,
      ['transport_operator_name', 'transport_assignee_name', '运输人姓名']
    ),
    toolCount: Array.isArray(record.items) ? record.items.length : (Number(pickValue(record, ['tool_count', '工装数量'], 0)) || 0),
    approvedCount: Number(pickValue(record, ['approved_count', '已确认数量'], 0)) || 0,
    createdAt: pickValue(record, ['created_at', '创建时间']),
    updatedAt: pickValue(record, ['updated_at', '修改时间']),
    submittedAt: pickValue(record, ['submitted_at', '提交时间']),
    keeperRequestText: pickValue(record, ['keeper_request_text', '保管员需求文本']),
    transportNoticeText: pickValue(record, ['transport_notice_text', '运输通知文本']),
    wechatCopyText: pickValue(record, ['wechat_copy_text', '微信复制文本']),
    remark: pickValue(record, ['remark', '备注']),
    rejectReason: pickValue(record, ['reject_reason', '驳回原因']),
    items: Array.isArray(record.items) ? record.items.map(normalizeItem) : [],
    logs: Array.isArray(record.logs) ? record.logs.map(normalizeLog) : [],
    notificationRecords: Array.isArray(record.notification_records)
      ? record.notification_records.map(normalizeNotification)
      : Array.isArray(record.notifications)
        ? record.notifications.map(normalizeNotification)
        : []
  }
}

export function normalizeItem(record = {}) {
  const itemStatus = pickValue(record, ['item_status', 'status', '明细状态'])
  const availableStatus = pickValue(record, ['available_status', '可用状态'])
  const validStatus = pickValue(record, ['valid_status', '有效状态'])
  const ioStatus = pickValue(record, ['io_status', '出入库状态'])
  const splitQuantityRaw = pickValue(record, ['split_quantity', '分体数量'], null)
  const splitQuantity = splitQuantityRaw === null ? null : Number(splitQuantityRaw)

  return {
    toolId: pickValue(record, ['tool_id', '工装ID']),
    toolCode: pickValue(record, ['serial_no', 'tool_code', '序列号']),
    toolName: pickValue(record, ['tool_name', '工装名称']),
    drawingNo: pickValue(record, ['drawing_no', '工装图号']),
    specModel: pickValue(record, ['spec_model', '机型', '规格型号']),
    currentVersion: pickValue(record, ['current_version', '当前版本']),
    applyQty: Number(pickValue(record, ['apply_qty', '申请数量'], 1)) || 1,
    approvedQty: Number(pickValue(record, ['approved_qty', '确认数量'], 0)) || 0,
    split_quantity: Number.isNaN(splitQuantity) ? null : splitQuantity,
    itemStatus,
    availableStatus,
    validStatus,
    ioStatus,
    statusText: pickValue(record, ['status_text', '状态'], ioStatus || availableStatus || validStatus || '-'),
    currentLocationText: pickValue(
      record,
      ['current_location_text', '当前位置文本', '工装快照位置文本', 'location_info', '库位', 'application_history']
    ),
    applicationHistory: pickValue(record, ['application_history', '应用历史']),
    ownerName: pickValue(record, ['owner_name', '保管人']),
    workPackage: pickValue(record, ['work_package', '工作包']),
    mainMaterial: pickValue(record, ['main_material', '主要材料']),
    manufacturer: pickValue(record, ['manufacturer', '生产厂家']),
    inspectionExpiryDate: pickValue(record, ['inspection_expiry_date', '定检有效截止']),
    keeperConfirmLocationText: pickValue(record, ['keeper_confirm_location_text', '保管员确认位置文本']),
    checkResult: pickValue(record, ['keeper_check_result', 'check_result', '保管员检查结果', '归还检查结果']),
    checkRemark: pickValue(record, ['keeper_check_remark', 'check_remark', '保管员检查备注', '归还检查备注']),
    confirmPerson: pickValue(record, ['confirm_person', '确认人']),
    confirmTime: pickValue(record, ['confirm_time', '确认时间']),
    rejectReason: pickValue(record, ['reject_reason', '驳回原因'])
  }
}

export function normalizeLog(record = {}) {
  return {
    actionType: pickValue(record, ['action_type', '操作类型']),
    operatorName: pickValue(record, ['operator_name', '操作人']),
    operatorRole: pickValue(record, ['operator_role', '操作角色']),
    content: pickValue(record, ['content', '内容']),
    actionTime: pickValue(record, ['action_time', '操作时间']),
    beforeStatus: pickValue(record, ['before_status', '变更前状态']),
    afterStatus: pickValue(record, ['after_status', '变更后状态'])
  }
}

export function normalizeNotification(record = {}) {
  return {
    notifyType: pickValue(record, ['notify_type', '通知类型']),
    notifyChannel: pickValue(record, ['notify_channel', '通知渠道']),
    receiver: pickValue(record, ['receiver', '接收人']),
    title: pickValue(record, ['title', '标题', 'notify_title', '通知标题']),
    content: pickValue(record, ['content', '内容', 'notify_content', '通知内容']),
    copyText: pickValue(record, ['copy_text', '复制文本']),
    sendStatus: pickValue(record, ['send_status', '发送状态']),
    sendResult: pickValue(record, ['send_result', '发送结果']),
    sendTime: pickValue(record, ['send_time', '发送时间', 'created_at', '创建时间'])
  }
}

export function resolveOrderStatusMeta(status, item = false) {
  const source = item ? itemStatusMap : orderStatusMap
  return source[status] || { label: status || '-', type: 'info' }
}

export function getStatusPresentation(status, item = false) {
  return resolveOrderStatusMeta(status, item)
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

export function notifyApiError(error, fallbackMessage = '请求失败') {
  const message = error?.response?.data?.error || error?.message || fallbackMessage
  ElMessage.error(message)
  return message
}
