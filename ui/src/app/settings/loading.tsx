import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function SettingsLoading() {
  return (
    <div className="h-full flex flex-col">
      {/* Header Skeleton */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-7 w-48" />
          <Skeleton className="h-9 w-24" />
        </div>
      </div>

      {/* Content Skeleton */}
      <div className="flex-1 flex">
        {/* Sidebar Skeleton */}
        <div className="w-64 border-r">
          <div className="p-4 border-b">
            <Skeleton className="h-9 w-full" />
          </div>
          <div className="p-2 space-y-1">
            {[...Array(7)].map((_, i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        </div>

        {/* Settings Content Skeleton */}
        <div className="flex-1 p-6">
          <div className="mb-6">
            <Skeleton className="h-6 w-40 mb-2" />
            <Skeleton className="h-4 w-60" />
          </div>

          <div className="space-y-6">
            {[...Array(3)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-5 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </CardHeader>
                <CardContent className="space-y-4">
                  {[...Array(2)].map((_, j) => (
                    <div key={j} className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                      <Skeleton className="h-9 w-24" />
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
