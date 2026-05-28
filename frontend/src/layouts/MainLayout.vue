<template>
  <el-container style="height:100vh">
    <el-aside :width="sidebarCollapsed ? '76px' : '264px'" class="sidebar">
      <div class="sidebar-inner">
        <div class="logo">
          <div class="logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <div class="logo-text" v-if="!sidebarCollapsed">
            <div class="logo-title">ERP</div>
            <div class="logo-subtitle">Учет посуды</div>
          </div>
        </div>
        <el-menu :default-active="$route.path" router class="menu" background-color="transparent" text-color="#94a3b8" active-text-color="#60a5fa">
          <el-menu-item index="/">
            <el-icon><Odometer /></el-icon>
            <span v-if="!sidebarCollapsed">Дашборд</span>
          </el-menu-item>
          <el-menu-item index="/products">
            <el-icon><Goods /></el-icon>
            <span v-if="!sidebarCollapsed">Продукция</span>
          </el-menu-item>
          <el-menu-item index="/stock">
            <el-icon><TakeawayBox /></el-icon>
            <span v-if="!sidebarCollapsed">Склад</span>
          </el-menu-item>
          <el-menu-item index="/purchases">
            <el-icon><ShoppingCart /></el-icon>
            <span v-if="!sidebarCollapsed">Закупки</span>
          </el-menu-item>
          <el-menu-item index="/sales">
            <el-icon><Sell /></el-icon>
            <span v-if="!sidebarCollapsed">Продажи</span>
          </el-menu-item>
          <el-menu-item index="/suppliers">
            <el-icon><OfficeBuilding /></el-icon>
            <span v-if="!sidebarCollapsed">Поставщики</span>
          </el-menu-item>
          <el-menu-item index="/clients">
            <el-icon><User /></el-icon>
            <span v-if="!sidebarCollapsed">Клиенты</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><Document /></el-icon>
            <span v-if="!sidebarCollapsed">Отчеты</span>
          </el-menu-item>
          <el-menu-item index="/references">
            <el-icon><Collection /></el-icon>
            <span v-if="!sidebarCollapsed">Справочники</span>
          </el-menu-item>
          <el-menu-item index="/users" v-if="isAdmin">
            <el-icon><UserFilled /></el-icon>
            <span v-if="!sidebarCollapsed">Пользователи</span>
          </el-menu-item>
          <el-menu-item index="/settings" v-if="isAdmin">
            <el-icon><Setting /></el-icon>
            <span v-if="!sidebarCollapsed">Настройки</span>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <div class="footer-version" v-if="!sidebarCollapsed">v1.0.0</div>
        </div>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed" title="Свернуть меню">
            <el-icon size="18"><Fold /></el-icon>
          </button>
          <div class="header-breadcrumb">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
        </div>
        <div class="header-right">
          <el-badge :value="notificationsCount" :hidden="notificationsCount === 0" class="badge-item" type="danger">
            <el-button circle text @click="showNotifications" class="header-icon-btn">
              <el-icon size="18"><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-dropdown>
            <div class="user-block">
              <div class="user-avatar">
                <el-icon size="16"><UserFilled /></el-icon>
              </div>
              <div class="user-info" v-if="!sidebarCollapsed">
                <div class="user-name">{{ auth.user?.name || 'Гость' }}</div>
                <div class="user-role">{{ userRoleLabel }}</div>
              </div>
              <el-icon class="user-chevron"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="auth.logout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>Выход</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
  <el-drawer v-model="notifOpen" title="Уведомления" size="380" class="notif-drawer">
    <div v-if="notifications.length" class="notif-list">
      <div v-for="n in notifications" :key="n.id" class="notif-item" :class="n.type">
        <div class="notif-icon">
          <el-icon size="18" v-if="n.type === 'warning'"><Warning /></el-icon>
          <el-icon size="18" v-else-if="n.type === 'info'"><InfoFilled /></el-icon>
          <el-icon size="18" v-else><Bell /></el-icon>
        </div>
        <div class="notif-content">
          <div class="notif-title">{{ n.title }}</div>
          <div class="notif-msg">{{ n.message }}</div>
          <div class="notif-date">{{ n.created_at }}</div>
        </div>
      </div>
    </div>
    <div v-else class="notif-empty">
      <el-icon size="48" color="#cbd5e1"><Bell /></el-icon>
      <div class="notif-empty-text">Нет новых уведомлений</div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useDashboardStore } from '../stores/dashboard'

