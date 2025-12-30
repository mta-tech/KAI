'use client';

import { useConnections } from '@/hooks/use-connections';
import { ConnectionTable } from '@/components/connections/connection-table';
import { ConnectionDialog } from '@/components/connections/connection-dialog';
import { ScanProgressBanner } from '@/components/connections/scan-progress-banner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function ConnectionsPage() {
  const { data: connections, isLoading, error } = useConnections();

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-destructive">Failed to load connections: {error.message}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-muted-foreground">
            Manage your database connections for KAI analysis.
          </p>
        </div>
        <ConnectionDialog />
      </div>

      <ScanProgressBanner />

      <Card>
        <CardHeader>
          <CardTitle>Connections</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : (
            <ConnectionTable connections={connections || []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
