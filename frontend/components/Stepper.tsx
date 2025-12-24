'use client'

import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StepperProps {
  steps: { id: string; label: string }[]
  currentStep: string
  onStepClick?: (stepId: string) => void
}

export function Stepper({ steps, currentStep, onStepClick }: StepperProps) {
  const currentIndex = steps.findIndex((s) => s.id === currentStep)

  return (
    <div className="flex items-center gap-4 w-full">
      {steps.map((step, index) => {
        const isActive = step.id === currentStep
        const isCompleted = index < currentIndex
        const isClickable = onStepClick && (isCompleted || isActive)

        return (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex flex-col items-center flex-1">
              <button
                onClick={() => isClickable && onStepClick?.(step.id)}
                disabled={!isClickable}
                className={cn(
                  'flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all',
                  isActive
                    ? 'border-primary bg-primary/20 text-primary'
                    : isCompleted
                    ? 'border-quantum-emerald-500 bg-quantum-emerald-500/20 text-quantum-emerald-300'
                    : 'border-muted bg-muted text-muted-foreground',
                  isClickable && 'cursor-pointer hover:scale-105'
                )}
              >
                {isCompleted ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <span className="font-semibold">{index + 1}</span>
                )}
              </button>
              <span
                className={cn(
                  'mt-2 text-xs font-medium text-center',
                  isActive ? 'text-foreground' : 'text-muted-foreground'
                )}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className="flex-1 h-0.5 mx-2 bg-muted">
                <div
                  className={cn(
                    'h-full transition-all duration-300',
                    isCompleted
                      ? 'bg-gradient-to-r from-quantum-emerald-500 to-quantum-cyan-500'
                      : 'bg-muted'
                  )}
                  style={{ width: isCompleted ? '100%' : '0%' }}
                />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

