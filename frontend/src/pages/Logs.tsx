import { useEffect, useState, useCallback } from 'react'
import Card from '../components/common/Card'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { logsService } from '../services/logs'
import { Log, LogLevel } from '../types'
import { LOG_LEVEL_COLORS } from '../utils/constants'

const PAGE_SIZE = 50

export default function Logs() {
  const [logs, setLogs] = useState<Log[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<LogLevel | 'all'>('all')
  const [page, setPage] = useState(1)

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    try {
      const query = {
        ...(selectedLevel !== 'all' ? { level: selectedLevel } : {}),
        ...(search.trim() ? { search: search.trim() } : {}),
      }
      const data = await logsService.list(query, page, PAGE_SIZE)
      setLogs(data.items)
      setTotal(data.total)
    } catch (err) {
      console.error('Failed to load logs', err)
    } finally {
      setLoading(false)
    }
  }, [selectedLevel, page])

  useEffect(() => {
    const debounce = setTimeout(() => fetchLogs(), search ? 400 : 0)
    return () => clearTimeout(debounce)
  }, [fetchLogs, search])

  function handleLevelChange(level: LogLevel | 'all') {
    setSelectedLevel(level)
    setPage(1)
  }

  function handleSearch(value: string) {
    setSearch(value)
    setPage(1)
  }

  const levels: (LogLevel | 'all')[] = ['all', 'debug', 'info', 'warning', 'error', 'critical']
  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-6">
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
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {levels.map((level) => (
              <button
                key={level}
                onClick={() => handleLevelChange(level)}
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
      {loading ? (
        <div className="py-16 text-center text-gray-400">Loading logs...</div>
      ) : logs.length === 0 ? (
        <Card>
          <div className="py-12 text-center text-gray-400">
            <p className="text-lg font-medium">No logs found</p>
            <p className="text-sm mt-1">
              Send logs to the API at <code className="font-mono">POST /api/v1/logs</code>
            </p>
          </div>
        </Card>
      ) : (
        <Card padding="none">
          <div className="divide-y divide-gray-200 dark:divide-dark-border">
            {logs.map((log) => (
              <div key={log._id} className="p-4 hover:bg-gray-50 dark:hover:bg-dark-border">
                <div className="flex items-start gap-4">
                  <span
                    className={`mt-0.5 px-2 py-0.5 text-xs font-medium rounded uppercase whitespace-nowrap ${
                      LOG_LEVEL_COLORS[log.level as LogLevel]
                    }`}
                  >
                    {log.level}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white font-mono break-all">
                      {log.message}
                    </p>
                    <div className="mt-1 flex flex-wrap items-center gap-4 text-xs text-gray-500">
                      <span>Source: {log.source}</span>
                      {log.namespace && <span>NS: {log.namespace}</span>}
                      {log.pod_name && <span>Pod: {log.pod_name}</span>}
                      <span>{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">
          {loading ? '...' : `Showing ${logs.length} of ${total} logs`}
        </span>
        {totalPages > 1 && (
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1 || loading}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages || loading}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
