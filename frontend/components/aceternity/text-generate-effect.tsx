"use client"

import React from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/cn"

export const TextGenerateEffect = ({
  words,
  className,
  filter = true,
  duration = 0.5,
}: {
  words: string
  className?: string
  filter?: boolean
  duration?: number
}) => {
  const wordsArray = words.split(" ")

  return (
    <div className={cn("font-bold", className)}>
      <div className="text-white leading-snug tracking-wide inline-block">
        {wordsArray.map((word, idx) => {
          return (
            <React.Fragment key={`${word}-${idx}`}>
              <motion.span
                className="inline-block text-white"
                initial={{ opacity: 0, filter: filter ? "blur(10px)" : "none" }}
                animate={{ opacity: 1, filter: filter ? "blur(0px)" : "none" }}
                transition={{ 
                  duration: duration || 0.5, 
                  delay: idx * 0.15,
                  ease: "easeOut"
                }}
              >
                {word}
              </motion.span>
              {idx < wordsArray.length - 1 && (
                <span className="inline-block" style={{ width: "0.3em", minWidth: "0.3em" }} aria-hidden="true"> </span>
              )}
            </React.Fragment>
          )
        })}
      </div>
    </div>
  )
}

