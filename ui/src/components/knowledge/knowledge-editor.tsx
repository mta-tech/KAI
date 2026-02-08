'use client';

import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/ui/loading-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Plus,
  Pencil,
  Trash2,
  BookOpen,
  Code,
  Search,
  Grid3x3,
  List,
  ArrowUpDown,
  Save,
  X,
  FileText,
  Tag,
  Sparkles,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import type { BusinessGlossary, Instruction } from '@/lib/api/types';
import { cn } from '@/lib/utils';

type ViewMode = 'grid' | 'list';
type SortBy = 'name' | 'date' | 'tables' | 'category';
type EditorTab = 'glossary' | 'instructions' | 'templates' | 'preview';
type KnowledgeItemType = 'glossary' | 'instruction' | 'template';

interface KnowledgeItem {
  id: string;
  type: KnowledgeItemType;
  title: string;
  content: string;
  category?: string;
  tags?: string[];
  relatedTables?: string[];
  isDefault?: boolean;
  createdAt: string;
  updatedAt: string;
}

interface KnowledgeEditorProps {
  connectionId: string;
  glossaries?: BusinessGlossary[];
  instructions?: Instruction[];
  onSaveGlossary?: (item: Omit<BusinessGlossary, 'id' | 'created_at'>) => Promise<void>;
  onUpdateGlossary?: (id: string, item: Partial<BusinessGlossary>) => Promise<void>;
  onDeleteGlossary?: (id: string) => Promise<void>;
  onSaveInstruction?: (item: Omit<Instruction, 'id' | 'created_at'>) => Promise<void>;
  onUpdateInstruction?: (id: string, item: Partial<Instruction>) => Promise<void>;
  onDeleteInstruction?: (id: string) => Promise<void>;
}

