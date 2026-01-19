/** axios请求封装 */
import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 如果响应码不是200，视为错误
    if (res.code !== 200 && res.code !== 201) {
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    // 处理401未授权
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    // 处理403禁止访问（未登录或无权限）
    if (error.response?.status === 403) {
      console.log('未登录或无权限访问')
      // 不显示错误提示，静默处理
      return Promise.reject(new Error('未登录'))
    }
    return Promise.reject(error.response?.data?.detail || error.message)
  }
)

export default request
