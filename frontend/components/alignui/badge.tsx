import * as React from 'react'
import { cn } from './cn'

type Variant = 'glow' | 'soft' | 'outline'

export function Badge({
  className,
  variant = 'soft',
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { variant?: Variant }) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold tracking-wide',
        variant === 'soft' && 'bg-white/6 text-white/85 border border-white/10',
        variant === 'outline' && 'bg-transparent text-white/80 border border-white/14',
        variant === 'glow' &&
          'bg-gradient-to-r from-quantum-purple-500/15 via-quantum-cyan-500/10 to-quantum-emerald-500/15 text-white border border-white/10 shadow-[0_0_0_1px_rgba(255,255,255,0.06),0_0_35px_rgba(168,85,247,0.15)]',
        className
      )}
      {...props}
    />
  )
}


