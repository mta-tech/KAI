'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/ui/loading-button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus } from 'lucide-react';
import { useBuildManifest } from '@/hooks/use-mdl';
import { useConnections } from '@/hooks/use-connections';

export function CreateManifestDialog() {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    db_connection_id: '',
    name: '',
    catalog: 'default',
    schema: 'public',
    infer_relationships: true,
  });

  const { data: connections = [] } = useConnections();
  const buildMutation = useBuildManifest();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await buildMutation.mutateAsync(formData);
    setOpen(false);
    setFormData({
      db_connection_id: '',
      name: '',
      catalog: 'default',
      schema: 'public',
      infer_relationships: true,
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Build from Database
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create MDL Manifest</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Database Connection</Label>
            <Select
              value={formData.db_connection_id}
              onValueChange={(v) => setFormData({ ...formData, db_connection_id: v })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select connection" />
              </SelectTrigger>
              <SelectContent>
                {connections.map((conn) => (
                  <SelectItem key={conn.id} value={conn.id}>
                    {conn.alias || conn.id.slice(0, 8)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Manifest Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Semantic Layer"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="catalog">Catalog</Label>
              <Input
                id="catalog"
                value={formData.catalog}
                onChange={(e) => setFormData({ ...formData, catalog: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="schema">Schema</Label>
              <Input
                id="schema"
                value={formData.schema}
                onChange={(e) => setFormData({ ...formData, schema: e.target.value })}
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="infer"
              checked={formData.infer_relationships}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, infer_relationships: !!checked })
              }
            />
            <Label htmlFor="infer" className="text-sm">
              Auto-infer relationships from foreign keys
            </Label>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <LoadingButton type="submit" isLoading={buildMutation.isPending} loadingText="Creating...">
              Create
            </LoadingButton>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
