/**
 * useSystemSettings - Composable for system settings and feature flags.
 *
 * This composable handles:
 * - Loading system configuration
 * - Loading feature flags
 * - Updating MPL configuration
 * - Updating feature flags
 * - URL config editing
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemConfigs, updateSystemConfig, getFeatureFlags, updateFeatureFlag } from '@/api/systemConfig'

export function useSystemSettings(session) {
  // State
  const systemConfigLoading = ref(false)
  const systemConfig = ref({
    mpl_enabled: false,
    mpl_strict_mode: false
  })
  const featureFlagsLoading = ref(false)
  const featureFlags = ref([])

  // URL config keys that should NOT use el-switch
  const urlConfigKeys = new Set([
    'feishu_webhook_supply_team',
    'feishu_webhook_transport',
    'feishu_webhook_url'
  ])

  // URL edit dialog state
  const urlEditDialog = ref({
    visible: false,
    loading: false,
    key: '',
    value: '',
    description: ''
  })

  // Actions
  async function loadSystemConfig() {
    if (!session.hasPermission('admin:user_manage')) return
    systemConfigLoading.value = true
    try {
      const result = await getSystemConfigs()
      const rows = Array.isArray(result.data) ? result.data : []
      systemConfig.value = {
        mpl_enabled: rows.find((item) => item.config_key === 'mpl_enabled')?.config_value === 'true',
        mpl_strict_mode: rows.find((item) => item.config_key === 'mpl_strict_mode')?.config_value === 'true'
      }
    } finally {
      systemConfigLoading.value = false
    }
  }

  async function updateMplConfig(configKey, value) {
    systemConfigLoading.value = true
    try {
      const result = await updateSystemConfig(configKey, { config_value: value ? 'true' : 'false' })
      if (result.success) {
        ElMessage.success('系统配置已更新')
      }
      return result
    } catch (error) {
      ElMessage.error(error.message || '系统配置更新失败')
      await loadSystemConfig()
      return { success: false, error }
    } finally {
      systemConfigLoading.value = false
    }
  }

  async function loadFeatureFlags() {
    if (!session.hasPermission('admin:user_manage')) return
    featureFlagsLoading.value = true
    try {
      const result = await getFeatureFlags()
      featureFlags.value = Array.isArray(result.data) ? result.data.map(f => ({ ...f, _loading: false })) : []
      return result
    } catch (error) {
      ElMessage.error(error.message || '获取功能开关列表失败')
      return { success: false, error }
    } finally {
      featureFlagsLoading.value = false
    }
  }

  async function updateFeatureFlagHandler(flagKey, value) {
    const flag = featureFlags.value.find(f => f.config_key === flagKey)
    if (flag) {
      flag._loading = true
    }
    try {
      const result = await updateFeatureFlag(flagKey, value ? 'true' : 'false')
      if (result.success) {
        ElMessage.success('功能开关已更新')
        await loadFeatureFlags()
      } else {
        ElMessage.error(result.error || '功能开关更新失败')
      }
      return result
    } catch (error) {
      ElMessage.error(error.message || '功能开关更新失败')
      return { success: false, error }
    } finally {
      if (flag) {
        flag._loading = false
      }
    }
  }

  function openUrlEditDialog(row) {
    urlEditDialog.value = {
      visible: true,
      loading: false,
      key: row.config_key,
      value: row.config_value,
      description: row.description || ''
    }
  }

  async function saveUrlConfig() {
    if (!urlEditDialog.value.value) {
      ElMessage.warning('请输入 Webhook URL')
      return { success: false }
    }
    urlEditDialog.value.loading = true
    try {
      const result = await updateSystemConfig(urlEditDialog.value.key, {
        config_value: urlEditDialog.value.value
      })
      if (result.success) {
        ElMessage.success('Webhook URL 已保存')
        urlEditDialog.value.visible = false
        await loadFeatureFlags()
      } else {
        ElMessage.error(result.error || '保存失败')
      }
      return result
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
      return { success: false, error }
    } finally {
      urlEditDialog.value.loading = false
    }
  }

  return {
    // State
    systemConfigLoading,
    systemConfig,
    featureFlagsLoading,
    featureFlags,
    urlConfigKeys,
    urlEditDialog,
    // Actions
    loadSystemConfig,
    updateMplConfig,
    loadFeatureFlags,
    updateFeatureFlagHandler,
    openUrlEditDialog,
    saveUrlConfig
  }
}
