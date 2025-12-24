'use client'

import { useTranslations, useLocale } from 'next-intl'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Globe, Menu, X, Layers } from 'lucide-react'
import { locales, type Locale } from '@/i18n'
import { useState } from 'react'

interface AppShellProps {
  children: React.ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const t = useTranslations('common')
  const locale = useLocale() as Locale
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const switchLocale = (newLocale: Locale) => {
    const pathWithoutLocale = pathname.replace(`/${locale}`, '') || '/'
    window.location.href = `/${newLocale}${pathWithoutLocale}`
  }

  const isHomePage = pathname === `/${locale}` || pathname === `/${locale}/`
  const isDashboard = pathname?.includes('/dashboard')
  const isResults = pathname?.includes('/results')

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-black/80 backdrop-blur-xl" role="banner">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo & Brand */}
            <Link href={`/${locale}`} className="flex items-center gap-3 group">
              <div className="flex items-center gap-2">
                <Layers className="h-6 w-6 text-white" />
                <motion.span
                  className="text-xl font-bold text-white"
                  whileHover={{ scale: 1.05 }}
                >
                  {t('appName')}
                </motion.span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              {isHomePage && (
                <>
                  <a
                    href="#features"
                    className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
                  >
                    {t('features')}
                    <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300" />
                  </a>
                  <a
                    href="#how-it-works"
                    className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
                  >
                    {t('howItWorks')}
                    <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300" />
                  </a>
                  <a
                    href="#benchmarks"
                    className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group"
                  >
                    {t('benchmarks')}
                    <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300" />
                  </a>
                </>
              )}
              {!isHomePage && (
                <>
                  <Link
                    href={`/${locale}/dashboard`}
                    className={`text-sm font-medium transition-colors ${
                      isDashboard
                        ? 'text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {t('dashboard')}
                  </Link>
                  <Link
                    href={`/${locale}/results`}
                    className={`text-sm font-medium transition-colors ${
                      isResults
                        ? 'text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {t('results')}
                  </Link>
                </>
              )}
            </nav>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {/* Language Switcher */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-9 w-9 text-white hover:bg-white/10">
                    <Globe className="h-4 w-4" />
                    <span className="sr-only">Switch language</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-black border-white/20 text-white">
                  {locales.map((loc) => (
                    <DropdownMenuItem
                      key={loc}
                      onClick={() => switchLocale(loc)}
                      className={`cursor-pointer hover:bg-white/10 ${
                        loc === locale ? 'bg-white/10 font-bold' : ''
                      }`}
                    >
                      {loc.toUpperCase()}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Get Started CTA */}
              {isHomePage && (
                <Link href={`/${locale}/dashboard`} className="hidden md:block">
                  <Button className="bg-white text-black hover:bg-gray-200 font-semibold">
                    {t('getStarted')}
                  </Button>
                </Link>
              )}

              {/* Mobile Menu Toggle */}
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden h-9 w-9 text-white"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-white/10 bg-black"
          >
            <nav className="container mx-auto px-4 py-4 flex flex-col gap-4">
              {isHomePage && (
                <>
                  <a
                    href="#features"
                    className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {t('features')}
                  </a>
                  <a
                    href="#how-it-works"
                    className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {t('howItWorks')}
                  </a>
                  <a
                    href="#benchmarks"
                    className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {t('benchmarks')}
                  </a>
                  <Link href={`/${locale}/dashboard`} onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full bg-white text-black hover:bg-gray-200">
                      {t('getStarted')}
                    </Button>
                  </Link>
                </>
              )}
              {!isHomePage && (
                <>
                  <Link
                    href={`/${locale}/dashboard`}
                    className={`text-sm font-medium transition-colors ${
                      isDashboard ? 'text-white' : 'text-gray-400 hover:text-white'
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {t('dashboard')}
                  </Link>
                  <Link
                    href={`/${locale}/results`}
                    className={`text-sm font-medium transition-colors ${
                      isResults ? 'text-white' : 'text-gray-400 hover:text-white'
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {t('results')}
                  </Link>
                </>
              )}
            </nav>
          </motion.div>
        )}
      </header>

      {/* Main Content */}
      <main>{children}</main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-black text-gray-400">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-white" />
              <span className="text-sm font-medium text-white">{t('appName')}</span>
            </div>
            <p className="text-sm text-gray-500">
              © 2024 {t('appName')}. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
