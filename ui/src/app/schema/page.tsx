'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useConnections } from '@/hooks/use-connections';
import { useTables, useTable } from '@/hooks/use-tables';
import { TableTree } from '@/components/schema/table-tree';
import { TableDetail } from '@/components/schema/table-detail';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

function SchemaContent() {
  const searchParams = useSearchParams();
  const initialConnection = searchParams.get('connection');

  const [selectedConnectionId, setSelectedConnectionId] = useState<string | null>(
    initialConnection
  );
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);

  const { data: connections = [] } = useConnections();
  const { data: tables = [] } = useTables(selectedConnectionId);
  const { data: selectedTable } = useTable(selectedTableId);

  const tablesByConnection: Record<string, typeof tables> = {};
  if (selectedConnectionId && tables.length > 0) {
    tablesByConnection[selectedConnectionId] = tables;
  }

  useEffect(() => {
    if (!selectedConnectionId && connections.length > 0) {
      setSelectedConnectionId(connections[0].id);
    }
  }, [connections, selectedConnectionId]);

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      <Card className="w-72 shrink-0">
        <ScrollArea className="h-full">
          <div className="p-4">
            <h3 className="mb-4 text-sm font-medium">Tables</h3>
            <TableTree
              connections={connections}
              tables={tablesByConnection}
              selectedTableId={selectedTableId}
              onSelectTable={setSelectedTableId}
              onSelectConnection={setSelectedConnectionId}
            />
          </div>
        </ScrollArea>
      </Card>

      <Card className="flex-1">
        <CardContent className="p-6">
          {selectedTable ? (
            <TableDetail table={selectedTable} />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              Select a table to view details
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function SchemaPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SchemaContent />
    </Suspense>
  );
}
