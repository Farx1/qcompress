'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts'
import { CheckCircle2, Clock, XCircle, AlertCircle, BarChart3 } from 'lucide-react'
import type { BenchmarkResult } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface BenchmarkDashboardProps {
  jobId?: string
  results?: BenchmarkResult[]
}

export default function BenchmarkDashboard({ 
  jobId, 
  results = [],
}: BenchmarkDashboardProps) {
  const [currentResults, setCurrentResults] = useState<Record<string, any>>({})
  const [overallMetrics, setOverallMetrics] = useState<any>(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<'pending' | 'running' | 'completed' | 'failed'>('pending')
  
  useEffect(() => {
    const latestResult = results[results.length - 1]
    if (latestResult) {
      setStatus('completed')
      setProgress(100)
      
      if (latestResult.metrics) {
        setCurrentResults((prev) => ({
          ...prev,
          [latestResult.test_name || 'unknown']: latestResult,
        }))
      }
    }
  }, [results])
  
  const taskData = Object.entries(currentResults).map(([task, data]: [string, any]) => ({
    task: task.toUpperCase(),
    original_time: data.original_time || 0,
    compressed_time: data.compressed_time || 0,
    speedup: data.speedup || 0,
    accuracy_drop: data.accuracy_drop || 0,
  }))

  const getStatusBadge = () => {
    switch (status) {
      case 'completed':
        return (
          <Badge className="bg-quantum-emerald-500/20 text-quantum-emerald-300 border-quantum-emerald-500/30">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Completed
          </Badge>
        )
      case 'running':
        return (
          <Badge className="bg-quantum-cyan-500/20 text-quantum-cyan-300 border-quantum-cyan-500/30">
            <Clock className="h-3 w-3 mr-1" />
            Running
          </Badge>
        )
      case 'failed':
        return (
          <Badge variant="destructive">
            <XCircle className="h-3 w-3 mr-1" />
            Failed
          </Badge>
        )
      default:
        return (
          <Badge variant="secondary">
            <AlertCircle className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        )
    }
  }
  
  return (
    <div className="w-full space-y-6">
      {/* Status and Progress */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Benchmark Evaluation</CardTitle>
              {getStatusBadge()}
        </div>
            <CardDescription>Performance metrics for compressed models</CardDescription>
          </CardHeader>
        {status === 'running' && (
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Progress</span>
              <span>{Math.round(progress * 100)}%</span>
            </div>
                <Progress value={progress * 100} />
            </div>
            </CardContent>
        )}
        </Card>
      </motion.div>
      
      {/* Overall Metrics */}
      {taskData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          {[
            { label: 'Number of Tests', value: taskData.length },
            {
              label: 'Average Speedup',
              value: (taskData.reduce((a, b) => a + b.speedup, 0) / taskData.length).toFixed(2) + 'x',
            },
            {
              label: 'Accuracy Drop',
              value:
                (taskData.reduce((a, b) => a + b.accuracy_drop, 0) / taskData.length).toFixed(2) + '%',
            },
            { label: 'Status', value: status === 'completed' ? '✓ Completed' : 'In Progress' },
          ].map((metric, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
            >
              <Card className="hover:border-primary transition-colors">
                <CardContent className="pt-6">
                  <div className="text-xs text-muted-foreground mb-2">{metric.label}</div>
                  <div className="text-2xl font-bold">{metric.value}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
      
      {/* Task Results Table */}
      {taskData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Test Results</CardTitle>
              <CardDescription>Detailed benchmark results for each test</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Test</TableHead>
                      <TableHead className="text-right">Original Time</TableHead>
                      <TableHead className="text-right">Compressed Time</TableHead>
                      <TableHead className="text-right">Speedup</TableHead>
                      <TableHead className="text-right">Accuracy Drop</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
              {taskData.map((task, idx) => (
                      <TableRow
                  key={idx}
                        className="hover:bg-muted/50"
                >
                        <TableCell className="font-medium">{task.task}</TableCell>
                        <TableCell className="text-right text-muted-foreground">
                          {task.original_time.toFixed(2)}ms
                        </TableCell>
                        <TableCell className="text-right text-quantum-emerald-400 font-semibold">
                          {task.compressed_time.toFixed(2)}ms
                        </TableCell>
                        <TableCell className="text-right text-quantum-cyan-400 font-semibold">
                          {task.speedup.toFixed(2)}x
                        </TableCell>
                        <TableCell className="text-right text-muted-foreground">
                          {task.accuracy_drop.toFixed(2)}%
                        </TableCell>
                      </TableRow>
              ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
      
      {/* Charts */}
      {taskData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {/* Speedup Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Speedup by Test</CardTitle>
              <CardDescription>Performance improvement for each benchmark</CardDescription>
            </CardHeader>
            <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={taskData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="task" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                      backgroundColor: 'hsl(var(--popover))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                  }}
                />
                  <Legend />
                  <Bar
                    dataKey="speedup"
                    fill="hsl(var(--chart-2))"
                    name="Speedup"
                    radius={[8, 8, 0, 0]}
                  />
              </BarChart>
            </ResponsiveContainer>
            </CardContent>
          </Card>
          
          {/* Time Comparison Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Time Comparison</CardTitle>
              <CardDescription>Original vs compressed inference time</CardDescription>
            </CardHeader>
            <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={taskData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="task" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                      backgroundColor: 'hsl(var(--popover))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                  }}
                />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="original_time"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth={2}
                    name="Original Time"
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="compressed_time"
                    stroke="hsl(var(--chart-2))"
                    strokeWidth={2}
                    name="Compressed Time"
                    dot={{ r: 4 }}
                  />
              </LineChart>
            </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      )}
      
      {/* Empty State */}
      {taskData.length === 0 && status === 'pending' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <Card className="border-dashed">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center justify-center gap-4 py-12">
                <BarChart3 className="h-12 w-12 text-muted-foreground/30" />
                <div className="text-center">
                  <p className="text-sm font-medium mb-1">No benchmark results yet</p>
                  <p className="text-xs text-muted-foreground">
                    Start a benchmark after compression to see results
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
