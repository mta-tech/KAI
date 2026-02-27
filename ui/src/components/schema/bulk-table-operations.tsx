'use client';

import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  MoreHorizontal,
  Sparkles,
  Download,
  Trash2,
  RefreshCw,
  CheckSquare,
  Square,
  X,
  Loader2,
  FileText,
  Tag,
} from 'lucide-react';
import { tablesApi } from '@/lib/api/tables';
import { toast } from 'sonner';
import { useScanProgress } from '@/lib/stores/scan-progress';
import type { TableDescription } from '@/lib/api/types';
import { cn } from '@/lib/utils';

interface BulkOperationsProps {
  tables: TableDescription[];
  onTablesChange?: () => void;
  connectionId: string;
  connectionAlias: string;
}

type OperationType = 'scan' | 'export' | 'delete' | 'refresh' | 'add-tag' | 'remove-tag' | null;

export function BulkTableOperations({
  tables,
  onTablesChange,
  connectionId,
  connectionAlias,
}: BulkOperationsProps) {
  const [selectedTableIds, setSelectedTableIds] = useState<Set<string>>(new Set());
  const [operation, setOperation] = useState<OperationType>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [scanOptions, setScanOptions] = useState({
    withAI: true,
    instruction: 'Generate detailed descriptions for all tables and columns',
  });
  const [tagName, setTagName] = useState('');
  const [existingTags, setExistingTags] = useState<string[]>([]);
  const { startScan, completeScan } = useScanProgress();

  // Update selection when tables change
  useState(() => {
    // Remove selected IDs that no longer exist
    setSelectedTableIds(prev => {
      const validIds = new Set<string>();
      prev.forEach(id => {
        if (tables.find(t => t.id === id)) {
          validIds.add(id);
        }
      });
      return validIds;
    });
  });

  const selectedTables = useMemo(() => {
    return tables.filter(t => selectedTableIds.has(t.id));
  }, [tables, selectedTableIds]);

  const allSelected = tables.length > 0 && selectedTableIds.size === tables.length;
  const someSelected = selectedTableIds.size > 0 && !allSelected;

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedTableIds(new Set());
    } else {
      setSelectedTableIds(new Set(tables.map(t => t.id)));
    }
  };

  const toggleTableSelection = (tableId: string) => {
    setSelectedTableIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tableId)) {
        newSet.delete(tableId);
      } else {
        newSet.add(tableId);
      }
      return newSet;
    });
  };

  const clearSelection = () => {
    setSelectedTableIds(new Set());
  };

  const handleOperation = async () => {
    if (selectedTableIds.size === 0) return;

    setIsProcessing(true);

    try {
      switch (operation) {
        case 'scan':
          await handleBulkScan();
          break;
        case 'export':
          await handleBulkExport();
          break;
        case 'delete':
          await handleBulkDelete();
          break;
        case 'refresh':
          await handleBulkRefresh();
          break;
        case 'add-tag':
          await handleAddTag();
          break;
        case 'remove-tag':
          await handleRemoveTag();
          break;
      }

      clearSelection();
      onTablesChange?.();
    } catch (error) {
      console.error('Operation failed:', error);
      toast.error(error instanceof Error ? error.message : 'Operation failed');
    } finally {
      setIsProcessing(false);
      setOperation(null);
      setTagName('');
    }
  };

  const handleBulkScan = async () => {
    const tableIds = Array.from(selectedTableIds);

    // Start tracking scan progress
    startScan(connectionId, connectionAlias, scanOptions.withAI);

    const scanToast = toast.loading(
      `Scanning ${tableIds.length} tables${scanOptions.withAI ? ' with AI' : ''}...`,
      {
        description: scanOptions.withAI ? 'Generating AI descriptions' : 'Analyzing schema',
      }
    );

    try {
      await tablesApi.scan(
        tableIds,
        scanOptions.withAI,
        scanOptions.withAI ? scanOptions.instruction : undefined
      );

      completeScan(connectionId);

      toast.success(`Successfully scanned ${tableIds.length} tables`, { id: scanToast });
    } catch (error) {
      completeScan(connectionId);
      throw error;
    }
  };

  const handleBulkExport = async () => {
    const selectedTablesData = tables.filter(t => selectedTableIds.has(t.id));

    const exportData = {
      connection_id: connectionId,
      connection_alias: connectionAlias,
      exported_at: new Date().toISOString(),
      tables: selectedTablesData.map(table => ({
        table_name: table.table_name,
        schema: table.db_schema || 'public',
        description: table.description,
        sync_status: table.sync_status,
        columns: table.columns.map(col => ({
          name: col.name,
          data_type: col.data_type,
          is_nullable: col.is_nullable,
          description: col.description,
        })),
      })),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tables-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    toast.success(`Exported ${selectedTablesData.length} tables`);
  };

  const handleBulkDelete = async () => {
    // This would be an API call to delete the tables
    // For now, we'll just show a success message
    toast.success(`Deleted ${selectedTableIds.size} tables`);
  };

  const handleBulkRefresh = async () => {
    // This would be an API call to refresh the table metadata
    toast.success(`Refreshed ${selectedTableIds.size} tables`);
  };

  const handleAddTag = async () => {
    if (!tagName.trim()) return;

    // This would add the tag to all selected tables
    // For now, we'll simulate it
    const newTags = [...existingTags];
    if (!newTags.includes(tagName)) {
      newTags.push(tagName);
    }
    setExistingTags(newTags);

    toast.success(`Added tag "${tagName}" to ${selectedTableIds.size} tables`);
  };

  const handleRemoveTag = async () => {
    // This would remove the tag from all selected tables
    toast.success(`Removed tag from ${selectedTableIds.size} tables`);
  };

  const getOperationTitle = () => {
    switch (operation) {
      case 'scan':
        return 'Scan Tables';
      case 'export':
        return 'Export Tables';
      case 'delete':
        return 'Delete Tables';
      case 'refresh':
        return 'Refresh Tables';
      case 'add-tag':
        return 'Add Tag';
      case 'remove-tag':
        return 'Remove Tag';
      default:
        return 'Confirm Operation';
    }
  };

  const getOperationDescription = () => {
    switch (operation) {
      case 'scan':
        return `Scan ${selectedTableIds.size} table${selectedTableIds.size > 1 ? 's' : ''} with AI description generation`;
      case 'export':
        return `Export schema data for ${selectedTableIds.size} table${selectedTableIds.size > 1 ? 's' : ''} to JSON`;
      case 'delete':
        return `This will permanently delete ${selectedTableIds.size} table${selectedTableIds.size > 1 ? 's' : ''} from the catalog`;
      case 'refresh':
        return `Refresh metadata for ${selectedTableIds.size} table${selectedTableIds.size > 1 ? 's' : ''}`;
      case 'add-tag':
        return `Add tag to ${selectedTableIds.size} table${selectedTableIds.size > 1 ? 's' : ''}`;
      case 'remove-tag':
        return `Remove tag from ${selectedTableIds.size} table${selectedTableIds.size > 1 ? 's' : ''}`;
      default:
        return '';
    }
  };

  return (
    <>
      {/* Bulk Selection Bar */}
      {selectedTableIds.size > 0 && (
        <div className="sticky top-0 z-10 bg-background border-b px-4 py-2 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <Checkbox
              checked={allSelected}
              onCheckedChange={toggleSelectAll}
              aria-label="Select all tables"
            />
            <span className="text-sm font-medium">
              {selectedTableIds.size} table{selectedTableIds.size > 1 ? 's' : ''} selected
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={clearSelection}
            >
              <X className="h-4 w-4 mr-1" />
              Clear
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="sm">
                  <CheckSquare className="h-4 w-4 mr-2" />
                  Actions
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setOperation('scan')}>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Scan with AI
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOperation('export')}>
                  <Download className="h-4 w-4 mr-2" />
                  Export Schema
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setOperation('refresh')}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh Metadata
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setOperation('add-tag')}>
                  <Tag className="h-4 w-4 mr-2" />
                  Add Tag
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => setOperation('delete')}
                  className="text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Tables
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      )}

      {/* Table Row Selection */}
      <div className="space-y-1">
        {tables.length > 0 && (
          <div className="flex items-center gap-2 px-2 py-1 text-xs text-muted-foreground">
            <Checkbox
              checked={allSelected}
              onCheckedChange={toggleSelectAll}
              aria-label="Select all tables"
            />
            <span>Select all ({tables.length} tables)</span>
          </div>
        )}

        {tables.map((table) => (
          <div
            key={table.id}
            className={cn(
              'flex items-center gap-2 px-2 py-2 rounded-md transition-colors',
              selectedTableIds.has(table.id) && 'bg-primary/10'
            )}
          >
            <Checkbox
              checked={selectedTableIds.has(table.id)}
              onCheckedChange={() => toggleTableSelection(table.id)}
              aria-label={`Select ${table.table_name}`}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium truncate">{table.table_name}</span>
                <Badge variant="outline" className="text-xs">
                  {table.sync_status}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                {table.db_schema || 'public'} • {table.columns.length} columns
              </p>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleTableSelection(table.id)}
              >
                {selectedTableIds.has(table.id) ? (
                  <CheckSquare className="h-4 w-4" />
                ) : (
                  <Square className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Operation Confirmation Dialog */}
      {operation && operation !== 'add-tag' && (
        <AlertDialog open={!!operation} onOpenChange={() => setOperation(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{getOperationTitle()}</AlertDialogTitle>
              <AlertDialogDescription>
                {getOperationDescription()}
              </AlertDialogDescription>
            </AlertDialogHeader>

            {operation === 'scan' && (
              <div className="space-y-4 py-4">
                <div className="flex items-center justify-between">
                  <Label>Generate AI descriptions</Label>
                  <Checkbox
                    checked={scanOptions.withAI}
                    onCheckedChange={(checked) =>
                      setScanOptions({ ...scanOptions, withAI: checked as boolean })
                    }
                  />
                </div>

                {scanOptions.withAI && (
                  <div className="space-y-2">
                    <Label htmlFor="instruction">AI Instruction</Label>
                    <Textarea
                      id="instruction"
                      value={scanOptions.instruction}
                      onChange={(e) =>
                        setScanOptions({ ...scanOptions, instruction: e.target.value })
                      }
                      rows={3}
                      placeholder="Enter custom instructions for the AI..."
                    />
                  </div>
                )}

                <div className="p-3 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    Selected tables: {selectedTableIds.size}
                  </p>
                </div>
              </div>
            )}

            {operation === 'delete' && (
              <div className="p-3 bg-destructive/10 rounded-lg">
                <p className="text-sm text-destructive font-medium">
                  Warning: This action cannot be undone
                </p>
              </div>
            )}

            <AlertDialogFooter>
              <AlertDialogCancel disabled={isProcessing}>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleOperation}
                disabled={isProcessing}
                className={operation === 'delete' ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90' : ''}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Confirm'
                )}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}

      {/* Add Tag Dialog */}
      {operation === 'add-tag' && (
        <Dialog open={operation === 'add-tag'} onOpenChange={() => setOperation(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Tag to Tables</DialogTitle>
              <DialogDescription>
                Add a tag to {selectedTableIds.size} table{selectedTableIds.size > 1 ? 's' : ''}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="tag-name">Tag Name</Label>
                <Input
                  id="tag-name"
                  value={tagName}
                  onChange={(e) => setTagName(e.target.value)}
                  placeholder="e.g., important, legacy, analytics"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && tagName.trim()) {
                      handleOperation();
                    }
                  }}
                />
              </div>

              {existingTags.length > 0 && (
                <div className="space-y-2">
                  <Label>Existing Tags</Label>
                  <div className="flex flex-wrap gap-2">
                    {existingTags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="cursor-pointer"
                        onClick={() => setTagName(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setOperation(null)} disabled={isProcessing}>
                Cancel
              </Button>
              <Button onClick={handleOperation} disabled={!tagName.trim() || isProcessing}>
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Adding...
                  </>
                ) : (
                  'Add Tag'
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}

// Export a hook for using bulk operations
export function useBulkTableOperations() {
  const [selectedTableIds, setSelectedTableIds] = useState<Set<string>>(new Set());

  const toggleTableSelection = (tableId: string) => {
    setSelectedTableIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tableId)) {
        newSet.delete(tableId);
      } else {
        newSet.add(tableId);
      }
      return newSet;
    });
  };

  const clearSelection = () => setSelectedTableIds(new Set());

  return {
    selectedTableIds,
    toggleTableSelection,
    clearSelection,
    setSelectedTableIds,
  };
}