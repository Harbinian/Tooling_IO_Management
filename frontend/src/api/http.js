import axios from 'axios'
import { ElMessage } from 'element-plus'

const viteEnv = import.meta.env || {}
const apiBaseUrl = (viteEnv.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
  headers: {
    Accept: 'application/json'
  }
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default http
