import { useEffect, useState } from 'react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  ChartBarIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import Card, { CardHeader } from '../components/common/Card'
import { alertsService } from '../services/alerts'
import { metricsService } from '../services/metrics'
import { logsService } from '../services/logs'
import { Alert, AlertSeverity, AlertStats, AlertStatus, Metric } from '../types'
import { ALERT_SEVERITY_COLORS, ALERT_STATUS_COLORS } from '../utils/constants'
import { format } from 'date-fns'

interface DashboardCounts {
  totalMetrics: number
  totalLogs: number
}

interface ChartPoint {
  time: string
  cpu?: number
  memory?: number
}

export default function Dashboard() {
  const [counts, setCounts] = useState<DashboardCounts>({ totalMetrics: 0, totalLogs: 0 })
  const [alertStats, setAlertStats] = useState<AlertStats | null>(null)
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [chartData, setChartData] = useState<ChartPoint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [metricsPage, logsStats, stats, activeAlerts, cpuMetrics, memMetrics] =
          await Promise.all([
            metricsService.list({}, 1, 1),
            logsService.getStats(),
            alertsService.getStats(),
            alertsService.list('active' as AlertStatus, 1, 5),
            metricsService.list({ metric_type: 'cpu', name: 'cpu_usage' }, 1, 20),
            metricsService.list({ metric_type: 'memory', name: 'memory_usage' }, 1, 20),
          ])

        setCounts({ totalMetrics: metricsPage.total, totalLogs: logsStats.total_count })
        setAlertStats(stats)
        setRecentAlerts(activeAlerts.items)
        setChartData(buildChartData(cpuMetrics.items, memMetrics.items))
      } catch (err) {
        console.error('Failed to load dashboard', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Overview of your infrastructure monitoring
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          name="Total Metrics"
          value={loading ? '...' : counts.totalMetrics.toLocaleString()}
          icon={ChartBarIcon}
        />
        <StatCard
          name="Total Logs"
          value={loading ? '...' : counts.totalLogs.toLocaleString()}
          icon={DocumentTextIcon}
        />
        <StatCard
          name="Active Alerts"
          value={loading ? '...' : (alertStats?.total_active ?? 0).toString()}
          icon={ExclamationTriangleIcon}
          danger={!!alertStats && alertStats.total_active > 0}
        />
        <StatCard
          name="Resolved"
          value={loading ? '...' : (alertStats?.total_resolved ?? 0).toString()}
          icon={CpuChipIcon}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="CPU Usage" subtitle="Last 20 data points" />
          {chartData.length === 0 ? (
            <EmptyChart message="No CPU metrics yet" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} unit="%" tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, 'CPU']} />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  stroke="#6366f1"
                  fill="url(#cpuGradient)"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Memory Usage" subtitle="Last 20 data points" />
          {chartData.length === 0 ? (
            <EmptyChart message="No memory metrics yet" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} unit="%" tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, 'Memory']} />
                <Area
                  type="monotone"
                  dataKey="memory"
                  stroke="#10b981"
                  fill="url(#memGradient)"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {/* Recent Active Alerts */}
      <Card>
        <CardHeader
          title="Active Alerts"
          subtitle={
            !loading && recentAlerts.length === 0
              ? 'No active alerts'
              : 'Latest active alerts'
          }
        />
        {loading ? (
          <div className="py-8 text-center text-gray-400 text-sm">Loading...</div>
        ) : recentAlerts.length === 0 ? (
          <div className="py-8 text-center text-gray-400 text-sm">
            No active alerts. Your infrastructure is healthy.
          </div>
        ) : (
          <div className="space-y-3">
            {recentAlerts.map((alert) => (
              <div
                key={alert._id}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-dark-bg"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2 py-0.5 text-xs font-medium rounded-full capitalize ${
                      ALERT_SEVERITY_COLORS[alert.severity as AlertSeverity]
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {alert.title}
                    </p>
                    <p className="text-xs text-gray-500">
                      {alert.source} • {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${
                    ALERT_STATUS_COLORS[alert.status as AlertStatus]
                  }`}
                >
                  {alert.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

// ── helpers ──────────────────────────────────────────────────────────────────

function buildChartData(cpuMetrics: Metric[], memMetrics: Metric[]): ChartPoint[] {
  // Create a time-keyed map merging both series
  const map = new Map<string, ChartPoint>()

  for (const m of [...cpuMetrics].reverse()) {
    const key = format(new Date(m.timestamp), 'HH:mm:ss')
    const entry = map.get(key) ?? { time: key }
    entry.cpu = m.value
    map.set(key, entry)
  }
  for (const m of [...memMetrics].reverse()) {
    const key = format(new Date(m.timestamp), 'HH:mm:ss')
    const entry = map.get(key) ?? { time: key }
    entry.memory = m.value
    map.set(key, entry)
  }

  return Array.from(map.values())
}

function StatCard({
  name,
  value,
  icon: Icon,
  danger = false,
}: {
  name: string
  value: string
  icon: React.ElementType
  danger?: boolean
}) {
  return (
    <Card>
      <div className="flex items-center">
        <div
          className={`p-3 rounded-lg ${
            danger
              ? 'bg-red-50 dark:bg-red-900/20'
              : 'bg-primary-50 dark:bg-primary-900/20'
          }`}
        >
          <Icon
            className={`h-6 w-6 ${
              danger ? 'text-red-600 dark:text-red-400' : 'text-primary-600 dark:text-primary-400'
            }`}
          />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{name}</p>
          <p
            className={`text-2xl font-semibold ${
              danger ? 'text-red-600' : 'text-gray-900 dark:text-white'
            }`}
          >
            {value}
          </p>
        </div>
      </div>
    </Card>
  )
}

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="h-[220px] flex items-center justify-center text-sm text-gray-400">
      {message} — send metrics via <code className="mx-1 font-mono">POST /api/v1/metrics</code>
    </div>
  )
}
