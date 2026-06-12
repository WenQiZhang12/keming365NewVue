import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getProfile, logout as apiLogout } from '@/api'
import type { UserInfo } from '@/types'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<UserInfo | null>(null)
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 初始化时从 localStorage 恢复 user
  const saved = localStorage.getItem('user')
  if (saved) {
    try { user.value = JSON.parse(saved) } catch { /* ignore */ }
  }

  const login = async (username: string, password: string) => {
    const res = await apiLogin(username, password)
    token.value = res.access
    user.value = res.user
    localStorage.setItem('token', res.access)
    localStorage.setItem('user', JSON.stringify(res.user))
  }

  const fetchUser = async () => {
    if (!token.value) return
    try {
      const profile = await getProfile()
      user.value = profile
      localStorage.setItem('user', JSON.stringify(profile))
    } catch {
      doLogout()
    }
  }

  const doLogout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    apiLogout()
  }

  return { token, user, isLoggedIn, login, fetchUser, logout: doLogout }
})
