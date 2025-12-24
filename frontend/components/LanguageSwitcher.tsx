'use client';

import { motion } from 'motion/react';
import { useLanguage } from '@/lib/language-context';
import { useEffect, useState } from 'react';

export default function LanguageSwitcher() {
  const [mounted, setMounted] = useState(false);
  const [language, setLanguageState] = useState<'en' | 'fr'>('en');

  useEffect(() => {
    setMounted(true);
    try {
      const { language: currentLang, setLanguage } = useLanguage();
      setLanguageState(currentLang);
    } catch (error) {
      // Fallback if context not available
      const saved = localStorage.getItem('language') as 'en' | 'fr' | null;
      if (saved) {
        setLanguageState(saved);
      }
    }
  }, []);

  const handleLanguageChange = (lang: 'en' | 'fr') => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
    try {
      const { setLanguage } = useLanguage();
      setLanguage(lang);
    } catch (error) {
      // Fallback if context not available
    }
  };

  if (!mounted) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex items-center gap-2 bg-white/10 rounded-lg p-1 backdrop-blur-sm border border-white/20"
    >
      <button
        onClick={() => handleLanguageChange('en')}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
          language === 'en'
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
            : 'text-white/60 hover:text-white/80'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => handleLanguageChange('fr')}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
          language === 'fr'
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
            : 'text-white/60 hover:text-white/80'
        }`}
      >
        FR
      </button>
    </motion.div>
  );
}
