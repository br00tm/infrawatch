import { useState } from 'react'
import Card from '../components/common/Card'
import Input from '../components/common/Input'
import { LOG_LEVEL_COLORS } from '../utils/constants'
import { LogLevel } from '../types'

const mockLogs = [
  { id: '1', level: 'info', message: 'Pod nginx-deployment-abc123 started successfully', source: 'kubelet', timestamp: '2024-02-12T10:30:00Z' },
  { id: '2', level: 'warning', message: 'High memory usage detected on node-1 (85%)', source: 'node-monitor', timestamp: '2024-02-12T10:29:45Z' },
  { id: '3', level: 'error', message: 'Failed to pull image: nginx:latest - timeout', source: 'containerd', timestamp: '2024-02-12T10:29:30Z' },
  { id: '4', level: 'debug', message: 'Health check passed for service api-gateway', source: 'health-checker', timestamp: '2024-02-12T10:29:15Z' },
  { id: '5', level: 'critical', message: 'Database connection lost - attempting reconnect', source: 'app-backend', timestamp: '2024-02-12T10:29:00Z' },
  { id: '6', level: 'info', message: 'Scaling deployment frontend from 2 to 4 replicas', source: 'hpa-controller', timestamp: '2024-02-12T10:28:45Z' },
  { id: '7', level: 'info', message: 'Certificate renewed for domain api.example.com', source: 'cert-manager', timestamp: '2024-02-12T10:28:30Z' },
  { id: '8', level: 'warning', message: 'Rate limit reached for API endpoint /users', source: 'api-gateway', timestamp: '2024-02-12T10:28:15Z' },
]

export default function Logs() {
  const [search, setSearch] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<LogLevel | 'all'>('all')

  const filteredLogs = mockLogs.filter((log) => {
    const matchesSearch = log.message.toLowerCase().includes(search.toLowerCase()) ||
                          log.source.toLowerCase().includes(search.toLowerCase())
    const matchesLevel = selectedLevel === 'all' || log.level === selectedLevel
    return matchesSearch && matchesLevel
  })

  const levels: (LogLevel | 'all')[] = ['all', 'debug', 'info', 'warning', 'error', 'critical']

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Logs</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          View and search through application and system logs
        </p>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            {levels.map((level) => (
              <button
                key={level}
                onClick={() => setSelectedLevel(level)}
                className={`px-3 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                  selectedLevel === level
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Logs List */}
      <Card padding="none">
        <div className="divide-y divide-gray-200 dark:divide-dark-border">
          {filteredLogs.map((log) => (
            <div key={log.id} className="p-4 hover:bg-gray-50 dark:hover:bg-dark-border">
              <div className="flex items-start gap-4">
                <span
                  className={`mt-1 px-2 py-0.5 text-xs font-medium rounded uppercase ${
                    LOG_LEVEL_COLORS[log.level as LogLevel]
                  }`}
                >
                  {log.level}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 dark:text-white font-mono break-all">
                    {log.message}
                  </p>
                  <div className="mt-1 flex items-center gap-4 text-xs text-gray-500">
                    <span>Source: {log.source}</span>
                    <span>{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Pagination placeholder */}
      <div className="flex justify-center">
        <div className="text-sm text-gray-500">
          Showing {filteredLogs.length} of {mockLogs.length} logs
        </div>
      </div>
    </div>
  )
}