export function KnowledgeEditor({
  connectionId,
  glossaries = [],
  instructions = [],
  onSaveGlossary,
  onUpdateGlossary,
  onDeleteGlossary,
  onSaveInstruction,
  onUpdateInstruction,
  onDeleteInstruction,
}: KnowledgeEditorProps) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<EditorTab>('glossary');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState<SortBy>('name');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<KnowledgeItem | null>(null);
  const [itemType, setItemType] = useState<KnowledgeItemType>('glossary');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    definition: '',
    condition: '',
    rules: '',
    category: '',
    tags: '',
    relatedTables: '',
    isDefault: false,
  });

  // Delete confirmation
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<KnowledgeItem | null>(null);

  // Categories
  const categories = useMemo(() => {
    const cats = new Set<string>();
    glossaries.forEach(g => {
      if (g.metadata?.category) cats.add(g.metadata.category as string);
    });
    return ['all', ...Array.from(cats).sort()];
  }, [glossaries]);

  // Transform data to unified format
  const knowledgeItems = useMemo(() => {
    const items: KnowledgeItem[] = [];

    // Add glossaries
    glossaries.forEach(g => {
      items.push({
        id: g.id,
        type: 'glossary',
        title: g.term,
        content: g.definition,
        category: (g.metadata?.category as string) || 'general',
        tags: g.synonyms || [],
        relatedTables: g.related_tables || [],
        createdAt: g.created_at,
        updatedAt: g.created_at,
      });
    });

    // Add instructions
    instructions.forEach(i => {
      items.push({
        id: i.id,
        type: 'instruction',
        title: i.condition.slice(0, 50) + (i.condition.length > 50 ? '...' : ''),
        content: i.rules,
        category: i.is_default ? 'default' : 'custom',
        isDefault: i.is_default,
        createdAt: i.created_at,
        updatedAt: i.created_at,
      });
    });

    return items;
  }, [glossaries, instructions]);

  // Filter and sort
  const filteredItems = useMemo(() => {
    const items = knowledgeItems.filter(item => {
      const matchesTab =
        activeTab === 'glossary' ? item.type === 'glossary' :
        activeTab === 'instructions' ? item.type === 'instruction' :
        true;

      const matchesSearch = !searchQuery ||
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.content.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;

      return matchesTab && matchesSearch && matchesCategory;
    });

    // Sort (using toSorted for non-mutating sort)
    return items.toSorted((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.title.localeCompare(b.title);
        case 'date':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'tables':
          return (b.relatedTables?.length || 0) - (a.relatedTables?.length || 0);
        case 'category':
          return (a.category || '').localeCompare(b.category || '');
        default:
          return 0;
      }
    });
  }, [knowledgeItems, activeTab, searchQuery, sortBy, selectedCategory]);

  const stats = useMemo(() => {
    return {
      total: knowledgeItems.length,
      glossary: knowledgeItems.filter(i => i.type === 'glossary').length,
      instructions: knowledgeItems.filter(i => i.type === 'instruction').length,
      default: knowledgeItems.filter(i => i.isDefault).length,
    };
  }, [knowledgeItems]);

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      definition: '',
      condition: '',
      rules: '',
      category: '',
      tags: '',
      relatedTables: '',
      isDefault: false,
    });
    setEditingItem(null);
    setIsFormOpen(false);
  };

  const handleAdd = (type: KnowledgeItemType) => {
    setItemType(type);
    setEditingItem(null);
    setFormData({
      title: '',
      content: '',
      definition: '',
      condition: '',
      rules: '',
      category: '',
      tags: '',
      relatedTables: '',
      isDefault: false,
    });
    setIsFormOpen(true);
  };

  const handleEdit = (item: KnowledgeItem) => {
    setItemType(item.type);
    setEditingItem(item);

    if (item.type === 'glossary') {
      setFormData({
        title: item.title,
        definition: item.content,
        content: '',
        condition: '',
        rules: '',
        category: item.category || '',
        tags: item.tags?.join(', ') || '',
        relatedTables: item.relatedTables?.join(', ') || '',
        isDefault: false,
      });
    } else if (item.type === 'instruction') {
      setFormData({
        title: '',
        content: '',
        definition: '',
        condition: item.title,
        rules: item.content,
        category: item.category || '',
        tags: '',
        relatedTables: '',
        isDefault: item.isDefault || false,
      });
    }

    setIsFormOpen(true);
  };

  const handleSave = async () => {
    try {
      if (itemType === 'glossary' && onSaveGlossary) {
        const data = {
          term: formData.title,
          definition: formData.definition,
          db_connection_id: connectionId,
          synonyms: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
          related_tables: formData.relatedTables.split(',').map(t => t.trim()).filter(Boolean),
          metadata: {
            category: formData.category || 'general',
          },
        };

        if (editingItem) {
          await onUpdateGlossary?.(editingItem.id, data);
        } else {
          await onSaveGlossary(data);
        }
      } else if (itemType === 'instruction' && onSaveInstruction) {
        const data = {
          condition: formData.condition,
          rules: formData.rules,
          db_connection_id: connectionId,
          is_default: formData.isDefault,
          metadata: {
            category: formData.category || 'custom',
          },
        };

        if (editingItem) {
          await onUpdateInstruction?.(editingItem.id, data);
        } else {
          await onSaveInstruction(data);
        }
      }

      toast({
        title: 'Success',
        description: `${itemType === 'glossary' ? 'Glossary term' : 'Instruction'} saved successfully`,
      });

      resetForm();
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to save item',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async () => {
    if (!itemToDelete) return;

    try {
      if (itemToDelete.type === 'glossary') {
        await onDeleteGlossary?.(itemToDelete.id);
      } else if (itemToDelete.type === 'instruction') {
        await onDeleteInstruction?.(itemToDelete.id);
      }

      toast({
        title: 'Success',
        description: 'Item deleted successfully',
      });

      setDeleteDialogOpen(false);
      setItemToDelete(null);
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to delete item',
        variant: 'destructive',
      });
    }
  };

  const confirmDelete = (item: KnowledgeItem) => {
    setItemToDelete(item);
    setDeleteDialogOpen(true);
  };

  const renderForm = () => {
    const isGlossary = itemType === 'glossary';

    return (
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {isGlossary ? <BookOpen className="h-5 w-5" /> : <Code className="h-5 w-5" />}
              {editingItem ? `Edit ${isGlossary ? 'Glossary Term' : 'Instruction'}` : `Add ${isGlossary ? 'Glossary Term' : 'Instruction'}`}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {isGlossary ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="term">Term</Label>
                  <Input
                    id="term"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="e.g., Gross Revenue, Active User"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="definition">Definition</Label>
                  <Textarea
                    id="definition"
                    value={formData.definition}
                    onChange={(e) => setFormData({ ...formData, definition: e.target.value })}
                    placeholder="Define this business term..."
                    rows={3}
                    required
                  />
                </div>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="condition">Condition</Label>
                  <Textarea
                    id="condition"
                    value={formData.condition}
                    onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                    placeholder="When the user asks about..."
                    rows={2}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rules">Rules</Label>
                  <Textarea
                    id="rules"
                    value={formData.rules}
                    onChange={(e) => setFormData({ ...formData, rules: e.target.value })}
                    placeholder="The AI should follow these rules..."
                    rows={4}
                    required
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="isDefault"
                    checked={formData.isDefault}
                    onChange={(e) => setFormData({ ...formData, isDefault: e.target.checked })}
                    className="h-4 w-4"
                  />
                  <Label htmlFor="isDefault" className="text-sm font-normal">
                    Apply as default instruction
                  </Label>
                </div>
              </>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="e.g., metrics, dimensions"
                />
              </div>

              {isGlossary && (
                <div className="space-y-2">
                  <Label htmlFor="tags">Synonyms/Tags</Label>
                  <Input
                    id="tags"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    placeholder="e.g., revenue, income, earnings"
                  />
                </div>
              )}
            </div>

            {isGlossary && (
              <div className="space-y-2">
                <Label htmlFor="relatedTables">Related Tables</Label>
                <Input
                  id="relatedTables"
                  value={formData.relatedTables}
                  onChange={(e) => setFormData({ ...formData, relatedTables: e.target.value })}
                  placeholder="e.g., orders, users, products"
                />
                <p className="text-xs text-muted-foreground">
                  Comma-separated table names
                </p>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={resetForm}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSave} loadingText="Saving...">
              <Save className="h-4 w-4 mr-2" />
              Save
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  const renderGridItem = (item: KnowledgeItem) => (
    <Card key={item.id} className="group hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {item.type === 'glossary' ? (
              <BookOpen className="h-4 w-4 text-blue-600 flex-shrink-0" />
            ) : (
              <Code className="h-4 w-4 text-purple-600 flex-shrink-0" />
            )}
            <CardTitle className="text-sm truncate">{item.title}</CardTitle>
          </div>
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button variant="ghost" size="sm" onClick={() => handleEdit(item)}>
              <Pencil className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => confirmDelete(item)}>
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm text-muted-foreground line-clamp-2">{item.content}</p>
        <div className="flex items-center gap-2 flex-wrap">
          {item.category && (
            <Badge variant="secondary" className="text-xs">
              {item.category}
            </Badge>
          )}
          {item.isDefault && (
            <Badge variant="default" className="text-xs">
              Default
            </Badge>
          )}
          {item.relatedTables && item.relatedTables.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {item.relatedTables.length} tables
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const renderListItem = (item: KnowledgeItem) => (
    <Card key={item.id}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            {item.type === 'glossary' ? (
              <BookOpen className="h-5 w-5 text-blue-600 mt-0.5" />
            ) : (
              <Code className="h-5 w-5 text-purple-600 mt-0.5" />
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium">{item.title}</h3>
                {item.category && (
                  <Badge variant="secondary" className="text-xs">
                    {item.category}
                  </Badge>
                )}
                {item.isDefault && (
                  <Badge variant="default" className="text-xs">
                    Default
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground line-clamp-1">{item.content}</p>
              {item.relatedTables && item.relatedTables.length > 0 && (
                <p className="text-xs text-muted-foreground mt-1">
                  {item.relatedTables.length} related tables
                </p>
              )}
            </div>
          </div>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => handleEdit(item)}>
              <Pencil className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => confirmDelete(item)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Knowledge Base</h2>
          <p className="text-sm text-muted-foreground">
            {stats.total} items • {stats.glossary} glossary terms • {stats.instructions} instructions
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleAdd('glossary')}
          >
            <BookOpen className="h-4 w-4 mr-2" />
            Add Term
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleAdd('instruction')}
          >
            <Code className="h-4 w-4 mr-2" />
            Add Instruction
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
          {searchQuery && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3"
              onClick={() => setSearchQuery('')}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map(cat => (
              <SelectItem key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={sortBy} onValueChange={(v: SortBy) => setSortBy(v)}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="tables">Tables</SelectItem>
            <SelectItem value="category">Category</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex border rounded-md">
          <Button
            variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
            className="rounded-r-none"
          >
            <Grid3x3 className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('list')}
            className="rounded-l-none"
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      {filteredItems.length === 0 ? (
        <EmptyState
          icon={activeTab === 'glossary' ? BookOpen : Code}
          title={searchQuery ? 'No items found' : `No ${activeTab} yet`}
          description={searchQuery
            ? 'Try adjusting your search or filters'
            : 'Get started by adding your first knowledge base item'}
          action={{
            label: activeTab === 'glossary' ? 'Add Glossary Term' : 'Add Instruction',
            onClick: () => handleAdd(activeTab === 'glossary' ? 'glossary' : 'instruction'),
          }}
        />
      ) : (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredItems.map(renderGridItem)}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredItems.map(renderListItem)}
            </div>
          )}
        </>
      )}

      {/* Form Dialog */}
      {renderForm()}

      {/* Delete Confirmation */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Knowledge Item?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{itemToDelete?.title}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}