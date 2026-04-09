/**
 * useFeedback - Composable for feedback management.
 *
 * This composable handles:
 * - Loading user feedback history
 * - Submitting new feedback
 * - Deleting feedback
 */

import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  submitFeedback,
  getUserFeedback,
  deleteFeedback,
  FeedbackCategory,
  FeedbackCategoryLabels,
  FeedbackStatus,
  FeedbackStatusLabels,
  validateFeedback
} from '@/api/feedback'

export function useFeedback(session) {
  // State
  const feedbackCategories = computed(() => [
    { value: FeedbackCategory.BUG, label: FeedbackCategoryLabels[FeedbackCategory.BUG] },
    { value: FeedbackCategory.FEATURE, label: FeedbackCategoryLabels[FeedbackCategory.FEATURE] },
    { value: FeedbackCategory.UX, label: FeedbackCategoryLabels[FeedbackCategory.UX] },
    { value: FeedbackCategory.OTHER, label: FeedbackCategoryLabels[FeedbackCategory.OTHER] }
  ])

  const feedbackForm = ref({
    category: FeedbackCategory.BUG,
    subject: '',
    content: ''
  })
  const feedbackLoading = ref(false)
  const userFeedbackList = ref([])

  // Helpers
  function getCategoryLabel(category) {
    return FeedbackCategoryLabels[category] || category
  }

  function getStatusLabel(status) {
    return FeedbackStatusLabels[status] || status
  }

  function formatDateTime(dateStr) {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Actions
  async function loadUserFeedback() {
    if (!session.loginName) return
    userFeedbackList.value = await getUserFeedback(session.loginName)
  }

  async function handleFeedbackSubmit() {
    const validation = validateFeedback(feedbackForm.value)
    if (!validation.valid) {
      ElMessage.warning(validation.error)
      return { success: false }
    }

    feedbackLoading.value = true
    try {
      const result = await submitFeedback(feedbackForm.value, {
        loginName: session.loginName,
        userName: session.userName
      })

      if (result.success) {
        ElMessage.success('反馈提交成功')
        feedbackForm.value = { category: FeedbackCategory.BUG, subject: '', content: '' }
        await loadUserFeedback()
        return { success: true }
      } else {
        ElMessage.error(result.error || '反馈提交失败')
        return { success: false, error: result.error }
      }
    } catch (error) {
      ElMessage.error(error.message || '反馈提交失败')
      return { success: false, error }
    } finally {
      feedbackLoading.value = false
    }
  }

  async function handleDeleteFeedback(id) {
    const result = await deleteFeedback(id)
    if (result.success) {
      ElMessage.success('反馈已删除')
      await loadUserFeedback()
      return { success: true }
    } else {
      ElMessage.error(result.error || '删除失败')
      return { success: false, error: result.error }
    }
  }

  return {
    // State
    feedbackCategories,
    feedbackForm,
    feedbackLoading,
    userFeedbackList,
    // Helpers
    getCategoryLabel,
    getStatusLabel,
    formatDateTime,
    // Actions
    loadUserFeedback,
    handleFeedbackSubmit,
    handleDeleteFeedback
  }
}
