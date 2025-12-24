"use client"

import { motion, useScroll, useTransform } from "framer-motion"
import { useRef } from "react"
import { cn } from "@/lib/utils"
import { IconType } from "react-icons"

export interface TimelineItem {
  title: string
  description: string
  icon?: IconType | React.ComponentType
  date?: string
}

interface TimelineProps {
  items: TimelineItem[]
  className?: string
}

export function Timeline({ items, className }: TimelineProps) {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  })

  return (
    <div ref={ref} className={cn("relative", className)}>
      {items.map((item, index) => {
        const y = useTransform(
          scrollYProgress,
          [0, 1],
          [50 * index, -50 * (items.length - index)]
        )
        const opacity = useTransform(
          scrollYProgress,
          [
            (index - 1) / items.length,
            index / items.length,
            (index + 1) / items.length,
          ],
          [0.3, 1, 0.3]
        )

        return (
          <motion.div
            key={index}
            style={{ y, opacity }}
            className="flex gap-4 mb-8"
          >
            <div className="flex flex-col items-center">
              <div className="h-12 w-12 rounded-full bg-gradient-to-br from-quantum-purple-500 to-quantum-cyan-500 flex items-center justify-center text-white font-bold shadow-lg">
                {item.icon ? (
                  <item.icon className="h-6 w-6" />
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              {index < items.length - 1 && (
                <div className="w-0.5 h-full bg-gradient-to-b from-quantum-purple-500/50 to-quantum-cyan-500/50 mt-2" />
              )}
            </div>
            <div className="flex-1 pt-2">
              <h3 className="text-xl font-bold text-foreground mb-2">
                {item.title}
              </h3>
              <p className="text-muted-foreground">{item.description}</p>
              {item.date && (
                <p className="text-sm text-muted-foreground/70 mt-1">
                  {item.date}
                </p>
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

