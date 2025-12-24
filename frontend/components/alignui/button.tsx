'use client'

import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cn } from './cn'

type Variant = 'primary' | 'secondary' | 'ghost' | 'outline'
type Size = 'sm' | 'md' | 'lg'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
  variant?: Variant
  size?: Size
}

export function Button({
  asChild,
  className,
  variant = 'primary',
  size = 'md',
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : 'button'

  return (
    <Comp
      className={cn(
        'relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl font-medium',
        'transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-quantum-purple-500/60',
        'disabled:pointer-events-none disabled:opacity-50',
        size === 'sm' && 'h-9 px-3 text-sm',
        size === 'md' && 'h-11 px-4 text-sm',
        size === 'lg' && 'h-12 px-5 text-base',
        variant === 'primary' &&
          'bg-gradient-to-r from-quantum-purple-500 via-quantum-cyan-500 to-quantum-emerald-500 text-white shadow-lg shadow-quantum-purple-500/20 hover:shadow-quantum-cyan-500/25',
        variant === 'secondary' &&
          'bg-white/7 text-white border border-white/12 hover:bg-white/10 hover:border-white/18',
        variant === 'outline' &&
          'bg-transparent text-white border border-white/14 hover:bg-white/6 hover:border-white/24',
        variant === 'ghost' && 'bg-transparent text-white/80 hover:text-white hover:bg-white/6',
        className
      )}
      {...props}
    />
  )
}


