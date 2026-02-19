import axios, { AxiosError, AxiosInstance } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const tokens = useAuthStore.getState().tokens
    if (tokens?.access_token) {
      config.headers.Authorization = `Bearer ${tokens.access_token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config

    // If 401 and not a refresh request, try to refresh token
    if (error.response?.status === 401 && originalRequest && !originalRequest.url?.includes('/auth/refresh')) {
      const tokens = useAuthStore.getState().tokens

      if (tokens?.refresh_token) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: tokens.refresh_token,
          })

          const newTokens = response.data
          useAuthStore.getState().setAuth(useAuthStore.getState().user!, newTokens)

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`
          return api(originalRequest)
        } catch {
          // Refresh failed, logout
          useAuthStore.getState().logout()
        }
      } else {
        useAuthStore.getState().logout()
      }
    }

    return Promise.reject(error)
  }
)

export default api
