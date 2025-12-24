'use client'

import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, Eye, BarChart3, Wifi, WifiOff, StopCircle, Sparkles, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { CompressionWebSocket } from '@/lib/websocket'
import MetricsChart from './MetricsChart'
import BenchmarkDashboard from './BenchmarkDashboard'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { ExportDialog } from './ExportDialog'
import { Download } from 'lucide-react'
import type { CompressionRequest, CompressionResult, CompressionMetrics, TTCoreData, BenchmarkResult } from '@/lib/types'

const TTCoreVisualization = dynamic(() => import('./TTCoreVisualization'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-64 text-white/60">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-quantum-purple-500"></div>
    </div>
  ),
})

type MonitorTab = 'monitor' | 'visualization' | 'benchmark'

interface CompressionMonitorProps {
  initialTab?: MonitorTab
}

export default function CompressionMonitor({ initialTab = 'monitor' }: CompressionMonitorProps) {
  const [modelName, setModelName] = useState('distilgpt2')
  const [compressionConfigs, setCompressionConfigs] = useState<Record<string, any>>({
    lm_head: {
      in_modes: [768],
      out_modes: [50257],
      ranks: [1, 1],
    },
  })

  const [currentJob, setCurrentJob] = useState<string | null>(null)
  const [metrics, setMetrics] = useState<CompressionMetrics[]>([])
  const [result, setResult] = useState<CompressionResult | null>(null)
  const [ws, setWs] = useState<CompressionWebSocket | null>(null)
  const [ttCores, setTTCores] = useState<TTCoreData[]>([])
  const [benchmarkResults, setBenchmarkResults] = useState<BenchmarkResult[]>([])
  const [activeTab, setActiveTab] = useState<MonitorTab>(initialTab)
  const [error, setError] = useState<string | null>(null)
  const [isCompressing, setIsCompressing] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const wsRef = useRef<CompressionWebSocket | null>(null)

  useEffect(() => {
    setActiveTab(initialTab)
  }, [initialTab])

  useEffect(() => {
    if (!currentJob) {
      if (wsRef.current) {
        wsRef.current.disconnect()
        wsRef.current = null
        setWs(null)
        setWsConnected(false)
      }
      return
    }

    if (wsRef.current) {
      wsRef.current.disconnect()
      wsRef.current = null
    }

    const websocket = new CompressionWebSocket(currentJob)
    websocket.onMessage((message) => {
      switch (message.type) {
        case 'metrics':
          setMetrics((prev) => [...prev, message.data])
          break
        case 'status':
          if (message.status === 'completed') {
            setIsCompressing(false)
            apiClient.getJobResults(message.job_id).then((result) => {
              setResult(result)
            }).catch((error) => {
              console.error('Failed to fetch job results:', error)
            })
          } else if (message.status === 'running') {
            setIsCompressing(true)
          }
          break
        case 'tt_core_data':
          setTTCores((prev) => [...prev, message.data])
          break
        case 'benchmark_result':
          setBenchmarkResults((prev) => [...prev, message.data])
          break
        case 'error':
          console.error('WebSocket error:', message.error)
          setError(message.error || 'A WebSocket error occurred')
          setIsCompressing(false)
          break
      }
    })

    websocket.onError(() => {
      setError('WebSocket connection error')
      setIsCompressing(false)
      setWsConnected(false)
    })

    websocket.onOpen(() => {
      setWsConnected(true)
    })

    websocket.onClose(() => {
      setWsConnected(false)
    })

    wsRef.current = websocket
    setWs(websocket)

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect()
        wsRef.current = null
        setWsConnected(false)
      }
    }
  }, [currentJob])

  const handleStartCompression = async () => {
    if (!modelName.trim()) return

    setIsCompressing(true)
    setError(null)
    setMetrics([])
    setResult(null)
    setTTCores([])
    setBenchmarkResults([])

    try {
      const request: CompressionRequest = {
        model_name: modelName,
        compression_ratio: 0.5,
        target_rank: 10,
        penalty_weight: 0.1,
      }

      const response = await apiClient.startCompression(request)
      setCurrentJob(response.job_id)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start compression'
      setError(message)
      setIsCompressing(false)
    }
  }

  const handleStopCompression = () => {
    if (currentJob) {
      setCurrentJob(null)
      setIsCompressing(false)
    }
  }

  const modelOptions = [
    { value: 'distilgpt2', label: 'DistilGPT-2 (recommended)' },
    { value: 'gpt2', label: 'GPT-2' },
    { value: 'microsoft/DialoGPT-small', label: 'DialoGPT-small' },
  ]

  const latestMetrics = metrics[metrics.length - 1]
  const compressionProgress = latestMetrics
    ? (latestMetrics.step / (latestMetrics.total_steps || 100)) * 100
    : 0

  return (
    <div className="w-full space-y-6">
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as MonitorTab)}>
        <TabsList className="w-full justify-start">
          <TabsTrigger value="monitor">
            <Activity className="h-4 w-4 mr-2" />
            Monitoring
          </TabsTrigger>
          <TabsTrigger value="visualization">
            <Eye className="h-4 w-4 mr-2" />
            Visualization
          </TabsTrigger>
          <TabsTrigger value="benchmark">
            <BarChart3 className="h-4 w-4 mr-2" />
            Benchmark
          </TabsTrigger>
        </TabsList>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-4"
            >
              <Card className="border-destructive/50 bg-destructive/10">
                <CardContent className="pt-6">
                  <p className="text-destructive text-sm font-medium">{error}</p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        <TabsContent value="monitor" className="space-y-6 mt-6">
          {!currentJob && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Start Compression</CardTitle>
                  <CardDescription>Select a model and start the compression process</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Select a model</Label>
                    <Select value={modelName} onValueChange={setModelName}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a model" />
                      </SelectTrigger>
                      <SelectContent>
                        {modelOptions.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button
                    onClick={handleStartCompression}
                    disabled={!modelName.trim() || isCompressing}
                    className="w-full"
                  >
                    {isCompressing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Compression running...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Start Compression
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {currentJob && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Job Info Card */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <CardTitle className="text-base">Job ID: {currentJob.slice(0, 8)}...</CardTitle>
                        {wsConnected ? (
                          <Badge variant="default" className="bg-quantum-emerald-500/20 text-quantum-emerald-300 border-quantum-emerald-500/30">
                            <Wifi className="h-3 w-3 mr-1" />
                            Connected
                          </Badge>
                        ) : (
                          <Badge variant="destructive">
                            <WifiOff className="h-3 w-3 mr-1" />
                            Disconnected
                          </Badge>
                        )}
                      </div>
                      <CardDescription>
                        {isCompressing ? (
                          <span className="flex items-center gap-2">
                            <motion.span
                              className="h-2 w-2 bg-quantum-emerald-400 rounded-full"
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ repeat: Infinity, duration: 1 }}
                            />
                            Compression in progress
                          </span>
                        ) : result ? (
                          `Status: ${result.status}`
                        ) : (
                          'Initializing...'
                        )}
                      </CardDescription>
                    </div>
                    {result && (
                      <div className="text-right">
                        <div className="text-xs text-white/70 mb-1">Compression Ratio</div>
                        <div className="text-2xl font-bold text-quantum-emerald-400">
                          {(result.compression_ratio * 100).toFixed(1)}%
                        </div>
                      </div>
                    )}
                  </div>
                </CardHeader>

                {isCompressing && (
                  <CardContent>
                    <div className="mb-4">
                      <div className="flex justify-between text-xs text-white/60 mb-2">
                        <span>Progress</span>
                        <span>{Math.round(compressionProgress)}%</span>
                      </div>
                      <Progress value={compressionProgress} />
                    </div>
                  </CardContent>
                )}

                {/* Metrics Grid */}
                {result && (
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <Card className="border-border bg-card">
                        <CardContent className="pt-6">
                          <p className="text-xs text-muted-foreground mb-1">Original Size</p>
                          <p className="text-lg font-semibold">
                            {(result.original_size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </CardContent>
                      </Card>
                      <Card className="border-border bg-card">
                        <CardContent className="pt-6">
                          <p className="text-xs text-muted-foreground mb-1">Compressed Size</p>
                          <p className="text-lg font-semibold">
                            {(result.compressed_size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </CardContent>
                      </Card>
                      <Card className="border-quantum-emerald-500/30 bg-quantum-emerald-500/10">
                        <CardContent className="pt-6">
                          <p className="text-xs text-muted-foreground mb-1">Speed Gain</p>
                          <p className="text-lg font-semibold text-quantum-emerald-400">
                            {(result.speed_gain * 100).toFixed(1)}%
                          </p>
                        </CardContent>
                      </Card>
                      <Card className="border-quantum-cyan-500/30 bg-quantum-cyan-500/10">
                        <CardContent className="pt-6">
                          <p className="text-xs text-muted-foreground mb-1">Quality Loss</p>
                          <p className="text-lg font-semibold text-quantum-cyan-400">
                            {(result.quality_loss * 100).toFixed(2)}%
                          </p>
                        </CardContent>
                      </Card>
                    </div>
                  </CardContent>
                )}

                <CardContent>
                  <div className="flex gap-3">
                    {result && (
                      <Button
                        onClick={() => setShowExportDialog(true)}
                        className="flex-1"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Export Model
                      </Button>
                    )}
                    <Button
                      variant="destructive"
                      onClick={handleStopCompression}
                      className={result && result.status === 'completed' ? 'flex-1' : 'w-full'}
                    >
                      <StopCircle className="h-4 w-4 mr-2" />
                      Stop Compression
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Metrics Chart */}
              {metrics.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Real-time Metrics</CardTitle>
                    <CardDescription>Live compression progress and statistics</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <MetricsChart metrics={metrics} />
                  </CardContent>
                </Card>
              )}
            </motion.div>
          )}
        </TabsContent>

        <TabsContent value="visualization" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>TT Cores Visualization</CardTitle>
              <CardDescription>Tensor-Train core structure visualization</CardDescription>
            </CardHeader>
            <CardContent>
              {ttCores.length > 0 ? (
                <TTCoreVisualization cores={ttCores} />
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                  <div className="text-center">
                    <Eye className="h-12 w-12 mx-auto mb-4 text-muted-foreground/20" />
                    <p>No visualization data available</p>
                    <p className="text-sm text-muted-foreground/60 mt-2">Start a compression job to see visualization</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="benchmark" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Benchmark Results</CardTitle>
              <CardDescription>Performance benchmarks for compressed models</CardDescription>
            </CardHeader>
            <CardContent>
              {benchmarkResults.length > 0 ? (
                <BenchmarkDashboard results={benchmarkResults} />
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground/20" />
                    <p>No benchmark data available</p>
                    <p className="text-sm text-muted-foreground/60 mt-2">Run benchmarks to see results</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Export Dialog */}
      {result && currentJob && (
        <ExportDialog
          isOpen={showExportDialog}
          onClose={() => setShowExportDialog(false)}
          jobId={currentJob}
          modelName={modelName}
          compressionRatio={result.compression_ratio || 0}
        />
      )}
    </div>
  )
}
