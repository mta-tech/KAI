'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Download, Trash2, ExternalLink } from 'lucide-react';
import type { MDLManifest } from '@/lib/api/types';
import { useDeleteManifest, useExportManifest } from '@/hooks/use-mdl';

interface ManifestCardProps {
  manifest: MDLManifest;
}

export function ManifestCard({ manifest }: ManifestCardProps) {
  const deleteMutation = useDeleteManifest();
  const exportMutation = useExportManifest();

  const handleDelete = () => {
    if (confirm('Delete this manifest?')) {
      deleteMutation.mutate(manifest.id);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle className="text-base">
            {manifest.name || `Manifest ${manifest.id.slice(0, 8)}`}
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            {manifest.catalog}.{manifest.schema}
          </p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/mdl/${manifest.id}`}>
                <ExternalLink className="mr-2 h-4 w-4" />
                View Details
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => exportMutation.mutate(manifest.id)}>
              <Download className="mr-2 h-4 w-4" />
              Export JSON
            </DropdownMenuItem>
            <DropdownMenuItem className="text-destructive" onClick={handleDelete}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Badge variant="secondary">{manifest.models.length} models</Badge>
          <Badge variant="secondary">{manifest.relationships.length} relationships</Badge>
          {manifest.data_source && (
            <Badge variant="outline">{manifest.data_source}</Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
