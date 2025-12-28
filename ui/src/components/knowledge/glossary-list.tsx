'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import type { BusinessGlossary } from '@/lib/api/types';
import { useCreateGlossary, useUpdateGlossary, useDeleteGlossary } from '@/hooks/use-knowledge';

interface GlossaryListProps {
  items: BusinessGlossary[];
  connectionId: string;
}

export function GlossaryList({ items, connectionId }: GlossaryListProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [editItem, setEditItem] = useState<BusinessGlossary | null>(null);
  const [formData, setFormData] = useState({
    term: '',
    definition: '',
    synonyms: '',
    related_tables: '',
  });

  const createMutation = useCreateGlossary();
  const updateMutation = useUpdateGlossary();
  const deleteMutation = useDeleteGlossary();

  const resetForm = () => {
    setFormData({ term: '', definition: '', synonyms: '', related_tables: '' });
    setEditItem(null);
  };

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) resetForm();
  };

  const handleEdit = (item: BusinessGlossary) => {
    setEditItem(item);
    setFormData({
      term: item.term,
      definition: item.definition,
      synonyms: item.synonyms?.join(', ') || '',
      related_tables: item.related_tables?.join(', ') || '',
    });
    setIsOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      term: formData.term,
      definition: formData.definition,
      synonyms: formData.synonyms ? formData.synonyms.split(',').map((s) => s.trim()) : undefined,
      related_tables: formData.related_tables ? formData.related_tables.split(',').map((s) => s.trim()) : undefined,
    };

    if (editItem) {
      await updateMutation.mutateAsync({ id: editItem.id, data });
    } else {
      await createMutation.mutateAsync({ dbConnectionId: connectionId, data });
    }
    handleOpenChange(false);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this term?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Dialog open={isOpen} onOpenChange={handleOpenChange}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-2 h-4 w-4" />
              Add Term
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editItem ? 'Edit Term' : 'Add Glossary Term'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="term">Term</Label>
                <Input
                  id="term"
                  value={formData.term}
                  onChange={(e) => setFormData({ ...formData, term: e.target.value })}
                  placeholder="e.g., Revenue"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="definition">Definition</Label>
                <Textarea
                  id="definition"
                  value={formData.definition}
                  onChange={(e) => setFormData({ ...formData, definition: e.target.value })}
                  placeholder="What this term means in your business context..."
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="synonyms">Synonyms (comma-separated)</Label>
                <Input
                  id="synonyms"
                  value={formData.synonyms}
                  onChange={(e) => setFormData({ ...formData, synonyms: e.target.value })}
                  placeholder="income, sales, earnings"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="related_tables">Related Tables (comma-separated)</Label>
                <Input
                  id="related_tables"
                  value={formData.related_tables}
                  onChange={(e) => setFormData({ ...formData, related_tables: e.target.value })}
                  placeholder="orders, transactions"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {editItem ? 'Update' : 'Create'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {items.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">No glossary terms defined yet.</p>
            <p className="text-sm text-muted-foreground">
              Add business terms to help the AI understand your domain language.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((item) => (
            <Card key={item.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base">{item.term}</CardTitle>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(item)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(item.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-2">{item.definition}</p>
                {item.synonyms && item.synonyms.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {item.synonyms.map((syn) => (
                      <Badge key={syn} variant="secondary" className="text-xs">
                        {syn}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
