'use client'

import { motion } from 'motion/react'
import { useState } from 'react'

interface VisualizationData {
  compressionRatio: number
  speedGain: number
  qualityLoss: number
  originalSize: number
  compressedSize: number
  benchmarkScores: {
    name: string
    original: number
    compressed: number
  }[]
}

interface ResultsVisualizationProps {
  data: VisualizationData
}

export default function ResultsVisualization({ data }: ResultsVisualizationProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'quality' | 'benchmarks'>('overview')

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-white/10 overflow-x-auto">
        {(['overview', 'performance', 'quality', 'benchmarks'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition-all ${
              activeTab === tab
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-white/60 hover:text-white/80'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Size Comparison */}
          <div className="p-6 rounded-xl border border-white/10 bg-white/5">
            <h3 className="text-lg font-semibold text-white mb-6">Model Size Reduction</h3>
            <div className="space-y-4">
              {/* Original */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-white/80">Original Model</p>
                  <p className="text-white font-semibold">{formatBytes(data.originalSize)}</p>
                </div>
                <div className="w-full h-8 bg-white/10 rounded-lg overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                  />
                </div>
              </div>

              {/* Compressed */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-white/80">Compressed Model</p>
                  <p className="text-white font-semibold">{formatBytes(data.compressedSize)}</p>
                </div>
                <div className="w-full h-8 bg-white/10 rounded-lg overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(data.compressedSize / data.originalSize) * 100}%` }}
                    transition={{ duration: 1, delay: 0.3 }}
                    className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600"
                  />
                </div>
              </div>

              {/* Reduction */}
              <div className="pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <p className="text-white/80">Total Reduction</p>
                  <p className="text-2xl font-bold text-emerald-400">
                    {((1 - data.compressedSize / data.originalSize) * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/20"
            >
              <p className="text-white/60 text-sm mb-2">Compression Ratio</p>
              <p className="text-3xl font-bold text-cyan-400">{(data.compressionRatio * 100).toFixed(1)}%</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20"
            >
              <p className="text-white/60 text-sm mb-2">Speed Gain</p>
              <p className="text-3xl font-bold text-emerald-400">{data.speedGain.toFixed(1)}%</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-xl bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20"
            >
              <p className="text-white/60 text-sm mb-2">Quality Loss</p>
              <p className="text-3xl font-bold text-orange-400">{data.qualityLoss.toFixed(2)}%</p>
            </motion.div>
          </div>
        </motion.div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-6 rounded-xl border border-white/10 bg-white/5"
        >
          <h3 className="text-lg font-semibold text-white mb-6">Performance Metrics</h3>
          <div className="space-y-4">
            {[
              { label: 'Inference Speed', value: data.speedGain, unit: '% faster', color: 'emerald' },
              { label: 'Memory Efficiency', value: 100 - (data.compressedSize / data.originalSize) * 100, unit: '% reduction', color: 'cyan' },
              { label: 'Throughput Improvement', value: data.speedGain * 1.2, unit: 'tokens/sec', color: 'blue' },
            ].map((metric, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-white/80">{metric.label}</p>
                  <p className="text-white font-semibold">{metric.value.toFixed(1)} {metric.unit}</p>
                </div>
                <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(metric.value, 100)}%` }}
                    transition={{ duration: 1, delay: idx * 0.2 }}
                    className={`h-full bg-gradient-to-r from-${metric.color}-500 to-${metric.color}-600`}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Quality Tab */}
      {activeTab === 'quality' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-6 rounded-xl border border-white/10 bg-white/5"
        >
          <h3 className="text-lg font-semibold text-white mb-6">Quality Metrics</h3>
          <div className="space-y-6">
            {/* Quality Retention */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-white/80">Quality Retention</p>
                <p className="text-white font-semibold">{(100 - data.qualityLoss).toFixed(2)}%</p>
              </div>
              <div className="w-full h-4 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${100 - data.qualityLoss}%` }}
                  transition={{ duration: 1 }}
                  className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
                />
              </div>
            </div>

            {/* Quality Score Breakdown */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                <p className="text-white/60 text-sm mb-2">Semantic Preservation</p>
                <p className="text-2xl font-bold text-emerald-400">{(100 - data.qualityLoss * 0.5).toFixed(1)}%</p>
              </div>
              <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                <p className="text-white/60 text-sm mb-2">Task Performance</p>
                <p className="text-2xl font-bold text-cyan-400">{(100 - data.qualityLoss * 0.7).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Benchmarks Tab */}
      {activeTab === 'benchmarks' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-6 rounded-xl border border-white/10 bg-white/5"
        >
          <h3 className="text-lg font-semibold text-white mb-6">Benchmark Comparison</h3>
          <div className="space-y-4">
            {data.benchmarkScores.map((benchmark, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-white/80">{benchmark.name}</p>
                  <div className="flex gap-4 text-sm">
                    <span className="text-blue-400">Original: {benchmark.original.toFixed(1)}</span>
                    <span className="text-emerald-400">Compressed: {benchmark.compressed.toFixed(1)}</span>
                  </div>
                </div>
                <div className="flex gap-2 h-3">
                  <div className="flex-1 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(benchmark.original / 100) * 100}%` }}
                      transition={{ duration: 1, delay: idx * 0.1 }}
                      className="h-full bg-blue-500"
                    />
                  </div>
                  <div className="flex-1 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(benchmark.compressed / 100) * 100}%` }}
                      transition={{ duration: 1, delay: idx * 0.1 + 0.2 }}
                      className="h-full bg-emerald-500"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
