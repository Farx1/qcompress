/**
 * API client for QCompress backend
 */

import { toast } from 'sonner'
import type {
  ModelInfo,
  CompressionRequest,
  CompressionResult,
  CompressionStatus,
  ChatRequest,
  ChatResponse,
} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    }

    if (data) {
      options.body = JSON.stringify(data)
    }

    try {
      const response = await fetch(url, options)

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        const errorMessage = error.detail || `API error: ${response.status} ${response.statusText}`
        toast.error('API Error', {
          description: errorMessage,
        })
        throw new Error(errorMessage)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${method} ${endpoint}`, error)
      throw error
    }
  }

  /**
   * Get list of available models
   */
  async getModels(): Promise<ModelInfo[]> {
    return this.request<ModelInfo[]>('GET', '/api/models')
  }

  /**
   * Start a compression job
   */
  async startCompression(
    request: CompressionRequest
  ): Promise<CompressionResult> {
    return this.request<CompressionResult>('POST', '/api/compress', request)
  }

  /**
   * Get compression job status
   */
  async getJobStatus(jobId: string): Promise<CompressionStatus> {
    return this.request<CompressionStatus>('GET', `/api/jobs/${jobId}`)
  }

  /**
   * Get compression job results
   */
  async getJobResults(jobId: string): Promise<CompressionResult> {
    return this.request<CompressionResult>('GET', `/api/jobs/${jobId}/results`)
  }

  /**
   * Cancel a compression job
   */
  async cancelJob(jobId: string): Promise<void> {
    return this.request<void>('POST', `/api/jobs/${jobId}/cancel`)
  }

  /**
   * Send a chat message
   */
  async chat(prompt: string, options?: Partial<ChatRequest>): Promise<ChatResponse> {
    const request: ChatRequest = {
      prompt,
      use_compressed: options?.use_compressed ?? false,
      max_length: options?.max_length ?? 100,
      temperature: options?.temperature ?? 0.7,
      top_p: options?.top_p ?? 1.0,
    }
    return this.request<ChatResponse>('POST', '/api/chat', request)
  }

  /**
   * Get benchmark results
   */
  async getBenchmarks(): Promise<any[]> {
    return this.request<any[]>('GET', '/api/benchmarks')
  }

  /**
   * Run a benchmark
   */
  async runBenchmark(modelName: string): Promise<any> {
    return this.request<any>('POST', '/api/benchmarks', { model_name: modelName })
  }

  /**
   * Get health status
   */
  async getHealth(): Promise<any> {
    return this.request<any>('GET', '/health')
  }

  /**
   * Export model to PyTorch format
   */
  async exportModel(jobId: string, format: 'pytorch' | 'safetensors' | 'onnx'): Promise<Blob> {
    const url = `${this.baseUrl}/api/jobs/${jobId}/export/${format}`
    const response = await fetch(url)
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `Export failed: ${response.statusText}`)
    }
    
    return await response.blob()
  }

  /**
   * Get export metadata
   */
  async getExportMetadata(jobId: string): Promise<any> {
    return this.request<any>('GET', `/api/jobs/${jobId}/export/metadata`)
  }
}

export const apiClient = new APIClient()
