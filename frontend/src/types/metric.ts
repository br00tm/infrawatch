export type MetricType =
  | 'cpu'
  | 'memory'
  | 'disk'
  | 'network'
  | 'pod'
  | 'node'
  | 'deployment'
  | 'container'
  | 'custom'

export interface Metric {
  _id: string
  name: string
  metric_type: MetricType
  value: number
  unit?: string
  source: string
  namespace?: string
  cluster?: string
  labels: Record<string, string>
  metadata: Record<string, unknown>
  timestamp: string
}

export interface MetricCreate {
  name: string
  metric_type: MetricType
  value: number
  unit?: string
  source: string
  namespace?: string
  cluster?: string
  labels?: Record<string, string>
  metadata?: Record<string, unknown>
}

export interface MetricQuery {
  metric_type?: MetricType
  source?: string
  namespace?: string
  cluster?: string
  name?: string
  start_time?: string
  end_time?: string
}

export interface MetricAggregation {
  name: string
  metric_type: string
  avg_value: number
  min_value: number
  max_value: number
  count: number
}
