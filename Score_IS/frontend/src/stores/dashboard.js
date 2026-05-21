import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardApi } from '../api'

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref(null)
  const notifications = ref([])

  const load = async (params = {}) => {
    const res = await dashboardApi.get(params)
    data.value = res.data
  }

  const loadNotifications = async () => {
    const res = await dashboardApi.notifications()
    notifications.value = res.data
  }

  return { data, notifications, load, loadNotifications }
})
