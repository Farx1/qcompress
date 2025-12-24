/**
 * Type definitions for QCompress API
 */

export interface ModelInfo {
  name: string
  description?: string
  parameters?: number
  size_mb?: number
}

export interface CompressionRequest {
  model_name: string
  compression_configs: Record<string, any>
  seed?: number
  device?: string
}

export interface CompressionResult {
  job_id: string
  model_name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  original_size: number
  compressed_size: number
  compression_ratio: number
  metrics?: CompressionMetrics
  error?: string
  timestamp?: string
}

export interface CompressionMetrics {
  timestamp: number
  layer_name: string
  original_params: number
  compressed_params: number
  compression_ratio: number
  rank: number
  in_modes: number[]
  out_modes: number[]
}

export interface CompressionStatus {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  message: string
}

export interface ChatRequest {
  prompt: string
  use_compressed?: boolean
  max_length?: number
  temperature?: number
  top_p?: number
}

export interface ChatResponse {
  response: string
  model_used: string
  generation_time: number
  tokens_generated: number
}

export interface TTCoreData {
  layer_name: string
  core_index: number
  shape: number[]
  rank: number
  data?: number[][]
}

export interface BenchmarkResult {
  model_name: string
  test_name: string
  original_time: number
  compressed_time: number
  speedup: number
  accuracy_drop: number
  timestamp: string
}

export interface WebSocketMessage {
  type: 'metrics' | 'status' | 'error' | 'complete'
  data?: any
  status?: string
  job_id?: string
  message?: string
  error?: string
}
