<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import {
  createAdminUser,
  getAdminRoles,
  getAdminUserDetail,
  getAdminUsers,
  resetAdminUserPassword,
  updateAdminUser,
  updateAdminUserRoles,
  updateAdminUserStatus
} from '@/api/adminUsers'
import { getOrgTree } from '@/api/orgs'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardDescription from '@/components/ui/CardDescription.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import NativeSelect from '@/components/ui/NativeSelect.vue'

// Temporary notification helper until toast library is set up
const showToast = (msg) => {
  console.log('[Toast]', msg)
  alert(msg)
}


const loading = ref(false)
const saving = ref(false)
const users = ref([])
const roles = ref([])
const orgTree = ref([])
const selectedUserId = ref('')
const resetPassword = ref('')

const filters = reactive({
  keyword: '',
  status: '',
  orgId: ''
})

const form = reactive({
  loginName: '',
  displayName: '',
  employeeNo: '',
  defaultOrgId: '',
  roleIds: [],
  status: 'active',
  initialPassword: ''
})

const isCreateMode = computed(() => !selectedUserId.value)

function getStatusLabel(status) {
  return status === 'active' ? '启用' : '停用'
}

const flattenedOrgs = computed(() => {
  const items = []
  const visit = (nodes, depth = 0) => {
    nodes.forEach((node) => {
      items.push({
        org_id: node.org_id,
        label: `${'  '.repeat(depth)}${node.org_name}`,
        status: node.status
      })
      if (Array.isArray(node.children) && node.children.length) {
        visit(node.children, depth + 1)
      }
    })
  }
  visit(orgTree.value)
  return items
})

const selectedUser = computed(() => users.value.find((user) => user.user_id === selectedUserId.value) || null)

function resetForm() {
  selectedUserId.value = ''
  resetPassword.value = ''
  form.loginName = ''
  form.displayName = ''
  form.employeeNo = ''
  form.defaultOrgId = ''
  form.roleIds = []
  form.status = 'active'
  form.initialPassword = ''
  // Scroll to form for visual feedback
  nextTick(() => {
    document.querySelector('[data-form-card]')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    // Focus first input for immediate editing
    const firstInput = document.querySelector('[data-form-card] input')
    firstInput?.focus()
  })
}

function applyUserDetail(user) {
  selectedUserId.value = user.user_id
  resetPassword.value = ''
  form.loginName = user.login_name || ''
  form.displayName = user.display_name || ''
  form.employeeNo = user.employee_no || ''
  form.defaultOrgId = user.default_org_id || ''
  form.roleIds = (user.roles || []).map((role) => role.role_id)
  form.status = user.status || 'active'
  form.initialPassword = ''
}

async function loadUsers() {
  loading.value = true
  try {
    users.value = await getAdminUsers({
      keyword: filters.keyword,
      status: filters.status,
      org_id: filters.orgId
    })
    if (selectedUserId.value) {
      const refreshed = users.value.find((user) => user.user_id === selectedUserId.value)
      if (refreshed) {
        const detail = await getAdminUserDetail(refreshed.user_id)
        applyUserDetail(detail)
      }
    }
  } finally {
    loading.value = false
  }
}

async function loadReferenceData() {
  const [roleData, orgData] = await Promise.all([getAdminRoles(), getOrgTree(true)])
  roles.value = roleData
  orgTree.value = orgData
}

async function selectUser(userId) {
  const detail = await getAdminUserDetail(userId)
  applyUserDetail(detail)
}

function toggleRole(roleId) {
  if (form.roleIds.includes(roleId)) {
    form.roleIds = form.roleIds.filter((current) => current !== roleId)
    return
  }
  form.roleIds = [...form.roleIds, roleId]
}

function buildBasePayload() {
  return {
    login_name: form.loginName.trim(),
    display_name: form.displayName.trim(),
    employee_no: form.employeeNo.trim(),
    default_org_id: form.defaultOrgId || null,
    role_ids: form.roleIds,
    status: form.status
  }
}

async function submitForm() {
  saving.value = true
  try {
    if (isCreateMode.value) {
      await createAdminUser({
        ...buildBasePayload(),
        initial_password: form.initialPassword
      })
      showToast('账户创建成功')
      resetForm()
    } else {
      await updateAdminUser(selectedUserId.value, buildBasePayload())
      await updateAdminUserRoles(selectedUserId.value, {
        role_ids: form.roleIds,
        org_id: form.defaultOrgId || null
      })
      showToast('账户更新成功')
    }
    await loadUsers()
  } finally {
    saving.value = false
  }
}

