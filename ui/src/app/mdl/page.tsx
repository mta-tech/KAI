'use client';

import { useManifests } from '@/hooks/use-mdl';
import { ManifestCard } from '@/components/mdl/manifest-card';
import { CreateManifestDialog } from '@/components/mdl/create-manifest-dialog';
import { Skeleton } from '@/components/ui/skeleton';

export default function MDLPage() {
  const { data: manifests = [], isLoading } = useManifests();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          Manage semantic layer definitions for your databases.
        </p>
        <CreateManifestDialog />
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      ) : manifests.length === 0 ? (
        <div className="rounded-md border p-8 text-center">
          <p className="text-muted-foreground">No MDL manifests yet.</p>
          <p className="text-sm text-muted-foreground">
            Create one by building from a database connection.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {manifests.map((manifest) => (
            <ManifestCard key={manifest.id} manifest={manifest} />
          ))}
        </div>
      )}
    </div>
  );
}
