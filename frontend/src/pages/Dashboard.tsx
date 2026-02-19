import {
  ChartBarIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import Card, { CardHeader } from '../components/common/Card'

const stats = [
  {
    name: 'Total Metrics',
    value: '12,543',
    change: '+12%',
    changeType: 'positive',
    icon: ChartBarIcon,
  },
  {
    name: 'Active Pods',
    value: '48',
    change: '+3',
    changeType: 'positive',
    icon: CpuChipIcon,
  },
  {
    name: 'Log Entries',
    value: '1.2M',
    change: '+8%',
    changeType: 'neutral',
    icon: DocumentTextIcon,
  },
  {
    name: 'Active Alerts',
    value: '7',
    change: '+2',
    changeType: 'negative',
    icon: ExclamationTriangleIcon,
  },
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Overview of your infrastructure monitoring
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-primary-50 dark:bg-primary-900/20">
                <stat.icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {stat.name}
                </p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                  <span
                    className={`ml-2 text-sm font-medium ${
                      stat.changeType === 'positive'
                        ? 'text-green-600'
                        : stat.changeType === 'negative'
                          ? 'text-red-600'
                          : 'text-gray-500'
                    }`}
                  >
                    {stat.change}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="CPU Usage" subtitle="Last 24 hours" />
          <div className="h-64 flex items-center justify-center text-gray-400">
            Chart placeholder - Integrate Recharts
          </div>
        </Card>

        <Card>
          <CardHeader title="Memory Usage" subtitle="Last 24 hours" />
          <div className="h-64 flex items-center justify-center text-gray-400">
            Chart placeholder - Integrate Recharts
          </div>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card>
        <CardHeader title="Recent Alerts" subtitle="Latest 5 alerts" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-dark-bg"
            >
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-yellow-500 mr-3" />
                <div>
                  <p className="text-sm font-medium">High CPU Usage on pod-{i}</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                Warning
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
