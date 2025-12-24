"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface Meteor {
  id: number
  left: number
  delay: number
  duration: number
}

interface MeteorsProps {
  number?: number
  className?: string
}

export function Meteors({ number = 20, className }: MeteorsProps) {
  const [meteors, setMeteors] = useState<Meteor[]>([])

  useEffect(() => {
    const newMeteors: Meteor[] = Array.from({ length: number }, (_, i) => ({
      id: i,
      left: Math.floor(Math.random() * (400 - -400) + -400) + "%",
      delay: Math.random() * (0.8 - 0.2) + 0.2,
      duration: Math.random() * (3 - 1) + 1,
    }))
    setMeteors(newMeteors)
  }, [number])

  return (
    <>
      {meteors.map((meteor) => (
        <span
          key={meteor.id}
          className={cn(
            "animate-meteor-effect absolute top-1/2 left-1/2 h-0.5 w-0.5 rounded-[9999px] bg-slate-500 shadow-[0_0_0_1px_#ffffff10] rotate-[215deg]",
            "before:content-[''] before:absolute before:top-1/2 before:transform before:-translate-y-[50%] before:w-[50px] before:h-[1px] before:bg-gradient-to-r before:from-[#64748b] before:to-transparent",
            className
          )}
          style={{
            top: 0,
            left: meteor.left,
            animationDelay: `${meteor.delay}s`,
            animationDuration: `${meteor.duration}s`,
          }}
        ></span>
      ))}
    </>
  )
}

