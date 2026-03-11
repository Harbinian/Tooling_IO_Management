import { ElMessage } from 'element-plus'

export const orderStatusMap = {
  draft: { label: '草稿', type: 'info' },
  submitted: { label: '已提交', type: 'warning' },
  keeper_confirmed: { label: '保管员已确认', type: 'success' },
  partially_confirmed: { label: '部分确认', type: 'warning' },
  transport_notified: { label: '已通知运输', type: 'primary' },
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
    orderNo: pickValue(record, ['order_no', '鍑哄叆搴撳崟鍙?']),
    orderType: pickValue(record, ['order_type', '鍗曟嵁绫诲瀷']),
    orderStatus: pickValue(record, ['order_status', '鍗曟嵁鐘舵€?']),
    initiatorId: pickValue(record, ['initiator_id', '鍙戣捣浜篒D']),
    initiatorName: pickValue(record, ['initiator_name', '鍙戣捣浜哄鍚?']),
    initiatorRole: pickValue(record, ['initiator_role', '鍙戣捣浜鸿鑹?']),
    department: pickValue(record, ['department', '閮ㄩ棬']),
    projectCode: pickValue(record, ['project_code', '椤圭洰浠ｅ彿']),
    usagePurpose: pickValue(record, ['usage_purpose', '鐢ㄩ€?']),
    targetLocationText: pickValue(record, ['target_location_text', '鐩爣浣嶇疆鏂囨湰']),
    keeperId: pickValue(record, ['keeper_id', '淇濈鍛業D']),
    keeperName: pickValue(record, ['keeper_name', '淇濈鍛樺鍚?']),
    transportType: pickValue(record, ['transport_type', '杩愯緭绫诲瀷']),
    transportOperatorName: pickValue(record, ['transport_operator_name', '杩愯緭浜哄鍚?']),
    toolCount: Number(pickValue(record, ['tool_count', '宸ヨ鏁伴噺'], 0)) || 0,
    approvedCount: Number(pickValue(record, ['approved_count', '宸茬‘璁ゆ暟閲?'], 0)) || 0,
    createdAt: pickValue(record, ['created_at', '鍒涘缓鏃堕棿']),
    updatedAt: pickValue(record, ['updated_at', '淇敼鏃堕棿']),
    keeperRequestText: pickValue(record, ['keeper_request_text', '淇濈鍛橀渶姹傛枃鏈?']),
    transportNoticeText: pickValue(record, ['transport_notice_text', '杩愯緭閫氱煡鏂囨湰']),
    wechatCopyText: pickValue(record, ['wechat_copy_text', '寰俊澶嶅埗鏂囨湰']),
    remark: pickValue(record, ['remark', '澶囨敞']),
    rejectReason: pickValue(record, ['reject_reason', '椹冲洖鍘熷洜']),
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
  const itemStatus = pickValue(record, ['item_status', 'status', '鏄庣粏鐘舵€?', '鐘舵€?'])
  const availableStatus = pickValue(record, ['available_status', '鍙敤鐘舵€?'])
  const validStatus = pickValue(record, ['valid_status', '宸ヨ鏈夋晥鐘舵€?'])
  const ioStatus = pickValue(record, ['io_status', '鍑哄叆搴撶姸鎬?'])

  return {
    toolId: pickValue(record, ['tool_id', '宸ヨID', 'tool_code', '搴忓垪鍙?']),
    toolCode: pickValue(record, ['tool_code', '宸ヨ缂栫爜', '搴忓垪鍙?']),
    toolName: pickValue(record, ['tool_name', '宸ヨ鍚嶇О']),
    drawingNo: pickValue(record, ['drawing_no', '宸ヨ鍥惧彿']),
    specModel: pickValue(record, ['spec_model', '鏈哄瀷']),
    currentVersion: pickValue(record, ['current_version', '褰撳墠鐗堟']),
    applyQty: Number(pickValue(record, ['apply_qty', '鐢宠鏁伴噺'], 1)) || 1,
    approvedQty: Number(pickValue(record, ['approved_qty', '纭鏁伴噺'], 0)) || 0,
    itemStatus,
    availableStatus,
    validStatus,
    ioStatus,
    statusText: pickValue(
      record,
      ['status_text', 'status', '鐘舵€?'],
      ioStatus || availableStatus || validStatus || '-'
    ),
    currentLocationText: pickValue(
      record,
      ['current_location_text', '搴撲綅', 'location_info', '搴旂敤鍘嗗彶', '褰撳墠浣嶇疆']
    ),
    applicationHistory: pickValue(record, ['application_history', '搴旂敤鍘嗗彶']),
    ownerName: pickValue(record, ['owner_name', '浜ф潈鎵€鏈?']),
    workPackage: pickValue(record, ['work_package', '宸ヤ綔鍖?']),
    mainMaterial: pickValue(record, ['main_material', '涓讳綋鏉愯川']),
    manufacturer: pickValue(record, ['manufacturer', '鍒堕€犲晢']),
    inspectionExpiryDate: pickValue(record, ['inspection_expiry_date', '瀹氭鏈夋晥鎴']),
    keeperConfirmLocationText: pickValue(
      record,
      ['keeper_confirm_location_text', '淇濈鍛樼‘璁や綅缃枃鏈?']
    ),
    checkResult: pickValue(
      record,
      ['keeper_check_result', 'check_result', '淇濈鍛樻鏌ョ粨鏋?', '妫€鏌ョ粨鏋?']
    ),
    checkRemark: pickValue(
      record,
      ['keeper_check_remark', 'check_remark', '淇濈鍛樻鏌ュ娉?', '妫€鏌ュ娉?']
    ),
    confirmTime: pickValue(record, ['confirm_time', '纭鏃堕棿'])
  }
}

