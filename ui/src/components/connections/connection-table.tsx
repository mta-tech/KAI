'use client';

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
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Trash2, Table2, Layers } from 'lucide-react';
import Link from 'next/link';
import type { DatabaseConnection } from '@/lib/api/types';
import { useDeleteConnection } from '@/hooks/use-connections';

interface ConnectionTableProps {
  connections: DatabaseConnection[];
}

export function ConnectionTable({ connections }: ConnectionTableProps) {
  const deleteMutation = useDeleteConnection();

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this connection?')) {
      await deleteMutation.mutateAsync(id);
    }
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
        {connections.map((connection) => (
          <TableRow key={connection.id}>
            <TableCell className="font-medium">
              {connection.alias || connection.id.slice(0, 8)}
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
                  <DropdownMenuItem asChild>
                    <Link href={`/mdl?connection=${connection.id}`}>
                      <Layers className="mr-2 h-4 w-4" />
                      Create MDL
                    </Link>
                  </DropdownMenuItem>
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
        ))}
      </TableBody>
    </Table>
  );
}
