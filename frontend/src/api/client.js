import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const viteEnv = import.meta.env || {}
const apiBaseUrl = (viteEnv.VITE_API_BASE_URL || '/api').replace(/\/$/, '')
const storageKey = 'tool-io-session'

const client = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
  headers: {
    Accept: 'application/json'
  }
})

// Request Interceptor: Inject Token
client.interceptors.request.use((config) => {
  try {
    const sessionStr = window.localStorage.getItem(storageKey)
    if (sessionStr) {
      const session = JSON.parse(sessionStr)
      if (session.token) {
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${session.token}`
      }
    }
  } catch (err) {
    console.error('[API Client] Failed to parse session token:', err)
  }

  if (import.meta.env.DEV) {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data || '')
  }

  return config
})

// Response Interceptor: Error Handling
client.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }
    return response
  },
  (error) => {
    const { response } = error
    const status = response?.status
    const errorPayload = response?.data?.error
    
    // Centralized Error Message
    const message =
      (typeof errorPayload === 'string' ? errorPayload : errorPayload?.message) ||
      error.message ||
      '请求失败'

    // 401: Unauthorized -> Redirect to Login
    if (status === 401) {
      console.warn('[API Client] 401 Unauthorized, redirecting to login...')
      window.localStorage.removeItem(storageKey)
      if (router.currentRoute.value.path !== '/login') {
        router.push({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath }
        })
      }
    } else {
      // Show error toast for other errors (including 500)
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

export default client
