'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Download, Loader2, Check, FileDown, AlertCircle } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { apiClient } from '@/lib/api'

interface ExportDialogProps {
  isOpen: boolean
  onClose: () => void
  jobId: string
  modelName?: string
  compressionRatio?: number
}

type ExportFormat = 'pytorch' | 'safetensors' | 'onnx'

interface ExportStatus {
  format: ExportFormat
  status: 'idle' | 'exporting' | 'success' | 'error'
  progress: number
  error?: string
  downloadUrl?: string
}

const formatInfo = {
  pytorch: {
    name: 'PyTorch',
    description: 'Native PyTorch format (.pt)',
    icon: '🔥',
    extension: '.pt',
  },
  safetensors: {
    name: 'SafeTensors',
    description: 'Safe, fast tensor storage format',
    icon: '🛡️',
    extension: '.safetensors',
  },
  onnx: {
    name: 'ONNX',
    description: 'Universal model format for deployment',
    icon: '🌐',
    extension: '.onnx',
  },
}

export function ExportDialog({
  isOpen,
  onClose,
  jobId,
  modelName = 'Unknown',
  compressionRatio = 0,
}: ExportDialogProps) {
  const [exportStatuses, setExportStatuses] = useState<Record<ExportFormat, ExportStatus>>({
    pytorch: { format: 'pytorch', status: 'idle', progress: 0 },
    safetensors: { format: 'safetensors', status: 'idle', progress: 0 },
    onnx: { format: 'onnx', status: 'idle', progress: 0 },
  })
  const [exportingAll, setExportingAll] = useState(false)

  const handleExport = async (format: ExportFormat) => {
    setExportStatuses((prev) => ({
      ...prev,
      [format]: { ...prev[format], status: 'exporting', progress: 0 },
    }))

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setExportStatuses((prev) => {
          const current = prev[format]
          if (current.status === 'exporting' && current.progress < 90) {
            return {
              ...prev,
              [format]: { ...current, progress: current.progress + 10 },
            }
          }
          return prev
        })
      }, 200)

      // Call export API using apiClient
      const blob = await apiClient.exportModel(jobId, format)

      clearInterval(progressInterval)
      const url = window.URL.createObjectURL(blob)
      
      // Trigger download
      const a = document.createElement('a')
      a.href = url
      a.download = `${jobId}_model${formatInfo[format].extension}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      setExportStatuses((prev) => ({
        ...prev,
        [format]: {
          ...prev[format],
          status: 'success',
          progress: 100,
          downloadUrl: url,
        },
      }))
    } catch (error) {
      setExportStatuses((prev) => ({
        ...prev,
        [format]: {
          ...prev[format],
          status: 'error',
          error: error instanceof Error ? error.message : 'Export failed',
        },
      }))
    }
  }

  const handleExportAll = async () => {
    setExportingAll(true)
    const formats: ExportFormat[] = ['pytorch', 'safetensors', 'onnx']
    
    for (const format of formats) {
      await handleExport(format)
      // Small delay between exports
      await new Promise((resolve) => setTimeout(resolve, 500))
    }
    
    setExportingAll(false)
  }

  const getStatusIcon = (status: ExportStatus['status']) => {
    switch (status) {
      case 'exporting':
        return <Loader2 className="h-4 w-4 animate-spin text-quantum-cyan-400" />
      case 'success':
        return <Check className="h-4 w-4 text-quantum-emerald-400" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-destructive" />
      default:
        return <FileDown className="h-4 w-4 text-muted-foreground" />
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Export Compressed Model</DialogTitle>
          <DialogDescription>
            Export {modelName} in your preferred format
          </DialogDescription>
        </DialogHeader>
      <div className="space-y-6">
        {/* Model Info */}
        <Card className="border-quantum-purple-500/30 bg-quantum-purple-500/10">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Model</p>
                <p className="font-semibold">{modelName}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground mb-1">Compression</p>
                <p className="text-quantum-emerald-400 font-semibold">
                  {(compressionRatio * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Export Formats */}
        <div className="space-y-3">
          {(Object.keys(formatInfo) as ExportFormat[]).map((format) => {
            const info = formatInfo[format]
            const status = exportStatuses[format]

            return (
              <Card key={format} className="hover:border-primary transition-colors">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="text-2xl">{info.icon}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <CardTitle className="text-base">{info.name}</CardTitle>
                          {status.status === 'success' && (
                            <Badge variant="default" className="bg-quantum-emerald-500/20 text-quantum-emerald-300 border-quantum-emerald-500/30">
                              Ready
                            </Badge>
                          )}
                          {status.status === 'error' && (
                            <Badge variant="destructive">Error</Badge>
                          )}
                        </div>
                        <CardDescription>{info.description}</CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {status.status === 'exporting' && (
                        <div className="w-32">
                          <Progress value={status.progress} />
                        </div>
                      )}
                      <Button
                        variant={status.status === 'success' ? 'secondary' : 'default'}
                        size="sm"
                        onClick={() => handleExport(format)}
                        disabled={status.status === 'exporting' || exportingAll}
                      >
                        {getStatusIcon(status.status)}
                        <span className="ml-2">
                          {status.status === 'exporting'
                            ? 'Exporting...'
                            : status.status === 'success'
                            ? 'Download'
                            : 'Export'}
                        </span>
                      </Button>
                    </div>
                  </div>
                  {status.error && (
                    <p className="text-xs text-destructive mt-2">{status.error}</p>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Export All Button */}
        <Button
          variant="outline"
          className="w-full"
          onClick={handleExportAll}
          disabled={exportingAll}
        >
          {exportingAll ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Exporting All Formats...
            </>
          ) : (
            <>
              <Download className="h-4 w-4 mr-2" />
              Export All Formats
            </>
          )}
        </Button>
      </div>
      </DialogContent>
    </Dialog>
  )
}