const auth = useAuthStore()
const dash = useDashboardStore()
const route = useRoute()
const notifOpen = ref(false)
const sidebarCollapsed = ref(false)

const isAdmin = computed(() => auth.user?.role === 'admin')
const notificationsCount = computed(() => dash.notifications?.length || 0)
const notifications = computed(() => dash.notifications || [])

const userRoleLabel = computed(() => {
  const roles = { admin: 'Администратор', manager: 'Менеджер', warehouse: 'Кладовщик' }
  return roles[auth.user?.role] || 'Пользователь'
})

const pageTitle = computed(() => {
  const titles = {
    '/': 'Дашборд',
    '/products': 'Продукция',
    '/stock': 'Склад',
    '/purchases': 'Закупки',
    '/sales': 'Продажи',
    '/suppliers': 'Поставщики',
    '/clients': 'Клиенты',
    '/reports': 'Отчеты',
    '/references': 'Справочники',
    '/users': 'Пользователи',
    '/settings': 'Настройки',
  }
  return titles[route.path] || ''
})

const showNotifications = () => { notifOpen.value = true }

onMounted(() => {
  dash.loadNotifications()
})
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #0B0A1A 0%, #13102A 100%);
  color: #fff;
  overflow: hidden;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 8px 0 40px rgba(11, 10, 26, 0.35);
  z-index: 50;
  position: relative;
}
.sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(109,40,217,0.08) 0%, transparent 60%);
  pointer-events: none;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  z-index: 1;
}

.logo {
  height: 76px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.logo-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, #7C3AED, #6D28D9);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 8px 24px rgba(109, 40, 217, 0.45);
}

.logo-title {
  font-size: 16px;
  font-weight: 800;
  color: #F1EEFE;
  letter-spacing: -0.3px;
  white-space: nowrap;
  overflow: hidden;
}

.logo-subtitle {
  font-size: 11px;
  color: #7B7394;
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  white-space: nowrap;
  overflow: hidden;
}

.menu {
  border-right: 0;
  flex: 1;
  padding-top: 12px;
  overflow-y: auto;
}

.sidebar-footer {
  padding: 18px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.footer-version {
  font-size: 11px;
  color: #4A4458;
  text-align: center;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.6);
  height: 72px !important;
  padding: 0 28px;
  position: sticky;
  top: 0;
  z-index: 40;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sidebar-toggle {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.6);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
}

.sidebar-toggle:hover {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}

.page-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon-btn {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-sm) !important;
  color: var(--text-secondary) !important;
  background: rgba(255, 255, 255, 0.5) !important;
}

.header-icon-btn:hover {
  background: var(--primary-light) !important;
  color: var(--primary) !important;
}

.badge-item { cursor: pointer; }

.user-block {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  transition: var(--transition);
  background: rgba(255, 255, 255, 0.4);
}

.user-block:hover {
  background: rgba(255, 255, 255, 0.8);
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, #F3E8FF, #EDE9FE);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.user-role {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
}

.user-chevron {
  color: var(--text-muted);
  margin-left: 2px;
}

.main-content {
  background: #F8FAFC;
  overflow-y: auto;
  padding: 28px;
}

.notif-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notif-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--surface-overlay);
  border: 1px solid var(--border-light);
  transition: var(--transition);
  cursor: pointer;
}

.notif-item:hover {
  background: var(--surface-solid);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.notif-item.warning { border-left: 3px solid var(--warning); }
.notif-item.info { border-left: 3px solid var(--primary); }

.notif-icon {
  color: var(--text-muted);
  margin-top: 2px;
}

.notif-title {
  font-weight: 700;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.notif-msg {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.4;
}

.notif-date {
  color: var(--text-muted);
  font-size: 11px;
  margin-top: 6px;
  font-weight: 500;
}

.notif-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.notif-empty-text {
  margin-top: 12px;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
}
</style>
