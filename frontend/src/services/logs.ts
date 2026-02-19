import api from './api'
import { Log, LogCreate, LogQuery, LogStats, PaginatedResponse } from '../types'

export const logsService = {
  async list(query: LogQuery = {}, page = 1, pageSize = 50): Promise<PaginatedResponse<Log>> {
    const params = { ...query, page, page_size: pageSize }
    const response = await api.get<PaginatedResponse<Log>>('/logs', { params })
    return response.data
  },

  async create(data: LogCreate): Promise<Log> {
    const response = await api.post<Log>('/logs', data)
    return response.data
  },

  async getStats(): Promise<LogStats> {
    const response = await api.get<LogStats>('/logs/stats')
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/logs/${id}`)
  },
}
