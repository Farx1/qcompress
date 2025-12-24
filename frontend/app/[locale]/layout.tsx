import { NextIntlClientProvider } from 'next-intl'
import { getMessages } from 'next-intl/server'
import { notFound } from 'next/navigation'
import { locales } from '@/i18n'
import Providers from '../providers'
import AppShell from '@/components/AppShell'
import '../globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'QCompress — TT Compression for LLMs',
  description: 'Compress your language models up to 10x with Tensor-Train decomposition without losing performance.',
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params

  if (!locales.includes(locale as any)) {
    notFound()
  }

  // Import messages directly
  let messages
  try {
    messages = (await import(`../../messages/${locale}.json`)).default
  } catch (error) {
    console.error(`Failed to load messages for locale ${locale}:`, error)
    notFound()
  }

  return (
    <html lang={locale} className="dark" suppressHydrationWarning>
      <body className="antialiased">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Providers>
            <AppShell>{children}</AppShell>
          </Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}

