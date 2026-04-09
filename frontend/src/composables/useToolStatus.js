/**
 * useToolStatus - Composable for tool status management.
 *
 * This composable handles the tool status management tab functionality:
 * - Searching and selecting tools
 * - Batch status updates
 * - Status history viewing
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { searchTools, batchUpdateToolStatus, getToolStatusHistory } from '@/api/tools'

export function useToolStatus(session) {
  // State
  const toolSearchKeyword = ref('')
  const selectedTools = ref([])
  const newToolStatus = ref('in_storage')
  const statusRemark = ref('')
  const submittingStatus = ref(false)
  const statusHistory = ref([])
  const historyLoading = ref(false)
  const searchLoading = ref(false)

  const toolStatusOptions = [
    { label: '在库', value: 'in_storage' },
    { label: '已出库', value: 'outbounded' },
    { label: '维修中', value: 'maintain' },
    { label: '已报废', value: 'scrapped' }
  ]

  // Helpers
  function toolStatusLabel(status) {
    return toolStatusOptions.find((opt) => opt.value === status)?.label || status
  }

  // Actions
  async function handleSearchTools(query) {
    if (!query) return
    searchLoading.value = true
    try {
      const result = await searchTools({ keyword: query })
      if (result.success && result.data.length > 0) {
        const tool = result.data[0]
        if (!selectedTools.value.some((t) => t.serialNo === tool.serialNo)) {
          selectedTools.value.push(tool)
          loadToolHistory(tool.serialNo)
        }
      } else {
        ElMessage.info('未找到匹配的工装')
      }
    } finally {
      searchLoading.value = false
      toolSearchKeyword.value = ''
    }
  }

  function removeTool(tool) {
    selectedTools.value = selectedTools.value.filter((t) => t.serialNo !== tool.serialNo)
  }

  async function applyStatusChange() {
    if (selectedTools.value.length === 0) {
      ElMessage.warning('请先选择工装')
      return
    }
    if (!newToolStatus.value) {
      ElMessage.warning('请选择新状态')
      return
    }

    submittingStatus.value = true
    try {
      const result = await batchUpdateToolStatus({
        serial_nos: selectedTools.value.map((t) => t.serialNo),
        new_status: newToolStatus.value,
        remark: statusRemark.value,
        operator_id: session.userId,
        operator_name: session.userName,
        operator_role: session.role
      })

      if (result.data.success) {
        ElMessage.success('状态更新成功')
        statusRemark.value = ''
        if (selectedTools.value.length > 0) {
          loadToolHistory(selectedTools.value[0].serialNo)
        }
        selectedTools.value.forEach((t) => {
          t.currentStatus = newToolStatus.value
          t.statusText = toolStatusOptions.find(opt => opt.value === newToolStatus.value)?.label || newToolStatus.value
        })
      }
    } finally {
      submittingStatus.value = false
    }
  }

  async function loadToolHistory(serialNo) {
    historyLoading.value = true
    try {
      const result = await getToolStatusHistory(serialNo)
      if (result.data.success) {
        statusHistory.value = result.data.data
      }
    } finally {
      historyLoading.value = false
    }
  }

  return {
    // State
    toolSearchKeyword,
    selectedTools,
    newToolStatus,
    statusRemark,
    submittingStatus,
    statusHistory,
    historyLoading,
    searchLoading,
    toolStatusOptions,
    // Actions
    handleSearchTools,
    removeTool,
    applyStatusChange,
    loadToolHistory,
    toolStatusLabel
  }
}
