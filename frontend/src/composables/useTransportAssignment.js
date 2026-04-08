/**
 * useTransportAssignment - Composable for transport assignment workflow.
 *
 * This composable handles transport assignment logic:
 * - Loading production prep users
 * - Transport type and assignee selection
 * - Dispatching transport tasks
 */

import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assignTransport } from '@/api/orders'
import { getUsersByRole } from '@/api/users'

export function useTransportAssignment(session, confirmFormRef) {
  // State
  const productionPrepUsers = ref([])

  // Computed
  const canDispatchTransport = computed(
    () =>
      session.hasPermission('order:keeper_confirm') &&
      ['keeper_confirmed', 'partially_confirmed'].includes(confirmFormRef.value?.orderStatus) &&
      !confirmFormRef.value?.transportOperatorId
  )

  // Helpers
  function applyDefaultTransportAssignee(users) {
    const normalizedUsers = Array.isArray(users) ? users : []
    const currentUser = normalizedUsers.find((user) => user.user_id === confirmFormRef.value?.transportAssigneeId)
    const fengliang = normalizedUsers.find((user) => user.login_name === 'fengliang')
    const fallbackUser = currentUser || fengliang || normalizedUsers[0] || null

    if (!fallbackUser) {
      confirmFormRef.value.transportAssigneeId = ''
      confirmFormRef.value.transportAssigneeName = ''
      return
    }

    confirmFormRef.value.transportAssigneeId = fallbackUser.user_id
    confirmFormRef.value.transportAssigneeName = fallbackUser.display_name
  }

  // Actions
  async function loadProductionPrepUsers() {
    const orgId = session.currentOrg?.org_id || session.defaultOrg?.org_id || ''
    try {
      productionPrepUsers.value = await getUsersByRole('production_prep_worker', orgId ? { org_id: orgId } : {})
      applyDefaultTransportAssignee(productionPrepUsers.value)
    } catch (error) {
      productionPrepUsers.value = []
      confirmFormRef.value.transportAssigneeId = ''
      confirmFormRef.value.transportAssigneeName = ''
      console.error('Failed to load production prep users:', error)
    }
  }

  function onTransportAssigneeChange(userId) {
    const user = productionPrepUsers.value.find((item) => item.user_id === userId)
    confirmFormRef.value.transportAssigneeName = user ? user.display_name : ''
  }

  async function openDispatchTransportDialog() {
    const action = await ElMessageBox.confirm(
      `确认派遣运输任务给 ${confirmFormRef.value.transportAssigneeName || '指定运输负责人'} 吗？`,
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

  async function dispatchTransport(orderNo) {
    const payload = {
      transport_type: confirmFormRef.value.transportType,
      transport_assignee_id: confirmFormRef.value.transportAssigneeId,
      transport_assignee_name: confirmFormRef.value.transportAssigneeName,
      operator_id: session.userId,
      operator_name: session.userName,
      operator_role: session.role
    }

    const result = await assignTransport(orderNo, payload)
    if (!result.success) return

    ElMessage.success('运输任务已派遣')
  }

  return {
    // State
    productionPrepUsers,
    // Computed
    canDispatchTransport,
    // Actions
    loadProductionPrepUsers,
    onTransportAssigneeChange,
    openDispatchTransportDialog,
    dispatchTransport,
    // Helpers
    applyDefaultTransportAssignee
  }
}
