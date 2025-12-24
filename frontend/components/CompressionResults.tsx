'use client'

import { motion } from 'motion/react'
import { useState } from 'react'

interface CompressionResult {
  jobId: string
  modelName: string
  originalParams: number
  compressedParams: number
  compressionRatio: number
  originalSize: number
  compressedSize: number
  speedGain: number
  qualityLoss: number
  status: 'completed' | 'failed' | 'running'
  timestamp: string
}

interface CompressionResultsProps {
  result: CompressionResult
  onRunBenchmark: () => void
  onDownload: () => void
}

export default function CompressionResults({ result, onRunBenchmark, onDownload }: CompressionResultsProps) {
  const [showDetails, setShowDetails] = useState(false)

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(2) + 'K'
    return num.toString()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Status Banner */}
      <div className={`p-6 rounded-xl border-2 ${
        result.status === 'completed'
          ? 'border-emerald-500/30 bg-emerald-500/10'
          : result.status === 'failed'
          ? 'border-red-500/30 bg-red-500/10'
          : 'border-cyan-500/30 bg-cyan-500/10'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-bold text-white">Compression Results</h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            result.status === 'completed'
              ? 'bg-emerald-500/20 text-emerald-400'
              : result.status === 'failed'
              ? 'bg-red-500/20 text-red-400'
              : 'bg-cyan-500/20 text-cyan-400'
          }`}>
            {result.status.charAt(0).toUpperCase() + result.status.slice(1)}
          </span>
        </div>
        <p className="text-white/60 text-sm">Model: <span className="text-white font-semibold">{result.modelName}</span></p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Parameters Reduction */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20"
        >
          <p className="text-white/60 text-sm mb-2">Parameters Reduction</p>
          <p className="text-2xl font-bold text-blue-400 mb-1">
            {((1 - result.compressedParams / result.originalParams) * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-white/50">
            {formatNumber(result.originalParams)} → {formatNumber(result.compressedParams)}
          </p>
        </motion.div>

        {/* Size Reduction */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20"
        >
          <p className="text-white/60 text-sm mb-2">Size Reduction</p>
          <p className="text-2xl font-bold text-emerald-400 mb-1">
            {((1 - result.compressedSize / result.originalSize) * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-white/50">
            {formatBytes(result.originalSize)} → {formatBytes(result.compressedSize)}
          </p>
        </motion.div>

        {/* Speed Gain */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/20"
        >
          <p className="text-white/60 text-sm mb-2">Speed Gain</p>
          <p className="text-2xl font-bold text-cyan-400 mb-1">{result.speedGain.toFixed(1)}%</p>
          <p className="text-xs text-white/50">Faster inference</p>
        </motion.div>

        {/* Quality Loss */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-xl bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20"
        >
          <p className="text-white/60 text-sm mb-2">Quality Loss</p>
          <p className="text-2xl font-bold text-orange-400 mb-1">{result.qualityLoss.toFixed(2)}%</p>
          <p className="text-xs text-white/50">Minimal impact</p>
        </motion.div>
      </div>

      {/* Detailed Metrics */}
      <motion.div
        className="p-6 rounded-xl border border-white/10 bg-white/5"
      >
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between mb-4"
        >
          <h4 className="text-lg font-semibold text-white">Detailed Metrics</h4>
          <svg
            className={`w-5 h-5 text-white/60 transition-transform ${showDetails ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>

        {showDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-3 border-t border-white/10 pt-4"
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-white/60 text-sm mb-1">Original Parameters</p>
                <p className="text-white font-semibold">{formatNumber(result.originalParams)}</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Compressed Parameters</p>
                <p className="text-white font-semibold">{formatNumber(result.compressedParams)}</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Original Size</p>
                <p className="text-white font-semibold">{formatBytes(result.originalSize)}</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Compressed Size</p>
                <p className="text-white font-semibold">{formatBytes(result.compressedSize)}</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Compression Ratio</p>
                <p className="text-white font-semibold">{(result.compressionRatio * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Job ID</p>
                <p className="text-white font-mono text-xs">{result.jobId.substring(0, 12)}...</p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onRunBenchmark}
          className="flex-1 px-6 py-3 rounded-lg bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold hover:shadow-lg hover:shadow-emerald-500/50 transition-all flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Run Benchmark
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onDownload}
          className="flex-1 px-6 py-3 rounded-lg border border-white/20 text-white font-semibold hover:bg-white/10 transition-all flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download Model
        </motion.button>
      </div>
    </motion.div>
  )
}
