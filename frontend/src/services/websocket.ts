import { Message } from '../types/api'

class WebSocketService {
  private socket: WebSocket | null = null
  private messageHandlers: ((message: Message) => void)[] = []
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 1000
  private heartbeatInterval: number | null = null
  private clientId: string = this.generateClientId()

  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/api/v1/chat/ws'
    const fullUrl = `${wsUrl}/${this.clientId}`
    
    this.socket = new WebSocket(fullUrl)

    this.socket.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }

    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason)
      this.stopHeartbeat()
      
      // Implement exponential backoff for reconnection
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts)
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`)
        
        setTimeout(() => {
          this.reconnectAttempts++
          this.connect()
        }, delay)
      } else {
        console.error('Max reconnection attempts reached')
      }
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        // Handle heartbeat ping messages
        if (data.type === 'ping') {
          this.sendPong()
          return
        }
        
        // Handle regular messages
        const message: Message = data as Message
        this.messageHandlers.forEach((handler) => handler(message))
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.socket) {
      this.socket.close(1000, 'Manual disconnect')
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
  
  private startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatInterval = window.setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // 30 seconds
  }
  
  private stopHeartbeat() {
    if (this.heartbeatInterval !== null) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }
  
  private sendPong() {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type: 'pong' }))
    }
  }
  
  getClientId() {
    return this.clientId
  }
}

export const websocketService = new WebSocketService()
