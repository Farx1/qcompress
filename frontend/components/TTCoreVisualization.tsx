'use client'

import { motion } from 'motion/react'
import type { TTCoreData } from '@/lib/types'

interface TTCoreVisualizationProps {
  cores?: TTCoreData[]
  onCoreSelect?: (core: TTCoreData) => void
}

export default function TTCoreVisualization({ cores = [], onCoreSelect }: TTCoreVisualizationProps) {
  // Generate mock cores if none provided
  const mockCores: TTCoreData[] = cores.length > 0 ? cores : [
    { id: '1', name: 'Core 1', shape: [768, 512], rank: 32 },
    { id: '2', name: 'Core 2', shape: [512, 256], rank: 16 },
    { id: '3', name: 'Core 3', shape: [256, 128], rank: 8 },
    { id: '4', name: 'Core 4', shape: [128, 64], rank: 4 },
  ]

  return (
    <div className="w-full space-y-6">
      {/* Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6"
      >
        <h3 className="card-title mb-3">Visualisation Tensor-Train</h3>
        <p className="text-sm text-white/70 mb-4">
          La décomposition Tensor-Train factorise les matrices de poids en chaînes de tenseurs plus petits. 
          Chaque core représente une partie de la décomposition.
        </p>
      </motion.div>

      {/* Cores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockCores.map((core, idx) => (
          <motion.div
            key={core.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            onClick={() => onCoreSelect?.(core)}
            className="card p-6 cursor-pointer hover:border-emerald-500/30 transition-all duration-300 group"
          >
            {/* Core Visualization */}
            <div className="mb-4 flex items-center justify-center">
              <div className="relative w-full h-32 bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg border border-white/10 flex items-center justify-center overflow-hidden group-hover:border-emerald-500/30 transition-all duration-300">
                {/* Animated tensor representation */}
                <svg className="w-24 h-24 text-emerald-400/50 group-hover:text-emerald-400/70 transition-colors" viewBox="0 0 100 100" fill="none">
                  {/* Outer cube */}
                  <rect x="20" y="20" width="60" height="60" stroke="currentColor" strokeWidth="2" />
                  {/* Inner lines */}
                  <line x1="20" y1="50" x2="80" y2="50" stroke="currentColor" strokeWidth="1" opacity="0.5" />
                  <line x1="50" y1="20" x2="50" y2="80" stroke="currentColor" strokeWidth="1" opacity="0.5" />
                  {/* Diagonal */}
                  <line x1="20" y1="20" x2="80" y2="80" stroke="currentColor" strokeWidth="1" opacity="0.3" />
                </svg>
              </div>
            </div>

            {/* Core Info */}
            <div className="space-y-3">
              <div>
                <div className="text-xs text-white/70 mb-1">Nom</div>
                <div className="text-sm font-semibold text-white">{core.name}</div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs text-white/70 mb-1">Dimensions</div>
                  <div className="text-xs text-white/90 font-mono">
                    {core.shape[0]} × {core.shape[1]}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-white/70 mb-1">Rang TT</div>
                  <div className="text-xs text-white/90 font-mono">{core.rank}</div>
                </div>
              </div>

              <div>
                <div className="text-xs text-white/70 mb-2">Compression</div>
                <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(core.rank / 64) * 100}%` }}
                    transition={{ duration: 0.5, delay: 0.2 + idx * 0.1 }}
                    className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card p-6"
      >
        <h3 className="card-title mb-4">Statistiques</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg p-4 border border-white/10">
            <div className="text-xs text-white/70 mb-2">Nombre de cores</div>
            <div className="text-2xl font-bold text-emerald-400">{mockCores.length}</div>
          </div>
          <div className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg p-4 border border-white/10">
            <div className="text-xs text-white/70 mb-2">Rang moyen</div>
            <div className="text-2xl font-bold text-cyan-400">
              {Math.round(mockCores.reduce((a, b) => a + b.rank, 0) / mockCores.length)}
            </div>
          </div>
          <div className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg p-4 border border-white/10">
            <div className="text-xs text-white/70 mb-2">Paramètres totaux</div>
            <div className="text-2xl font-bold text-white">
              {mockCores.reduce((a, b) => a + (b.shape[0] * b.shape[1]), 0).toLocaleString()}
            </div>
          </div>
          <div className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg p-4 border border-white/10">
            <div className="text-xs text-white/70 mb-2">Compression</div>
            <div className="text-2xl font-bold text-emerald-400">10.0x</div>
          </div>
        </div>
      </motion.div>

      {/* Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="card p-4 border-dashed bg-white/5"
      >
        <p className="text-xs text-white/60">
          💡 <b>Conseil :</b> Cliquez sur un core pour voir plus de détails. Les cores avec un rang plus faible 
          offrent une meilleure compression mais peuvent affecter la qualité.
        </p>
      </motion.div>
    </div>
  )
}
