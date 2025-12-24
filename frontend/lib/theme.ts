/**
 * Quantum theme tokens for QCompress
 * Combines Shadcn UI theme with quantum-inspired colors
 */

export const quantumTheme = {
  colors: {
    quantum: {
      purple: {
        50: '#faf5ff',
        100: '#f3e8ff',
        200: '#e9d5ff',
        300: '#d8b4fe',
        400: '#c084fc',
        500: '#a855f7',
        600: '#9333ea',
        700: '#7e22ce',
        800: '#6b21a8',
        900: '#581c87',
      },
      cyan: {
        50: '#ecfeff',
        100: '#cffafe',
        200: '#a5f3fc',
        300: '#67e8f9',
        400: '#22d3ee',
        500: '#06b6d4',
        600: '#0891b2',
        700: '#0e7490',
        800: '#155e75',
        900: '#164e63',
      },
      emerald: {
        50: '#ecfdf5',
        100: '#d1fae5',
        200: '#a7f3d0',
        300: '#6ee7b7',
        400: '#34d399',
        500: '#10b981',
        600: '#059669',
        700: '#047857',
        800: '#065f46',
        900: '#064e3b',
      },
    },
  },
  gradients: {
    primary: 'linear-gradient(135deg, #a855f7 0%, #06b6d4 100%)',
    secondary: 'linear-gradient(135deg, #06b6d4 0%, #10b981 100%)',
    accent: 'linear-gradient(135deg, #10b981 0%, #a855f7 100%)',
  },
  shadows: {
    glow: '0 0 20px rgba(168, 85, 247, 0.4)',
    'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.4)',
    'glow-emerald': '0 0 20px rgba(16, 185, 129, 0.4)',
  },
} as const

