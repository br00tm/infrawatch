import { useCallback, useEffect, useState } from 'react'
import { alertsService } from '../services/alerts'
import { wsService } from '../services/websocket'
import { Alert, AlertStats, AlertStatus, PaginatedResponse } from '../types'

export function useAlerts(status?: AlertStatus, page = 1, pageSize = 20) {
  const [data, setData] = useState<PaginatedResponse<Alert>>({
    items: [],
    total: 0,
    page: 1,
    page_size: pageSize,
    total_pages: 0,
  })
  const [stats, setStats] = useState<AlertStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [alertsData, statsData] = await Promise.all([
        alertsService.list(status, page, pageSize),
        alertsService.getStats(),
      ])
      setData(alertsData)
      setStats(statsData)
    } catch (e) {
      setError('Failed to load alerts')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [status, page, pageSize])

  useEffect(() => {
    fetch()
  }, [fetch])

  // Live updates via WebSocket
  useEffect(() => {
    const handler = (newAlert: unknown) => {
      const alert = newAlert as Alert
      // Only prepend if matches current status filter
      if (!status || alert.status === status) {
        setData((prev) => ({
          ...prev,
          items: [alert, ...prev.items].slice(0, pageSize),
          total: prev.total + 1,
        }))
      }
      setStats((prev) =>
        prev ? { ...prev, total_active: prev.total_active + 1 } : prev
      )
    }
    wsService.on('alert', handler)
    return () => wsService.off('alert', handler)
  }, [status, pageSize])

  const acknowledge = useCallback(async (id: string) => {
    const updated = await alertsService.acknowledge(id)
    setData((prev) => ({
      ...prev,
      items: prev.items.map((a) => (a._id === id ? updated : a)),
    }))
    setStats((prev) =>
      prev
        ? { ...prev, total_active: Math.max(0, prev.total_active - 1), total_acknowledged: prev.total_acknowledged + 1 }
        : prev
    )
  }, [])

  const resolve = useCallback(async (id: string) => {
    const updated = await alertsService.resolve(id)
    setData((prev) => ({
      ...prev,
      items: prev.items.map((a) => (a._id === id ? updated : a)),
    }))
  }, [])

  return { ...data, stats, loading, error, refetch: fetch, acknowledge, resolve }
}