export function normalizeLog(record = {}) {
  return {
    actionType: pickValue(record, ['action_type', '鎿嶄綔绫诲瀷']),
    operatorName: pickValue(record, ['operator_name', '鎿嶄綔浜哄鍚?']),
    operatorRole: pickValue(record, ['operator_role', '鎿嶄綔浜鸿鑹?']),
    content: pickValue(record, ['content', '鎿嶄綔鍐呭']),
    actionTime: pickValue(record, ['action_time', '鎿嶄綔鏃堕棿']),
    beforeStatus: pickValue(record, ['before_status', '鍙樻洿鍓嶇姸鎬?']),
    afterStatus: pickValue(record, ['after_status', '鍙樻洿鍚庣姸鎬?'])
  }
}

export function normalizeNotification(record = {}) {
  return {
    notifyType: pickValue(record, ['notify_type', '閫氱煡绫诲瀷']),
    notifyChannel: pickValue(record, ['notify_channel', '閫氱煡娓犻亾']),
    receiver: pickValue(record, ['receiver', '鎺ユ敹浜?']),
    title: pickValue(record, ['title', '鏍囬', 'notify_title', '閫氱煡鏍囬']),
    content: pickValue(record, ['content', '鍐呭', 'notify_content', '閫氱煡鍐呭']),
    copyText: pickValue(record, ['copy_text', '澶嶅埗鏂囨湰']),
    sendStatus: pickValue(record, ['send_status', '鍙戦€佺姸鎬?']),
    sendResult: pickValue(record, ['send_result', '鍙戦€佺粨鏋?']),
    sendTime: pickValue(record, ['send_time', '鍙戦€佹椂闂?', 'created_at', '鍒涘缓鏃堕棿'])
  }
}

export function getStatusPresentation(status, isItem = false) {
  const source = isItem ? itemStatusMap : orderStatusMap
  return source[status] || { label: status || '-', type: 'info' }
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('zh-CN', { hour12: false })
}

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text || '')
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}
