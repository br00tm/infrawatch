import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import Modal from '../components/common/Modal'
import { alertsService } from '../services/alerts'
import { Alert, AlertCreate, AlertSeverity, AlertStats, AlertStatus } from '../types'
import { ALERT_SEVERITY_COLORS, ALERT_STATUS_COLORS } from '../utils/constants'

const PAGE_SIZE = 20

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [total, setTotal] = useState(0)
  const [stats, setStats] = useState<AlertStats | null>(null)
  const [selectedStatus, setSelectedStatus] = useState<AlertStatus | 'all'>('all')
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [showCreateModal, setShowCreateModal] = useState(false)

  async function fetchAlerts() {
    setLoading(true)
    try {
      const statusParam = selectedStatus !== 'all' ? selectedStatus : undefined
      const [alertsData, statsData] = await Promise.all([
        alertsService.list(statusParam, page, PAGE_SIZE),
        alertsService.getStats(),
      ])
      setAlerts(alertsData.items)
      setTotal(alertsData.total)
      setStats(statsData)
    } catch (err) {
      console.error('Failed to load alerts', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [selectedStatus, page])

  async function handleAcknowledge(id: string) {
    try {
      const updated = await alertsService.acknowledge(id)
      setAlerts((prev) => prev.map((a) => (a._id === id ? updated : a)))
      setStats((prev) =>
        prev
          ? { ...prev, total_active: Math.max(0, prev.total_active - 1), total_acknowledged: prev.total_acknowledged + 1 }
          : prev
      )
      toast.success('Alert acknowledged')
    } catch {
      toast.error('Failed to acknowledge alert')
    }
  }

  async function handleResolve(id: string) {
    try {
      const updated = await alertsService.resolve(id)
      setAlerts((prev) => prev.map((a) => (a._id === id ? updated : a)))
      toast.success('Alert resolved')
    } catch {
      toast.error('Failed to resolve alert')
    }
  }

  async function handleCreate(data: AlertCreate) {
    try {
      const newAlert = await alertsService.create(data)
      setAlerts((prev) => [newAlert, ...prev])
      setTotal((t) => t + 1)
      setStats((prev) => prev ? { ...prev, total_active: prev.total_active + 1 } : prev)
      toast.success('Alert created')
      setShowCreateModal(false)
    } catch {
      toast.error('Failed to create alert')
    }
  }

  function handleStatusChange(status: AlertStatus | 'all') {
    setSelectedStatus(status)
    setPage(1)
  }

  const statuses: (AlertStatus | 'all')[] = ['all', 'active', 'acknowledged', 'resolved', 'silenced']
  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Alerts</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor and manage infrastructure alerts
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>Create Alert</Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-red-600">{stats ? stats.total_active : '—'}</p>
            <p className="text-sm text-gray-500">Active</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-yellow-600">{stats ? stats.total_acknowledged : '—'}</p>
            <p className="text-sm text-gray-500">Acknowledged</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{stats ? stats.total_resolved : '—'}</p>
            <p className="text-sm text-gray-500">Resolved</p>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-2">
          {statuses.map((status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
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
      {loading ? (
        <div className="py-16 text-center text-gray-400">Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <Card>
          <div className="py-12 text-center text-gray-400">
            <p className="text-lg font-medium">No alerts found</p>
            <p className="text-sm mt-1">Your infrastructure is running smoothly.</p>
          </div>
        </Card>
      ) : (
        <Card padding="none">
          <div className="divide-y divide-gray-200 dark:divide-dark-border">
            {alerts.map((alert) => (
              <div
                key={alert._id}
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
                    {alert.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">{alert.description}</p>
                    )}
                    <p className="text-sm text-gray-500">
                      {alert.source} • {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${
                      ALERT_STATUS_COLORS[alert.status as AlertStatus]
                    }`}
                  >
                    {alert.status}
                  </span>
                  {alert.status === 'active' && (
                    <Button size="sm" variant="secondary" onClick={() => handleAcknowledge(alert._id)}>
                      Acknowledge
                    </Button>
                  )}
                  {(alert.status === 'active' || alert.status === 'acknowledged') && (
                    <Button size="sm" variant="secondary" onClick={() => handleResolve(alert._id)}>
                      Resolve
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => setPage((p) => p - 1)} disabled={page === 1}>
              Previous
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setPage((p) => p + 1)} disabled={page === totalPages}>
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Create Alert Modal */}
      <CreateAlertModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreate}
      />
    </div>
  )
}

// ── Create Alert Modal ────────────────────────────────────────────────────────

function CreateAlertModal({
  isOpen,
  onClose,
  onCreate,
}: {
  isOpen: boolean
  onClose: () => void
  onCreate: (data: AlertCreate) => Promise<void>
}) {
  const [form, setForm] = useState<AlertCreate>({
    title: '',
    source: '',
    severity: 'warning',
    description: '',
  })
  const [submitting, setSubmitting] = useState(false)

  function handleChange(field: keyof AlertCreate, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.title.trim() || !form.source.trim()) return
    setSubmitting(true)
    try {
      await onCreate(form)
      setForm({ title: '', source: '', severity: 'warning', description: '' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Alert">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title"
          required
          placeholder="e.g. High CPU Usage"
          value={form.title}
          onChange={(e) => handleChange('title', e.target.value)}
        />
        <Input
          label="Source"
          required
          placeholder="e.g. node-1, api-pod"
          value={form.source}
          onChange={(e) => handleChange('source', e.target.value)}
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Severity
          </label>
          <select
            value={form.severity}
            onChange={(e) => handleChange('severity', e.target.value)}
            className="w-full rounded-lg border border-gray-300 dark:border-dark-border bg-white dark:bg-dark-bg text-gray-900 dark:text-white px-3 py-2 text-sm"
          >
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <Input
          label="Description (optional)"
          placeholder="Brief description of the alert"
          value={form.description ?? ''}
          onChange={(e) => handleChange('description', e.target.value)}
        />
        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={submitting || !form.title || !form.source}>
            {submitting ? 'Creating...' : 'Create Alert'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
