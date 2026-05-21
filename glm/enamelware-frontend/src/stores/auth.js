import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')
  const isAdmin = computed(() => userRole.value === 'admin')
  const isManager = computed(() => userRole.value === 'manager')
  const isWarehouse = computed(() => userRole.value === 'warehouse')

  async function login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    const meResponse = await api.get('/auth/me')
    user.value = meResponse.data
    localStorage.setItem('user', JSON.stringify(user.value))
    return user.value
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchUser() {
    if (!token.value) return null
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return user.value
    } catch {
      logout()
      return null
    }
  }

  async function getNotifications() {
    const response = await api.get('/auth/notifications')
    return response.data
  }

  async function getUnreadCount() {
    const response = await api.get('/dashboard/unread-count')
    return response.data.count
  }

  async function markNotificationRead(id) {
    await api.put(`/auth/notifications/${id}/read`)
  }

  async function markAllNotificationsRead() {
    await api.put('/auth/notifications/read-all')
  }

  return {
    token, user, isAuthenticated, userRole, isAdmin, isManager, isWarehouse,
    login, logout, fetchUser, getNotifications, getUnreadCount,
    markNotificationRead, markAllNotificationsRead,
  }
})