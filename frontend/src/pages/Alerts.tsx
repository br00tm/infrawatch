import { useState } from 'react'
import Card, { CardHeader } from '../components/common/Card'
import Button from '../components/common/Button'
import { ALERT_SEVERITY_COLORS, ALERT_STATUS_COLORS } from '../utils/constants'
import { AlertSeverity, AlertStatus } from '../types'

const mockAlerts = [
  { id: '1', title: 'High CPU Usage', severity: 'warning', status: 'active', source: 'node-1', created_at: '2024-02-12T10:30:00Z' },
  { id: '2', title: 'Pod CrashLoopBackOff', severity: 'error', status: 'active', source: 'api-pod-xyz', created_at: '2024-02-12T10:25:00Z' },
  { id: '3', title: 'Memory Limit Reached', severity: 'critical', status: 'acknowledged', source: 'database-pod', created_at: '2024-02-12T10:20:00Z' },
  { id: '4', title: 'Certificate Expiring', severity: 'warning', status: 'resolved', source: 'ingress-controller', created_at: '2024-02-12T10:15:00Z' },
  { id: '5', title: 'Disk Space Low', severity: 'warning', status: 'active', source: 'node-2', created_at: '2024-02-12T10:10:00Z' },
]

export default function Alerts() {
  const [selectedStatus, setSelectedStatus] = useState<AlertStatus | 'all'>('all')

  const filteredAlerts =
    selectedStatus === 'all'
      ? mockAlerts
      : mockAlerts.filter((a) => a.status === selectedStatus)

  const statuses: (AlertStatus | 'all')[] = ['all', 'active', 'acknowledged', 'resolved', 'silenced']

  const stats = {
    active: mockAlerts.filter((a) => a.status === 'active').length,
    acknowledged: mockAlerts.filter((a) => a.status === 'acknowledged').length,
    resolved: mockAlerts.filter((a) => a.status === 'resolved').length,
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Alerts</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor and manage infrastructure alerts
          </p>
        </div>
        <Button>Create Alert Rule</Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-red-600">{stats.active}</p>
            <p className="text-sm text-gray-500">Active Alerts</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-yellow-600">{stats.acknowledged}</p>
            <p className="text-sm text-gray-500">Acknowledged</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{stats.resolved}</p>
            <p className="text-sm text-gray-500">Resolved Today</p>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-2">
          {statuses.map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                selectedStatus === status
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </Card>

      {/* Alerts List */}
      <Card padding="none">
        <div className="divide-y divide-gray-200 dark:divide-dark-border">
          {filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className="p-4 hover:bg-gray-50 dark:hover:bg-dark-border flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${
                    ALERT_SEVERITY_COLORS[alert.severity as AlertSeverity]
                  }`}
                >
                  {alert.severity}
                </span>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{alert.title}</p>
                  <p className="text-sm text-gray-500">
                    Source: {alert.source} • {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${
                    ALERT_STATUS_COLORS[alert.status as AlertStatus]
                  }`}
                >
                  {alert.status}
                </span>
                {alert.status === 'active' && (
                  <Button size="sm" variant="secondary">
                    Acknowledge
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
