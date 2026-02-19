import { useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { wsService } from '../services/websocket'

/**
 * Connects the WebSocket when the user is logged in,
 * disconnects on logout. Import this once at the top-level layout.
 */
export function useWebSocket() {
  const tokens = useAuthStore((s) => s.tokens)

  useEffect(() => {
    if (tokens?.access_token) {
      wsService.connect()
    } else {
      wsService.disconnect()
    }

    return () => {
      // Don't disconnect on re-renders — only on logout
    }
  }, [tokens?.access_token])

  return wsService
}
