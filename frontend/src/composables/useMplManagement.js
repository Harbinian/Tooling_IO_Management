/**
 * useMplManagement - Composable for MPL (Maintenance Parts List) management.
 *
 * This composable handles MPL-related functionality:
 * - Loading MPL statuses for order items
 * - Opening MPL detail dialogs
 * - Managing MPL warnings
 */

import { ref } from 'vue'
import { getMplByTool } from '@/api/mpl'

export function useMplManagement() {
  // State
  const mplDialogVisible = ref(false)
  const selectedMplItem = ref(null)
  const selectedMplGroup = ref(null)

  // Actions
  function openMplDetail(item) {
    selectedMplItem.value = item
    selectedMplGroup.value = item.mplGroup || null
    mplDialogVisible.value = true
  }

  async function loadMplStatuses(items, confirmItemsRef, mplWarningsRef) {
    const results = await Promise.all(
      (items || []).map(async (item) => {
        if (!item.drawingNo || !item.currentVersion) {
          return { key: item.serialNo, exists: false, message: `工装 ${item.drawingNo || item.serialNo || '-'} 缺少版次，无法匹配 MPL`, group: null }
        }
        const result = await getMplByTool(item.drawingNo, item.currentVersion).catch(() => ({ success: false }))
        return {
          key: item.serialNo,
          exists: !!result.success,
          message: result.success ? '' : `工装 ${item.drawingNo} (版次 ${item.currentVersion}) 缺少可拆卸件清单`,
          group: result.data || null
        }
      })
    )

    const groupMap = new Map(results.map((entry) => [entry.key, entry]))
    confirmItemsRef.value = confirmItemsRef.value.map((item) => {
      const match = groupMap.get(item.serialNo)
      return { ...item, mplExists: !!match?.exists, mplGroup: match?.group || null }
    })
    if (mplWarningsRef) {
      mplWarningsRef.value = results.filter((entry) => !entry.exists && entry.message).map((entry) => entry.message)
    }
  }

  return {
    // State
    mplDialogVisible,
    selectedMplItem,
    selectedMplGroup,
    // Actions
    openMplDetail,
    loadMplStatuses
  }
}
