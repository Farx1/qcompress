"use client"

import { cn } from "@/lib/utils"

interface GridBackgroundProps {
  className?: string
  children?: React.ReactNode
}

export function GridBackground({ className, children }: GridBackgroundProps) {
  return (
    <div
      className={cn(
        "absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px]",
        className
      )}
    >
      <div className="absolute pointer-events-none inset-0 flex items-center justify-center bg-background [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]"></div>
      {children}
    </div>
  )
}

