/**
 * WebSocket client for real-time compression monitoring
 */

import type { WebSocketMessage } from './types'

const WS_BASE_URL = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000').replace(/^http/, 'ws')

type MessageHandler = (message: WebSocketMessage) => void
type ErrorHandler = (error: Event) => void
type OpenHandler = () => void
type CloseHandler = () => void

export class CompressionWebSocket {
  private ws: WebSocket | null = null
  private jobId: string
  private messageHandlers: MessageHandler[] = []
  private errorHandlers: ErrorHandler[] = []
  private openHandlers: OpenHandler[] = []
  private closeHandlers: CloseHandler[] = []
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private isManuallyClosed = false

  constructor(jobId: string) {
    this.jobId = jobId
    this.connect()
  }

  private connect(): void {
    try {
      const url = `${WS_BASE_URL}/ws/compression/${this.jobId}`
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log(`WebSocket connected to job ${this.jobId}`)
        this.reconnectAttempts = 0
        this.openHandlers.forEach((handler) => handler())
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.messageHandlers.forEach((handler) => handler(message))
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.errorHandlers.forEach((handler) => handler(error))
      }

      this.ws.onclose = () => {
        console.log(`WebSocket disconnected from job ${this.jobId}`)
        this.closeHandlers.forEach((handler) => handler())

        // Attempt to reconnect if not manually closed
        if (!this.isManuallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
          console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
          setTimeout(() => this.connect(), delay)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.errorHandlers.forEach((handler) => handler(error as Event))
    }
  }

  onMessage(handler: MessageHandler): void {
    this.messageHandlers.push(handler)
  }

  onError(handler: ErrorHandler): void {
    this.errorHandlers.push(handler)
  }

  onOpen(handler: OpenHandler): void {
    this.openHandlers.push(handler)
  }

  onClose(handler: CloseHandler): void {
    this.closeHandlers.push(handler)
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not open')
    }
  }

  disconnect(): void {
    this.isManuallyClosed = true
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}
