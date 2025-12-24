"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface Sparkle {
  id: number
  x: number
  y: number
  delay: number
  duration: number
}

interface SparklesProps {
  className?: string
  count?: number
  colors?: string[]
}

export function Sparkles({
  className,
  count = 20,
  colors = ["#a855f7", "#06b6d4", "#10b981"],
}: SparklesProps) {
  const [sparkles, setSparkles] = useState<Sparkle[]>([])

  useEffect(() => {
    const newSparkles: Sparkle[] = Array.from({ length: count }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 2,
      duration: 1 + Math.random() * 2,
    }))
    setSparkles(newSparkles)
  }, [count])

  return (
    <div className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      {sparkles.map((sparkle) => (
        <motion.div
          key={sparkle.id}
          className="absolute w-1 h-1 rounded-full"
          style={{
            left: `${sparkle.x}%`,
            top: `${sparkle.y}%`,
            backgroundColor: colors[Math.floor(Math.random() * colors.length)],
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: sparkle.duration,
            delay: sparkle.delay,
            repeat: Infinity,
            repeatDelay: sparkle.duration,
          }}
        />
      ))}
    </div>
  )
}

