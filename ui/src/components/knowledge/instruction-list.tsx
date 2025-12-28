'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import type { Instruction } from '@/lib/api/types';
import { useCreateInstruction, useUpdateInstruction, useDeleteInstruction } from '@/hooks/use-knowledge';

interface InstructionListProps {
  items: Instruction[];
  connectionId: string;
}

export function InstructionList({ items, connectionId }: InstructionListProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [editItem, setEditItem] = useState<Instruction | null>(null);
  const [content, setContent] = useState('');

  const createMutation = useCreateInstruction();
  const updateMutation = useUpdateInstruction();
  const deleteMutation = useDeleteInstruction();

  const resetForm = () => {
    setContent('');
    setEditItem(null);
  };

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) resetForm();
  };

  const handleEdit = (item: Instruction) => {
    setEditItem(item);
    setContent(item.content);
    setIsOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (editItem) {
      await updateMutation.mutateAsync({ id: editItem.id, data: { content } });
    } else {
      await createMutation.mutateAsync({ db_connection_id: connectionId, content });
    }
    handleOpenChange(false);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this instruction?')) {
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
              Add Instruction
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>{editItem ? 'Edit Instruction' : 'Add Custom Instruction'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="content">Instruction</Label>
                <Textarea
                  id="content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="When calculating totals, always exclude cancelled orders..."
                  className="min-h-[150px]"
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Provide specific instructions for how the AI should handle queries for this database.
                </p>
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
            <p className="text-muted-foreground">No custom instructions defined yet.</p>
            <p className="text-sm text-muted-foreground">
              Add instructions to guide how the AI interprets and responds to queries.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {items.map((item, index) => (
            <Card key={item.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-sm text-muted-foreground">
                    Instruction #{index + 1}
                  </CardTitle>
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
                <p className="text-sm whitespace-pre-wrap">{item.content}</p>
                <p className="mt-2 text-xs text-muted-foreground">
                  Created: {new Date(item.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
