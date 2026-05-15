import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// Make ElMessage globally available
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$msgbox = ElMessageBox
app.config.globalProperties.$alert = ElMessageBox.alert
app.config.globalProperties.$confirm = ElMessageBox.confirm
app.config.globalProperties.$prompt = ElMessageBox.prompt

window.ElMessage = ElMessage
window.ElMessageBox = ElMessageBox

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.mount('#app')
