import client from './client'

/**
 * Feedback categories
 */
export const FeedbackCategory = {
  BUG: 'bug',
  FEATURE: 'feature',
  UX: 'ux',
  OTHER: 'other'
}

export const FeedbackCategoryLabels = {
  [FeedbackCategory.BUG]: 'Bug 报告',
  [FeedbackCategory.FEATURE]: '功能建议',
  [FeedbackCategory.UX]: '用户体验',
  [FeedbackCategory.OTHER]: '其他'
}

export const FeedbackStatus = {
  PENDING: 'pending',
  REVIEWED: 'reviewed',
  RESOLVED: 'resolved'
}

export const FeedbackStatusLabels = {
  [FeedbackStatus.PENDING]: '待处理',
  [FeedbackStatus.REVIEWED]: '已查看',
  [FeedbackStatus.RESOLVED]: '已解决'
}

/**
 * Get all feedback from backend
 * @returns {Array} Array of feedback objects
 */
export async function getAllFeedback(params = {}) {
  try {
    const { data } = await client.get('/feedback', { params })
    const feedbackList = Array.isArray(data?.data) ? data.data : []
    return feedbackList.map(normalizeFeedbackRecord)
  } catch (error) {
    console.error('[Feedback API] Failed to get feedback:', error)
    return []
  }
}

/**
 * 获取所有反馈（管理员用）
 * @param {Object} params - { status, category, keyword, limit, offset }
 * @returns {Object} { success, data: [...], total }
 */
export async function getAllFeedbackAdmin(params = {}) {
  try {
    const { data } = await client.get('/feedback/all', { params })
    return {
      success: true,
      data: (data?.data || []).map(normalizeFeedbackRecord),
      total: data?.total || 0
    }
  } catch (error) {
    console.error('[Feedback API] Failed to get all feedback (admin):', error)
    return { success: false, data: [], total: 0 }
  }
}

/**
 * 更新反馈状态
 * @param {number|string} id - 反馈ID
 * @param {string} status - 新状态
 * @returns {Object} { success }
 */
export async function updateFeedbackStatus(id, status) {
  try {
    await client.put(`/feedback/${id}/status`, { new_status: status })
    return { success: true }
  } catch (error) {
    console.error('[Feedback API] Failed to update feedback status:', error)
    return {
      success: false,
      error: error?.response?.data?.error || error.message || '更新反馈状态失败'
    }
  }
}

/**
 * 添加回复
 * @param {number|string} feedbackId - 反馈ID
 * @param {string} content - 回复内容
 * @returns {Object} { success, data: { reply } }
 */
export async function addFeedbackReply(feedbackId, content) {
  try {
    const { data } = await client.post(`/feedback/${feedbackId}/reply`, { content })
    return {
      success: true,
      data: data?.data
    }
  } catch (error) {
    console.error('[Feedback API] Failed to add feedback reply:', error)
    return {
      success: false,
      error: error?.response?.data?.error || error.message || '添加回复失败'
    }
  }
}

/**
 * 获取回复列表
 * @param {number|string} feedbackId - 反馈ID
 * @returns {Array} 回复列表
 */
export async function getFeedbackReplies(feedbackId) {
  try {
    const { data } = await client.get(`/feedback/${feedbackId}/replies`)
    return data?.data || []
  } catch (error) {
    console.error('[Feedback API] Failed to get feedback replies:', error)
    return []
  }
}

/**
 * Get feedback by ID
 * @param {string} id - Feedback ID
 * @returns {Object|null} Feedback object or null
 */
export async function getFeedbackById(id) {
  const feedbackList = await getAllFeedback()
  return feedbackList.find(f => String(f.id) === String(id)) || null
}

/**
 * Get feedback history for current user
 * @param {string} loginName - User login name
 * @returns {Array} Array of user's feedback
 */
export async function getUserFeedback(loginName) {
  const params = {}
  if (loginName) {
    params.login_name = loginName
  }
  return getAllFeedback(params)
}

/**
 * Submit new feedback
 * @param {Object} feedbackData - Feedback data
 * @param {Object} userInfo - User info
 * @returns {Object} Result with success flag
 */
export async function submitFeedback(feedbackData, userInfo) {
  try {
    const payload = {
      category: feedbackData.category,
      subject: feedbackData.subject,
      content: feedbackData.content,
      status: FeedbackStatus.PENDING
    }

    if (userInfo?.loginName) {
      payload.login_name = userInfo.loginName
    }
    if (userInfo?.userName) {
      payload.user_name = userInfo.userName
    }

    const { data } = await client.post('/feedback', payload)
    return {
      success: true,
      data: normalizeFeedbackRecord(data?.data || {})
    }
  } catch (error) {
    console.error('[Feedback API] Failed to submit feedback:', error)
    return {
      success: false,
      error: error?.response?.data?.error || error.message || '反馈提交失败'
    }
  }
}

/**
 * Delete feedback by ID
 * @param {string|number} id - Feedback ID
 * @returns {Object} Result with success flag
 */
export async function deleteFeedback(id) {
  try {
    await client.delete(`/feedback/${id}`)
    return { success: true }
  } catch (error) {
    console.error('[Feedback API] Failed to delete feedback:', error)
    return {
      success: false,
      error: error?.response?.data?.error || error.message || '删除反馈失败'
    }
  }
}

function normalizeFeedbackRecord(raw) {
  return {
    id: raw?.id,
    category: raw?.category || '',
    subject: raw?.subject || '',
    content: raw?.content || '',
    loginName: raw?.login_name || raw?.loginName || '',
    userName: raw?.user_name || raw?.userName || '',
    status: raw?.status || FeedbackStatus.PENDING,
    createdAt: raw?.created_at || raw?.createdAt || null,
    updatedAt: raw?.updated_at || raw?.updatedAt || null
  }
}

/**
 * Validate feedback data
 * @param {Object} data - Feedback data
 * @returns {Object} Validation result with error message if invalid
 */
export function validateFeedback(data) {
  if (!data.category) {
    return { valid: false, error: '请选择反馈类型' }
  }
  if (!data.subject || data.subject.trim().length < 2) {
    return { valid: false, error: '请输入主题（至少2个字符）' }
  }
  if (!data.content || data.content.trim().length < 10) {
    return { valid: false, error: '请输入详细内容（至少10个字符）' }
  }
  if (data.subject.length > 100) {
    return { valid: false, error: '主题不能超过100个字符' }
  }
  if (data.content.length > 2000) {
    return { valid: false, error: '内容不能超过2000个字符' }
  }
  return { valid: true }
}
