'use client';

import { useLanguage } from './language-context';
import { t } from './translations';

export function useTranslation() {
  try {
    const { language } = useLanguage();
    return {
      t: (key: string) => t(key, language),
      language,
    };
  } catch (error) {
    // Fallback to English if context is not available
    return {
      t: (key: string) => t(key, 'en'),
      language: 'en' as const,
    };
  }
}
