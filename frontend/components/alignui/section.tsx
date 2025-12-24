import * as React from 'react'
import { cn } from './cn'

export function Container({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8', className)} {...props} />
}

export function Section({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  return <section className={cn('relative py-20 md:py-28', className)} {...props} />
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  className,
}: {
  eyebrow?: React.ReactNode
  title: React.ReactNode
  description?: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn('mx-auto max-w-3xl text-center', className)}>
      {eyebrow ? <div className="mb-4 flex justify-center">{eyebrow}</div> : null}
      <h2 className="text-balance text-3xl md:text-5xl font-semibold tracking-tight text-white">
        {title}
      </h2>
      {description ? (
        <p className="mt-4 text-pretty text-base md:text-lg text-white/65">{description}</p>
      ) : null}
    </div>
  )
}


