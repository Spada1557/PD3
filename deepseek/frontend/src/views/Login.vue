<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-blob blob-1"></div>
      <div class="bg-blob blob-2"></div>
      <div class="bg-blob blob-3"></div>
      <div class="bg-grid"></div>
    </div>
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        </div>
        <h1>ЭМАЛЬПРОМ</h1>
        <p>Информационная система учёта товарооборота</p>
      </div>
      <el-form @submit.prevent="handleLogin" :model="form" label-width="0" class="login-form">
        <div class="field-wrapper">
          <label class="field-label">Email</label>
          <el-input v-model="form.email" placeholder="Введите email" size="large" clearable :prefix-icon="mailIcon" />
        </div>
        <div class="field-wrapper">
          <label class="field-label">Пароль</label>
          <el-input v-model="form.password" type="password" placeholder="Введите пароль" size="large" show-password @keyup.enter="handleLogin" :prefix-icon="lockIcon" />
        </div>
        <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
          {{ loading ? 'Выполняется вход...' : 'Войти в систему' }}
        </el-button>
      </el-form>
      <div v-if="error" class="login-error">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ error }}
      </div>
      <div class="login-footer">
        <div class="demo-credentials">
          <span class="demo-label">Демо-доступ</span>
          <code>{{ form.email }} / {{ form.password }}</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({ email: 'admin@enamelpro.local', password: 'admin123' })
const loading = ref(false)
const error = ref('')

const mailIcon = () => h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z' }),
  h('polyline', { points: '22,6 12,13 2,6' }),
])
const lockIcon = () => h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('rect', { x: 3, y: 11, width: 18, height: 11, rx: 2, ry: 2 }),
  h('path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' }),
])

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.email, form.password)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail?.message || 'Неверный email или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #060918;
  position: relative;
  overflow: hidden;
}

.login-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-blob { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.18; }
.blob-1 { width: 600px; height: 600px; background: #7C3AED; top: -200px; right: -150px; animation: floatBlob 12s ease-in-out infinite; }
.blob-2 { width: 450px; height: 450px; background: #10B981; bottom: -150px; left: -100px; animation: floatBlob 15s ease-in-out infinite reverse; }
.blob-3 { width: 350px; height: 350px; background: #3B82F6; top: 45%; left: 35%; animation: floatBlob 10s ease-in-out infinite 3s; }

@keyframes floatBlob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 60px 60px;
}

.login-card {
  width: 460px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: var(--radius-xl);
  padding: 48px 44px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.08);
  position: relative;
  z-index: 1;
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.login-header { text-align: center; margin-bottom: 36px; }

.login-logo {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #7C3AED, #A78BFA);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #fff;
  box-shadow: 0 10px 28px rgba(124, 58, 237, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.login-header h1 {
  font-size: 24px;
  font-weight: 800;
  color: #0F172A;
  letter-spacing: 2px;
}

.login-header p {
  color: #94A3B8;
  font-size: 13px;
  margin-top: 6px;
  font-weight: 500;
}

.login-form { display: flex; flex-direction: column; gap: 4px; }

.field-wrapper { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.login-btn {
  margin-top: 12px;
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 700;
  border-radius: var(--radius-md);
  letter-spacing: 0.3px;
}

.login-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #EF4444;
  font-size: 13px;
  font-weight: 600;
  margin-top: 18px;
  padding: 14px;
  background: var(--danger-soft);
  border-radius: var(--radius-md);
  border: 1px solid #FECACA;
}

.login-footer { margin-top: 28px; text-align: center; }
.demo-credentials {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.demo-label { font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.8px; }
.demo-credentials code {
  font-size: 12.5px;
  color: #64748B;
  background: var(--bg-surface);
  padding: 3px 10px;
  border-radius: 6px;
  font-family: var(--font-family);
  font-weight: 600;
}
</style>