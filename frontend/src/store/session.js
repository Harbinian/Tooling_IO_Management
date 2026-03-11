import { reactive } from 'vue'

const STORAGE_KEY = 'tool-io-session'

const defaults = {
  userId: 'U001',
  userName: '当前用户',
  role: 'initiator'
}

function loadSession() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}')
    return { ...defaults, ...parsed }
  } catch {
    return { ...defaults }
  }
}

const state = reactive({
  ...loadSession(),
  persist() {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        userId: state.userId,
        userName: state.userName,
        role: state.role
      })
    )
  }
})

export function useSessionStore() {
  return state
}
