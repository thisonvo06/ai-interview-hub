import axios, { type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('zh_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Response interceptor: unwrap data & handle errors
client.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    // If backend returned unified ResponseModel { code, message, data }
    if (res && typeof res.code === 'number') {
      if (res.code >= 200 && res.code < 300) {
        return res.data !== undefined ? res.data : res
      } else {
        ElMessage.error(res.message || '请求处理失败')
        return Promise.reject(new Error(res.message || 'Error'))
      }
    }
    return res
  },
  (error: AxiosError<any>) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.response?.data?.detail || '网络请求错误，请稍后重试'

    if (status === 401) {
      ElMessage.warning('登录凭证已过期或未登录，请重新登录')
      localStorage.removeItem('zh_access_token')
      localStorage.removeItem('zh_user_info')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`
      }
    } else if (status === 403) {
      ElMessage.error(`【权限拦截】${message}`)
    } else if (status === 404) {
      ElMessage.error(`【未找到】${message}`)
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

export default client
