import { useState, useEffect, useCallback } from 'react'
import { storageService, type JobHistoryItem } from '../storage'

export function useJobHistory() {
  const [history, setHistory] = useState<JobHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Load history on mount
  useEffect(() => {
    const loadHistory = () => {
      const jobs = storageService.getJobHistory()
      setHistory(jobs)
      setIsLoading(false)
    }

    loadHistory()
  }, [])

  // Add job to history
  const addJob = useCallback((job: JobHistoryItem) => {
    storageService.addJobToHistory(job)
    setHistory(storageService.getJobHistory())
  }, [])

  // Update job in history
  const updateJob = useCallback((jobId: string, updates: Partial<JobHistoryItem>) => {
    storageService.updateJobInHistory(jobId, updates)
    setHistory(storageService.getJobHistory())
  }, [])

  // Remove job from history
  const removeJob = useCallback((jobId: string) => {
    storageService.removeJobFromHistory(jobId)
    setHistory(storageService.getJobHistory())
  }, [])

  // Clear all history
  const clearHistory = useCallback(() => {
    storageService.clearJobHistory()
    setHistory([])
  }, [])

  // Filter history
  const filterHistory = useCallback((
    filters: {
      status?: JobHistoryItem['status']
      modelName?: string
      searchTerm?: string
    }
  ) => {
    let filtered = history

    if (filters.status) {
      filtered = filtered.filter(job => job.status === filters.status)
    }

    if (filters.modelName) {
      filtered = filtered.filter(job => 
        job.modelName.toLowerCase().includes(filters.modelName!.toLowerCase())
      )
    }

    if (filters.searchTerm) {
      const term = filters.searchTerm.toLowerCase()
      filtered = filtered.filter(job =>
        job.jobId.toLowerCase().includes(term) ||
        job.modelName.toLowerCase().includes(term)
      )
    }

    return filtered
  }, [history])

  // Get statistics
  const getStats = useCallback(() => {
    const total = history.length
    const completed = history.filter(j => j.status === 'completed').length
    const failed = history.filter(j => j.status === 'failed').length
    const avgCompressionRatio = history.length > 0
      ? history.reduce((sum, j) => sum + j.compressionRatio, 0) / history.length
      : 0

    return {
      total,
      completed,
      failed,
      avgCompressionRatio,
    }
  }, [history])

  return {
    history,
    isLoading,
    addJob,
    updateJob,
    removeJob,
    clearHistory,
    filterHistory,
    getStats,
  }
}

