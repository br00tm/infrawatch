import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { format } from 'date-fns'
import Card, { CardHeader } from '../components/common/Card'
import Button from '../components/common/Button'
import { metricsService } from '../services/metrics'
import { Metric, MetricType } from '../types'
import { METRIC_TYPE_LABELS } from '../utils/constants'

const PAGE_SIZE = 18
const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

interface ChartSeries {
  name: string
  data: { time: string; value: number }[]
}

export default function Metrics() {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [total, setTotal] = useState(0)
  const [selectedType, setSelectedType] = useState<MetricType | 'all'>('all')
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [chartSeries, setChartSeries] = useState<ChartSeries[]>([])

  useEffect(() => {
    async function fetchMetrics() {
      setLoading(true)
      try {
        const query = selectedType !== 'all' ? { metric_type: selectedType } : {}
        const data = await metricsService.list(query, page, PAGE_SIZE)
        setMetrics(data.items)
        setTotal(data.total)
        setChartSeries(buildSeries(data.items))
      } catch (err) {
        console.error('Failed to load metrics', err)
      } finally {
        setLoading(false)
      }
    }
    fetchMetrics()
  }, [selectedType, page])

  function handleTypeChange(type: MetricType | 'all') {
    setSelectedType(type)
    setPage(1)
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Metrics</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor your infrastructure metrics in real-time
          </p>
        </div>
        <span className="text-sm text-gray-500">{total.toLocaleString()} total</span>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-2">
          <FilterBtn label="All" active={selectedType === 'all'} onClick={() => handleTypeChange('all')} />
          {Object.entries(METRIC_TYPE_LABELS).map(([key, label]) => (
            <FilterBtn
              key={key}
              label={label}
              active={selectedType === key}
              onClick={() => handleTypeChange(key as MetricType)}
            />
          ))}
        </div>
      </Card>

      {/* Timeline chart */}
      {!loading && chartSeries.length > 0 && (
        <Card>
          <CardHeader title="Metrics Timeline" subtitle="Current page — values over time" />
          <ResponsiveContainer width="100%" height={260}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="time"
                type="category"
                allowDuplicatedCategory={false}
                tick={{ fontSize: 11 }}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              {chartSeries.map((series, i) => (
                <Line
                  key={series.name}
                  data={series.data}
                  dataKey="value"
                  name={series.name}
                  stroke={COLORS[i % COLORS.length]}
                  dot={false}
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Metrics Grid */}
      {loading ? (
        <div className="py-16 text-center text-gray-400">Loading metrics...</div>
      ) : metrics.length === 0 ? (
        <Card>
          <div className="py-12 text-center text-gray-400">
            <p className="text-lg font-medium">No metrics found</p>
            <p className="text-sm mt-1">
              Send metrics to the API at{' '}
              <code className="font-mono">POST /api/v1/metrics</code>
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {metrics.map((metric) => (
            <Card key={metric._id}>
              <div className="flex items-center justify-between mb-3">
                <span className="px-2 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-400">
                  {METRIC_TYPE_LABELS[metric.metric_type as keyof typeof METRIC_TYPE_LABELS] ||
                    metric.metric_type}
                </span>
                <span className="text-xs text-gray-500">{metric.namespace || '—'}</span>
              </div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                {metric.name}
              </h3>
              <div className="mt-2 flex items-baseline">
                <span className="text-3xl font-bold text-primary-600">
                  {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value}
                </span>
                {metric.unit && (
                  <span className="ml-1 text-sm text-gray-500">{metric.unit}</span>
                )}
              </div>
              <div className="mt-2 text-xs text-gray-500 space-y-0.5">
                <p>Source: {metric.source}</p>
                <p>{format(new Date(metric.timestamp), 'dd/MM HH:mm:ss')}</p>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setPage((p) => p - 1)}
              disabled={page === 1}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

function FilterBtn({
  label,
  active,
  onClick,
}: {
  label: string
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        active
          ? 'bg-primary-600 text-white'
          : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
      }`}
    >
      {label}
    </button>
  )
}

function buildSeries(metrics: Metric[]): ChartSeries[] {
  const grouped = new Map<string, { time: string; value: number }[]>()

  for (const m of [...metrics].reverse()) {
    if (!grouped.has(m.name)) grouped.set(m.name, [])
    grouped.get(m.name)!.push({
      time: format(new Date(m.timestamp), 'HH:mm:ss'),
      value: m.value,
    })
  }

  return Array.from(grouped.entries()).map(([name, data]) => ({ name, data }))
}
