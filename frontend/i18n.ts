import { getRequestConfig } from 'next-intl/server'

export const locales = ['en', 'fr'] as const
export type Locale = (typeof locales)[number]

export const defaultLocale: Locale = 'en'

export default getRequestConfig(async ({ requestLocale }) => {
  // Get the locale from the URL segment
  let locale = await requestLocale
  
  // Fallback to default locale if undefined or invalid
  if (!locale || !locales.includes(locale as Locale)) {
    locale = defaultLocale
  }

  return {
    locale,
    messages: (await import(`./messages/${locale}.json`)).default,
  }
})

