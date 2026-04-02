import client from './client'

function unwrap(response) {
  return response.data
}

// 计划 API

/**
 * 创建定检计划
 * @param {Object} payload 
 */
export async function createPlan(payload) {
  return unwrap(await client.post('/inspection/plans', payload))
}

/**
 * 获取定检计划列表
 * @param {Object} params 
 */
export async function getPlanList(params) {
  return unwrap(await client.get('/inspection/plans', { params }))
}

/**
 * 获取定检计划详情
 * @param {string} planNo 
 */
export async function getPlanDetail(planNo) {
  return unwrap(await client.get(`/inspection/plans/${planNo}`))
}

/**
 * 更新定检计划
 * @param {string} planNo 
 * @param {Object} payload 
 */
export async function updatePlan(planNo, payload) {
  return unwrap(await client.put(`/inspection/plans/${planNo}`, payload))
}

/**
 * 发布定检计划
 * @param {string} planNo 
 */
export async function publishPlan(planNo) {
  return unwrap(await client.post(`/inspection/plans/${planNo}/publish`))
}

/**
 * 预览定检任务
 * @param {string} planNo 
 */
export async function previewTasks(planNo) {
  return unwrap(await client.get(`/inspection/plans/${planNo}/preview-tasks`))
}

// 任务 API

/**
 * 获取定检任务列表
 * @param {Object} params 
 */
export async function getTaskList(params) {
  return unwrap(await client.get('/inspection/tasks', { params }))
}

/**
 * 获取定检任务详情
 * @param {string} taskNo 
 */
export async function getTaskDetail(taskNo) {
  return unwrap(await client.get(`/inspection/tasks/${taskNo}`))
}

/**
 * 领取定检任务
 * @param {string} taskNo 
 */
export async function receiveTask(taskNo) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/receive`))
}

/**
 * 开始定检
 * @param {string} taskNo 
 */
export async function startInspection(taskNo) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/start-inspection`))
}

/**
 * 提交定检报告
 * @param {string} taskNo 
 * @param {Object} payload { inspection_date, result, data, attachment_base64, ... }
 */
export async function submitReport(taskNo, payload) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/submit-report`, payload))
}

/**
 * 验收通过报告
 * @param {string} taskNo 
 */
export async function acceptReport(taskNo) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/accept`))
}

/**
 * 驳回报告
 * @param {string} taskNo 
 * @param {Object} payload { reason }
 */
export async function rejectReport(taskNo, payload) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/reject`, payload))
}

/**
 * 创建出库单（后端跳转逻辑或前端引导）
 * @param {string} taskNo 
 */
export async function createOutbound(taskNo) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/create-outbound`))
}

/**
 * 创建入库单（后端跳转逻辑或前端引导）
 * @param {string} taskNo 
 */
export async function createInbound(taskNo) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/create-inbound`))
}

/**
 * 关闭任务
 * @param {string} taskNo 
 */
export async function closeTask(taskNo) {
  return unwrap(await client.post(`/inspection/tasks/${taskNo}/close`))
}

/**
 * 获取任务关联单据
 * @param {string} taskNo 
 */
export async function getLinkedOrders(taskNo) {
  return unwrap(await client.get(`/inspection/tasks/${taskNo}/linked-orders`))
}

/**
 * 关联单据到任务
 * @param {string} orderNo 
 * @param {string} taskNo 
 */
export async function linkOrderToTask(orderNo, taskNo) {
  return unwrap(await client.post(`/inspection/orders/${orderNo}/link-task`, { task_no: taskNo }))
}

// 工装定检状态 API

/**
 * 获取工装定检状态
 * @param {string} serialNo 
 */
export async function getInspectionStatus(serialNo) {
  return unwrap(await client.get(`/inspection/status/${serialNo}`))
}

// 统计 API

/**
 * 获取定检概览统计（四宫格）
 * @param {Object} params { org_id }
 */
export async function getStatsSummary(params) {
  return unwrap(await client.get('/inspection/stats/summary', { params }))
}

/**
 * 获取任务状态分布
 * @param {Object} params { org_id }
 */
export async function getTaskDistribution(params) {
  return unwrap(await client.get('/inspection/stats/task-distribution', { params }))
}

/**
 * 获取逾期率统计
 * @param {Object} params { org_id }
 */
export async function getOverdueRate(params) {
  return unwrap(await client.get('/inspection/stats/overdue-rate', { params }))
}

/**
 * 获取月度对比统计
 * @param {Object} params { org_id }
 */
export async function getMonthlyComparison(params) {
  return unwrap(await client.get('/inspection/stats/monthly-comparison', { params }))
}

// 日历 API

/**
 * 获取日历视图数据
 * @param {Object} params { org_id, start_date, end_date }
 */
export async function getCalendarData(params) {
  return unwrap(await client.get('/inspection/plans/calendar', { params }))
}

/**
 * 拖拽调整任务时间
 * @param {string} taskNo 
 * @param {Object} payload { deadline }
 */
export async function rescheduleTask(taskNo, payload) {
  return unwrap(await client.put(`/inspection/tasks/${taskNo}/reschedule`, payload))
}

// 导出 API

/**
 * 导出定检状态列表 (Excel)
 * @param {Object} params 
 */
export async function exportInspectionStatus(params) {
  return client.get('/inspection/status/export', { params, responseType: 'blob' })
}

// 订单推进 API

/**
 * 订单状态变更触发任务推进
 * @param {string} orderNo 
 */
export async function advanceByOrder(orderNo) {
  return unwrap(await client.post(`/inspection/advance-by-order/${orderNo}`))
}
