import api from './api'
import { Metric, MetricCreate, MetricQuery, MetricAggregation, PaginatedResponse } from '../types'

export const metricsService = {
  async list(query: MetricQuery = {}, page = 1, pageSize = 20): Promise<PaginatedResponse<Metric>> {
    const params = { ...query, page, page_size: pageSize }
    const response = await api.get<PaginatedResponse<Metric>>('/metrics', { params })
    return response.data
  },

  async create(data: MetricCreate): Promise<Metric> {
    const response = await api.post<Metric>('/metrics', data)
    return response.data
  },

  async getAggregations(query: MetricQuery = {}): Promise<MetricAggregation[]> {
    const response = await api.get<MetricAggregation[]>('/metrics/aggregations', { params: query })
    return response.data
  },

  async getBySource(source: string, limit = 10): Promise<Metric[]> {
    const response = await api.get<Metric[]>(`/metrics/source/${source}`, { params: { limit } })
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/metrics/${id}`)
  },
}
