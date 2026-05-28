<template>
  <div class="login-wrap">
    <!-- Animated gradient background -->
    <div class="gradient-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="blob blob-4"></div>
    </div>

    <div class="login-content">
      <div class="login-left">
        <div class="brand">
          <div class="brand-icon-wrap">
            <div class="brand-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
            </div>
            <div class="brand-pulse"></div>
          </div>
          <div class="brand-name">ERP</div>
          <div class="brand-desc">ERP-система для управления производством и продажами эмалированной посуды</div>
        </div>
        <div class="features">
          <div v-for="(f,i) in features" :key="i" class="feature" :style="{ animationDelay: `${i * 0.12}s` }">
            <div class="feature-icon">
              <el-icon size="16" color="#fff"><component :is="f.icon" /></el-icon>
            </div>
            <span>{{ f.text }}</span>
          </div>
        </div>
      </div>

      <div class="login-right">
        <div class="glass-card">
          <div class="login-header">
            <div class="login-title">Добро пожаловать</div>
            <div class="login-subtitle">Войдите в систему для продолжения</div>
          </div>
          <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @submit.prevent="submit">
            <el-form-item label="Email" prop="email">
              <el-input v-model="form.email" placeholder="admin@example.com" size="large" :prefix-icon="Message" />
            </el-form-item>
            <el-form-item label="Пароль" prop="password">
              <el-input v-model="form.password" type="password" placeholder="Введите пароль" show-password size="large" :prefix-icon="Lock" />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" native-type="submit">
              Войти в систему
            </el-button>
          </el-form>
          <div class="login-hint">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            <span>Логин: admin@example.com / Пароль: admin123</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Message, Lock, Box, ShoppingCart, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({ email: '', password: '' })
const rules = {
  email: [{ required: true, message: 'Введите email', type: 'email' }],
  password: [{ required: true, message: 'Введите пароль' }],
}

const features = [
  { icon: 'Box', text: 'Учет продукции и складских запасов' },
  { icon: 'ShoppingCart', text: 'Управление закупками и продажами' },
  { icon: 'TrendCharts', text: 'Аналитика и отчетность в реальном времени' },
]

const submit = async () => {
  const ok = await formRef.value.validate().catch(() => false)
  if (!ok) return
  loading.value = true
  try {
    await auth.login({ ...form })
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка входа')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #0f0c29;
}

.gradient-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  z-index: 0;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
  animation: blobMove 20s infinite alternate;
}

.blob-1 {
  width: 500px;
  height: 500px;
  background: #7c3aed;
  top: -10%;
  left: -5%;
  animation-delay: 0s;
}

.blob-2 {
  width: 400px;
  height: 400px;
  background: #4f46e5;
  bottom: -10%;
  right: -5%;
  animation-delay: -5s;
}

.blob-3 {
  width: 350px;
  height: 350px;
  background: #ec4899;
  top: 40%;
  left: 30%;
  animation-delay: -10s;
  opacity: 0.25;
}

.blob-4 {
  width: 300px;
  height: 300px;
  background: #06b6d4;
  top: 10%;
  right: 20%;
  animation-delay: -15s;
  opacity: 0.2;
}

@keyframes blobMove {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0, 0) scale(1); }
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1200px;
  padding: 40px;
  gap: 80px;
  align-items: center;
}

.login-left {
  flex: 1;
  color: #fff;
}

.brand {
  margin-bottom: 48px;
}

.brand-icon-wrap {
  position: relative;
  display: inline-block;
  margin-bottom: 28px;
}

.brand-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(124, 58, 237, 0.45);
  position: relative;
  z-index: 1;
}

.brand-pulse {
  position: absolute;
  inset: -8px;
  border-radius: 26px;
  background: rgba(124, 58, 237, 0.3);
  animation: pulse 2s infinite;
  z-index: 0;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 0.25; }
}

.brand-name {
  font-size: 44px;
  font-weight: 800;
  letter-spacing: -1px;
  margin-bottom: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.6;
  max-width: 420px;
  font-weight: 500;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 500;
  opacity: 0;
  animation: slideInLeft 0.6s forwards;
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

.feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.login-right {
  width: 440px;
  flex-shrink: 0;
}

.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 40px 36px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.35);
}

.login-header {
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 700;
  margin-top: 8px;
  background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(124, 58, 237, 0.55);
}

.login-hint {
  margin-top: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  font-weight: 500;
}

/* Override Element Plus inputs for glass theme */
:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08) !important;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset !important;
  border-radius: 12px !important;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.6) inset !important;
}

:deep(.el-input__inner) {
  color: #ffffff !important;
  font-weight: 500;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.35) !important;
}

:deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.7) !important;
  font-weight: 600;
  font-size: 13px;
}

@media (max-width: 900px) {
  .login-content {
    flex-direction: column;
    gap: 40px;
    padding: 24px;
  }
  .login-left {
    text-align: center;
  }
  .brand-desc {
    margin: 0 auto;
  }
  .features {
    align-items: center;
  }
  .login-right {
    width: 100%;
    max-width: 420px;
  }
}
</style>
