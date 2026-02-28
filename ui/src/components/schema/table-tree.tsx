'use client';

import { useState, useMemo } from 'react';
import { ChevronRight, ChevronDown, Table2, Database, Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSchemaFilter, setSelectedSchemaFilter] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  // Get all unique schemas across all connections
  const allSchemas = useMemo(() => {
    const schemas = new Set<string>();
    Object.values(tables).forEach((connTables) => {
      connTables.forEach((table) => {
        schemas.add(table.db_schema || 'public');
      });
    });
    return Array.from(schemas).sort();
  }, [tables]);

  // Filter tables based on search query and schema filter
  const filteredTables = useMemo(() => {
    const result: Record<string, TableDescription[]> = {};

    Object.entries(tables).forEach(([connId, connTables]) => {
      let filtered = connTables;

      // Apply search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(
          (table) =>
            table.table_name.toLowerCase().includes(query) ||
            (table.description && table.description.toLowerCase().includes(query))
        );
      }

      // Apply schema filter
      if (selectedSchemaFilter) {
        filtered = filtered.filter(
          (table) => (table.db_schema || 'public') === selectedSchemaFilter
        );
      }

      if (filtered.length > 0) {
        result[connId] = filtered;
      }
    });

    return result;
  }, [tables, searchQuery, selectedSchemaFilter]);

  // Auto-expand when searching or filtering
  useMemo(() => {
    if (searchQuery || selectedSchemaFilter) {
      const newExpanded: Record<string, boolean> = {};
      Object.keys(filteredTables).forEach((connId) => {
        newExpanded[connId] = true;
      });
      setExpanded(newExpanded);
    }
  }, [searchQuery, selectedSchemaFilter, filteredTables]);

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedSchemaFilter(null);
  };

  const hasActiveFilters = searchQuery || selectedSchemaFilter;

  return (
    <div className="flex flex-col h-full">
      {/* Search and Filter Controls */}
      <div className="p-2 space-y-2 border-b">
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            placeholder="Search tables..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 pl-8 text-sm"
          />
          {searchQuery && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-8 w-8 p-0"
              onClick={() => setSearchQuery('')}
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>

        {/* Schema Filter */}
        {allSchemas.length > 1 && (
          <div className="flex gap-1 flex-wrap">
            <Button
              variant={selectedSchemaFilter === null ? 'default' : 'outline'}
              size="sm"
              className="h-7 text-xs"
              onClick={() => setSelectedSchemaFilter(null)}
            >
              All Schemas
            </Button>
            {allSchemas.map((schema) => (
              <Button
                key={schema}
                variant={selectedSchemaFilter === schema ? 'default' : 'outline'}
                size="sm"
                className="h-7 text-xs"
                onClick={() => setSelectedSchemaFilter(schema)}
              >
                {schema}
              </Button>
            ))}
          </div>
        )}

        {/* Clear Filters */}
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-full text-xs"
            onClick={clearFilters}
          >
            Clear Filters
          </Button>
        )}
      </div>

      {/* Tree */}
      <div className="flex-1 overflow-y-auto p-1">
        {Object.keys(filteredTables).length === 0 ? (
          <div className="px-2 py-4 text-center text-sm text-muted-foreground">
            {searchQuery
              ? 'No tables match your search'
              : selectedSchemaFilter
              ? 'No tables in this schema'
              : 'No tables available'}
          </div>
        ) : (
          <div className="space-y-1">
            {connections.map((conn) => {
              const connTables = filteredTables[conn.id] || [];
              if (connTables.length === 0) return null;

              const isExpanded = expanded[conn.id];

              const bySchema = connTables.reduce((acc, table) => {
                const schema = table.db_schema || 'public';
                if (!acc[schema]) acc[schema] = [];
                acc[schema].push(table);
                return acc;
              }, {} as Record<string, TableDescription[]>);

              return (
                <div key={conn.id}>
                  <Button
                    variant="ghost"
                    className="flex w-full items-center gap-1 justify-start px-2 py-1.5 h-auto hover:bg-muted"
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
                  </Button>

                  {isExpanded && (
                    <div className="ml-4 space-y-0.5">
                      {Object.entries(bySchema).map(([schema, schemaTables]) => (
                        <div key={schema}>
                          <div className="px-2 py-1 text-xs text-muted-foreground">
                            {schema}
                          </div>
                          {schemaTables.map((table) => (
                            <Button
                              key={table.id}
                              variant="ghost"
                              className={cn(
                                'flex w-full items-center gap-2 justify-start px-2 py-1.5 h-auto hover:bg-muted',
                                selectedTableId === table.id && 'bg-muted'
                              )}
                              onClick={() => onSelectTable(table.id)}
                            >
                              <Table2 className="h-4 w-4 text-muted-foreground" />
                              {table.table_name}
                            </Button>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
