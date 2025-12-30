'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2 } from 'lucide-react';
import { mdlApi } from '@/lib/api/mdl';
import { toast } from 'sonner';
import type { DatabaseConnection } from '@/lib/api/types';

interface MDLBuildDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  connection: DatabaseConnection | null;
}

export function MDLBuildDialog({ open, onOpenChange, connection }: MDLBuildDialogProps) {
  const router = useRouter();
  const [name, setName] = useState('');
  const [catalog, setCatalog] = useState('');
  const [schema, setSchema] = useState('');
  const [inferRelationships, setInferRelationships] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleBuild = async () => {
    if (!connection) return;

    if (!name.trim() || !catalog.trim() || !schema.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const result = await mdlApi.buildFromDatabase({
        db_connection_id: connection.id,
        name: name.trim(),
        catalog: catalog.trim(),
        schema: schema.trim(),
        infer_relationships: inferRelationships,
      });

      toast.success('MDL manifest built successfully!');
      onOpenChange(false);

      // Navigate to MDL page to view the manifest
      router.push(`/mdl?manifest=${result.manifest_id}`);
    } catch (error) {
      console.error('MDL build error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to build MDL manifest');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset form when dialog opens with new connection
  const handleOpenChange = (open: boolean) => {
    if (open && connection) {
      setName(`${connection.alias || 'database'}_mdl`);
      setCatalog(connection.schemas?.[0] || '');
      setSchema(connection.schemas?.[0] || '');
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Build MDL Manifest</DialogTitle>
          <DialogDescription>
            Generate a Metrics Definition Layer (MDL) manifest from {connection?.alias || 'database'} schema.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Manifest Name *</Label>
            <Input
              id="name"
              placeholder="e.g., my_data_model"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="catalog">Catalog *</Label>
            <Input
              id="catalog"
              placeholder="e.g., production"
              value={catalog}
              onChange={(e) => setCatalog(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              The database catalog name
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="schema">Schema *</Label>
            <Input
              id="schema"
              placeholder="e.g., public"
              value={schema}
              onChange={(e) => setSchema(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              The database schema to build MDL from
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="infer-relationships"
              checked={inferRelationships}
              onCheckedChange={(checked) => setInferRelationships(checked as boolean)}
            />
            <Label
              htmlFor="infer-relationships"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Automatically infer table relationships
            </Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleBuild} disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? 'Building...' : 'Build MDL'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
