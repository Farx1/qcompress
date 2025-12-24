'use client'

import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Sparkles, Database, TrendingUp, Zap } from 'lucide-react'
import { apiClient } from '@/lib/api'
import MetricsChart from './MetricsChart'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import type { ModelInfo } from '@/lib/types'

// Spotlight effect component
function SpotlightCard({ children, className }: { children: React.ReactNode; className?: string }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isHovering, setIsHovering] = useState(false)

  return (
    <div
      className={`relative group ${className}`}
      onMouseMove={(e) => {
        const rect = e.currentTarget.getBoundingClientRect()
        setMousePosition({ x: e.clientX - rect.left, y: e.clientY - rect.top })
        setIsHovering(true)
      }}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div
        className="pointer-events-none absolute -inset-0.5 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          background: isHovering
            ? `radial-gradient(300px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(168, 85, 247, 0.15), transparent 40%)`
            : 'transparent',
        }}
      />
      {children}
    </div>
  )
}

// Skeleton loader
function ModelCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2 mt-2" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-3 w-1/3 mt-2" />
        <Skeleton className="h-3 w-1/4 mt-2" />
      </CardContent>
    </Card>
  )
}

// Animated counter
function AnimatedCounter({ value, suffix = '' }: { value: number | string; suffix?: string }) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    if (typeof value === 'number') {
      const duration = 1000
      const steps = 30
      const increment = value / steps
      let current = 0
      const timer = setInterval(() => {
        current += increment
        if (current >= value) {
          setDisplayValue(value)
          clearInterval(timer)
        } else {
          setDisplayValue(Math.floor(current))
        }
      }, duration / steps)
      return () => clearInterval(timer)
    } else {
      setDisplayValue(value as any)
    }
  }, [value])

  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-2xl font-bold"
    >
      {typeof value === 'number' ? displayValue.toLocaleString() : value}
      {suffix}
    </motion.span>
  )
}

export default function Dashboard() {
  const { data: models, isLoading, error } = useQuery<ModelInfo[]>({
    queryKey: ['models'],
    queryFn: () => apiClient.getModels(),
    retry: 2,
    retryDelay: 1000,
  })

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  }

  return (
    <motion.div
      className="w-full space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Models Section */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center gap-2 mb-4">
          <Database className="h-5 w-5 text-quantum-cyan-400" aria-hidden="true" />
          <h2 className="text-lg font-semibold">Available Models</h2>
        </div>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <ModelCardSkeleton key={i} />
            ))}
          </div>
        ) : error ? (
          <Card className="border-destructive/50 bg-destructive/10">
            <CardContent className="pt-6">
              <p className="text-destructive">Error loading models: {error instanceof Error ? error.message : 'Unknown error'}</p>
              <p className="text-xs text-muted-foreground mt-2">
                Make sure the backend API is running on {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
              </p>
            </CardContent>
          </Card>
        ) : models && models.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {models.map((model, index) => (
              <motion.div
                key={model.name}
                variants={itemVariants}
                transition={{ delay: index * 0.1 }}
              >
                <SpotlightCard>
                  <Card className="h-full hover:border-primary transition-colors">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-base">{model.name}</CardTitle>
                        <Badge variant="secondary">
                          <Sparkles className="h-3 w-3 mr-1" />
                        </Badge>
                      </div>
                      {model.description && (
                        <CardDescription>{model.description}</CardDescription>
                      )}
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {model.parameters && (
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">Parameters</span>
                            <span className="font-medium">
                              {model.parameters.toLocaleString()}
                            </span>
                          </div>
                        )}
                        {model.size_mb && (
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">Size</span>
                            <span className="font-medium">
                              {model.size_mb.toFixed(2)} MB
                            </span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </SpotlightCard>
              </motion.div>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground text-center">No models available</p>
            </CardContent>
          </Card>
        )}
      </motion.div>

      {/* Metrics Section */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-5 w-5 text-quantum-purple-400" />
          <h3 className="text-lg font-semibold">Compression Metrics</h3>
        </div>
        <Card>
          <CardContent className="pt-6">
            <MetricsChart />
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Stats */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="hover:border-primary transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <AnimatedCounter value={0} />
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <Sparkles className="h-4 w-4 text-quantum-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-quantum-emerald-400">
              <AnimatedCounter value={0} />
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Compression</CardTitle>
            <Zap className="h-4 w-4 text-quantum-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-quantum-cyan-400">
              <AnimatedCounter value={0} suffix="%" />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
