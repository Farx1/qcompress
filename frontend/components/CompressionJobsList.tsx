'use client';

import { motion } from 'motion/react';
import { useTranslation } from '@/lib/use-translation';

export interface CompressionJob {
  id: string;
  modelName: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: Date;
  endTime?: Date;
  compressionRatio: number;
  originalSize: number;
  compressedSize: number;
}

interface CompressionJobsListProps {
  jobs: CompressionJob[];
  onCancel?: (jobId: string) => void;
}

export default function CompressionJobsList({ jobs, onCancel }: CompressionJobsListProps) {
  const { t } = useTranslation();

  const getStatusColor = (status: CompressionJob['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'running':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'completed':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      default:
        return 'bg-white/10 text-white/60 border-white/20';
    }
  };

  const getStatusLabel = (status: CompressionJob['status']) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-white/60">{t('dashboard.noMetrics')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => (
        <motion.div
          key={job.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm hover:border-white/20 transition-all"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white">{job.modelName}</h3>
              <p className="text-sm text-white/60 mt-1">ID: {job.id.slice(0, 8)}...</p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(job.status)}`}>
              {getStatusLabel(job.status)}
            </div>
          </div>

          {/* Progress bar */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-white/60">{t('common.progress')}</span>
              <span className="text-sm font-semibold text-emerald-400">{job.progress}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${job.progress}%` }}
                transition={{ duration: 0.5 }}
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
              />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-white/60 mb-1">Compression Ratio</p>
              <p className="text-sm font-semibold text-white">{(job.compressionRatio * 100).toFixed(1)}%</p>
            </div>
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-white/60 mb-1">Original Size</p>
              <p className="text-sm font-semibold text-white">{(job.originalSize / 1024 / 1024).toFixed(1)} MB</p>
            </div>
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-white/60 mb-1">Compressed Size</p>
              <p className="text-sm font-semibold text-white">{(job.compressedSize / 1024 / 1024).toFixed(1)} MB</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            {job.status === 'running' && onCancel && (
              <button
                onClick={() => onCancel(job.id)}
                className="px-4 py-2 rounded-lg text-sm font-medium text-red-300 border border-red-500/30 hover:bg-red-500/10 transition-colors"
              >
                Cancel
              </button>
            )}
            {job.status === 'completed' && (
              <button
                className="px-4 py-2 rounded-lg text-sm font-medium text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/10 transition-colors"
              >
                Download Results
              </button>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
