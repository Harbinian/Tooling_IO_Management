<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import rolesApi from '@/api/roles'
import permissionsApi from '@/api/permissions'
import { DEBUG_IDS } from '@/debug/debugIds'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardDescription from '@/components/ui/CardDescription.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'

const route = useRoute()
const router = useRouter()

const showToast = (msg) => {
  console.log('[Toast]', msg)
  alert(msg)
}

const loading = ref(false)
const saving = ref(false)
const roles = ref([])
const permissions = ref([])
const currentRolePermissions = ref([])
const selectedRoleId = ref(route.params.roleId || '')

// Permissions selected by the user in the checkboxes
const selectedPermissionCodes = ref([])

const groupedPermissions = computed(() => {
  const groups = {}
  permissions.value.forEach(perm => {
    const resource = perm.resource_name || '其他'
    if (!groups[resource]) {
      groups[resource] = []
    }
    groups[resource].push(perm)
  })
  return groups
})

const currentRole = computed(() => {
  return roles.value.find(r => r.role_id === selectedRoleId.value) || null
})

async function loadData() {
  loading.value = true
  try {
    const [rolesData, permsData] = await Promise.all([
      rolesApi.getAdminRoles(),
      permissionsApi.getPermissions()
    ])
    roles.value = rolesData
    permissions.value = permsData
    
    if (selectedRoleId.value) {
      await loadRolePermissions(selectedRoleId.value)
    }
  } catch (err) {
    showToast('加载数据失败')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadRolePermissions(roleId) {
  try {
    const rolePerms = await rolesApi.getRolePermissions(roleId)
    currentRolePermissions.value = rolePerms
    selectedPermissionCodes.value = rolePerms.map(p => p.permission_code)
  } catch (err) {
    showToast('加载角色权限失败')
    console.error(err)
  }
}

function selectRole(role) {
  selectedRoleId.value = role.role_id
  // Update route without reloading page
  router.replace(`/admin/roles/${role.role_id}/permissions`)
}

watch(selectedRoleId, async (newVal) => {
  if (newVal) {
    await loadRolePermissions(newVal)
  }
})

function togglePermission(code) {
  const index = selectedPermissionCodes.value.indexOf(code)
  if (index > -1) {
    selectedPermissionCodes.value.splice(index, 1)
  } else {
    selectedPermissionCodes.value.push(code)
  }
}

async function savePermissions() {
  if (!selectedRoleId.value) return
  
  saving.value = true
  try {
    await rolesApi.assignPermissions(selectedRoleId.value, {
      permission_codes: selectedPermissionCodes.value
    })
    showToast('权限分配保存成功')
    await loadRolePermissions(selectedRoleId.value)
  } catch (err) {
    showToast(err.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/admin/roles')
}

onMounted(async () => {
  await loadData()
})
</script>

<template>
  <div class="space-y-6 text-foreground">
    <section class="space-y-2">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs font-medium uppercase tracking-[0.28em] text-muted-foreground">系统管理</p>
          <h1 class="text-3xl font-semibold tracking-tight text-foreground">权限分配</h1>
        </div>
        <Button variant="outline" @click="goBack">返回角色列表</Button>
      </div>
      <p class="max-w-3xl text-sm leading-6 text-muted-foreground">
        为指定角色分配细粒度权限，权限将按资源名称分组显示。
      </p>
    </section>

    <div class="grid gap-6 xl:grid-cols-[250px_1fr]">
      <!-- Left: Role List -->
      <Card class="overflow-hidden border-border bg-card shadow-sm h-fit">
        <CardHeader class="border-b border-border bg-muted/30">
          <CardTitle class="text-lg text-foreground">选择角色</CardTitle>
        </CardHeader>
        <CardContent class="p-0">
          <div v-if="loading && !roles.length" class="p-4 text-center text-muted-foreground text-sm">
            加载中...
          </div>
          <ul v-else class="divide-y divide-border">
            <li 
              v-for="role in roles" 
              :key="role.role_id"
              class="px-4 py-3 cursor-pointer transition hover:bg-muted/30 text-sm"
              :class="selectedRoleId === role.role_id ? 'bg-accent/50 border-l-4 border-l-primary' : 'border-l-4 border-l-transparent'"
              @click="selectRole(role)"
            >
              <div class="font-medium text-foreground">{{ role.role_name }}</div>
              <div class="text-xs text-muted-foreground mt-1">{{ role.role_code }}</div>
            </li>
          </ul>
        </CardContent>
      </Card>

      <!-- Right: Permission Matrix -->
      <Card v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_PERM_CARD" class="border-border bg-card shadow-sm">
        <CardHeader class="border-b border-border bg-muted/30 flex flex-row items-center justify-between">
          <div>
            <CardTitle class="text-lg text-foreground">
              {{ currentRole ? `分配权限给：${currentRole.role_name}` : '请在左侧选择角色' }}
            </CardTitle>
            <CardDescription v-if="currentRole">当前已选 {{ selectedPermissionCodes.length }} 项权限</CardDescription>
          </div>
          <Button 
            v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_PERM_SAVE_BTN" 
            :disabled="!currentRole"
            :loading="saving"
            @click="savePermissions"
          >
            保存分配
          </Button>
        </CardHeader>
        <CardContent class="p-6">
          <div v-if="!currentRole" class="text-center py-10 text-muted-foreground">
            请在左侧列表中选择一个角色
          </div>
          <div v-else-if="loading" class="text-center py-10 text-muted-foreground">
            正在加载权限数据...
          </div>
          <div v-else class="space-y-8">
            <div v-for="(perms, resource) in groupedPermissions" :key="resource" class="space-y-3">
              <h3 class="text-sm font-semibold uppercase tracking-wider text-muted-foreground border-b border-border pb-2">
                {{ resource }}
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                <label 
                  v-for="perm in perms" 
                  :key="perm.permission_code"
                  class="flex items-start gap-3 p-3 rounded-lg border border-border cursor-pointer transition-colors hover:bg-muted/30"
                  :class="selectedPermissionCodes.includes(perm.permission_code) ? 'bg-primary/5 border-primary/20' : 'bg-card'"
                >
                  <div class="flex items-center h-5 mt-0.5">
                    <input 
                      v-debug-id="DEBUG_IDS.ADMIN.U_ADMIN_ROLE_PERM_CHECK"
                      type="checkbox" 
                      :value="perm.permission_code"
                      :checked="selectedPermissionCodes.includes(perm.permission_code)"
                      @change="togglePermission(perm.permission_code)"
                      class="w-4 h-4 rounded border-input text-primary focus:ring-primary"
                    />
                  </div>
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-foreground">{{ perm.permission_name }}</span>
                    <span class="text-xs text-muted-foreground mt-0.5">{{ perm.permission_code }}</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
