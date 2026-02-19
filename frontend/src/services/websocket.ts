type EventCallback = (data: unknown) => void

class WebSocketService {
  private socket: WebSocket | null = null
  private listeners: Map<string, Set<EventCallback>> = new Map()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectDelay = 3000

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`

    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      console.info('[WS] Connected')
      this.reconnectDelay = 3000
    }

    this.socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as { type: string; data: unknown }
        const callbacks = this.listeners.get(msg.type)
        callbacks?.forEach((cb) => cb(msg.data))
      } catch {
        // ignore malformed messages
      }
    }

    this.socket.onclose = () => {
      console.info('[WS] Disconnected, reconnecting...')
      this.scheduleReconnect()
    }

    this.socket.onerror = () => {
      this.socket?.close()
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.socket?.close()
    this.socket = null
  }

  on(event: string, callback: EventCallback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: EventCallback) {
    this.listeners.get(event)?.delete(callback)
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => {
      this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000)
      this.connect()
    }, this.reconnectDelay)
  }
}

export const wsService = new WebSocketService()
