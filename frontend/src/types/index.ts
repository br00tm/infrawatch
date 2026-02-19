export * from './user'
export * from './metric'
export * from './log'
export * from './alert'

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiError {
  error: string
  message: string
  details?: Record<string, unknown>
  status_code: number
}
