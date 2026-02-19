import { useState } from 'react'
import Card, { CardHeader } from '../components/common/Card'
import Button from '../components/common/Button'
import { METRIC_TYPE_LABELS } from '../utils/constants'

const mockMetrics = [
  { id: '1', name: 'cpu_usage', type: 'cpu', value: 75.5, source: 'node-1', namespace: 'default' },
  { id: '2', name: 'memory_usage', type: 'memory', value: 62.3, source: 'node-1', namespace: 'default' },
  { id: '3', name: 'disk_usage', type: 'disk', value: 45.8, source: 'node-1', namespace: 'default' },
  { id: '4', name: 'network_in', type: 'network', value: 1024.5, source: 'node-1', namespace: 'default' },
  { id: '5', name: 'pod_count', type: 'pod', value: 48, source: 'cluster-1', namespace: 'kube-system' },
]

export default function Metrics() {
  const [selectedType, setSelectedType] = useState<string>('all')

  const filteredMetrics =
    selectedType === 'all'
      ? mockMetrics
      : mockMetrics.filter((m) => m.type === selectedType)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Metrics</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor your infrastructure metrics in real-time
          </p>
        </div>
        <Button>Export Metrics</Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedType('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedType === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            All
          </button>
          {Object.entries(METRIC_TYPE_LABELS).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSelectedType(key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedType === key
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredMetrics.map((metric) => (
          <Card key={metric.id}>
            <div className="flex items-center justify-between mb-4">
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-400">
                {METRIC_TYPE_LABELS[metric.type as keyof typeof METRIC_TYPE_LABELS] || metric.type}
              </span>
              <span className="text-xs text-gray-500">{metric.namespace}</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {metric.name}
            </h3>
            <div className="mt-2 flex items-baseline">
              <span className="text-3xl font-bold text-primary-600">
                {metric.value}
              </span>
              <span className="ml-1 text-sm text-gray-500">
                {metric.type === 'cpu' || metric.type === 'memory' || metric.type === 'disk'
                  ? '%'
                  : metric.type === 'network'
                    ? 'KB/s'
                    : ''}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-500">Source: {metric.source}</p>
          </Card>
        ))}
      </div>

      {/* Chart */}
      <Card>
        <CardHeader title="Metrics Timeline" subtitle="Last hour" />
        <div className="h-80 flex items-center justify-center text-gray-400">
          Chart placeholder - Integrate Recharts for time-series visualization
        </div>
      </Card>
    </div>
  )
}
