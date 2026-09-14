import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, adminApi } from '@/api'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('zh_access_token'))
  const user = ref<UserInfo | null>(
    localStorage.getItem('zh_user_info')
      ? JSON.parse(localStorage.getItem('zh_user_info')!)
      : null
  )

  const isAuthenticated = computed(() => !!token.value)
  const isPersonal = computed(() => user.value?.account_type === 'PERSONAL')
  const isEnterprise = computed(() => user.value?.account_type === 'ENTERPRISE')
  const isAdmin = computed(() => user.value?.account_type === 'ADMIN' || user.value?.roles.includes('PLATFORM_ADMIN') || user.value?.roles.includes('SUPER_ADMIN'))

  const setAuth = (accessToken: string, userInfo: any) => {
    token.value = accessToken
    user.value = userInfo
    localStorage.setItem('zh_access_token', accessToken)
    localStorage.setItem('zh_user_info', JSON.stringify(userInfo))
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('zh_access_token')
    localStorage.removeItem('zh_user_info')
  }

  const login = async (credentials: { account: string; password: string }) => {
    const res: any = await authApi.login(credentials)
    setAuth(res.access_token, {
      id: res.user_id,
      email: credentials.account.includes('@') ? credentials.account : '',
      account_type: res.account_type,
      roles: res.role_codes,
      name: res.name,
      avatar_url: res.avatar_url,
      company_id: res.company_id
    })
    return res
  }

  const adminLogin = async (credentials: { account: string; password: string }) => {
    const res: any = await adminApi.login(credentials)
    setAuth(res.access_token, {
      id: res.user_id,
      email: credentials.account,
      account_type: 'ADMIN',
      roles: res.role_codes,
      name: res.name
    })
    return res
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return null
    try {
      const info = await authApi.getMe()
      user.value = info
      localStorage.setItem('zh_user_info', JSON.stringify(info))
      return info
    } catch (e) {
      clearAuth()
      return null
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (e) {
      // ignore
    } finally {
      clearAuth()
      window.location.href = '/login'
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isPersonal,
    isEnterprise,
    isAdmin,
    login,
    adminLogin,
    logout,
    fetchCurrentUser,
    setAuth,
    clearAuth
  }
})
