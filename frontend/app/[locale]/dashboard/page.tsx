'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTranslations, useLocale } from 'next-intl'
import { Activity, BarChart3, Network, MessageSquare, Plus, Layers } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { GridBackground } from '@/components/aceternity/grid-background'
import { HoverBorderGradient } from '@/components/aceternity/hover-border-gradient'
import { GlareCard } from '@/components/aceternity/glare-card'
import Dashboard from '@/components/Dashboard'
import CompressionMonitor from '@/components/CompressionMonitor'
import ChatInterface from '@/components/ChatInterface'
import CompressionWizard from '@/components/CompressionWizard'
import { apiClient } from '@/lib/api'

type TabId = 'overview' | 'monitor' | 'bench' | 'tt' | 'chat'

export default function DashboardPage() {
  const t = useTranslations('dashboard')
  const tCommon = useTranslations('common')
  const locale = useLocale()
  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const [showWizard, setShowWizard] = useState(false)
  const [isLaunching, setIsLaunching] = useState(false)

  const tabs = [
    { id: 'overview' as const, label: t('overview'), icon: Activity },
    { id: 'monitor' as const, label: t('monitoring'), icon: Activity },
    { id: 'bench' as const, label: t('benchmarks'), icon: BarChart3 },
    { id: 'tt' as const, label: t('ttCores'), icon: Network },
    { id: 'chat' as const, label: t('chatArena'), icon: MessageSquare },
  ] as const

  const handleWizardSubmit = async (config: any) => {
    setIsLaunching(true)
    try {
      await apiClient.startCompression(config)
    } catch (error) {
      console.error('Error starting compression:', error)
    } finally {
      setIsLaunching(false)
      setShowWizard(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-black">
      <GridBackground />

      {/* Main Content */}
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
              <span className="text-white font-medium">{t('title')}</span>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">{t('title')}</h1>
              <p className="text-lg text-gray-400">
                Tensor-Train compression for large language models
              </p>
            </div>
            <HoverBorderGradient
              containerClassName="inline-block"
              className="px-6 py-3"
              onClick={() => setShowWizard(true)}
              as="button"
            >
              <Plus className="h-4 w-4 mr-2 inline" />
              New Compression
            </HoverBorderGradient>
          </div>

          {/* Info Cards */}
          <div className="grid gap-6 md:grid-cols-3">
            <GlareCard className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-lg bg-white/10">
                  <Layers className="h-6 w-6 text-white" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-400 mb-1">Technology</div>
                  <div className="text-lg font-bold text-white mb-1">Tensor-Train</div>
                  <div className="text-sm text-gray-500">Decomposition method for efficient compression</div>
                </div>
              </div>
            </GlareCard>

            <GlareCard className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-lg bg-white/10">
                  <Activity className="h-6 w-6 text-white" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-400 mb-1">Monitoring</div>
                  <div className="text-lg font-bold text-white mb-1">Real-time</div>
                  <div className="text-sm text-gray-500">WebSocket updates during compression</div>
                </div>
              </div>
            </GlareCard>

            <GlareCard className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-lg bg-white/10">
                  <MessageSquare className="h-6 w-6 text-white" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-400 mb-1">Testing</div>
                  <div className="text-lg font-bold text-white mb-1">Chat Arena</div>
                  <div className="text-sm text-gray-500">Compare model outputs side-by-side</div>
                </div>
              </div>
            </GlareCard>
          </div>
        </motion.div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabId)} className="space-y-8">
          <TabsList className="bg-black border border-white/20 p-1 rounded-lg inline-flex gap-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <TabsTrigger
                  key={tab.id}
                  value={tab.id}
                  className="data-[state=active]:bg-white data-[state=active]:text-black text-white hover:text-white/80 transition-colors rounded-md px-4 py-2 flex items-center gap-2"
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </TabsTrigger>
              )
            })}
          </TabsList>

          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <TabsContent value="overview" className="mt-0">
                <Dashboard />
              </TabsContent>

              <TabsContent value="monitor" className="mt-0">
                <CompressionMonitor initialTab="monitor" />
              </TabsContent>

              <TabsContent value="bench" className="mt-0">
                <CompressionMonitor initialTab="benchmark" />
              </TabsContent>

              <TabsContent value="tt" className="mt-0">
                <CompressionMonitor initialTab="visualization" />
              </TabsContent>

              <TabsContent value="chat" className="mt-0">
                <ChatInterface />
              </TabsContent>
            </motion.div>
          </AnimatePresence>
        </Tabs>
      </main>

      {/* Compression Wizard */}
      <CompressionWizard
        isOpen={showWizard}
        onClose={() => setShowWizard(false)}
        onSubmit={handleWizardSubmit}
        isLoading={isLaunching}
      />
    </div>
  )
}
