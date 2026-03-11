import http from './http'
import { normalizeItem, normalizeLog, normalizeNotification, normalizeOrder } from '@/utils/toolIO'

function unwrap(response) {
  return response.data
}

export async function createOrder(payload) {
  return unwrap(await http.post('/tool-io-orders', payload))
}

export async function getOrderList(params) {
  const result = unwrap(await http.get('/tool-io-orders', { params }))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeOrder) : []
  }
}

export async function getOrderDetail(orderNo) {
  const result = unwrap(await http.get(`/tool-io-orders/${orderNo}`))
  return {
    ...result,
    data: result.data ? normalizeOrder(result.data) : null
  }
}

export async function submitOrder(orderNo, payload) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/submit`, payload))
}

export async function keeperConfirmOrder(orderNo, payload) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/keeper-confirm`, payload))
}

export async function notifyTransport(orderNo, payload = {}) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/notify-transport`, payload))
}

export async function notifyKeeper(orderNo, payload = {}) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/notify-keeper`, payload))
}

export async function finalConfirmOrder(orderNo, payload) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/final-confirm`, payload))
}

export async function getFinalConfirmAvailability(orderNo, params = {}) {
  return unwrap(await http.get(`/tool-io-orders/${orderNo}/final-confirm-availability`, { params }))
}

export async function rejectOrder(orderNo, payload) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/reject`, payload))
}

export async function cancelOrder(orderNo, payload) {
  return unwrap(await http.post(`/tool-io-orders/${orderNo}/cancel`, payload))
}

export async function getPendingKeeperOrders(keeperId) {
  const result = unwrap(await http.get('/tool-io-orders/pending-keeper', { params: { keeper_id: keeperId } }))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeOrder) : []
  }
}

export async function getOrderLogs(orderNo) {
  const result = unwrap(await http.get(`/tool-io-orders/${orderNo}/logs`))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeLog) : []
  }
}

export async function getNotificationRecords(orderNo) {
  const result = unwrap(await http.get(`/tool-io-orders/${orderNo}/notification-records`))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map(normalizeNotification) : []
  }
}

export async function generateKeeperText(orderNo) {
  return unwrap(await http.get(`/tool-io-orders/${orderNo}/generate-keeper-text`))
}

export async function generateTransportText(orderNo) {
  return unwrap(await http.get(`/tool-io-orders/${orderNo}/generate-transport-text`))
}

export async function searchTools(params) {
  const result = unwrap(await http.get('/tools/search', { params }))
  return {
    ...result,
    data: Array.isArray(result.data)
      ? result.data.map((item) =>
          normalizeItem({
            ...item,
            tool_id: item.tool_id ?? item.tool_code,
            current_location_text:
              item.current_location_text ?? item.location ?? item.location_info ?? item.application_history ?? '',
            status_text:
              item.status_text ?? item.io_status ?? item.available_status ?? item.valid_status ?? ''
          })
        )
      : []
  }
}

export async function batchQueryTools(toolCodes) {
  const result = unwrap(await http.post('/tools/batch-query', { tool_codes: toolCodes }))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map((item) => normalizeItem(item)) : []
  }
}

export function normalizeOrderDetailForView(order, logs = []) {
  return {
    ...order,
    logs,
    items: order.items || [],
    notificationRecords: (order.notificationRecords || []).map(normalizeNotification)
  }
}

