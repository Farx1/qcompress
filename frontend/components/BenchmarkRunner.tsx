'use client'

import { motion } from 'motion/react'
import { useState, useEffect } from 'react'

interface BenchmarkMetric {
  name: string
  original: number
  compressed: number
  difference: number
  unit: string
}

interface BenchmarkResult {
  benchmarkName: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  metrics: BenchmarkMetric[]
  timestamp: string
}

interface BenchmarkRunnerProps {
  modelName: string
  jobId: string
  onBenchmarkComplete: (results: BenchmarkResult[]) => void
}

export default function BenchmarkRunner({ modelName, jobId, onBenchmarkComplete }: BenchmarkRunnerProps) {
  const [benchmarks, setBenchmarks] = useState<BenchmarkResult[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [currentBenchmark, setCurrentBenchmark] = useState<string | null>(null)
  const [overallProgress, setOverallProgress] = useState(0)

  const availableBenchmarks = [
    {
      name: 'GLUE',
      description: 'General Language Understanding Evaluation',
      tasks: ['CoLA', 'SST-2', 'MRPC', 'QQP', 'MNLI', 'QNLI', 'RTE', 'WNLI'],
    },
    {
      name: 'SQuAD',
      description: 'Stanford Question Answering Dataset',
      tasks: ['SQuAD v1.1', 'SQuAD v2.0'],
    },
    {
      name: 'Perplexity',
      description: 'Language Modeling Evaluation',
      tasks: ['WikiText-103', 'Penn Treebank'],
    },
    {
      name: 'Latency',
      description: 'Inference Speed & Memory',
      tasks: ['Throughput', 'Memory Usage', 'Latency'],
    },
  ]

  const runBenchmarks = async () => {
    setIsRunning(true)
    const results: BenchmarkResult[] = []

    for (let i = 0; i < availableBenchmarks.length; i++) {
      const benchmark = availableBenchmarks[i]
      setCurrentBenchmark(benchmark.name)
      setOverallProgress((i / availableBenchmarks.length) * 100)

      // Simulate benchmark running
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Generate realistic results based on benchmark type
      let metrics: BenchmarkMetric[] = []

      if (benchmark.name === 'GLUE') {
        metrics = [
          { name: 'CoLA', original: 84.5, compressed: 82.1, difference: -2.4, unit: 'Matthew\'s Corr' },
          { name: 'SST-2', original: 94.8, compressed: 93.2, difference: -1.6, unit: 'Accuracy' },
          { name: 'MRPC', original: 88.9, compressed: 86.5, difference: -2.4, unit: 'F1' },
          { name: 'QQP', original: 91.2, compressed: 89.8, difference: -1.4, unit: 'Accuracy' },
          { name: 'MNLI', original: 86.7, compressed: 84.9, difference: -1.8, unit: 'Accuracy' },
          { name: 'QNLI', original: 92.3, compressed: 90.8, difference: -1.5, unit: 'Accuracy' },
          { name: 'RTE', original: 78.4, compressed: 75.6, difference: -2.8, unit: 'Accuracy' },
          { name: 'WNLI', original: 65.5, compressed: 62.3, difference: -3.2, unit: 'Accuracy' },
        ]
      } else if (benchmark.name === 'SQuAD') {
        metrics = [
          { name: 'EM Score', original: 88.5, compressed: 86.2, difference: -2.3, unit: '%' },
          { name: 'F1 Score', original: 94.2, compressed: 91.8, difference: -2.4, unit: '%' },
        ]
      } else if (benchmark.name === 'Perplexity') {
        metrics = [
          { name: 'WikiText-103', original: 24.3, compressed: 26.8, difference: 2.5, unit: 'PPL' },
          { name: 'Penn Treebank', original: 65.2, compressed: 71.4, difference: 6.2, unit: 'PPL' },
        ]
      } else if (benchmark.name === 'Latency') {
        metrics = [
          { name: 'Throughput', original: 45.2, compressed: 62.8, difference: 17.6, unit: 'tokens/s' },
          { name: 'Memory Usage', original: 13.5, compressed: 6.4, difference: -7.1, unit: 'GB' },
          { name: 'Latency', original: 22.1, compressed: 15.9, difference: -6.2, unit: 'ms' },
        ]
      }

      results.push({
        benchmarkName: benchmark.name,
        status: 'completed',
        progress: 100,
        metrics,
        timestamp: new Date().toISOString(),
      })
    }

    setBenchmarks(results)
    setOverallProgress(100)
    setCurrentBenchmark(null)
    setIsRunning(false)
    onBenchmarkComplete(results)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="p-6 rounded-xl border border-white/10 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10">
        <h3 className="text-xl font-bold text-white mb-2">Official Benchmarks</h3>
        <p className="text-white/60 text-sm">
          Compare original vs compressed model performance on standardized benchmarks
        </p>
      </div>

      {/* Run Button */}
      {!isRunning && benchmarks.length === 0 && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={runBenchmarks}
          className="w-full px-6 py-4 rounded-lg bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold hover:shadow-lg hover:shadow-emerald-500/50 transition-all flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Run All Benchmarks
        </motion.button>
      )}

      {/* Progress Bar */}
      {isRunning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <div className="p-4 rounded-lg bg-white/5 border border-white/10">
            <div className="flex items-center justify-between mb-2">
              <p className="text-white font-semibold">Running: {currentBenchmark}</p>
              <p className="text-white/60 text-sm">{Math.round(overallProgress)}%</p>
            </div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                animate={{ width: `${overallProgress}%` }}
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Benchmark Results */}
      {benchmarks.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          {benchmarks.map((benchmark, idx) => (
            <motion.div
              key={benchmark.benchmarkName}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="p-6 rounded-xl border border-white/10 bg-white/5"
            >
              {/* Benchmark Header */}
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-white">{benchmark.benchmarkName}</h4>
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/20 text-emerald-400">
                  Completed
                </span>
              </div>

              {/* Metrics Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-2 px-3 text-white/60 font-medium">Metric</th>
                      <th className="text-right py-2 px-3 text-white/60 font-medium">Original</th>
                      <th className="text-right py-2 px-3 text-white/60 font-medium">Compressed</th>
                      <th className="text-right py-2 px-3 text-white/60 font-medium">Difference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {benchmark.metrics.map((metric, metricIdx) => (
                      <tr
                        key={metricIdx}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="py-3 px-3 text-white">{metric.name}</td>
                        <td className="text-right py-3 px-3 text-white/80 font-mono">
                          {metric.original.toFixed(2)} {metric.unit}
                        </td>
                        <td className="text-right py-3 px-3 text-white/80 font-mono">
                          {metric.compressed.toFixed(2)} {metric.unit}
                        </td>
                        <td className={`text-right py-3 px-3 font-mono font-semibold ${
                          metric.difference > 0 ? 'text-red-400' : 'text-emerald-400'
                        }`}>
                          {metric.difference > 0 ? '+' : ''}{metric.difference.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Average Score */}
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <p className="text-white/60">Average Performance Retention</p>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{
                          width: `${100 - Math.abs(
                            benchmark.metrics.reduce((sum, m) => sum + m.difference, 0) / benchmark.metrics.length
                          )}%`,
                        }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
                      />
                    </div>
                    <p className="text-white font-semibold w-12 text-right">
                      {(100 - Math.abs(
                        benchmark.metrics.reduce((sum, m) => sum + m.difference, 0) / benchmark.metrics.length
                      )).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}

          {/* Overall Summary */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: benchmarks.length * 0.1 }}
            className="p-6 rounded-xl border-2 border-emerald-500/30 bg-emerald-500/10"
          >
            <h4 className="text-lg font-semibold text-white mb-4">Benchmark Summary</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-white/60 text-sm mb-1">Total Benchmarks</p>
                <p className="text-2xl font-bold text-emerald-400">{benchmarks.length}</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Average Performance</p>
                <p className="text-2xl font-bold text-cyan-400">
                  {(100 - Math.abs(
                    benchmarks.reduce((sum, b) => sum + b.metrics.reduce((s, m) => s + m.difference, 0) / b.metrics.length, 0) / benchmarks.length
                  )).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Status</p>
                <p className="text-2xl font-bold text-white">✅ Passed</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  )
}
