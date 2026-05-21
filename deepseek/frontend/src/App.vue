<template>
  <div v-if="!auth.isLoggedIn" class="login-wrapper">
    <router-view />
  </div>
  <div v-else class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">Э</div>
        <h2>ЭМАЛЬПРОМ</h2>
        <span>Учёт товарооборота</span>
      </div>

      <div class="nav-section">Основное</div>
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg></span>
        <span>Дашборд</span>
      </router-link>
      <router-link to="/products" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.29 7 12 12 20.71 7"/></svg></span>
        <span>Продукция</span>
      </router-link>
      <router-link to="/stock" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg></span>
        <span>Склад</span>
      </router-link>

      <div class="nav-section">Документы</div>
      <router-link to="/sales" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></span>
        <span>Продажи</span>
      </router-link>
      <router-link to="/purchases" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg></span>
        <span>Закупки</span>
      </router-link>
      <router-link to="/reports" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></span>
        <span>Отчеты</span>
      </router-link>

      <div class="nav-section">Справочники</div>
      <router-link to="/categories" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></span>
        <span>Категории</span>
      </router-link>
      <router-link to="/units" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg></span>
        <span>Ед. измерения</span>
      </router-link>
      <router-link to="/warehouses" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span>
        <span>Склады</span>
      </router-link>
      <router-link to="/suppliers" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></span>
        <span>Поставщики</span>
      </router-link>
      <router-link to="/clients" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>
        <span>Клиенты</span>
      </router-link>

      <div v-if="auth.role === 'admin'" class="nav-section">Администрирование</div>
      <router-link v-if="auth.role === 'admin'" to="/users" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></span>
        <span>Пользователи</span>
      </router-link>
      <router-link v-if="auth.role === 'admin'" to="/settings" class="nav-item" active-class="active">
        <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></span>
        <span>Настройки</span>
      </router-link>

      <div class="sidebar-footer">ЭмальПром &copy; {{ new Date().getFullYear() }}</div>
    </aside>

    <main class="main">
      <header class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
          <div class="page-breadcrumb">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            <span>Главная</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            <span>{{ pageTitle }}</span>
          </div>
        </div>
        <div class="header-right">
          <button class="notification-btn" title="Уведомления" @click="$router.push('/notifications')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span v-if="unread > 0" class="badge">{{ unread > 99 ? '99+' : unread }}</span>
          </button>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-trigger">
              <div class="user-avatar">{{ auth.user?.name?.[0] }}</div>
              <div class="user-info">
                <span class="name">{{ auth.user?.name }}</span>
                <span class="role">{{ roleLabel }}</span>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-left:2px"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">Выйти из системы</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import api from './api/client'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const unread = ref(0)
let timer = null

const titleMap = {
  Dashboard: 'Дашборд',
  Products: 'Продукция',
  Stock: 'Склад',
  Purchases: 'Закупки',
  Sales: 'Продажи',
  Reports: 'Отчёты',
  Categories: 'Категории',
  Units: 'Единицы измерения',
  Warehouses: 'Склады',
  Suppliers: 'Поставщики',
  Clients: 'Клиенты',
  Users: 'Пользователи',
  Settings: 'Настройки',
  Notifications: 'Уведомления',
}

const roleLabels = { admin: 'Администратор', manager: 'Менеджер', warehouse: 'Кладовщик' }
const pageTitle = computed(() => titleMap[route.name] || '')
const roleLabel = computed(() => roleLabels[auth.role] || auth.role || '')

async function fetchUnread() {
  try {
    const { data } = await api.get('/notifications/unread-count')
    unread.value = data.count
  } catch (e) { /* ignore */ }
}

function handleCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}

onMounted(() => {
  if (auth.isLoggedIn) fetchUnread()
  timer = setInterval(() => { if (auth.isLoggedIn) fetchUnread() }, 30000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.login-wrapper { min-height: 100vh; }
</style>