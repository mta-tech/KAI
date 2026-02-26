'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Eye, EyeOff } from 'lucide-react';
import { useCreateConnection } from '@/hooks/use-connections';
import type { DatabaseConnection } from '@/lib/api/types';

interface ConnectionDialogProps {
  connection?: DatabaseConnection;
  trigger?: React.ReactNode;
}

export function ConnectionDialog({ connection, trigger }: ConnectionDialogProps) {
  const [open, setOpen] = useState(false);
  const [showUri, setShowUri] = useState(false);
  const [formData, setFormData] = useState({
    alias: connection?.alias || '',
    connection_uri: '',
    schemas: connection?.schemas?.join(', ') || '',
  });

  const createMutation = useCreateConnection();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await createMutation.mutateAsync({
      alias: formData.alias,
      connection_uri: formData.connection_uri,
      schemas: formData.schemas ? formData.schemas.split(',').map(s => s.trim()) : undefined,
    });

    setOpen(false);
    setFormData({ alias: '', connection_uri: '', schemas: '' });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Connection
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {connection ? 'Edit Connection' : 'Add Database Connection'}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="alias">Alias</Label>
            <Input
              id="alias"
              placeholder="my-database"
              value={formData.alias}
              onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="uri">Connection URI</Label>
            <div className="relative">
              <Input
                id="uri"
                type={showUri ? 'text' : 'password'}
                placeholder="postgresql://user:pass@host:5432/db"
                value={formData.connection_uri}
                onChange={(e) => setFormData({ ...formData, connection_uri: e.target.value })}
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowUri(!showUri)}
              >
                {showUri ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Format: dialect://user:password@host:port/database
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="schemas">Schemas (optional)</Label>
            <Input
              id="schemas"
              placeholder="public, sales, analytics"
              value={formData.schemas}
              onChange={(e) => setFormData({ ...formData, schemas: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated list of schemas to include
            </p>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
