<script setup>
import { Bell, Settings, LogOut, User } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useSessionStore } from '@/store/session'

const router = useRouter()
const session = useSessionStore()
const showSettingsDialog = ref(false)

const logout = () => {
  session.clear()
  // Use replace to prevent back-nav returning to authenticated state
  router.replace('/login')
}

const openSettings = () => {
  showSettingsDialog.value = true
}
</script>

<template>
  <div class="flex h-screen flex-col bg-background">
    <!-- Top Header -->
    <header class="flex h-16 shrink-0 items-center justify-between border-b border-header-border bg-header px-8">
      <div class="flex items-center gap-4">
        <h2 class="text-sm font-bold uppercase tracking-[0.2em] text-muted-foreground">
          模块入口
        </h2>
      </div>
      <div class="flex items-center gap-3">
        <button class="relative rounded-xl p-2 text-muted-foreground transition-all hover:bg-accent hover:text-accent-foreground">
          <Bell class="h-5 w-5" />
        </button>
        <button class="rounded-xl p-2 text-muted-foreground transition-all hover:bg-accent hover:text-accent-foreground" @click="openSettings">
          <Settings class="h-5 w-5" />
        </button>
        <div class="flex items-center gap-2 border-l border-header-border pl-3">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-sidebar-border bg-card shadow-sm">
            <User class="h-5 w-5 text-muted-foreground" />
          </div>
          <div class="overflow-hidden">
            <p class="truncate text-sm font-bold text-foreground">{{ session.userName || '未登录' }}</p>
            <p class="truncate text-[10px] font-bold uppercase tracking-tight text-muted-foreground">
              {{ session.employeeNo || '-' }}
            </p>
          </div>
          <button class="ml-2 text-muted-foreground transition-colors hover:text-destructive" @click="logout">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="custom-scrollbar flex-1 overflow-y-auto bg-background p-8">
      <div class="mx-auto max-w-7xl">
        <router-view />
      </div>
    </main>

    <!-- Settings Dialog -->
    <el-dialog v-model="showSettingsDialog" title="系统设置" width="400px">
      <div class="space-y-4">
        <div class="flex items-center justify-between rounded-lg border border-border p-4">
          <div>
            <p class="font-semibold text-foreground">个人设置</p>
            <p class="text-sm text-muted-foreground">配置您的个人偏好</p>
          </div>
          <router-link to="/settings">
            <el-button size="small">打开设置</el-button>
          </router-link>
        </div>
      </div>
    </el-dialog>
  </div>
</template>
