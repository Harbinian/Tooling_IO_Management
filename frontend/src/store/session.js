import { reactive } from 'vue'

import { getCurrentUser, login as loginRequest } from '@/api/auth'

export const STORAGE_KEY = 'tool-io-session'

const defaults = {
  token: '',
  userId: '',
  loginName: '',
  userName: '',
  employeeNo: '',
  role: '',
  roleName: '',
  roles: [],
  permissions: [],
  defaultOrg: null,
  currentOrg: null,
  roleOrgs: [],
  initialized: false
}

function mapLegacyRole(user) {
  const roleCodes = new Set((user.roles || []).map((role) => role.role_code))

  if (roleCodes.has('keeper')) {
    return 'keeper'
  }

  if (roleCodes.has('team_leader') || roleCodes.has('planner') || roleCodes.has('sys_admin')) {
    return 'initiator'
  }

  return (user.permissions || []).includes('order:keeper_confirm') ? 'keeper' : 'initiator'
}

function normalizeUser(user, token = '') {
  const roles = user.roles || []
  const primaryRole = roles.find((role) => role.is_primary) || roles[0] || {}

  return {
    token,
    userId: user.user_id || '',
    loginName: user.login_name || '',
    userName: user.display_name || '',
    employeeNo: user.employee_no || '',
    role: mapLegacyRole(user),
    roleName: primaryRole.role_name || primaryRole.role_code || '',
    roles,
    permissions: user.permissions || [],
    defaultOrg: user.default_org || null,
    currentOrg: user.current_org || null,
    roleOrgs: user.role_orgs || [],
    initialized: true
  }
}

function loadSession() {
  if (typeof window === 'undefined') {
    return { ...defaults }
  }

  try {
    const parsed = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}')
    return { ...defaults, ...parsed, initialized: false }
  } catch {
    return { ...defaults }
  }
}

const state = reactive({
  ...loadSession(),
  persist() {
    if (typeof window === 'undefined') {
      return
    }

    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        token: state.token,
        userId: state.userId,
        loginName: state.loginName,
        userName: state.userName,
        employeeNo: state.employeeNo,
        role: state.role,
        roleName: state.roleName,
        roles: state.roles,
        permissions: state.permissions,
        defaultOrg: state.defaultOrg,
        currentOrg: state.currentOrg,
        roleOrgs: state.roleOrgs
      })
    )
  },
  applyUser(user, token = state.token) {
    Object.assign(state, normalizeUser(user, token))
    state.persist()
  },
  async login(credentials) {
    const result = await loginRequest(credentials)
    state.applyUser(result.user, result.token)
    return result.user
  },
  async hydrate() {
    if (!state.token) {
      state.initialized = true
      return false
    }

    try {
      const user = await getCurrentUser()
      state.applyUser(user, state.token)
      return true
    } catch (error) {
      console.error('Session hydration failed:', error)
      state.clear()
      return false
    }
  },
  clear() {
    Object.assign(state, { ...defaults, initialized: true })
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(STORAGE_KEY)
    }
  },
  hasPermission(permission) {
    return state.permissions.includes(permission)
  },
  isAdmin() {
    const roleCodes = new Set((state.roles || []).map((role) => role.role_code))
    return roleCodes.has('sys_admin') || state.permissions.includes('admin:user_manage')
  }
})

export function useSessionStore() {
  return state
}
