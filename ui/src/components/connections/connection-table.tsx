'use client';

import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Trash2, Table2, Layers, Scan, Sparkles, Loader2 } from 'lucide-react';
import Link from 'next/link';
import type { DatabaseConnection } from '@/lib/api/types';
import { useDeleteConnection } from '@/hooks/use-connections';
import { ScanWizard } from '@/components/schema/scan-wizard';
import { MDLBuildDialog } from './mdl-build-dialog';
import { useScanProgress } from '@/lib/stores/scan-progress';

interface ConnectionTableProps {
  connections: DatabaseConnection[];
}

export function ConnectionTable({ connections }: ConnectionTableProps) {
  const deleteMutation = useDeleteConnection();
  const { isScanning, getActiveScan } = useScanProgress();
  const [scanDialogOpen, setScanDialogOpen] = useState(false);
  const [mdlDialogOpen, setMdlDialogOpen] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState<DatabaseConnection | null>(null);

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this connection?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  const handleScanWithAI = (connection: DatabaseConnection) => {
    setSelectedConnection(connection);
    setScanDialogOpen(true);
  };

  const handleBuildMDL = (connection: DatabaseConnection) => {
    setSelectedConnection(connection);
    setMdlDialogOpen(true);
  };

  if (connections.length === 0) {
    return (
      <div className="rounded-md border p-8 text-center">
        <p className="text-muted-foreground">No database connections yet.</p>
        <p className="text-sm text-muted-foreground">
          Add a connection to get started.
        </p>
      </div>
    );
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Alias</TableHead>
            <TableHead>Dialect</TableHead>
            <TableHead>Schemas</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {connections.map((connection) => {
            const scanning = isScanning(connection.id);
            const scanInfo = getActiveScan(connection.id);

            return (
              <TableRow key={connection.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center gap-2">
                    {connection.alias || connection.id.slice(0, 8)}
                    {scanning && (
                      <Badge variant="secondary" className="gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Scanning{scanInfo?.withAI ? ' with AI' : ''}...
                      </Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{connection.dialect}</Badge>
                </TableCell>
              <TableCell>
                {connection.schemas?.length ? (
                  <div className="flex flex-wrap gap-1">
                    {connection.schemas.map((schema) => (
                      <Badge key={schema} variant="secondary">
                        {schema}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <span className="text-muted-foreground">-</span>
                )}
              </TableCell>
              <TableCell>
                {new Date(connection.created_at).toLocaleDateString()}
              </TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link href={`/schema?connection=${connection.id}`}>
                        <Table2 className="mr-2 h-4 w-4" />
                        View Schema
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => handleScanWithAI(connection)}
                      disabled={scanning}
                    >
                      <Scan className="mr-2 h-4 w-4" />
                      {scanning ? 'Scanning...' : 'Scan Database...'}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href={`/mdl?connection=${connection.id}`}>
                        <Layers className="mr-2 h-4 w-4" />
                        View MDL
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleBuildMDL(connection)}>
                      <Scan className="mr-2 h-4 w-4" />
                      Build MDL
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-destructive"
                      onClick={() => handleDelete(connection.id)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <ScanWizard
        open={scanDialogOpen}
        onOpenChange={setScanDialogOpen}
        connection={selectedConnection}
      />
      <MDLBuildDialog
        open={mdlDialogOpen}
        onOpenChange={setMdlDialogOpen}
        connection={selectedConnection}
      />
    </>
  );
}
