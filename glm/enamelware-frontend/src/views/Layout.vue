<template>
  <div class="layout-container">
    <aside class="aside-menu">
      <div class="aside-logo">
        <div style="display:flex;align-items:center;gap:10px">
          <div class="aside-logo-icon">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color:#fff">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <div>
            <h2>Enamelware</h2>
            <p>Учёт товарооборота</p>
          </div>
        </div>
      </div>
      <nav class="nav-menu">
        <div class="nav-section-title">Основное</div>
        <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
          <el-icon><DataAnalysis /></el-icon> Дашборд
        </router-link>
        <router-link to="/products" class="nav-item" :class="{ active: $route.path.startsWith('/products') }">
          <el-icon><Goods /></el-icon> Продукция
        </router-link>
        <router-link to="/stock" class="nav-item" :class="{ active: $route.path === '/stock' }">
          <el-icon><Box /></el-icon> Склад
        </router-link>
        <div class="nav-section-title">Документы</div>
        <router-link to="/purchases" class="nav-item" :class="{ active: $route.path.startsWith('/purchases') }">
          <el-icon><Van /></el-icon> Закупки
        </router-link>
        <router-link v-if="auth.isAdmin || auth.isManager" to="/sales" class="nav-item" :class="{ active: $route.path.startsWith('/sales') }">
          <el-icon><ShoppingCart /></el-icon> Продажи
        </router-link>
        <div class="nav-section-title">Справочники</div>
        <router-link v-if="auth.isAdmin || auth.isManager" to="/clients" class="nav-item" :class="{ active: $route.path === '/clients' }">
          <el-icon><User /></el-icon> Клиенты
        </router-link>
        <router-link v-if="auth.isAdmin || auth.isWarehouse" to="/suppliers" class="nav-item" :class="{ active: $route.path === '/suppliers' }">
          <el-icon><OfficeBuilding /></el-icon> Поставщики
        </router-link>
        <div class="nav-section-title">Аналитика</div>
        <router-link to="/reports" class="nav-item" :class="{ active: $route.path === '/reports' }">
          <el-icon><Document /></el-icon> Отчёты
        </router-link>
        <template v-if="auth.isAdmin">
          <div class="nav-section-title">Управление</div>
          <router-link to="/users" class="nav-item" :class="{ active: $route.path === '/users' }">
            <el-icon><UserFilled /></el-icon> Пользователи
          </router-link>
          <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
            <el-icon><Setting /></el-icon> Настройки
          </router-link>
        </template>
      </nav>
      <div class="aside-footer">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,var(--primary),var(--primary-dark));display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;box-shadow:0 0 10px var(--primary-glow)">{{ auth.user?.name?.charAt(0) || 'U' }}</div>
          <div>
            <div style="font-weight:600;color:#fff;font-size:12px;letter-spacing:-0.01em">{{ auth.user?.name || 'Пользователь' }}</div>
            <div style="color:var(--text-muted);font-size:10px;letter-spacing:0.02em">{{ roleLabel }}</div>
          </div>
        </div>
      </div>
    </aside>
    <div class="main-content">
      <header class="top-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <el-popover placement="bottom-end" :width="360" trigger="click" @show="loadNotifications" popper-class="notification-popover">
            <template #reference>
              <el-badge :value="unreadCount || undefined" :hidden="!unreadCount" :max="9" class="notification-badge">
                <el-button text circle style="font-size:17px;color:var(--text-muted);cursor:pointer"><el-icon><Bell /></el-icon></el-button>
              </el-badge>
            </template>
            <div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <span style="font-weight:700;font-size:13px;color:var(--text-primary)">Уведомления</span>
                <el-button v-if="notifications.length" link type="primary" size="small" @click="markAllRead" style="cursor:pointer;font-size:11px">Прочитать все</el-button>
              </div>
              <div v-if="!notifications.length" class="empty-state" style="padding:18px">
                <el-icon><BellFilled /></el-icon>
                <p>Нет новых уведомлений</p>
              </div>
              <div v-for="n in notifications" :key="n.id" class="notification-item" @click="markRead(n.id)">
                <el-icon :color="n.is_read ? 'var(--text-muted)' : 'var(--primary-light)'" style="margin-top:2px;flex-shrink:0"><InfoFilled v-if="!n.is_read" /><Check v-else /></el-icon>
                <div style="flex:1;min-width:0">
                  <div style="font-size:11px;font-weight:600;color:var(--text-primary);letter-spacing:-0.01em">{{ n.title }}</div>
                  <div style="font-size:10px;color:var(--text-secondary);margin-top:1px">{{ n.message }}</div>
                  <div style="font-size:9px;color:var(--text-muted);margin-top:2px">{{ formatDateTime(n.created_at) }}</div>
                </div>
              </div>
            </div>
          </el-popover>
          <el-dropdown @command="handleCommand" trigger="click">
            <div style="display:flex;align-items:center;gap:9px;cursor:pointer">
              <el-avatar :size="32" :style="{ background: 'linear-gradient(135deg, var(--primary), var(--primary-dark))', color: '#fff', fontWeight: 700, fontSize: '12px', boxShadow: '0 0 10px var(--primary-glow)' }">{{ auth.user?.name?.charAt(0) || 'U' }}</el-avatar>
              <div style="line-height:1.2">
                <div style="font-weight:600;font-size:12px;color:var(--text-primary);letter-spacing:-0.01em">{{ auth.user?.name }}</div>
                <div style="font-size:10px;color:var(--text-muted)">{{ roleLabel }}</div>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon> Выйти
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { formatDateTime, roleLabel as rl } from '../utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const notifications = ref([])
const unreadCount = ref(0)

const roleLabel = computed(() => rl(auth.user?.role))

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Дашборд',
    '/products': 'Продукция',
    '/stock': 'Склад',
    '/purchases': 'Закупки',
    '/sales': 'Продажи',
    '/clients': 'Клиенты',
    '/suppliers': 'Поставщики',
    '/reports': 'Отчёты',
    '/users': 'Пользователи',
    '/settings': 'Настройки',
  }
  if (route.path.match(/\/products\/\d+/)) return 'Редактирование товара'
  if (route.path === '/products/new') return 'Новый товар'
  if (route.path.match(/\/purchases\/\d+/)) return 'Закупка'
  if (route.path === '/purchases/new') return 'Новая закупка'
  if (route.path.match(/\/sales\/\d+/)) return 'Продажа'
  if (route.path === '/sales/new') return 'Новая продажа'
  return titles[route.path] || route.name || ''
})

function handleCommand(cmd) {
  if (cmd === 'logout') { auth.logout(); router.push('/login') }
}

async function loadNotifications() {
  try {
    notifications.value = await auth.getNotifications()
    unreadCount.value = await auth.getUnreadCount()
  } catch {}
}

async function markRead(id) {
  try { await auth.markNotificationRead(id); await loadNotifications() } catch {}
}

async function markAllRead() {
  try { await auth.markAllNotificationsRead(); await loadNotifications() } catch {}
}

onMounted(async () => {
  if (auth.isAuthenticated) {
    try { unreadCount.value = await auth.getUnreadCount() } catch {}
  }
})
</script>

<style scoped>
</style>