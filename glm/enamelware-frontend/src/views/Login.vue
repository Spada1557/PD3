<template>
  <div class="login-container">
    <div class="login-card">
      <div style="text-align:center;margin-bottom:28px">
        <div class="login-logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color:#fff">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
        </div>
        <h1 class="login-title">Enamelware</h1>
        <p class="login-subtitle">Система учёта товарооборота</p>
      </div>
      <el-form :model="form" @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="Email">
          <el-input v-model="form.email" type="email" placeholder="admin@enamelware.ru" prefix-icon="Message" size="large" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="form.password" type="password" placeholder="Введите пароль" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;font-weight:600;margin-top:4px;height:44px;border-radius:10px;cursor:pointer;letter-spacing:0.01em">Войти в систему</el-button>
      </el-form>
      <div style="margin-top:22px;text-align:center;color:var(--text-muted);font-size:11px;letter-spacing:0.02em">
        Демо: admin@enamelware.ru / admin123
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const form = ref({ email: '', password: '' })
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

async function handleLogin() {
  if (!form.value.email || !form.value.password) {
    ElMessage.warning('Заполните все поля')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    ElMessage.success('Добро пожаловать!')
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail?.message || e.response?.data?.message || 'Ошибка входа')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>