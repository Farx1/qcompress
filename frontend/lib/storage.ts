/**
 * LocalStorage utilities for persisting data
 */

const STORAGE_KEYS = {
  JOB_HISTORY: 'qcompress_job_history',
  USER_PREFERENCES: 'qcompress_preferences',
} as const

export interface JobHistoryItem {
  jobId: string
  modelName: string
  status: 'completed' | 'failed' | 'cancelled'
  compressionRatio: number
  originalParams: number
  compressedParams: number
  originalSize: number
  compressedSize: number
  createdAt: string
  completedAt?: string
  error?: string
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'system'
  language?: 'en' | 'fr'
  defaultCompressionRatio?: number
}

class StorageService {
  private isAvailable(): boolean {
    try {
      const test = '__storage_test__'
      localStorage.setItem(test, test)
      localStorage.removeItem(test)
      return true
    } catch {
      return false
    }
  }

  // Job History
  getJobHistory(): JobHistoryItem[] {
    if (!this.isAvailable()) return []
    
    try {
      const data = localStorage.getItem(STORAGE_KEYS.JOB_HISTORY)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Error reading job history:', error)
      return []
    }
  }

  addJobToHistory(job: JobHistoryItem): void {
    if (!this.isAvailable()) return

    try {
      const history = this.getJobHistory()
      
      // Remove duplicates
      const filtered = history.filter(item => item.jobId !== job.jobId)
      
      // Add new job at the beginning
      filtered.unshift(job)
      
      // Keep only last 50 jobs
      const limited = filtered.slice(0, 50)
      
      localStorage.setItem(STORAGE_KEYS.JOB_HISTORY, JSON.stringify(limited))
    } catch (error) {
      console.error('Error saving job to history:', error)
    }
  }

  updateJobInHistory(jobId: string, updates: Partial<JobHistoryItem>): void {
    if (!this.isAvailable()) return

    try {
      const history = this.getJobHistory()
      const index = history.findIndex(item => item.jobId === jobId)
      
      if (index !== -1) {
        history[index] = { ...history[index], ...updates }
        localStorage.setItem(STORAGE_KEYS.JOB_HISTORY, JSON.stringify(history))
      }
    } catch (error) {
      console.error('Error updating job in history:', error)
    }
  }

  removeJobFromHistory(jobId: string): void {
    if (!this.isAvailable()) return

    try {
      const history = this.getJobHistory()
      const filtered = history.filter(item => item.jobId !== jobId)
      localStorage.setItem(STORAGE_KEYS.JOB_HISTORY, JSON.stringify(filtered))
    } catch (error) {
      console.error('Error removing job from history:', error)
    }
  }

  clearJobHistory(): void {
    if (!this.isAvailable()) return
    
    try {
      localStorage.removeItem(STORAGE_KEYS.JOB_HISTORY)
    } catch (error) {
      console.error('Error clearing job history:', error)
    }
  }

  // User Preferences
  getPreferences(): UserPreferences {
    if (!this.isAvailable()) return {}
    
    try {
      const data = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES)
      return data ? JSON.parse(data) : {}
    } catch (error) {
      console.error('Error reading preferences:', error)
      return {}
    }
  }

  setPreferences(preferences: UserPreferences): void {
    if (!this.isAvailable()) return

    try {
      const current = this.getPreferences()
      const updated = { ...current, ...preferences }
      localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(updated))
    } catch (error) {
      console.error('Error saving preferences:', error)
    }
  }
}

export const storageService = new StorageService()

