import api from './api'
import { User, LoginCredentials, RegisterData, AuthTokens } from '../types'

export const authService = {
  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    const tokenResponse = await api.post<AuthTokens>('/auth/login', credentials)
    const tokens = tokenResponse.data

    // Set token temporarily to get user info
    const userResponse = await api.get<User>('/auth/me', {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
    })

    return { user: userResponse.data, tokens }
  },

  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },
}
