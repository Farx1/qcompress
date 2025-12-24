import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader } from '@/components/ui/card'

export function ChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40" />
        <Skeleton className="h-4 w-56 mt-2" />
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-end gap-2 h-48">
            {Array.from({ length: 12 }).map((_, i) => (
              <Skeleton 
                key={i} 
                className="flex-1" 
                style={{ height: `${Math.random() * 100 + 50}px` }}
              />
            ))}
          </div>
          <div className="flex justify-between">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

