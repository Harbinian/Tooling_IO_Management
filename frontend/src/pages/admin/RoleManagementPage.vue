<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import rolesApi from '@/api/roles'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardDescription from '@/components/ui/CardDescription.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

const router = useRouter()

const showToast = (msg) => {
  console.log('[Toast]', msg)
  alert(msg)
}

const loading = ref(false)
const saving = ref(false)
const roles = ref([])
const selectedRoleId = ref('')

const filters = reactive({
  keyword: '',
  status: ''
})

const form = reactive({
  roleCode: '',
  roleName: '',
  roleType: 'custom',
  status: 'active'
})

const isCreateMode = computed(() => !selectedRoleId.value)

function getStatusLabel(status) {
  return status === 'active' ? '启用' : '停用'
}

function getTypeLabel(type) {
  return type === 'system' ? '系统' : '自定义'
}

const filteredRoles = computed(() => {
  return roles.value.filter(role => {
    const matchKeyword = !filters.keyword || 
      role.role_name.toLowerCase().includes(filters.keyword.toLowerCase()) || 
      role.role_code.toLowerCase().includes(filters.keyword.toLowerCase())
    const matchStatus = !filters.status || role.status === filters.status
    return matchKeyword && matchStatus
  })
})

function resetForm() {
  selectedRoleId.value = ''
  form.roleCode = ''
  form.roleName = ''
  form.roleType = 'custom'
  form.status = 'active'
  
  nextTick(() => {
    document.querySelector('[data-form-card]')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    const firstInput = document.querySelector('[data-form-card] input')
    firstInput?.focus()
  })
}

function selectRole(role) {
  selectedRoleId.value = role.role_id
  form.roleCode = role.role_code
  form.roleName = role.role_name
  form.roleType = role.role_type || 'custom'
  form.status = role.status || 'active'
}

