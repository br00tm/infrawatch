export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical'
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'silenced'
export type NotificationChannel = 'email' | 'telegram' | 'discord' | 'slack' | 'webhook'

export interface Alert {
  _id: string
  title: string
  description?: string
  severity: AlertSeverity
  status: AlertStatus
  source: string
  namespace?: string
  cluster?: string
  labels: Record<string, string>
  metadata: Record<string, unknown>
  rule_id?: string
  acknowledged_by?: string
  acknowledged_at?: string
  resolved_at?: string
  created_at: string
}

export interface AlertCreate {
  title: string
  description?: string
  severity: AlertSeverity
  source: string
  namespace?: string
  cluster?: string
  labels?: Record<string, string>
  metadata?: Record<string, unknown>
  rule_id?: string
}

export interface AlertCondition {
  metric_name: string
  operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq' | 'ne'
  threshold: number
  duration_seconds: number
}

export interface AlertRule {
  _id: string
  name: string
  description?: string
  enabled: boolean
  severity: AlertSeverity
  conditions: AlertCondition[]
  namespace_filter?: string
  cluster_filter?: string
  labels_filter: Record<string, string>
  notification_channels: NotificationChannel[]
  cooldown_minutes: number
  user_id: string
  last_triggered?: string
  created_at: string
  updated_at: string
}

export interface AlertRuleCreate {
  name: string
  description?: string
  enabled?: boolean
  severity?: AlertSeverity
  conditions: AlertCondition[]
  namespace_filter?: string
  cluster_filter?: string
  labels_filter?: Record<string, string>
  notification_channels?: NotificationChannel[]
  cooldown_minutes?: number
}

export interface AlertStats {
  total_active: number
  total_acknowledged: number
  total_resolved: number
  by_severity: Record<string, number>
  by_source: Record<string, number>
}