async function submitPasswordReset() {
  if (!selectedUserId.value || !resetPassword.value.trim()) {
    return
  }
  saving.value = true
  try {
    await resetAdminUserPassword(selectedUserId.value, {
      new_password: resetPassword.value
    })
    resetPassword.value = ''
    showToast('密码重置成功')
  } finally {
    saving.value = false
  }
}

async function quickToggleStatus(user) {
  const nextStatus = user.status === 'active' ? 'disabled' : 'active'
  await updateAdminUserStatus(user.user_id, { status: nextStatus })
  if (user.user_id === selectedUserId.value) {
    form.status = nextStatus
  }
  await loadUsers()
}

onMounted(async () => {
  await loadReferenceData()
  await loadUsers()
})
</script>

<template>
  <div class="space-y-6 text-foreground">
    <section class="space-y-2">
      <p class="text-xs font-medium uppercase tracking-[0.28em] text-muted-foreground">系统管理</p>
      <h1 class="text-3xl font-semibold tracking-tight text-foreground">账号管理</h1>
      <p class="max-w-3xl text-sm leading-6 text-muted-foreground">
        创建系统账号，维护员工身份信息，设置默认部门，并绑定一个或多个 RBAC 角色。
      </p>
    </section>

    <div class="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
      <Card v-debug-id="DEBUG_IDS.ADMIN.USER_LIST_CARD" class="overflow-hidden border-border bg-card shadow-sm">
        <CardHeader class="border-b border-border bg-muted/30">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div class="space-y-1">
              <CardTitle class="text-lg text-foreground">账号列表</CardTitle>
              <CardDescription>仅管理员可见的账号清单，展示角色与部门归属信息。</CardDescription>
            </div>
            <div class="flex flex-wrap gap-2">
              <Button v-debug-id="DEBUG_IDS.ADMIN.CREATE_USER_BTN" variant="outline" @click="resetForm">新建账号</Button>
              <Button v-debug-id="DEBUG_IDS.ADMIN.REFRESH_BTN" variant="outline" @click="loadUsers">刷新</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="space-y-4 pt-6">
          <div class="grid gap-3 md:grid-cols-3">
            <Input v-debug-id="DEBUG_IDS.ADMIN.KEYWORD_FILTER" v-model="filters.keyword" placeholder="登录名 / 员工姓名 / 工号" />
            <Select v-debug-id="DEBUG_IDS.ADMIN.STATUS_FILTER" v-model="filters.status">
              <option value="">全部状态</option>
              <option value="active">启用</option>
              <option value="disabled">停用</option>
            </Select>
            <NativeSelect
              v-debug-id="DEBUG_IDS.ADMIN.ORG_FILTER"
              v-model="filters.orgId"
              :options="flattenedOrgs"
              option-label="label"
              option-value="org_id"
              placeholder="全部部门"
            />
          </div>

          <div class="flex justify-end">
            <Button v-debug-id="DEBUG_IDS.ADMIN.QUERY_BTN" @click="loadUsers">查询</Button>
          </div>

          <div class="overflow-hidden rounded-2xl border border-border">
            <table class="min-w-full divide-y divide-border text-sm">
              <thead class="bg-muted/50 text-left text-muted-foreground">
                <tr>
                  <th class="px-4 py-3 font-medium">登录名</th>
                  <th class="px-4 py-3 font-medium">员工姓名</th>
                  <th class="px-4 py-3 font-medium">工号</th>
                  <th class="px-4 py-3 font-medium">部门</th>
                  <th class="px-4 py-3 font-medium">角色</th>
                  <th class="px-4 py-3 font-medium">状态</th>
                  <th class="px-4 py-3 font-medium">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border bg-card">
                <tr v-if="loading">
                  <td colspan="7" class="px-4 py-10 text-center text-muted-foreground">正在加载账号数据...</td>
                </tr>
                <tr v-else-if="!users.length">
                  <td colspan="7" class="px-4 py-10 text-center text-muted-foreground">未查询到账号数据。</td>
                </tr>
                <tr
                  v-for="user in users"
                  :key="user.user_id"
                  class="cursor-pointer transition hover:bg-muted/30"
                  :class="selectedUserId === user.user_id ? 'bg-accent/50' : ''"
                  @click="selectUser(user.user_id)"
                >
                  <td class="px-4 py-3 font-medium text-foreground">{{ user.login_name }}</td>
                  <td class="px-4 py-3 text-foreground/80">{{ user.display_name }}</td>
                  <td class="px-4 py-3 text-foreground/80">{{ user.employee_no || '-' }}</td>
                  <td class="px-4 py-3 text-foreground/80">{{ user.default_org_name || '-' }}</td>
                  <td class="px-4 py-3">
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="role in user.roles"
                        :key="`${user.user_id}-${role.role_id}`"
                        class="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground border border-border/50"
                      >
                        {{ role.role_name }}
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase"
                      :class="user.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'"
                    >
                      {{ getStatusLabel(user.status) }}
                    </span>
                  </td>
                  <td class="px-4 py-3" @click.stop>
                    <Button variant="ghost" size="sm" @click="quickToggleStatus(user)" :class="user.status === 'active' ? 'text-rose-500' : 'text-emerald-500'">
                      {{ user.status === 'active' ? '停用' : '启用' }}
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div class="space-y-6">
        <!-- Edit/Create Form Card -->
        <Card data-form-card class="border-border bg-card shadow-lg">
          <CardHeader class="border-b border-border bg-muted/30">
            <CardTitle class="text-lg text-foreground">{{ isCreateMode ? '新建账号' : '编辑账号' }}</CardTitle>
            <CardDescription>{{ isCreateMode ? '填写基本信息以创建新员工账号。' : '更新选定账号的身份信息与角色绑定。' }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-6 pt-6">
            <div class="grid gap-4">
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">登录名</label>
                <Input v-model="form.loginName" placeholder="登录用户名" :disabled="!isCreateMode" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">显示姓名</label>
                <Input v-model="form.displayName" placeholder="员工真实姓名" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">工号</label>
                <Input v-model="form.employeeNo" placeholder="员工唯一工号" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">默认部门</label>
                <NativeSelect
                  v-model="form.defaultOrgId"
                  :options="flattenedOrgs"
                  option-label="label"
                  option-value="org_id"
                  placeholder="请选择默认部门"
                />
              </div>
              <div v-if="isCreateMode" class="space-y-2">
                <label class="text-sm font-semibold text-foreground">初始密码</label>
                <Input v-model="form.initialPassword" type="password" placeholder="留空则默认为 admin123" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">角色分配</label>
                <div class="flex flex-wrap gap-2 pt-1">
                  <button
                    v-for="role in roles"
                    :key="role.role_id"
                    type="button"
                    class="rounded-xl border px-3 py-1.5 text-xs font-medium transition-all"
                    :class="form.roleIds.includes(role.role_id) ? 'bg-primary text-primary-foreground border-primary shadow-sm' : 'bg-background text-muted-foreground border-border hover:bg-accent'"
                    @click="toggleRole(role.role_id)"
                  >
                    {{ role.role_name }}
                  </button>
                </div>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">账号状态</label>
                <Select v-model="form.status">
                  <option value="active">启用</option>
                  <option value="disabled">停用</option>
                </Select>
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <Button class="flex-1 bg-primary text-primary-foreground border-none hover:bg-primary/90" :loading="saving" @click="submitForm">
                {{ isCreateMode ? '确认创建' : '保存更新' }}
              </Button>
              <Button v-if="!isCreateMode" variant="outline" @click="resetForm">取消编辑</Button>
            </div>
          </CardContent>
        </Card>

        <!-- Password Reset Card (Only for Edit Mode) -->
        <Card v-if="!isCreateMode" class="border-border bg-card shadow-lg">
          <CardHeader class="border-b border-border bg-muted/30">
            <CardTitle class="text-lg text-foreground">重置密码</CardTitle>
            <CardDescription>直接重置该账号的登录密码，操作后立即生效。</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4 pt-6">
            <div class="space-y-2">
              <label class="text-sm font-semibold text-foreground">新密码</label>
              <Input v-model="resetPassword" type="password" placeholder="请输入新密码" />
            </div>
            <Button variant="outline" class="w-full border-border" :disabled="!resetPassword.trim()" :loading="saving" @click="submitPasswordReset">
              确认重置密码
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
