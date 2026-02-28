'use client';

import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Sparkles, Loader2, ChevronDown, Info, Hash, Type } from 'lucide-react';
import type { TableDescription, ColumnDescription } from '@/lib/api/types';
import { useScanTables } from '@/hooks/use-tables';

interface TableDetailProps {
  table: TableDescription;
}

export function TableDetail({ table }: TableDetailProps) {
  const scanMutation = useScanTables();
  const [expandedColumn, setExpandedColumn] = useState<string | null>(null);

  const handleScan = () => {
    scanMutation.mutate([table.id]);
  };

  const toggleColumn = (colName: string) => {
    setExpandedColumn((prev) => (prev === colName ? null : colName));
  };

  return (
    <div className="space-y-4">
      {/* Table Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold">{table.table_name}</h2>
          <p className="text-sm text-muted-foreground">
            {table.db_schema || 'public'} • {table.columns.length} columns
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant={table.sync_status === 'SCANNED' ? 'default' : 'secondary'}>
            {table.sync_status}
          </Badge>
          <Button
            size="sm"
            variant="outline"
            onClick={handleScan}
            disabled={scanMutation.isPending}
          >
            {scanMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="mr-2 h-4 w-4" />
            )}
            Scan with AI
          </Button>
        </div>
      </div>

      {/* Table Description */}
      {table.description && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Info className="h-4 w-4" />
              Description
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{table.description}</p>
          </CardContent>
        </Card>
      )}

      {/* Columns Section */}
      <Tabs defaultValue="list" className="w-full">
        <TabsList className="grid w-full max-w-xs grid-cols-2">
          <TabsTrigger value="list">List View</TabsTrigger>
          <TabsTrigger value="detail">Detail View</TabsTrigger>
        </TabsList>

        {/* Compact List View */}
        <TabsContent value="list">
          <Card>
            <CardHeader>
              <CardTitle>Columns</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Nullable</TableHead>
                    <TableHead className="max-w-xs">Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {table.columns.map((col) => (
                    <TableRow key={col.name}>
                      <TableCell className="font-mono text-sm">{col.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{col.data_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <NullableBadge nullable={col.is_nullable} />
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {col.description || <span className="text-muted-foreground">-</span>}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Detailed View */}
        <TabsContent value="detail">
          <div className="space-y-2">
            {table.columns.map((col) => (
              <ColumnCard
                key={col.name}
                column={col}
                isExpanded={expandedColumn === col.name}
                onToggle={() => toggleColumn(col.name)}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Table Metadata */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Table Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-muted-foreground">Table Name</dt>
              <dd className="font-mono">{table.table_name}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Schema</dt>
              <dd>{table.db_schema || 'public'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Column Count</dt>
              <dd>{table.columns.length}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Sync Status</dt>
              <dd>{table.sync_status}</dd>
            </div>
            {table.created_at && (
              <div>
                <dt className="text-muted-foreground">Created</dt>
                <dd>{new Date(table.created_at).toLocaleDateString()}</dd>
              </div>
            )}
            <div>
              <dt className="text-muted-foreground">Connection ID</dt>
              <dd className="font-mono text-xs">{table.db_connection_id.slice(0, 8)}...</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}

// Column Card Component for Detail View
function ColumnCard({
  column,
  isExpanded,
  onToggle,
}: {
  column: ColumnDescription;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <Collapsible open={isExpanded} onOpenChange={onToggle}>
      <Card>
        <CollapsibleTrigger asChild>
          <CardHeader className="hover:bg-muted/50 cursor-pointer transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Hash className="h-4 w-4 text-muted-foreground" />
                <div className="text-left">
                  <p className="font-mono text-sm font-medium">{column.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      <Type className="h-3 w-3 mr-1" />
                      {column.data_type}
                    </Badge>
                    <NullableBadge nullable={column.is_nullable} />
                  </div>
                </div>
              </div>
              <ChevronDown
                className={`h-4 w-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              />
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">
            <div className="space-y-3 text-sm">
              {column.description && (
                <div>
                  <p className="text-muted-foreground mb-1">Description</p>
                  <p>{column.description}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-muted-foreground mb-1">Data Type</p>
                  <p className="font-mono">{column.data_type}</p>
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Nullable</p>
                  <p>{column.is_nullable ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}

// Nullable Badge Component
function NullableBadge({ nullable }: { nullable: boolean }) {
  return nullable ? (
    <Badge variant="secondary" className="text-xs">
      Nullable
    </Badge>
  ) : (
    <Badge variant="default" className="text-xs">
      Required
    </Badge>
  );
}
