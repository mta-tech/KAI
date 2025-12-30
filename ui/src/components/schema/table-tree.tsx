'use client';

import { useState } from 'react';
import { ChevronRight, ChevronDown, Table2, Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TableDescription, DatabaseConnection } from '@/lib/api/types';

interface TableTreeProps {
  connections: DatabaseConnection[];
  tables: Record<string, TableDescription[]>;
  selectedTableId: string | null;
  onSelectTable: (id: string) => void;
  onSelectConnection: (id: string) => void;
}

export function TableTree({
  connections,
  tables,
  selectedTableId,
  onSelectTable,
  onSelectConnection,
}: TableTreeProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-1">
      {connections.map((conn) => {
        const connTables = tables[conn.id] || [];
        const isExpanded = expanded[conn.id];

        const bySchema = connTables.reduce((acc, table) => {
          const schema = table.db_schema || 'public';
          if (!acc[schema]) acc[schema] = [];
          acc[schema].push(table);
          return acc;
        }, {} as Record<string, TableDescription[]>);

        return (
          <div key={conn.id}>
            <button
              className="flex w-full items-center gap-1 rounded-md px-2 py-1.5 text-sm hover:bg-muted"
              onClick={() => {
                toggleExpand(conn.id);
                onSelectConnection(conn.id);
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
              <Database className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{conn.alias || conn.id.slice(0, 8)}</span>
              <span className="ml-auto text-xs text-muted-foreground">
                {connTables.length}
              </span>
            </button>

            {isExpanded && (
              <div className="ml-4 space-y-0.5">
                {Object.entries(bySchema).map(([schema, schemaTables]) => (
                  <div key={schema}>
                    <div className="px-2 py-1 text-xs text-muted-foreground">
                      {schema}
                    </div>
                    {schemaTables.map((table) => (
                      <button
                        key={table.id}
                        className={cn(
                          'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted',
                          selectedTableId === table.id && 'bg-muted'
                        )}
                        onClick={() => onSelectTable(table.id)}
                      >
                        <Table2 className="h-4 w-4 text-muted-foreground" />
                        {table.table_name}
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
