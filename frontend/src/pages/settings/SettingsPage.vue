<template>
  <div class="space-y-8 animate-in fade-in duration-500 text-foreground">
    <!-- Page Header -->
    <header class="relative overflow-hidden rounded-3xl bg-primary px-8 py-12 text-primary-foreground shadow-2xl">
      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-4">
          <Badge variant="outline" class="border-primary-foreground/20 bg-primary-foreground/10 text-primary-foreground backdrop-blur-sm uppercase tracking-widest text-[10px]">
            个人中心
          </Badge>
        </div>
        <h1 class="text-3xl font-bold tracking-tight md:text-4xl text-primary-foreground">
          设置
        </h1>
        <p class="mt-3 text-primary-foreground/80 max-w-2xl text-sm leading-relaxed">
          管理您的个人资料、修改密码、切换主题风格，以及提交问题反馈。
        </p>
      </div>
      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary-foreground/10 blur-3xl"></div>
      <div class="absolute left-1/3 bottom-0 h-32 w-32 rounded-full bg-blue-500/10 blur-2xl"></div>
    </header>

    <!-- Settings Tabs -->
    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane label="个人资料" name="profile">
        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">个人资料</p>
              <CardTitle class="text-lg text-foreground">账户信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="grid gap-6 md:grid-cols-2">
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">用户名</p>
                <p class="text-sm font-semibold text-foreground/80">{{ session.userName || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">登录名</p>
                <p class="text-sm font-semibold text-foreground/80">{{ session.loginName || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">工号</p>
                <p class="text-sm font-semibold text-foreground/80">{{ session.employeeNo || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">角色</p>
                <p class="text-sm font-semibold text-foreground/80">{{ displayRole }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">所属部门</p>
                <p class="text-sm font-semibold text-foreground/80">{{ session.department || '-' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">权限</p>
                <div class="flex flex-wrap gap-2 mt-1">
                  <span
                    v-for="perm in session.permissions || []"
                    :key="perm"
                    class="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground border border-border/50"
                  >
                    {{ formatPermission(perm) }}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </el-tab-pane>

      <el-tab-pane label="修改密码" name="password">
        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">安全设置</p>
              <CardTitle class="text-lg text-foreground">修改密码</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <form @submit.prevent="handlePasswordChange" class="max-w-md space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">当前密码</label>
                <Input
                  v-model="passwordForm.oldPassword"
                  type="password"
                  placeholder="请输入当前密码"
                  :disabled="passwordLoading"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">新密码</label>
                <Input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码（至少6位）"
                  :disabled="passwordLoading"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">确认新密码</label>
                <Input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                  :disabled="passwordLoading"
                />
              </div>
              <Button type="submit" :disabled="passwordLoading" class="bg-primary text-primary-foreground border-none hover:bg-primary/90">
                {{ passwordLoading ? '提交中...' : '确认修改' }}
              </Button>
            </form>
          </CardContent>
        </Card>
      </el-tab-pane>

      <el-tab-pane label="外观" name="appearance">
        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">显示设置</p>
              <CardTitle class="text-lg text-foreground">外观主题</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-6">
              <div class="space-y-1">
                <p class="text-sm font-semibold text-foreground">深色模式</p>
                <p class="text-sm text-muted-foreground">切换系统界面的明暗主题风格</p>
              </div>
              <el-switch v-model="isDarkMode" @change="toggleTheme" />
            </div>
          </CardContent>
        </Card>
      </el-tab-pane>

      <el-tab-pane v-if="session.hasPermission('admin:user_manage')" label="系统设置" name="system">
        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">系统能力</p>
              <CardTitle class="text-lg text-foreground">功能开关</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <!-- Feature Flags Table -->
            <div class="mb-6">
              <h3 class="text-sm font-semibold text-foreground mb-4">功能开关管理</h3>
              <el-table :data="featureFlags" stripe class="w-full" v-loading="featureFlagsLoading">
                <el-table-column prop="config_key" label="开关键" min-width="180" />
                <el-table-column prop="config_value" label="当前值" min-width="140">
                  <template #default="{ row }">
                    <template v-if="urlConfigKeys.has(row.config_key)">
                      <el-tag type="info" disable-transitions class="max-w-[120px] truncate" :title="row.config_value">
                        {{ row.config_value }}
                      </el-tag>
                    </template>
                    <template v-else>
                      <el-tag :type="row.config_value === 'true' ? 'success' : 'info'" disable-transitions>
                        {{ row.config_value }}
                      </el-tag>
                    </template>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" min-width="240" show-overflow-tooltip />
                <el-table-column prop="updated_by" label="最后更新人" min-width="100" />
                <el-table-column prop="updated_at" label="更新时间" min-width="160">
                  <template #default="{ row }">
                    {{ formatDateTime(row.updated_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="120" fixed="right">
                  <template #default="{ row }">
                    <template v-if="urlConfigKeys.has(row.config_key)">
                      <el-button type="primary" link @click="openUrlEditDialog(row)">
                        编辑
                      </el-button>
                    </template>
                    <template v-else>
                      <el-switch
                        :model-value="row.config_value === 'true'"
                        :loading="row._loading"
                        @change="(value) => updateFeatureFlagHandler(row.config_key, value)"
                        active-value="true"
                        inactive-value="false"
                      />
                    </template>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- URL Edit Dialog -->
            <el-dialog
              v-model="urlEditDialog.visible"
              title="编辑 Webhook URL"
              width="500px"
              :close-on-click-modal="false"
            >
              <div class="space-y-4">
                <div class="space-y-2">
                  <label class="text-sm font-medium text-foreground">{{ urlEditDialog.key }}</label>
                  <p class="text-xs text-muted-foreground">{{ urlEditDialog.description }}</p>
                </div>
                <el-input
                  v-model="urlEditDialog.value"
                  placeholder="请输入 Webhook URL"
                  :loading="urlEditDialog.loading"
                />
              </div>
              <template #footer>
                <el-button @click="urlEditDialog.visible = false" :disabled="urlEditDialog.loading">
                  取消
                </el-button>
                <el-button type="primary" @click="saveUrlConfig" :loading="urlEditDialog.loading">
                  保存
                </el-button>
              </template>
            </el-dialog>

            <!-- MPL Specific Settings -->
            <div>
              <h3 class="text-sm font-semibold text-foreground mb-4">MPL 功能</h3>
              <div class="space-y-4">
                <div class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-6">
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-foreground">启用 MPL 校验</p>
                    <p class="text-sm text-muted-foreground">保管员确认时检查工装是否已维护可拆卸件清单。</p>
                  </div>
                  <el-switch v-model="systemConfig.mpl_enabled" :loading="systemConfigLoading" @change="(value) => updateMplConfig('mpl_enabled', value)" />
                </div>
                <div class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-6">
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-foreground">严格模式</p>
                    <p class="text-sm text-muted-foreground">缺少 MPL 时阻止保管员完成确认，而不是仅显示警告。</p>
                  </div>
                  <el-switch v-model="systemConfig.mpl_strict_mode" :loading="systemConfigLoading" @change="(value) => updateMplConfig('mpl_strict_mode', value)" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </el-tab-pane>

      <el-tab-pane label="问题反馈" name="feedback">
        <Card class="border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">问题反馈</p>
              <CardTitle class="text-lg text-foreground">提交反馈</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <form @submit.prevent="handleFeedbackSubmit" class="space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">反馈类型</label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="cat in feedbackCategories"
                    :key="cat.value"
                    type="button"
                    :class="[
                      'rounded-xl px-4 py-2 text-sm font-medium transition-all border',
                      feedbackForm.category === cat.value
                        ? 'bg-primary text-primary-foreground border-primary'
                        : 'bg-muted text-muted-foreground border-border hover:bg-accent'
                    ]"
                    @click="feedbackForm.category = cat.value"
                  >
                    {{ cat.label }}
                  </button>
                </div>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">主题</label>
                <Input
                  v-model="feedbackForm.subject"
                  placeholder="请简要描述问题或建议"
                  :disabled="feedbackLoading"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">详情内容</label>
                <Textarea
                  v-model="feedbackForm.content"
                  placeholder="请详细描述您遇到的问题或改进建议，以便我们更好地理解和解决..."
                  :rows="5"
                  :disabled="feedbackLoading"
                />
              </div>
              <Button type="submit" :disabled="feedbackLoading" class="bg-primary text-primary-foreground border-none hover:bg-primary/90">
                {{ feedbackLoading ? '提交中...' : '提交反馈' }}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card v-if="userFeedbackList.length > 0" class="mt-6 border-border bg-card shadow-xl">
          <CardHeader class="border-b border-border">
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">我的反馈</p>
              <CardTitle class="text-lg text-foreground">历史记录</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="space-y-4">
              <div
                v-for="feedback in userFeedbackList"
                :key="feedback.id"
                class="rounded-2xl border border-border bg-muted/20 p-4"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="space-y-2 flex-1">
                    <div class="flex items-center gap-2">
                      <span
                        :class="[
                          'rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider',
                          feedback.category === 'bug' ? 'bg-rose-500/10 text-rose-500' :
                          feedback.category === 'feature' ? 'bg-emerald-500/10 text-emerald-500' :
                          feedback.category === 'ux' ? 'bg-amber-500/10 text-amber-500' :
                          'bg-muted text-muted-foreground'
                        ]"
                      >
                        {{ getCategoryLabel(feedback.category) }}
                      </span>
                      <span class="text-xs text-muted-foreground/60">{{ formatDateTime(feedback.createdAt) }}</span>
                    </div>
                    <p class="font-semibold text-foreground">{{ feedback.subject }}</p>
                    <p class="text-sm text-muted-foreground">{{ feedback.content }}</p>
                  </div>
                  <div class="flex items-center gap-2">
                    <span
                      :class="[
                        'rounded-full px-3 py-1 text-xs font-medium',
                        feedback.status === 'pending' ? 'bg-amber-500/10 text-amber-500' :
                        feedback.status === 'reviewed' ? 'bg-blue-500/10 text-blue-500' :
                        'bg-emerald-500/10 text-emerald-500'
                      ]"
                    >
                      {{ getStatusLabel(feedback.status) }}
                    </span>
                    <button
                      class="p-1 text-muted-foreground hover:text-destructive transition-colors"
                      @click="handleDeleteFeedback(feedback.id)"
                      title="删除"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Trash2 } from 'lucide-vue-next'

import { useSessionStore } from '@/store/session'
import { changePassword } from '@/api/auth'
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
import { getSystemConfigs, updateSystemConfig, getFeatureFlags, updateFeatureFlag } from '@/api/systemConfig'

import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'

const session = useSessionStore()
const activeTab = ref('profile')

const displayRole = computed(() => {
  const roleMap = {
    admin: '管理员',
    keeper: '保管员',
    team_leader: '班组长',
    initiator: '发起人'
  }
  return roleMap[session.role] || session.roleName || '-'
})

function formatPermission(perm) {
  const permMap = {
    'dashboard:view': '查看仪表盘',
    'order:list': '订单列表',
    'order:create': '创建订单',
    'order:view': '查看详情',
    'order:submit': '提交订单',
    'order:keeper_confirm': '保管员确认',
    'order:final_confirm': '最终确认',
    'order:cancel': '取消订单',
    'tool:search': '工装搜索',
    'tool:view': '工装查看',
    'mpl:view': 'MPL查看',
    'mpl:write': 'MPL维护',
    'notification:view': '通知查看',
    'admin:user_manage': '账号管理'
  }
  return permMap[perm] || perm
}

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordLoading = ref(false)

async function handlePasswordChange() {
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (passwordForm.value.newPassword.length < 8) {
    ElMessage.warning('新密码长度至少为 8 位')
    return
  }
  const hasUpper = /[A-Z]/.test(passwordForm.value.newPassword)
  const hasLower = /[a-z]/.test(passwordForm.value.newPassword)
  const hasDigit = /\d/.test(passwordForm.value.newPassword)
  if (!(hasUpper && hasLower && hasDigit)) {
    ElMessage.warning('新密码必须包含大小写字母和数字')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  passwordLoading.value = true
  try {
    await changePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    ElMessage.success('密码修改成功')
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  } catch (error) {
    ElMessage.error(error.message || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

// Theme
const isDarkMode = ref(false)
let userManualOverride = false
let mediaQuery = null
let mediaQueryHandler = null

function toggleTheme(value) {
  userManualOverride = true // 用户手动选择后不再响应系统
  const theme = value ? 'dark' : 'light'
  localStorage.setItem('theme', theme)
  applyTheme(value)
}

function applyTheme(isDark) {
  document.documentElement.classList.toggle('dark', isDark)
}

function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
    userManualOverride = true // 如果有保存的主题，视为已手动覆盖
  } else {
    // No saved preference, use system preference
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme(isDarkMode.value)
}

function bindSystemThemeListener() {
  mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQueryHandler = (event) => {
    if (!userManualOverride) {
      isDarkMode.value = event.matches
      applyTheme(event.matches)
    }
  }
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', mediaQueryHandler)
  } else if (mediaQuery.addListener) {
    mediaQuery.addListener(mediaQueryHandler)
  }
}

// Feedback
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

async function loadUserFeedback() {
  if (!session.loginName) return
  userFeedbackList.value = await getUserFeedback(session.loginName)
}

async function handleFeedbackSubmit() {
  const validation = validateFeedback(feedbackForm.value)
  if (!validation.valid) {
    ElMessage.warning(validation.error)
    return
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
    } else {
      ElMessage.error(result.error || '反馈提交失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '反馈提交失败')
  } finally {
    feedbackLoading.value = false
  }
}

async function handleDeleteFeedback(id) {
  const result = await deleteFeedback(id)
  if (result.success) {
    ElMessage.success('反馈已删除')
    await loadUserFeedback()
  } else {
    ElMessage.error(result.error || '删除失败')
  }
}

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
  } catch (error) {
    ElMessage.error(error.message || '系统配置更新失败')
    await loadSystemConfig()
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
  } catch (error) {
    ElMessage.error(error.message || '获取功能开关列表失败')
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
  } catch (error) {
    ElMessage.error(error.message || '功能开关更新失败')
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
    return
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
  } catch (error) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    urlEditDialog.value.loading = false
  }
}

onMounted(async () => {
  initTheme()
  bindSystemThemeListener()
  await loadUserFeedback()
  await loadSystemConfig()
  await loadFeatureFlags()
})

onBeforeUnmount(() => {
  if (mediaQuery && mediaQueryHandler) {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', mediaQueryHandler)
    } else if (mediaQuery.removeListener) {
      mediaQuery.removeListener(mediaQueryHandler)
    }
  }
})
</script>

<style scoped>
.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: hsl(var(--border) / 0.5);
}

.settings-tabs :deep(.el-tabs__active-bar) {
  background-color: hsl(var(--primary));
  height: 2px;
}

.settings-tabs :deep(.el-tabs__item) {
  font-size: 0.875rem;
  font-weight: 600;
  color: hsl(var(--muted-foreground));
  transition: all 0.2s ease;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: hsl(var(--foreground));
}

.settings-tabs :deep(.el-tabs__item:hover) {
  color: hsl(var(--foreground));
}
</style>
