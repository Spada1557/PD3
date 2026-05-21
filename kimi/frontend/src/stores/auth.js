import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const login = async (payload) => {
    const res = await authApi.login(payload)
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    await fetchMe()
    return res
  }

  const fetchMe = async () => {
    try {
      const res = await authApi.me()
      user.value = res.data
      return res.data
    } catch {
      logout()
    }
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return { token, user, login, fetchMe, logout }
})
