export const LOG_LEVEL_COLORS = {
  debug: 'text-gray-500',
  info: 'text-blue-500',
  warning: 'text-yellow-500',
  error: 'text-red-500',
  critical: 'text-red-700',
} as const

export const ALERT_SEVERITY_COLORS = {
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  critical: 'bg-red-200 text-red-900 dark:bg-red-800 dark:text-red-100',
} as const

export const ALERT_STATUS_COLORS = {
  active: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  acknowledged: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  resolved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  silenced: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
} as const

export const METRIC_TYPE_LABELS = {
  cpu: 'CPU',
  memory: 'Memory',
  disk: 'Disk',
  network: 'Network',
  pod: 'Pod',
  node: 'Node',
  deployment: 'Deployment',
  container: 'Container',
  custom: 'Custom',
} as const

export const REFRESH_INTERVALS = [
  { label: 'Off', value: 0 },
  { label: '5s', value: 5000 },
  { label: '10s', value: 10000 },
  { label: '30s', value: 30000 },
  { label: '1m', value: 60000 },
  { label: '5m', value: 300000 },
] as const
