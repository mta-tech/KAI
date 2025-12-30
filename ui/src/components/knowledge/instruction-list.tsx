'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
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
  const [condition, setCondition] = useState('');
  const [rules, setRules] = useState('');
  const [isDefault, setIsDefault] = useState(false);

  const createMutation = useCreateInstruction();
  const updateMutation = useUpdateInstruction();
  const deleteMutation = useDeleteInstruction();

  const resetForm = () => {
    setCondition('');
    setRules('');
    setIsDefault(false);
    setEditItem(null);
  };

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) resetForm();
  };

  const handleEdit = (item: Instruction) => {
    setEditItem(item);
    setCondition(item.condition);
    setRules(item.rules);
    setIsDefault(item.is_default);
    setIsOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (editItem) {
      await updateMutation.mutateAsync({ id: editItem.id, data: { condition, rules, is_default: isDefault } });
    } else {
      await createMutation.mutateAsync({ db_connection_id: connectionId, condition, rules, is_default: isDefault });
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
                <Label htmlFor="condition">Condition</Label>
                <Textarea
                  id="condition"
                  value={condition}
                  onChange={(e) => setCondition(e.target.value)}
                  placeholder="When the user asks about sales data..."
                  className="min-h-[80px]"
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Describe when this instruction should apply.
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="rules">Rules</Label>
                <Textarea
                  id="rules"
                  value={rules}
                  onChange={(e) => setRules(e.target.value)}
                  placeholder="Always exclude cancelled orders from calculations..."
                  className="min-h-[100px]"
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Specify the rules the AI should follow when the condition is met.
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_default"
                  checked={isDefault}
                  onCheckedChange={(checked) => setIsDefault(checked === true)}
                />
                <Label htmlFor="is_default" className="text-sm font-normal">
                  Apply as default instruction for all queries
                </Label>
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
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-sm text-muted-foreground">
                      Instruction #{index + 1}
                    </CardTitle>
                    {item.is_default && (
                      <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                        Default
                      </span>
                    )}
                  </div>
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
              <CardContent className="space-y-2">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Condition:</p>
                  <p className="text-sm whitespace-pre-wrap">{item.condition}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Rules:</p>
                  <p className="text-sm whitespace-pre-wrap">{item.rules}</p>
                </div>
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
