import { useCallback, useEffect, useState } from 'react'
import { logsService } from '../services/logs'
import { Log, LogQuery, PaginatedResponse } from '../types'

export function useLogs(query: LogQuery = {}, page = 1, pageSize = 50) {
  const [data, setData] = useState<PaginatedResponse<Log>>({
    items: [],
    total: 0,
    page: 1,
    page_size: pageSize,
    total_pages: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await logsService.list(query, page, pageSize)
      setData(result)
    } catch (e) {
      setError('Failed to load logs')
      console.error(e)
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, JSON.stringify(query)])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { ...data, loading, error, refetch: fetch }
}
