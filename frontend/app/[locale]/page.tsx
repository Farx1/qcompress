'use client'

import { useTranslations, useLocale } from 'next-intl'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { motion } from 'framer-motion'
import { ArrowRight, Zap, Database, BarChart3, Download, Layers, Cpu } from 'lucide-react'
import { TextGenerateEffect } from '@/components/aceternity/text-generate-effect'
import { Button as MovingBorderButton } from '@/components/aceternity/moving-border'
import { GlareCard } from '@/components/aceternity/glare-card'
import { HoverBorderGradient } from '@/components/aceternity/hover-border-gradient'
import { LampContainer } from '@/components/aceternity/lamp-effect'
import { Timeline } from '@/components/aceternity/timeline'
import { BentoGrid, BentoGridItem } from '@/components/ui/bento-grid'
import { useAnimeLanding } from '@/lib/hooks/useAnimeLanding'

// Dynamic import for Three.js (avoid SSR)
const LLMAnimation = dynamic(
  () => import('@/components/LLMAnimation').then((mod) => mod.LLMAnimation),
  { ssr: false, loading: () => <div className="w-full h-full bg-black" /> }
)

export default function Home() {
  const t = useTranslations('home')
  const tCommon = useTranslations('common')
  const locale = useLocale()

  // Initialize anime.js animations
  useAnimeLanding()

  const timelineItems = [
    {
      title: t('howItWorks.step1.title'),
      description: t('howItWorks.step1.description'),
    },
    {
      title: t('howItWorks.step2.title'),
      description: t('howItWorks.step2.description'),
    },
    {
      title: t('howItWorks.step3.title'),
      description: t('howItWorks.step3.description'),
    },
    {
      title: t('howItWorks.step4.title'),
      description: t('howItWorks.step4.description'),
    },
    {
      title: t('howItWorks.step5.title'),
      description: t('howItWorks.step5.description'),
    },
    {
      title: t('howItWorks.step6.title'),
      description: t('howItWorks.step6.description'),
    },
  ]

  const features = [
    {
      title: t('features.item1.title'),
      description: t('features.item1.description'),
      icon: <Layers className="h-8 w-8 text-white" />,
      className: 'md:col-span-2',
    },
    {
      title: t('features.item2.title'),
      description: t('features.item2.description'),
      icon: <BarChart3 className="h-8 w-8 text-white" />,
    },
    {
      title: t('features.item3.title'),
      description: t('features.item3.description'),
      icon: <Cpu className="h-8 w-8 text-white" />,
    },
    {
      title: t('features.item4.title'),
      description: t('features.item4.description'),
      icon: <Download className="h-8 w-8 text-white" />,
    },
    {
      title: t('features.item5.title'),
      description: t('features.item5.description'),
      icon: <Zap className="h-8 w-8 text-white" />,
      className: 'md:col-span-2',
    },
  ]

  const stats = [
    { label: t('hero.stats.sizeReduction'), value: '50%', icon: Database },
    { label: t('hero.stats.performanceRetention'), value: '95%', icon: Cpu },
    { label: t('hero.stats.speedGain'), value: '38%', icon: Zap },
  ]

  return (
    <div className="relative min-h-screen overflow-hidden bg-black" style={{ position: 'relative' }}>
      {/* Hero Section with 3D Animation Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden" aria-label="Hero section">
        {/* Three.js Animation Background */}
        <div className="absolute inset-0 opacity-40">
          <LLMAnimation />
        </div>

        {/* Gradient overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black" />

        {/* Hero Content */}
        <div className="container mx-auto max-w-7xl relative z-10 px-4 py-32">
          <div className="text-center space-y-8" data-animate="fade-up">
            {/* Title with TextGenerateEffect */}
            <div className="space-y-4">
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-tight">
                <TextGenerateEffect
                  words={t('hero.title.line1') + ' ' + t('hero.title.line2') + ' ' + t('hero.title.line3')}
                  className="block"
                />
              </h1>
              {/* Fallback title in case animation doesn't work */}
              <noscript>
                <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-tight">
                  {t('hero.title.line1')} {t('hero.title.line2')} {t('hero.title.line3')}
                </h1>
              </noscript>
            </div>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed"
            >
              {t('hero.subtitle', {
                sizeReduction: '50%',
                performanceRetention: '95%',
              })}
            </motion.p>

            {/* CTA Buttons with MovingBorder */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
              className="flex flex-col sm:flex-row gap-6 justify-center items-center pt-8"
            >
              <Link href={`/${locale}/dashboard`} className="inline-block">
                <MovingBorderButton
                  borderRadius="1.5rem"
                  className="bg-black text-white border-white px-8 py-4 text-lg font-semibold"
                >
                  {t('hero.ctaPrimary')}
                  <ArrowRight className="ml-2 h-5 w-5 inline" />
                </MovingBorderButton>
              </Link>
              <Link href="#features" className="inline-block">
                <HoverBorderGradient
                  containerClassName="cursor-pointer"
                  className="text-lg font-medium px-8 py-4"
                >
                  {t('hero.ctaSecondary')}
                </HoverBorderGradient>
              </Link>
            </motion.div>

            {/* Stats with GlareCard */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 max-w-4xl mx-auto"
            >
              {stats.map((stat, index) => {
                const Icon = stat.icon
                return (
                  <GlareCard key={stat.label} className="p-6">
                    <div className="flex flex-col items-center text-center space-y-3">
                      <div className="p-3 rounded-lg bg-white/10">
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="text-4xl font-bold text-white">{stat.value}</div>
                      <div className="text-sm text-gray-400">{stat.label}</div>
                    </div>
                  </GlareCard>
                )
              })}
            </motion.div>
          </div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="w-6 h-10 border-2 border-white/30 rounded-full flex items-start justify-center p-2"
          >
            <motion.div className="w-1 h-2 bg-white rounded-full" />
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-32 px-4 bg-black" aria-labelledby="features-title">
        <div className="container mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16 space-y-4"
          >
            <h2 id="features-title" className="text-4xl md:text-6xl font-bold text-white">
              {t('features.title')}
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">{t('features.subtitle')}</p>
          </motion.div>

          <BentoGrid className="max-w-6xl mx-auto">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <HoverBorderGradient
                  containerClassName={`w-full h-full ${feature.className || ''}`}
                  className="p-8 h-full flex flex-col"
                >
                  <div className="flex items-center gap-4 mb-4">
                    {feature.icon}
                    <h3 className="text-xl font-bold text-white">{feature.title}</h3>
                  </div>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                </HoverBorderGradient>
              </motion.div>
            ))}
          </BentoGrid>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative py-32 px-4 bg-black" aria-labelledby="how-it-works-title">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16 space-y-4"
          >
            <h2 id="how-it-works-title" className="text-4xl md:text-6xl font-bold text-white">
              {t('howItWorks.title')}
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">{t('howItWorks.subtitle')}</p>
          </motion.div>

          <Timeline items={timelineItems} />
        </div>
      </section>

      {/* Benchmarks Section */}
      <section id="benchmarks" className="relative py-32 px-4 bg-black" aria-labelledby="benchmarks-title">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16 space-y-4"
          >
            <h2 id="benchmarks-title" className="text-4xl md:text-6xl font-bold text-white">
              {t('benchmarks.title')}
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">{t('benchmarks.subtitle')}</p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {[
              { name: 'GLUE Average', original: 86.7, compressed: 84.9, retention: 97.9 },
              { name: 'SQuAD F1', original: 94.2, compressed: 91.8, retention: 97.4 },
              { name: 'Perplexity', original: 24.3, compressed: 26.8, retention: 90.4 },
              { name: 'Latency (ms)', original: 22.1, compressed: 15.9, improvement: '38.5%' },
            ].map((bench, index) => (
              <motion.div
                key={bench.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <GlareCard className="p-8">
                  <h3 className="text-2xl font-bold text-white mb-6">{bench.name}</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">{t('benchmarks.original')}</span>
                        <span className="font-bold text-white">{bench.original}</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-white"
                          initial={{ width: 0 }}
                          whileInView={{ width: '100%' }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: index * 0.1 }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">{t('benchmarks.compressed')}</span>
                        <span className="font-bold text-white">{bench.compressed}</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gray-400"
                          initial={{ width: 0 }}
                          whileInView={{ width: `${(bench.compressed / bench.original) * 100}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: index * 0.1 + 0.2 }}
                        />
                      </div>
                    </div>
                    {bench.retention && (
                      <div className="pt-4 border-t border-white/10">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-400">{t('benchmarks.retention')}</span>
                          <span className="font-bold text-white">{bench.retention}%</span>
                        </div>
                      </div>
                    )}
                    {bench.improvement && (
                      <div className="pt-4 border-t border-white/10">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-400">Improvement</span>
                          <span className="font-bold text-white">+{bench.improvement}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </GlareCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section with LampEffect */}
      <section className="relative" aria-labelledby="cta-title">
        <LampContainer>
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.3,
              duration: 0.8,
              ease: "easeInOut",
            }}
            className="text-center space-y-8"
          >
            <h2 id="cta-title" className="text-4xl md:text-6xl lg:text-7xl font-bold text-white">
              {t('cta.title')}
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">{t('cta.subtitle')}</p>
            <Link href={`/${locale}/dashboard`}>
              <MovingBorderButton
                borderRadius="1.5rem"
                className="bg-black text-white border-white px-8 py-4 text-lg font-semibold"
              >
                {t('cta.button')}
                <ArrowRight className="ml-2 h-5 w-5 inline" />
              </MovingBorderButton>
            </Link>
          </motion.div>
        </LampContainer>
      </section>
    </div>
  )
}
