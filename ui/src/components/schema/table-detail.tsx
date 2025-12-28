'use client';

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
import { Sparkles, Loader2 } from 'lucide-react';
import type { TableDescription } from '@/lib/api/types';
import { useScanTables } from '@/hooks/use-tables';

interface TableDetailProps {
  table: TableDescription;
}

export function TableDetail({ table }: TableDetailProps) {
  const scanMutation = useScanTables();

  const handleScan = () => {
    scanMutation.mutate([table.id]);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold">{table.table_name}</h2>
          <p className="text-sm text-muted-foreground">
            {table.db_schema || 'public'} &bull; {table.columns.length} columns
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

      {table.description && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{table.description}</p>
          </CardContent>
        </Card>
      )}

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
                <TableHead>Description</TableHead>
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
                    {col.is_nullable ? (
                      <span className="text-muted-foreground">Yes</span>
                    ) : (
                      'No'
                    )}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {col.description || (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
