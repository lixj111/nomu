/** 用户状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || '')

  // 设置token
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  // 设置用户信息
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  // 从localStorage恢复用户信息
  const restoreUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('恢复用户信息失败', e)
      }
    }
  }

  // 登录
  const login = async (username, password) => {
    const res = await authApi.login({ username, password })
    setToken(res.data.access_token)
    setUser(res.data.user)
    return res
  }

  // 注册
  const register = async (username, password, email) => {
    const res = await authApi.register({ username, password, email })
    setToken(res.data.access_token)
    setUser(res.data.user)
    return res
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    const res = await authApi.getCurrentUser()
    setUser(res.data)
    return res
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  // 检查是否已登录
  const isLoggedIn = () => {
    return !!token.value
  }

  return {
    user,
    token,
    setToken,
    setUser,
    restoreUser,
    login,
    register,
    fetchCurrentUser,
    logout,
    isLoggedIn
  }
})
