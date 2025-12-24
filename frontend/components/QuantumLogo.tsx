'use client'

import { motion } from 'framer-motion'

interface QuantumLogoProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function QuantumLogo({ className = '', size = 'md' }: QuantumLogoProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  }

  const textSizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  }

  return (
    <motion.div
      className={`relative ${className}`}
      whileHover={{ scale: 1.05 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      <div className="relative">
        {/* Outer glow ring */}
        <motion.div
          className="absolute inset-0 rounded-xl"
          animate={{
            boxShadow: [
              '0 0 20px rgba(168, 85, 247, 0.3)',
              '0 0 30px rgba(6, 182, 212, 0.4)',
              '0 0 20px rgba(168, 85, 247, 0.3)',
            ],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        
        {/* Main logo container */}
        <div className={`relative ${sizeClasses[size]} rounded-xl bg-gradient-to-br from-quantum-purple-500 via-quantum-purple-600 to-quantum-cyan-500 p-1.5`}>
          {/* Inner gradient */}
          <div className="h-full w-full rounded-lg bg-gradient-to-br from-quantum-purple-400 to-quantum-cyan-400 flex items-center justify-center relative overflow-hidden">
            {/* Animated background pattern */}
            <motion.div
              className="absolute inset-0 opacity-20"
              animate={{
                backgroundPosition: ['0% 0%', '100% 100%'],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                repeatType: 'reverse',
              }}
              style={{
                backgroundImage: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)',
                backgroundSize: '200% 200%',
              }}
            />
            
            {/* Q letter */}
            <span className={`relative z-10 text-white font-bold ${textSizes[size]} tracking-tight`}>
              Q
            </span>
            
            {/* Quantum particles */}
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full"
                animate={{
                  x: [
                    Math.random() * 20 - 10,
                    Math.random() * 20 - 10,
                    Math.random() * 20 - 10,
                  ],
                  y: [
                    Math.random() * 20 - 10,
                    Math.random() * 20 - 10,
                    Math.random() * 20 - 10,
                  ],
                  opacity: [0.3, 0.8, 0.3],
                }}
                transition={{
                  duration: 2 + Math.random() * 2,
                  repeat: Infinity,
                  delay: i * 0.5,
                }}
                style={{
                  left: '50%',
                  top: '50%',
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

