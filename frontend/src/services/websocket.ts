import { Message } from '../types/api'

class WebSocketService {
  private socket: WebSocket | null = null
  private messageHandlers: ((message: Message) => void)[] = []

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return

    this.socket = new WebSocket(import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/chat/ws')

    this.socket.onopen = () => {
      console.log('WebSocket connected')
    }

    this.socket.onclose = () => {
      console.log('WebSocket disconnected')
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.socket.onmessage = (event) => {
      const message: Message = JSON.parse(event.data)
      this.messageHandlers.forEach((handler) => handler(message))
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  subscribeToMessages(handler: (message: Message) => void) {
    this.messageHandlers.push(handler)
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler)
    }
  }

  sendMessage(content: string) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }
    this.socket.send(JSON.stringify({ content }))
  }
}

export const websocketService = new WebSocketService() 