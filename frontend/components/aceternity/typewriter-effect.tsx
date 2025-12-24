"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

export function TypewriterEffect({
  words,
  className,
  cursorClassName,
}: {
  words: {
    text: string
    className?: string
  }[]
  className?: string
  cursorClassName?: string
}) {
  const wordsArray = words.map((word) => ({
    ...word,
    text: word.text.split(""),
  }))

  const [currentWordIndex, setCurrentWordIndex] = useState(0)
  const [currentCharIndex, setCurrentCharIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)
  const [displayedText, setDisplayedText] = useState("")

  useEffect(() => {
    const currentWord = wordsArray[currentWordIndex]

    if (!isDeleting && currentCharIndex < currentWord.text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + currentWord.text[currentCharIndex])
        setCurrentCharIndex((prev) => prev + 1)
      }, 100)
      return () => clearTimeout(timeout)
    } else if (!isDeleting && currentCharIndex === currentWord.text.length) {
      const timeout = setTimeout(() => {
        setIsDeleting(true)
      }, 2000)
      return () => clearTimeout(timeout)
    } else if (isDeleting && currentCharIndex > 0) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev.slice(0, -1))
        setCurrentCharIndex((prev) => prev - 1)
      }, 50)
      return () => clearTimeout(timeout)
    } else if (isDeleting && currentCharIndex === 0) {
      setIsDeleting(false)
      setCurrentWordIndex((prev) => (prev + 1) % wordsArray.length)
    }
  }, [currentCharIndex, isDeleting, currentWordIndex, wordsArray])

  return (
    <div className={cn("flex space-x-1 my-6", className)}>
      <motion.div className="overflow-hidden">
        {wordsArray[currentWordIndex].text.map((char, index) => {
          return (
            <motion.span
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.25,
                delay: index * 0.05,
              }}
              key={`${char}-${index}`}
              className={cn(
                "dark:text-white text-black",
                wordsArray[currentWordIndex].className
              )}
            >
              {index < displayedText.length ? displayedText[index] : char}
            </motion.span>
          )
        })}
      </motion.div>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          repeatType: "reverse",
        }}
        className={cn(
          "block rounded-sm w-[4px] h-4 bg-blue-500",
          cursorClassName
        )}
      ></motion.span>
    </div>
  )
}

