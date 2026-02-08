'use client';

import { useState, useMemo, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import {
  Download,
  FileSpreadsheet,
  FileJson,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Search,
  X,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { AgentEvent } from '@/lib/api/types';

interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  executionTime?: number;
}

interface SqlResultsTableProps {
  results?: QueryResult;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

// Parse results from tool_end event output
function parseQueryResults(event: AgentEvent): QueryResult | null {
  if (event.type !== 'tool_end' || !event.output) return null;

  const output = typeof event.output === 'string'
    ? JSON.parse(event.output)
    : event.output;

  // Handle different output formats
  if (output.results && Array.isArray(output.results)) {
    return {
      columns: output.columns || Object.keys(output.results[0] || {}),
      rows: output.results,
      rowCount: output.row_count || output.results.length,
      executionTime: output.execution_time,
    };
  }

  // Handle array format directly
  if (Array.isArray(output) && output.length > 0) {
    return {
      columns: Object.keys(output[0]),
      rows: output,
      rowCount: output.length,
    };
  }

  return null;
}

export function SqlResultsTable({ results, isLoading, error, className }: SqlResultsTableProps) {
  const [pagination, setPagination] = useState({ page: 1, pageSize: 25 });
  const [sortConfig, setSortConfig] = useState<{ column: string; direction: 'asc' | 'desc' } | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [columnVisibility, setColumnVisibility] = useState<Record<string, boolean>>({});

  // Initialize column visibility
  const allColumns = results?.columns || [];
  useEffect(() => {
    if (allColumns.length > 0 && Object.keys(columnVisibility).length === 0) {
      const initial: Record<string, boolean> = {};
      allColumns.forEach((col) => initial[col] = true);
      setColumnVisibility(initial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allColumns]);

  // Filter and sort data
  const processedData = useMemo(() => {
    if (!results?.rows) return [];

    let data = [...results.rows];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      data = data.filter((row) =>
        Object.values(row).some((val) =>
          String(val).toLowerCase().includes(query)
        )
      );
    }

    // Apply sorting
    if (sortConfig) {
      data.sort((a, b) => {
        const aVal = a[sortConfig.column];
        const bVal = b[sortConfig.column];

        if (aVal === bVal) return 0;

        // Handle unknown types with string comparison as fallback
        const aStr = String(aVal ?? '');
        const bStr = String(bVal ?? '');
        const comparison = aStr < bStr ? -1 : 1;
        return sortConfig.direction === 'asc' ? comparison : -comparison;
      });
    }

    return data;
  }, [results?.rows, searchQuery, sortConfig]);

  // Pagination
  const paginatedData = useMemo(() => {
    const start = (pagination.page - 1) * pagination.pageSize;
    return processedData.slice(start, start + pagination.pageSize);
  }, [processedData, pagination]);

  const totalPages = Math.ceil(processedData.length / pagination.pageSize);
  const visibleColumns = allColumns.filter((col) => columnVisibility[col]);

  // Export functions
  const exportAsCSV = () => {
    if (!results) return;

    const headers = visibleColumns;
    const rows = processedData.map((row) =>
      visibleColumns.map((col) => {
        const val = row[col];
        // Escape CSV values
        const stringVal = String(val ?? '');
        if (stringVal.includes(',') || stringVal.includes('"') || stringVal.includes('\n')) {
          return `"${stringVal.replace(/"/g, '""')}"`;
        }
        return stringVal;
      })
    );

    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    downloadFile(csv, 'query-results.csv', 'text/csv');
  };

  const exportAsJSON = () => {
    if (!results) return;

    const data = processedData.map((row) => {
      const filtered: Record<string, unknown> = {};
      visibleColumns.forEach((col) => {
        filtered[col] = row[col];
      });
      return filtered;
    });

    const json = JSON.stringify(data, null, 2);
    downloadFile(json, 'query-results.json', 'application/json');
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSort = (column: string) => {
    setSortConfig((current) => {
      if (current?.column === column) {
        if (current.direction === 'asc') {
          return { column, direction: 'desc' };
        }
        return null;
      }
      return { column, direction: 'asc' };
    });
  };

  if (isLoading) {
    return (
      <div className={cn('rounded-lg border bg-card', className)}>
        <div className="flex items-center justify-center p-8">
          <div className="flex items-center gap-3 text-muted-foreground">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <span className="text-sm">Loading results...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn('rounded-lg border border-destructive bg-destructive/10', className)}>
        <div className="p-4">
          <p className="text-sm text-destructive font-medium">Query Error</p>
          <p className="text-sm text-destructive/80 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!results || results.rowCount === 0) {
    return (
      <div className={cn('rounded-lg border bg-card', className)}>
        <div className="flex items-center justify-center p-8 text-muted-foreground">
          <span className="text-sm">No results returned</span>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('rounded-lg border bg-card overflow-hidden', className)}>
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-3 border-b bg-muted/20">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            {results.rowCount.toLocaleString()} rows
          </Badge>
          {results.executionTime && (
            <Badge variant="outline" className="text-xs">
              {(results.executionTime / 1000).toFixed(2)}s
            </Badge>
          )}
          {searchQuery && (
            <Badge variant="secondary" className="text-xs">
              {processedData.length.toLocaleString()} filtered
            </Badge>
          )}
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
          {/* Search */}
          <div className="relative flex-1 sm:flex-none">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPagination({ ...pagination, page: 1 });
              }}
              className="h-11 w-full sm:w-40 pl-10 pr-11 text-sm"
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-11 w-11 p-0"
                onClick={() => {
                  setSearchQuery('');
                  setPagination({ ...pagination, page: 1 });
                }}
                aria-label="Clear search"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Column visibility - 44x44px touch target */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="h-11 w-11 p-0 flex-shrink-0"
                aria-label="Column visibility"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <div className="px-2 py-1.5 text-xs font-medium">Show Columns</div>
              <DropdownMenuSeparator />
              {allColumns.map((col) => (
                <DropdownMenuItem
                  key={col}
                  className="flex items-center gap-2 min-h-[44px]"
                  onClick={(e) => {
                    e.preventDefault();
                    setColumnVisibility((prev) => ({
                      ...prev,
                      [col]: !prev[col],
                    }));
                  }}
                >
                  <input
                    type="checkbox"
                    checked={columnVisibility[col] ?? true}
                    onChange={() => {}}
                    className="pointer-events-none"
                  />
                  <span className="truncate">{col}</span>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Export - 44x44px touch target */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="h-11 px-3 flex-shrink-0"
                aria-label="Export data"
              >
                <Download className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Export</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={exportAsCSV} className="min-h-[44px]">
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Export as CSV
              </DropdownMenuItem>
              <DropdownMenuItem onClick={exportAsJSON} className="min-h-[44px]">
                <FileJson className="h-4 w-4 mr-2" />
                Export as JSON
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {visibleColumns.map((column) => (
                <TableHead key={column} className="whitespace-nowrap">
                  <button
                    onClick={() => handleSort(column)}
                    className="flex items-center gap-1 hover:text-primary transition-colors font-medium min-h-[44px] px-2 rounded active:bg-accent/50"
                    aria-label={`Sort by ${column}`}
                  >
                    {column}
                    {sortConfig?.column === column && (
                      <span className="text-xs" aria-live="polite">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </button>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={visibleColumns.length} className="text-center text-muted-foreground">
                  No matching results
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, idx) => (
                <TableRow key={idx}>
                  {visibleColumns.map((column) => (
                    <TableCell key={column} className="max-w-md truncate">
                      {formatCellValue(row[column])}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-3 border-t bg-muted/20">
          <div className="text-sm text-muted-foreground text-center sm:text-left">
            Showing {(pagination.page - 1) * pagination.pageSize + 1} to{' '}
            {Math.min(pagination.page * pagination.pageSize, processedData.length)} of{' '}
            {processedData.length.toLocaleString()}
          </div>

          <div className="flex items-center justify-center gap-1 sm:gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-11 w-11 p-0 flex-shrink-0"
              onClick={() => setPagination({ ...pagination, page: 1 })}
              disabled={pagination.page === 1}
              aria-label="First page"
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-11 w-11 p-0 flex-shrink-0"
              onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
              disabled={pagination.page === 1}
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm px-2 sm:px-3 min-w-[100px] text-center" aria-live="polite">
              Page {pagination.page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              className="h-11 w-11 p-0 flex-shrink-0"
              onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
              disabled={pagination.page === totalPages}
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-11 w-11 p-0 flex-shrink-0"
              onClick={() => setPagination({ ...pagination, page: totalPages })}
              disabled={pagination.page === totalPages}
              aria-label="Last page"
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper to format cell values - returns JSX for safe rendering (prevents XSS)
function formatCellValue(value: unknown): React.ReactNode {
  if (value === null || value === undefined) {
    return <span className="text-muted-foreground italic">NULL</span>;
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (typeof value === 'object') {
    return <code className="text-xs bg-muted px-1 py-0.5 rounded">{JSON.stringify(value)}</code>;
  }
  return String(value);
}

// Hook to extract results from message events
export function useQueryResults(events: AgentEvent[] = []): QueryResult | null {
  return useMemo(() => {
    // Find the last sql_execute tool_end event
    for (let i = events.length - 1; i >= 0; i--) {
      const event = events[i];
      if (event.type === 'tool_end' && event.tool === 'sql_execute') {
        return parseQueryResults(event);
      }
    }
    return null;
  }, [events]);
}
