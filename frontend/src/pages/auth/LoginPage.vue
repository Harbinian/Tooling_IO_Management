<script setup>
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ShieldCheck, Lock, User as UserIcon, ArrowRight, Loader2, AlertCircle } from 'lucide-vue-next'
import { ElMessageBox } from 'element-plus'
import { useSessionStore } from '@/store/session'
import { DEBUG_IDS } from '@/debug/debugIds'

const router = useRouter()

const route = useRoute()
const session = useSessionStore()
const submitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  login_name: '',
  password: ''
})

// Show error when redirected due to permission denial
if (route.query.denied === '1') {
  errorMessage.value = '您没有权限访问该页面，请使用有权限的账号登录'
}

function handleForgotPassword() {
  ElMessageBox.alert('请联系管理员重置密码', '提示', {
    confirmButtonText: '确定',
    type: 'info'
  })
}

async function submitLogin() {
  if (!form.login_name || !form.password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  submitting.value = true
  errorMessage.value = ''

  try {
    await session.login(form)
    // Determine redirect target after successful login
    let redirectTarget = '/home'
    if (route.query.denied !== '1' && route.query.redirect) {
      redirectTarget = String(Array.isArray(route.query.redirect)
        ? route.query.redirect[0] || '/home'
        : route.query.redirect)
    }
    router.replace(redirectTarget)
  } catch (err) {
    const error = /** @type {any} */ (err)
    errorMessage.value = error.response?.data?.error || '登录失败，请检查用户名或密码'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-background flex items-center justify-center p-6 font-sans text-foreground">
    <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-emerald-500/5 blur-[120px]"></div>
      <div class="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] rounded-full bg-blue-500/5 blur-[120px]"></div>
    </div>

    <div v-debug-id="DEBUG_IDS.LOGIN.CARD" class="relative z-10 w-full max-w-[1100px] grid lg:grid-cols-2 bg-card rounded-[40px] shadow-[0_40px_100px_-20px_rgba(15,23,42,0.1)] border border-border/60 overflow-hidden">

      <div class="hidden lg:flex flex-col justify-between p-12 bg-primary text-primary-foreground relative overflow-hidden">
        <div class="relative z-10">
          <div class="flex items-center gap-3 mb-12">
            <div class="h-10 w-10 rounded-2xl bg-white flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <ShieldCheck class="h-6 w-6 text-slate-900" />
            </div>
            <span class="text-xl font-bold tracking-tight">工装出入库 <span class="text-emerald-400">平台</span></span>
          </div>

          <div class="space-y-8">
            <h1 class="text-5xl font-black leading-[1.1] tracking-tight text-primary-foreground">
              智能工装管理<br />
              <span class="text-primary-foreground/60">全流程数字化平台</span>
            </h1>
            <p class="text-primary-foreground/80 text-lg leading-relaxed max-w-md">
              基于 RBAC 权限体系与飞书通知集成，为制造现场提供高效、透明、闭环的工装流转体验。
            </p>
          </div>
        </div>

        <div class="relative z-10 grid grid-cols-2 gap-6 mt-12">
          <div class="p-5 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm">
            <div class="h-8 w-8 rounded-xl bg-emerald-500/20 flex items-center justify-center mb-3">
              <Lock class="h-4 w-4 text-emerald-400" />
            </div>
            <h3 class="font-bold text-sm mb-1">安全可靠</h3>
            <p class="text-xs text-primary-foreground/50 leading-normal">支持安全认证与令牌访问控制。</p>
          </div>
          <div class="p-5 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm">
            <div class="h-8 w-8 rounded-xl bg-blue-500/20 flex items-center justify-center mb-3">
              <ShieldCheck class="h-4 w-4 text-blue-400" />
            </div>
            <h3 class="font-bold text-sm mb-1">细粒度权限</h3>
            <p class="text-xs text-primary-foreground/50 leading-normal">支持界面权限控制与接口级权限校验。</p>
          </div>
        </div>

        <div class="absolute -right-20 -bottom-20 w-80 h-80 bg-emerald-500/10 rounded-full blur-[80px]"></div>
      </div>

      <div class="p-8 sm:p-12 lg:p-16 flex flex-col justify-center bg-card">
        <div class="max-w-sm mx-auto w-full">
          <div class="mb-10">
            <h2 v-debug-id="DEBUG_IDS.LOGIN.TITLE" class="text-3xl font-black text-foreground mb-2">欢迎回来</h2>
            <p class="text-muted-foreground text-sm">请输入您的凭据以访问系统</p>
          </div>

          <form @submit.prevent="submitLogin" class="space-y-6">
            <div class="space-y-2">
              <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground ml-1">用户名</label>
              <div class="relative group">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-foreground transition-colors">
                  <UserIcon class="h-4 w-4" />
                </div>
                <input
                  v-debug-id="DEBUG_IDS.LOGIN.USERNAME_FIELD"
                  v-model="form.login_name"
                  type="text"
                  placeholder="请输入用户名"
                  autocomplete="username"
                  class="w-full h-12 pl-11 pr-4 bg-muted/50 border border-border rounded-2xl text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-primary/5 focus:border-primary focus:bg-background"
                />
              </div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between px-1">
                <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">密码</label>
                <a href="#" class="text-[11px] font-bold text-muted-foreground hover:text-foreground transition-colors" @click.prevent="handleForgotPassword">忘记密码？</a>
              </div>
              <div class="relative group">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-foreground transition-colors">
                  <Lock class="h-4 w-4" />
                </div>
                <input
                  v-debug-id="DEBUG_IDS.LOGIN.PASSWORD_FIELD"
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  autocomplete="current-password"
                  class="w-full h-12 pl-11 pr-4 bg-muted/50 border border-border rounded-2xl text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-primary/5 focus:border-primary focus:bg-background"
                />
              </div>
            </div>

            <div v-if="errorMessage" v-debug-id="DEBUG_IDS.LOGIN.ERROR_ALERT" class="flex items-center gap-3 p-4 rounded-2xl bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium animate-in fade-in slide-in-from-top-2">
              <AlertCircle class="h-4 w-4 shrink-0" />
              <span>{{ errorMessage }}</span>
            </div>

            <button
              v-debug-id="DEBUG_IDS.LOGIN.LOGIN_BTN"
              type="submit"
              :disabled="submitting"
              class="w-full h-12 bg-primary hover:bg-primary/90 disabled:bg-muted text-primary-foreground rounded-2xl font-bold text-sm transition-all shadow-lg shadow-primary/10 flex items-center justify-center gap-2 group"
            >

              <template v-if="submitting">
                <Loader2 class="h-4 w-4 animate-spin" />
                <span>验证中...</span>
              </template>
              <template v-else>
                <span>进入系统</span>
                <ArrowRight class="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </template>
            </button>
          </form>

          <div class="mt-12 pt-8 border-t border-border">
            <p class="text-xs text-muted-foreground text-center">
              首次使用？请联系系统管理员分配权限
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
