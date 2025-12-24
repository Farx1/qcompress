'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import type { CompressionMetrics } from '@/lib/types'

interface MetricsChartProps {
  metrics?: CompressionMetrics[]
}

export default function MetricsChart({ metrics = [] }: MetricsChartProps) {
  if (metrics.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center border border-white/10 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02]">
        <p className="text-white/60">Aucune donnée de métriques disponible</p>
      </div>
    )
  }

  const chartData = metrics.map((m, idx) => ({
    step: idx + 1,
    compression_ratio: m.compression_ratio || 0,
    compressed_params: m.compressed_params || 0,
    original_params: m.original_params || 0,
    timestamp: new Date(m.timestamp * 1000).toLocaleTimeString(),
    layer: m.layer_name || `Layer ${idx + 1}`,
  }))

  return (
    <div className="w-full h-80 card p-6">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="step" 
            stroke="rgba(255,255,255,0.5)"
            tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
          />
          <YAxis 
            stroke="rgba(255,255,255,0.5)"
            tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(15, 23, 42, 0.95)', 
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              color: '#fff'
            }}
            labelStyle={{ color: '#fff' }}
            formatter={(value: any) => {
              if (typeof value === 'number') {
                return value.toFixed(2)
              }
              return value
            }}
          />
          <Legend 
            wrapperStyle={{ color: 'rgba(255,255,255,0.8)', paddingTop: '16px' }}
          />
          <Line
            type="monotone"
            dataKey="compression_ratio"
            stroke="#10B981"
            strokeWidth={2}
            name="Ratio de compression"
            dot={{ fill: '#10B981', r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="compressed_params"
            stroke="#3B82F6"
            strokeWidth={2}
            name="Paramètres compressés"
            dot={{ fill: '#3B82F6', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
