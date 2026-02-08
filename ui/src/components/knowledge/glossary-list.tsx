'use client';

import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/ui/loading-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, Pencil, Trash2, BookOpen, Search, Grid3x3, List, ArrowUpDown } from 'lucide-react';
import type { BusinessGlossary } from '@/lib/api/types';
import { useCreateGlossary, useUpdateGlossary, useDeleteGlossary } from '@/hooks/use-knowledge';

type ViewMode = 'grid' | 'list';
type SortBy = 'name' | 'date' | 'tables';

interface GlossaryListProps {
  items: BusinessGlossary[];
  connectionId: string;
}

export function GlossaryList({ items, connectionId }: GlossaryListProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [editItem, setEditItem] = useState<BusinessGlossary | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState<SortBy>('name');
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({
    term: '',
    definition: '',
    synonyms: '',
    related_tables: '',
  });

  const createMutation = useCreateGlossary();
  const updateMutation = useUpdateGlossary();
  const deleteMutation = useDeleteGlossary();

  // Filter and sort items
  const filteredAndSortedItems = useMemo(() => {
    let filtered = items;

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (item) =>
          item.term.toLowerCase().includes(query) ||
          item.definition.toLowerCase().includes(query) ||
          item.synonyms?.some((s) => s.toLowerCase().includes(query))
      );
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.term.localeCompare(b.term);
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'tables':
          const aTables = a.related_tables?.length || 0;
          const bTables = b.related_tables?.length || 0;
          return bTables - aTables;
        default:
          return 0;
      }
    });

    return sorted;
  }, [items, searchQuery, sortBy]);

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
      {/* Header with actions */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search terms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Sort */}
          <Select value={sortBy} onValueChange={(v: SortBy) => setSortBy(v)}>
            <SelectTrigger className="w-[140px]">
              <ArrowUpDown className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Sort by..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="name">Name</SelectItem>
              <SelectItem value="date">Date</SelectItem>
              <SelectItem value="tables">Tables</SelectItem>
            </SelectContent>
          </Select>

          {/* View toggle */}
          <div className="flex border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="sm"
              className="rounded-r-none"
              onClick={() => setViewMode('grid')}
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'secondary' : 'ghost'}
              size="sm"
              className="rounded-l-none"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          {/* Add button */}
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
                  <LoadingButton
                    type="submit"
                    isLoading={createMutation.isPending || updateMutation.isPending}
                    loadingText={editItem ? 'Updating...' : 'Creating...'}
                  >
                    {editItem ? 'Update' : 'Create'}
                  </LoadingButton>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Results count */}
      {searchQuery && (
        <p className="text-sm text-muted-foreground">
          Found {filteredAndSortedItems.length} of {items.length} terms
        </p>
      )}

      {filteredAndSortedItems.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title={searchQuery ? 'No matching terms found' : 'No glossary terms yet'}
          description={
            searchQuery
              ? 'Try adjusting your search query'
              : 'Add business terms to help the AI understand your domain language and improve query accuracy.'
          }
          action={
            !searchQuery
              ? {
                  label: 'Add Your First Term',
                  onClick: () => setIsOpen(true),
                }
              : undefined
          }
        />
      ) : viewMode === 'grid' ? (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredAndSortedItems.map((item) => (
            <GlossaryCard
              key={item.id}
              item={item}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredAndSortedItems.map((item) => (
            <GlossaryListItem
              key={item.id}
              item={item}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Extracted card component for grid view
function GlossaryCard({
  item,
  onEdit,
  onDelete,
}: {
  item: BusinessGlossary;
  onEdit: (item: BusinessGlossary) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{item.term}</CardTitle>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => onEdit(item)}>
              <Pencil className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => onDelete(item.id)}>
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-2">{item.definition}</p>
        {item.synonyms && item.synonyms.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {item.synonyms.map((syn) => (
              <Badge key={syn} variant="secondary" className="text-xs">
                {syn}
              </Badge>
            ))}
          </div>
        )}
        {item.related_tables && item.related_tables.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.related_tables.map((table) => (
              <Badge key={table} variant="outline" className="text-xs">
                {table}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Extracted list item component for list view
function GlossaryListItem({
  item,
  onEdit,
  onDelete,
}: {
  item: BusinessGlossary;
  onEdit: (item: BusinessGlossary) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <Card>
      <CardContent className="py-3">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="font-medium">{item.term}</p>
              {item.related_tables && item.related_tables.length > 0 && (
                <Badge variant="outline" className="text-xs">
                  {item.related_tables.length} tables
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground truncate max-w-xl">{item.definition}</p>
          </div>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => onEdit(item)}>
              <Pencil className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => onDelete(item.id)}>
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
