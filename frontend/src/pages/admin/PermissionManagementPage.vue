<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import permissionsApi from '@/api/permissions'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardDescription from '@/components/ui/CardDescription.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import Input from '@/components/ui/Input.vue'

const showToast = (msg) => {
  console.log('[Toast]', msg)
  alert(msg)
}

const loading = ref(false)
const saving = ref(false)
const permissions = ref([])
const selectedCode = ref('')

const filters = reactive({
  keyword: ''
})

const form = reactive({
  permissionCode: '',
  permissionName: '',
  resourceName: '',
  actionName: ''
})

const isCreateMode = computed(() => !selectedCode.value)

const filteredPermissions = computed(() => {
  return permissions.value.filter(perm => {
    const keyword = filters.keyword.toLowerCase()
    return !keyword || 
      perm.permission_code.toLowerCase().includes(keyword) || 
      perm.permission_name.toLowerCase().includes(keyword) ||
      (perm.resource_name && perm.resource_name.toLowerCase().includes(keyword))
  })
})

function resetForm() {
  selectedCode.value = ''
  form.permissionCode = ''
  form.permissionName = ''
  form.resourceName = ''
  form.actionName = ''
  
  nextTick(() => {
    document.querySelector('[data-form-card]')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    const firstInput = document.querySelector('[data-form-card] input')
    firstInput?.focus()
  })
}

function selectPermission(perm) {
  selectedCode.value = perm.permission_code
  form.permissionCode = perm.permission_code
  form.permissionName = perm.permission_name
  form.resourceName = perm.resource_name || ''
  form.actionName = perm.action_name || ''
}

async function loadPermissions() {
  loading.value = true
  try {
    permissions.value = await permissionsApi.getPermissions()
    if (selectedCode.value) {
      const refreshed = permissions.value.find((p) => p.permission_code === selectedCode.value)
      if (refreshed) {
        selectPermission(refreshed)
      } else {
        resetForm()
      }
    }
  } catch (err) {
    showToast('加载权限失败')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  if (!form.permissionCode || !form.permissionName) {
    showToast('请填写权限代码和权限名称')
    return
  }
  
  saving.value = true
  try {
    const payload = {
      permission_code: form.permissionCode,
      permission_name: form.permissionName,
      resource_name: form.resourceName,
      action_name: form.actionName
    }
    
    if (isCreateMode.value) {
      await permissionsApi.createPermission(payload)
      showToast('权限创建成功')
      resetForm()
    } else {
      await permissionsApi.updatePermission(selectedCode.value, payload)
      showToast('权限更新成功')
    }
    await loadPermissions()
  } catch (err) {
    showToast(err.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deletePermission(perm) {
  if (!confirm(`确定要删除权限 [${perm.permission_name}] 吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await permissionsApi.deletePermission(perm.permission_code)
    showToast('权限删除成功')
    if (selectedCode.value === perm.permission_code) {
      resetForm()
    }
    await loadPermissions()
  } catch (err) {
    showToast(err.response?.data?.message || '删除失败')
  }
}

onMounted(async () => {
  await loadPermissions()
})
</script>

<template>
  <div class="space-y-6 text-foreground">
    <section class="space-y-2">
      <p class="text-xs font-medium uppercase tracking-[0.28em] text-muted-foreground">系统管理</p>
      <h1 class="text-3xl font-semibold tracking-tight text-foreground">权限管理</h1>
      <p class="max-w-3xl text-sm leading-6 text-muted-foreground">
        维护系统中的 RBAC 权限条目。
      </p>
    </section>

    <div class="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
      <Card v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_PERM_CARD" class="overflow-hidden border-border bg-card shadow-sm">
        <CardHeader class="border-b border-border bg-muted/30">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div class="space-y-1">
              <CardTitle class="text-lg text-foreground">权限列表</CardTitle>
              <CardDescription>系统中的所有细粒度权限。</CardDescription>
            </div>
            <div class="flex flex-wrap gap-2">
              <Button v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_PERM_CREATE_BTN" variant="outline" @click="resetForm">新建权限</Button>
              <Button variant="outline" @click="loadPermissions">刷新</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="space-y-4 pt-6">
          <div class="grid gap-3 md:grid-cols-2">
            <Input v-model="filters.keyword" placeholder="权限代码 / 名称 / 资源" />
          </div>

          <div class="overflow-hidden rounded-2xl border border-border">
            <table v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_PERM_TABLE" class="min-w-full divide-y divide-border text-sm">
              <thead class="bg-muted/50 text-left text-muted-foreground">
                <tr>
                  <th class="px-4 py-3 font-medium">权限代码</th>
                  <th class="px-4 py-3 font-medium">权限名称</th>
                  <th class="px-4 py-3 font-medium">资源名称</th>
                  <th class="px-4 py-3 font-medium">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border bg-card">
                <tr v-if="loading">
                  <td colspan="4" class="px-4 py-10 text-center text-muted-foreground">正在加载权限数据...</td>
                </tr>
                <tr v-else-if="!filteredPermissions.length">
                  <td colspan="4" class="px-4 py-10 text-center text-muted-foreground">未查询到权限数据。</td>
                </tr>
                <tr
                  v-for="perm in filteredPermissions"
                  :key="perm.permission_code"
                  class="cursor-pointer transition hover:bg-muted/30"
                  :class="selectedCode === perm.permission_code ? 'bg-accent/50' : ''"
                  @click="selectPermission(perm)"
                >
                  <td class="px-4 py-3 font-medium text-foreground">{{ perm.permission_code }}</td>
                  <td class="px-4 py-3 text-foreground/80">{{ perm.permission_name }}</td>
                  <td class="px-4 py-3 text-foreground/80">{{ perm.resource_name || '-' }}</td>
                  <td class="px-4 py-3" @click.stop>
                    <div class="flex items-center gap-2">
                      <Button v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_PERM_EDIT_BTN" variant="ghost" size="sm" @click="selectPermission(perm)">
                        编辑
                      </Button>
                      <Button 
                        v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_PERM_DELETE_BTN" 
                        variant="ghost" 
                        size="sm" 
                        class="text-rose-500" 
                        @click="deletePermission(perm)"
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
        <Card data-form-card v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_PERM_FORM_DIALOG" class="border-border bg-card shadow-lg">
          <CardHeader class="border-b border-border bg-muted/30">
            <CardTitle class="text-lg text-foreground">{{ isCreateMode ? '新建权限' : '编辑权限' }}</CardTitle>
            <CardDescription>{{ isCreateMode ? '填写基本信息以创建新权限。' : '更新选定权限的基本信息。' }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-6 pt-6">
            <div class="grid gap-4">
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">权限代码</label>
                <Input v-model="form.permissionCode" placeholder="如 order:create" :disabled="!isCreateMode" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">权限名称</label>
                <Input v-model="form.permissionName" placeholder="如 创建订单" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">资源名称</label>
                <Input v-model="form.resourceName" placeholder="如 order" />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-foreground">操作名称</label>
                <Input v-model="form.actionName" placeholder="如 create" />
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
