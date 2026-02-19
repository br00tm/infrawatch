export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical'

export interface Log {
  _id: string
  message: string
  level: LogLevel
  source: string
  namespace?: string
  cluster?: string
  pod_name?: string
  container_name?: string
  labels: Record<string, string>
  metadata: Record<string, unknown>
  timestamp: string
}

export interface LogCreate {
  message: string
  level: LogLevel
  source: string
  namespace?: string
  cluster?: string
  pod_name?: string
  container_name?: string
  labels?: Record<string, string>
  metadata?: Record<string, unknown>
}

export interface LogQuery {
  level?: LogLevel
  source?: string
  namespace?: string
  cluster?: string
  pod_name?: string
  container_name?: string
  search?: string
  start_time?: string
  end_time?: string
}

export interface LogStats {
  total_count: number
  by_level: Record<string, number>
  by_source: Record<string, number>
  by_namespace: Record<string, number>
}
