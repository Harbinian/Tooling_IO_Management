<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
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
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardDescription from '@/components/ui/CardDescription.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

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
  <div class="space-y-6">
    <section class="space-y-2">
      <p class="text-xs font-medium uppercase tracking-[0.28em] text-slate-400">系统管理</p>
      <h1 class="text-3xl font-semibold tracking-tight text-slate-900">账号管理</h1>
      <p class="max-w-3xl text-sm leading-6 text-slate-500">
        创建系统账号，维护员工身份信息，设置默认部门，并绑定一个或多个 RBAC 角色。
      </p>
    </section>

    <div class="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
      <Card class="overflow-hidden border-slate-200/80 bg-white shadow-sm">
        <CardHeader class="border-b border-slate-100">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div class="space-y-1">
              <CardTitle class="text-lg text-slate-900">账号列表</CardTitle>
              <CardDescription>仅管理员可见的账号清单，展示角色与部门归属信息。</CardDescription>
            </div>
            <div class="flex flex-wrap gap-2">
              <Button variant="outline" @click="resetForm">新建账号</Button>
              <Button variant="outline" @click="loadUsers">刷新</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="space-y-4 pt-6">
          <div class="grid gap-3 md:grid-cols-3">
            <Input v-model="filters.keyword" placeholder="登录名 / 员工姓名 / 工号" />
            <Select v-model="filters.status">
              <option value="">全部状态</option>
              <option value="active">启用</option>
              <option value="disabled">停用</option>
            </Select>
            <Select v-model="filters.orgId">
              <option value="">全部部门</option>
              <option
                v-for="org in flattenedOrgs"
                :key="org.org_id"
                :value="org.org_id"
              >
                {{ org.label }}
              </option>
            </Select>
          </div>

          <div class="flex justify-end">
            <Button @click="loadUsers">查询</Button>
          </div>

          <div class="overflow-hidden rounded-2xl border border-slate-200">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-left text-slate-500">
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
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-if="loading">
                  <td colspan="7" class="px-4 py-10 text-center text-slate-400">正在加载账号数据...</td>
                </tr>
                <tr v-else-if="!users.length">
                  <td colspan="7" class="px-4 py-10 text-center text-slate-400">未查询到账号数据。</td>
                </tr>
                <tr
                  v-for="user in users"
                  :key="user.user_id"
                  class="cursor-pointer transition hover:bg-slate-50"
                  :class="selectedUserId === user.user_id ? 'bg-slate-50' : ''"
                  @click="selectUser(user.user_id)"
                >
                  <td class="px-4 py-3 font-medium text-slate-900">{{ user.login_name }}</td>
                  <td class="px-4 py-3">{{ user.display_name }}</td>
                  <td class="px-4 py-3">{{ user.employee_no || '-' }}</td>
                  <td class="px-4 py-3">{{ user.default_org_name || '-' }}</td>
                  <td class="px-4 py-3">
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="role in user.roles"
                        :key="`${user.user_id}-${role.role_id}`"
                        class="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600"
                      >
                        {{ role.role_name }}
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="rounded-full px-2 py-1 text-xs font-medium"
                      :class="user.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
                    >
                      {{ getStatusLabel(user.status) }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <Button size="sm" variant="outline" @click.stop="quickToggleStatus(user)">
                      {{ user.status === 'active' ? '停用' : '启用' }}
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card class="overflow-hidden border-slate-200/80 bg-white shadow-sm">
        <CardHeader class="border-b border-slate-100">
          <CardTitle class="text-lg text-slate-900">
            {{ isCreateMode ? '创建账号' : '编辑账号' }}
          </CardTitle>
          <CardDescription>
            密码以哈希方式存储。创建账号时需要设置初始密码，编辑账号时可单独执行密码重置。
          </CardDescription>
        </CardHeader>
        <CardContent class="pt-6">
          <form class="space-y-5" @submit.prevent="submitForm">
          <div class="grid gap-4 md:grid-cols-2">
            <label class="space-y-2">
              <span class="text-sm font-medium text-slate-700">登录名</span>
              <Input v-model="form.loginName" placeholder="请输入登录名" autocomplete="username" />
            </label>
            <label class="space-y-2">
              <span class="text-sm font-medium text-slate-700">员工姓名</span>
              <Input v-model="form.displayName" placeholder="请输入员工姓名" autocomplete="name" />
            </label>
            <label class="space-y-2">
              <span class="text-sm font-medium text-slate-700">工号</span>
              <Input v-model="form.employeeNo" placeholder="请输入工号" autocomplete="off" />
            </label>
            <label class="space-y-2">
              <span class="text-sm font-medium text-slate-700">账号状态</span>
              <Select v-model="form.status">
                <option value="active">启用</option>
                <option value="disabled">停用</option>
              </Select>
            </label>
            <label class="space-y-2 md:col-span-2">
              <span class="text-sm font-medium text-slate-700">默认部门 / 组织</span>
              <Select v-model="form.defaultOrgId">
                <option value="">未分配</option>
                <option
                  v-for="org in flattenedOrgs"
                  :key="org.org_id"
                  :value="org.org_id"
                >
                  {{ org.label }}
                </option>
              </Select>
            </label>
            <label v-if="isCreateMode" class="space-y-2 md:col-span-2">
              <span class="text-sm font-medium text-slate-700">初始密码</span>
              <Input
                v-model="form.initialPassword"
                type="password"
                placeholder="请输入初始密码"
                autocomplete="new-password"
              />
            </label>
          </div>

          <div class="space-y-3">
            <div>
              <p class="text-sm font-medium text-slate-700">角色分配</p>
              <p class="text-xs text-slate-500">可选择一个或多个角色，首个选中的角色视为主角色。</p>
            </div>
            <div class="grid gap-2 sm:grid-cols-2">
              <label
                v-for="role in roles"
                :key="role.role_id"
                class="flex items-start gap-3 rounded-xl border border-slate-200 p-3 text-sm transition hover:border-slate-300"
              >
                <input
                  :checked="form.roleIds.includes(role.role_id)"
                  type="checkbox"
                  class="mt-0.5 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-300"
                  @change="toggleRole(role.role_id)"
                />
                <span class="space-y-1">
                  <span class="block font-medium text-slate-800">{{ role.role_name }}</span>
                  <span class="block text-xs text-slate-500">{{ role.role_code }}</span>
                </span>
              </label>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <Button type="submit" :disabled="saving">
              {{ saving ? '保存中...' : isCreateMode ? '创建账号' : '保存修改' }}
            </Button>
            <Button type="button" variant="outline" :disabled="saving" @click="resetForm">清空</Button>
          </div>

          </form>

          <form
            v-if="!isCreateMode"
            class="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4"
            @submit.prevent="submitPasswordReset"
          >
            <div>
              <p class="text-sm font-medium text-slate-700">密码重置</p>
              <p class="text-xs text-slate-500">为当前选中的账号设置新的临时密码。</p>
            </div>
            <div class="flex flex-col gap-3 md:flex-row">
              <Input
                v-model="resetPassword"
                type="password"
                placeholder="请输入新密码"
                autocomplete="new-password"
                class="flex-1"
              />
              <Button type="submit" :disabled="saving || !resetPassword.trim()">
                重置密码
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