async function loadRoles() {
  loading.value = true
  try {
    roles.value = await rolesApi.getAdminRoles()
    if (selectedRoleId.value) {
      const refreshed = roles.value.find((r) => r.role_id === selectedRoleId.value)
      if (refreshed) {
        selectRole(refreshed)
      } else {
        resetForm()
      }
    }
  } catch (err) {
    showToast('加载角色失败')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  if (!form.roleCode || !form.roleName) {
    showToast('请填写角色代码和角色名称')
    return
  }
  
  saving.value = true
  try {
    const payload = {
      role_code: form.roleCode,
      role_name: form.roleName,
      role_type: form.roleType,
      status: form.status
    }
    
    if (isCreateMode.value) {
      await rolesApi.createRole(payload)
      showToast('角色创建成功')
      resetForm()
    } else {
      await rolesApi.updateRole(selectedRoleId.value, payload)
      showToast('角色更新成功')
    }
    await loadRoles()
  } catch (err) {
    showToast(err.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteRole(role) {
  if (role.role_type === 'system') {
    showToast('系统角色不可删除')
    return
  }
  
  if (!confirm(`确定要删除角色 [${role.role_name}] 吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await rolesApi.deleteRole(role.role_id)
    showToast('角色删除成功')
    if (selectedRoleId.value === role.role_id) {
      resetForm()
    }
    await loadRoles()
  } catch (err) {
    showToast(err.response?.data?.message || '删除失败')
  }
}

function assignPermissions(role) {
  router.push(`/admin/roles/${role.role_id}/permissions`)
}

onMounted(async () => {
  await loadRoles()
})
</script>

<template>
  <div class="space-y-6 text-foreground">
    <section class="space-y-2">
      <p class="text-xs font-medium uppercase tracking-[0.28em] text-muted-foreground">系统管理</p>
      <h1 class="text-3xl font-semibold tracking-tight text-foreground">角色管理</h1>
      <p class="max-w-3xl text-sm leading-6 text-muted-foreground">
        维护系统中的 RBAC 角色，管理角色基本信息，并为其分配权限。
      </p>
    </section>

    <div class="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
      <Card v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_CARD" class="overflow-hidden border-border bg-card shadow-sm">
        <CardHeader class="border-b border-border bg-muted/30">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div class="space-y-1">
              <CardTitle class="text-lg text-foreground">角色列表</CardTitle>
              <CardDescription>系统中的所有角色，系统角色无法删除。</CardDescription>
            </div>
            <div class="flex flex-wrap gap-2">
              <Button v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_CREATE_BTN" variant="outline" @click="resetForm">新建角色</Button>
              <Button variant="outline" @click="loadRoles">刷新</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="space-y-4 pt-6">
          <div class="grid gap-3 md:grid-cols-2">
            <Input v-model="filters.keyword" placeholder="角色代码 / 角色名称" />
            <Select v-model="filters.status">
              <option value="">全部状态</option>
              <option value="active">启用</option>
              <option value="disabled">停用</option>
            </Select>
          </div>

          <div class="overflow-hidden rounded-2xl border border-border">
            <table v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_TABLE" class="min-w-full divide-y divide-border text-sm">
              <thead class="bg-muted/50 text-left text-muted-foreground">
                <tr>
                  <th class="px-4 py-3 font-medium">角色代码</th>
                  <th class="px-4 py-3 font-medium">角色名称</th>
                  <th class="px-4 py-3 font-medium">类型</th>
                  <th class="px-4 py-3 font-medium">状态</th>
                  <th class="px-4 py-3 font-medium">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border bg-card">
                <tr v-if="loading">
                  <td colspan="5" class="px-4 py-10 text-center text-muted-foreground">正在加载角色数据...</td>
                </tr>
                <tr v-else-if="!filteredRoles.length">
                  <td colspan="5" class="px-4 py-10 text-center text-muted-foreground">未查询到角色数据。</td>
                </tr>
                <tr
                  v-for="role in filteredRoles"
                  :key="role.role_id"
                  class="cursor-pointer transition hover:bg-muted/30"
                  :class="selectedRoleId === role.role_id ? 'bg-accent/50' : ''"
                  @click="selectRole(role)"
                >
                  <td class="px-4 py-3 font-medium text-foreground">{{ role.role_code }}</td>
                  <td class="px-4 py-3 text-foreground/80">{{ role.role_name }}</td>
                  <td class="px-4 py-3">
                    <span class="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground border border-border/50">
                      {{ getTypeLabel(role.role_type) }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase"
                      :class="role.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'"
                    >
                      {{ getStatusLabel(role.status) }}
                    </span>
                  </td>
                  <td class="px-4 py-3" @click.stop>
                    <div class="flex items-center gap-2">
                      <Button v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_EDIT_BTN" variant="ghost" size="sm" @click="selectRole(role)">
                        编辑
                      </Button>
                      <Button v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_PERM_BTN" variant="ghost" size="sm" @click="assignPermissions(role)">
                        分配权限
                      </Button>
                      <Button 
                        v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_DELETE_BTN" 
                        variant="ghost" 
                        size="sm" 
                        class="text-rose-500" 
                        :disabled="role.role_type === 'system'"
                        @click="deleteRole(role)"
                      >
                        删除
                      </Button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div class="space-y-6">
        <Card data-form-card v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_FORM_DIALOG" class="border-border bg-card shadow-lg">
          <CardHeader class="border-b border-border bg-muted/30">
            <CardTitle class="text-lg text-foreground">{{ isCreateMode ? '新建角色' : '编辑角色' }}</CardTitle>
            <CardDescription>{{ isCreateMode ? '填写基本信息以创建新角色。' : '更新选定角色的基本信息。' }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-6 pt-6">
            <div class="grid gap-4">
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">角色代码</label>
                <Input v-model="form.roleCode" placeholder="如 sys_admin" :disabled="!isCreateMode" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">角色名称</label>
                <Input v-model="form.roleName" placeholder="如 系统管理员" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">角色类型</label>
                <Select v-model="form.roleType" :disabled="form.roleType === 'system'">
                  <option value="custom">自定义</option>
                  <option value="system" disabled>系统 (不可修改)</option>
                </Select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">状态</label>
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
      </div>
    </div>
  </div>
</template>
