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
