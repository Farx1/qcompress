'use client'

import { useState } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Download, BarChart3, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Stepper } from '@/components/Stepper'
import CompressionResults from '@/components/CompressionResults'
import BenchmarkRunner from '@/components/BenchmarkRunner'
import ResultsVisualization from '@/components/ResultsVisualization'
import { ExportDialog } from '@/components/ExportDialog'
import { GridBackground } from '@/components/aceternity/grid-background'
import { HoverBorderGradient } from '@/components/aceternity/hover-border-gradient'
import { GlareCard } from '@/components/aceternity/glare-card'
import { Button as MovingBorderButton } from '@/components/aceternity/moving-border'

type StepId = 'results' | 'benchmarks' | 'export'

export default function ResultsPage() {
  const t = useTranslations('results')
  const tCommon = useTranslations('common')
  const locale = useLocale()
  const [activeStep, setActiveStep] = useState<StepId>('results')
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)

  // Mock data
  const compressionResult = {
    jobId: jobId || 'job-' + Math.random().toString(36).substr(2, 9),
    modelName: 'Llama 2 (7B)',
    originalParams: 7000000000,
    compressedParams: 3500000000,
    compressionRatio: 0.5,
    originalSize: 13500000000,
    compressedSize: 6400000000,
    speedGain: 38.5,
    qualityLoss: 2.3,
    status: 'completed' as const,
    timestamp: new Date().toISOString(),
  }

  const [benchmarkResults, setBenchmarkResults] = useState<any[]>([])

  const steps = [
    { id: 'results' as const, label: t('steps.results') },
    { id: 'benchmarks' as const, label: t('steps.benchmarks') },
    { id: 'export' as const, label: t('steps.export') },
  ]

  const handleRunBenchmark = () => {
    setActiveStep('benchmarks')
  }

  const handleBenchmarkComplete = (results: any[]) => {
    setBenchmarkResults(results)
    setActiveStep('export')
  }

  const handleExport = () => {
    setShowExportDialog(true)
  }

  return (
    <div className="relative min-h-screen bg-black">
      <GridBackground />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Breadcrumb */}
        <Breadcrumb className="mb-8">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href={`/${locale}`} className="text-gray-400 hover:text-white transition-colors">
                {tCommon('appName')}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-600" />
            <BreadcrumbItem>
              <BreadcrumbLink href={`/${locale}/dashboard`} className="text-gray-400 hover:text-white transition-colors">
                {tCommon('dashboard')}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="text-gray-600" />
            <BreadcrumbItem>
              <span className="text-white font-medium">{t('title')}</span>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">{t('title')}</h1>
              <p className="text-lg text-gray-400">{t('subtitle')}</p>
            </div>
            <Link href={`/${locale}/dashboard`}>
              <HoverBorderGradient containerClassName="inline-block" className="px-6 py-3" as="button">
                <ArrowLeft className="h-4 w-4 mr-2 inline" />
                Back to Dashboard
              </HoverBorderGradient>
            </Link>
          </div>
        </motion.div>

        {/* Stepper */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <GlareCard className="p-8">
            <Stepper steps={steps} currentStep={activeStep} onStepClick={setActiveStep} />
          </GlareCard>
        </motion.div>

        {/* Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeStep}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="space-y-8"
          >
            {/* Results Step */}
            {activeStep === 'results' && (
              <div className="space-y-8">
                <CompressionResults
                  result={compressionResult}
                  onRunBenchmark={handleRunBenchmark}
                  onDownload={handleExport}
                />
              </div>
            )}

            {/* Benchmarks Step */}
            {activeStep === 'benchmarks' && (
              <div className="space-y-8">
                <BenchmarkRunner
                  modelName={compressionResult.modelName}
                  jobId={compressionResult.jobId}
                  onBenchmarkComplete={handleBenchmarkComplete}
                />
              </div>
            )}

            {/* Export Step */}
            {activeStep === 'export' && (
              <div className="space-y-8">
                <ResultsVisualization
                  data={{
                    compressionRatio: compressionResult.compressionRatio,
                    speedGain: compressionResult.speedGain,
                    qualityLoss: compressionResult.qualityLoss,
                    originalSize: compressionResult.originalSize,
                    compressedSize: compressionResult.compressedSize,
                    benchmarkScores: [
                      { name: 'GLUE Average', original: 86.7, compressed: 84.9 },
                      { name: 'SQuAD F1', original: 94.2, compressed: 91.8 },
                      { name: 'Perplexity', original: 24.3, compressed: 26.8 },
                      { name: 'Latency', original: 22.1, compressed: 15.9 },
                    ],
                  }}
                />

                {/* Summary Card */}
                <GlareCard className="p-8 bg-white/5">
                  <div className="flex items-center gap-3 mb-6">
                    <CheckCircle className="h-8 w-8 text-white" />
                    <h2 className="text-2xl font-bold text-white">{t('summary.complete')}</h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div>
                      <p className="text-sm text-gray-400 mb-2">{t('summary.compressionEfficiency')}</p>
                      <p className="text-3xl font-bold text-white">
                        {((1 - compressionResult.compressedSize / compressionResult.originalSize) * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400 mb-2">{t('summary.performanceRetention')}</p>
                      <p className="text-3xl font-bold text-white">
                        {(100 - compressionResult.qualityLoss).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400 mb-2">{t('summary.speedImprovement')}</p>
                      <p className="text-3xl font-bold text-white">
                        {compressionResult.speedGain.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400 mb-2">{t('summary.benchmarksPassed')}</p>
                      <p className="text-3xl font-bold text-white">4/4 ✓</p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row gap-4">
                    <MovingBorderButton
                      borderRadius="1.5rem"
                      className="bg-black text-white border-white px-8 py-4 text-lg font-semibold flex-1"
                      onClick={handleExport}
                    >
                      <Download className="h-5 w-5 mr-2 inline" />
                      {t('actions.exportModel')}
                    </MovingBorderButton>
                    <Link href={`/${locale}/dashboard`} className="flex-1">
                      <HoverBorderGradient
                        containerClassName="w-full"
                        className="px-8 py-4 w-full text-center"
                        as="button"
                      >
                        {t('actions.newCompression')}
                      </HoverBorderGradient>
                    </Link>
                  </div>
                </GlareCard>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Export Dialog */}
      {compressionResult.jobId && (
        <ExportDialog
          isOpen={showExportDialog}
          onClose={() => setShowExportDialog(false)}
          jobId={compressionResult.jobId}
          modelName={compressionResult.modelName}
          compressionRatio={compressionResult.compressionRatio}
        />
      )}
    </div>
  )
}
