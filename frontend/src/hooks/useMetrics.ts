import { useCallback, useEffect, useRef, useState } from 'react'
import { metricsService } from '../services/metrics'
import { wsService } from '../services/websocket'
import { Metric, MetricQuery, PaginatedResponse } from '../types'

export function useMetrics(query: MetricQuery = {}, page = 1, pageSize = 20) {
  const [data, setData] = useState<PaginatedResponse<Metric>>({
    items: [],
    total: 0,
    page: 1,
    page_size: pageSize,
    total_pages: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const queryRef = useRef(query)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await metricsService.list(queryRef.current, page, pageSize)
      setData(result)
    } catch (e) {
      setError('Failed to load metrics')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize])

  useEffect(() => {
    queryRef.current = query
  })

  useEffect(() => {
    fetch()
  }, [fetch])

  // Live updates via WebSocket
  useEffect(() => {
    const handler = (newMetric: unknown) => {
      setData((prev) => ({
        ...prev,
        items: [newMetric as Metric, ...prev.items].slice(0, pageSize),
        total: prev.total + 1,
      }))
    }
    wsService.on('metric', handler)
    return () => wsService.off('metric', handler)
  }, [pageSize])

  return { ...data, loading, error, refetch: fetch }
}
