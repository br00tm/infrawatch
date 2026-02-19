import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '../stores/authStore'
import { authService } from '../services/auth'
import { LoginCredentials, RegisterData } from '../types'

export function useAuth() {
  const navigate = useNavigate()
  const { user, isAuthenticated, setAuth, logout: storeLogout } = useAuthStore()

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        const { user, tokens } = await authService.login(credentials)
        setAuth(user, tokens)
        toast.success('Welcome back!')
        navigate('/')
        return true
      } catch {
        toast.error('Invalid email or password')
        return false
      }
    },
    [navigate, setAuth]
  )

  const register = useCallback(
    async (data: RegisterData) => {
      try {
        await authService.register(data)
        toast.success('Account created successfully! Please login.')
        navigate('/login')
        return true
      } catch {
        toast.error('Registration failed')
        return false
      }
    },
    [navigate]
  )

  const logout = useCallback(() => {
    storeLogout()
    toast.success('Logged out successfully')
    navigate('/login')
  }, [navigate, storeLogout])

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
  }
}
