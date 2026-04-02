import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import './assets/index.css'
import './styles/inspection-theme.css'
import App from './App.vue'
import router from './router'
import { hasPermission } from '@/utils/permission'
import vDebugId from '@/directives/vDebugId'

const app = createApp(App)

// Global permission directive
app.directive('permission', {
  mounted(el, binding) {
    const { value } = binding
    if (value && !hasPermission(value)) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  }
})

// Global debug ID directive
app.directive('debug-id', vDebugId)

app.use(router).use(ElementPlus, { locale: zhCn }).mount('#app')

