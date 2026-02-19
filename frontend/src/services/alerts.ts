import api from './api'
import {
  Alert,
  AlertCreate,
  AlertRule,
  AlertRuleCreate,
  AlertStats,
  AlertStatus,
  PaginatedResponse,
} from '../types'

export const alertsService = {
  async list(status?: AlertStatus, page = 1, pageSize = 20): Promise<PaginatedResponse<Alert>> {
    const params: Record<string, unknown> = { page, page_size: pageSize }
    if (status) params.status = status
    const response = await api.get<PaginatedResponse<Alert>>('/alerts', { params })
    return response.data
  },

  async getStats(): Promise<AlertStats> {
    const response = await api.get<AlertStats>('/alerts/stats')
    return response.data
  },

  async create(data: AlertCreate): Promise<Alert> {
    const response = await api.post<Alert>('/alerts', data)
    return response.data
  },

  async acknowledge(id: string): Promise<Alert> {
    const response = await api.post<Alert>(`/alerts/${id}/acknowledge`)
    return response.data
  },

  async resolve(id: string): Promise<Alert> {
    const response = await api.post<Alert>(`/alerts/${id}/resolve`)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/alerts/${id}`)
  },

  async listRules(page = 1, pageSize = 20): Promise<PaginatedResponse<AlertRule>> {
    const response = await api.get<PaginatedResponse<AlertRule>>('/alerts/rules', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  async createRule(data: AlertRuleCreate): Promise<AlertRule> {
    const response = await api.post<AlertRule>('/alerts/rules', data)
    return response.data
  },

  async toggleRule(id: string, enabled: boolean): Promise<AlertRule> {
    const response = await api.post<AlertRule>(`/alerts/rules/${id}/toggle`, null, {
      params: { enabled },
    })
    return response.data
  },

  async deleteRule(id: string): Promise<void> {
    await api.delete(`/alerts/rules/${id}`)
  },
}
