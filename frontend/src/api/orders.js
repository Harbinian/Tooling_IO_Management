import client from './client'
import { normalizeLog, normalizeNotification, normalizeOrder } from '@/utils/toolIO'

function unwrap(response) {
  return response.data
}

/**
 * 创建出入库申请单
 * @param {Object} payload 
 */
export async function createOrder(payload) {
  return unwrap(await client.post('/tool-io-orders', payload))
}

/**
 * 生成保管员通知文本预览（不落库）
 * @param {Object} payload
 */
export async function previewKeeperText(payload) {
  return unwrap(await client.post('/tool-io-orders/preview-keeper-text', payload))
}

/**
 * 获取申请单列表
 * @param {Object} params { page_no, page_size, keyword, order_type, order_status, ... }
 */
export async function getOrderList(params) {
  const result = unwrap(await client.get('/tool-io-orders', { params }))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeOrder) : []
  }
}

/**
 * 获取单据详情
 * @param {string} orderNo 
 */
export async function getOrderDetail(orderNo) {
  const result = unwrap(await client.get(`/tool-io-orders/${orderNo}`))
  return {
    ...result,
    data: result.data ? normalizeOrder(result.data) : null
  }
}

/**
 * 提交草稿
 * @param {string} orderNo 
 * @param {Object} payload { operator_id, operator_name, operator_role }
 */
export async function submitOrder(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/submit`, payload))
}

/**
 * 保管员确认
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function keeperConfirmOrder(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/keeper-confirm`, payload))
}

/**
 * 分配运输人
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function assignTransport(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/assign-transport`, payload))
}

/**
 * 开始运输
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function startTransport(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/transport-start`, payload))
}

/**
 * 完成运输
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function completeTransport(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/transport-complete`, payload))
}

/**
 * 发送运输通知
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function notifyTransport(orderNo, payload = {}) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/notify-transport`, payload))
}

/**
 * 发送保管员通知
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function notifyKeeper(orderNo, payload = {}) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/notify-keeper`, payload))
}

/**
 * 最终确认
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function finalConfirmOrder(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/final-confirm`, payload))
}

/**
 * 检查是否可以进行最终确认
 * @param {string} orderNo 
 * @param {Object} params 
 */
export async function getFinalConfirmAvailability(orderNo, params = {}) {
  return unwrap(await client.get(`/tool-io-orders/${orderNo}/final-confirm-availability`, { params }))
}

/**
 * 驳回单据
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function rejectOrder(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/reject`, payload))
}

/**
 * 取消单据
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function cancelOrder(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/cancel`, payload))
}

/**
 * 重置单据为草稿（用于被驳回单据重新编辑）
 * @param {string} orderNo
 * @param {Object} payload { operator_id, operator_name, operator_role }
 */
export async function resetOrderToDraft(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/reset-to-draft`, payload))
}

/**
 * 更新草稿订单内容
 * @param {string} orderNo
 * @param {Object} payload { items, remark }
 */
export async function updateOrder(orderNo, payload) {
  return unwrap(await client.put(`/tool-io-orders/${orderNo}`, payload))
}

/**
 * 获取保管员待确认单据
 * @param {string} keeperId 
 */
export async function getPendingKeeperOrders(keeperId) {
  const result = unwrap(await client.get('/tool-io-orders/pending-keeper', { params: { keeper_id: keeperId } }))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeOrder) : []
  }
}

/**
 * 获取单据操作日志
 * @param {string} orderNo 
 */
export async function getOrderLogs(orderNo) {
  const result = unwrap(await client.get(`/tool-io-orders/${orderNo}/logs`))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeLog) : []
  }
}

/**
 * 获取通知记录
 * @param {string} orderNo 
 */
export async function getNotificationRecords(orderNo) {
  const result = unwrap(await client.get(`/tool-io-orders/${orderNo}/notification-records`))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeNotification) : []
  }
}

/**
 * 生成保管员通知文本预览
 * @param {string} orderNo 
 */
export async function generateKeeperText(orderNo) {
  return unwrap(await client.get(`/tool-io-orders/${orderNo}/generate-keeper-text`))
}

/**
 * 生成运输通知文本预览
 * @param {string} orderNo
 */
export async function generateTransportText(orderNo) {
  return unwrap(await client.get(`/tool-io-orders/${orderNo}/generate-transport-text`))
}

/**
 * 删除草稿订单
 * @param {string} orderNo
 * @param {Object} payload { operator_id, operator_name, operator_role }
 */
export async function deleteOrder(orderNo, payload) {
  return unwrap(await client.delete(`/tool-io-orders/${orderNo}`, { data: payload }))
}

/**
 * 上报运输异常
 * @param {string} orderNo 
 * @param {Object} payload 
 */
export async function reportTransportIssue(orderNo, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/report-transport-issue`, payload))
}

/**
 * 获取订单的运输异常列表
 * @param {string} orderNo 
 */
export async function getTransportIssues(orderNo) {
  return unwrap(await client.get(`/tool-io-orders/${orderNo}/transport-issues`))
}

/**
 * 处理运输异常
 * @param {string} orderNo 
 * @param {number} issueId 
 * @param {Object} payload 
 */
export async function resolveTransportIssue(orderNo, issueId, payload) {
  return unwrap(await client.post(`/tool-io-orders/${orderNo}/resolve-transport-issue`, { issue_id: issueId, ...payload }))
}

/**
 * 获取准备工预知运输列表
 * @param {Object} params 
 */
export async function getPreTransportOrders(params) {
  return unwrap(await client.get('/tool-io-orders/pre-transport', { params }))
}
