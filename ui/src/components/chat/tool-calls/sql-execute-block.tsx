'use client';

import { useState } from 'react';
import { Database, ChevronDown, ChevronUp, Copy, Check, Table, Code } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { AgentEvent } from '@/lib/api/types';

interface SqlExecuteBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

type ViewMode = 'results' | 'query';

interface SqlOutput {
  success?: boolean;
  row_count?: number;
  columns?: string[];
  data?: Record<string, unknown>[];
  truncated?: boolean;
  error?: string;
  results?: Record<string, unknown>[];
}

function parseOutput(raw: AgentEvent['output']): SqlOutput | null {
  if (!raw) return null;
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw) as SqlOutput;
    } catch {
      return null;
    }
  }
  return raw as SqlOutput;
}

export function SqlExecuteBlock({ event, result }: SqlExecuteBlockProps) {
  const [expanded, setExpanded] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('results');
  const [copied, setCopied] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';
  const sql = (event.input?.query ?? event.input?.sql_query ?? '') as string;
  const output = parseOutput(result?.output);
  const rows = output?.data ?? output?.results ?? [];
  const columns = output?.columns ?? (rows.length > 0 ? Object.keys(rows[0]) : []);
  const rowCount = output?.row_count ?? rows.length;
  const hasError = output?.success === false || !!output?.error;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn(
        'my-2 rounded-md border overflow-hidden',
        'transition-all duration-200',
        !isCompleted && 'border-blue-500/50 bg-blue-50/50 dark:bg-blue-950/20',
        isCompleted && hasError && 'border-red-500/50 bg-red-50/50 dark:bg-red-950/20',
        isCompleted && !hasError && 'border-emerald-500/30 bg-muted/50',
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 bg-muted/30">
        <Database
          className={cn(
            'h-3.5 w-3.5 shrink-0',
            isCompleted && !hasError ? 'text-emerald-600' : 'text-blue-500',
          )}
        />
        <span className="text-xs sm:text-sm font-mono text-muted-foreground flex-1 truncate">
          {isCompleted ? 'Executed SQL' : 'Executing SQL'}
          {sql && (
            <span className="ml-1 text-foreground/60 truncate">{sql.slice(0, 60)}{sql.length > 60 ? '...' : ''}</span>
          )}
        </span>

        <div className="flex items-center gap-1 shrink-0">
          {isCompleted && !hasError && rowCount >= 0 && (
            <Badge variant="secondary" className="text-[10px] h-5">
              {rowCount} rows
            </Badge>
          )}
          {isCompleted && (
            <>
              <Button
                variant="ghost"
                size="sm"
                className={cn('h-6 w-6 p-0', viewMode === 'results' && 'bg-muted')}
                onClick={() => { setViewMode('results'); setExpanded(true); }}
                aria-label="Show results"
                title="Show results"
              >
                <Table className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className={cn('h-6 w-6 p-0', viewMode === 'query' && 'bg-muted')}
                onClick={() => { setViewMode('query'); setExpanded(true); }}
                aria-label="Show SQL query"
                title="Show SQL query"
              >
                <Code className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={handleCopy}
                aria-label="Copy SQL"
                title="Copy SQL"
              >
                {copied ? <Check className="h-3 w-3 text-green-600" /> : <Copy className="h-3 w-3" />}
              </Button>
            </>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={() => setExpanded(!expanded)}
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </Button>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t">
          {viewMode === 'query' && sql && (
            <pre className="p-3 text-[10px] sm:text-xs overflow-x-auto bg-slate-950 text-slate-50">
              <code>{sql}</code>
            </pre>
          )}

          {viewMode === 'results' && isCompleted && (
            <>
              {hasError ? (
                <div className="p-3 text-xs text-red-600 dark:text-red-400">
                  {output?.error ?? 'Query failed'}
                </div>
              ) : rows.length === 0 ? (
                <div className="p-3 text-xs text-muted-foreground text-center">
                  No rows returned
                </div>
              ) : (
                <div className="overflow-x-auto max-h-64">
                  <table className="text-xs border-collapse w-full">
                    <thead>
                      <tr className="border-b border-border bg-muted/50">
                        {columns.map((col) => (
                          <th key={col} className="text-left p-2 font-medium text-muted-foreground whitespace-nowrap">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.slice(0, 50).map((row, i) => (
                        <tr key={i} className="border-b border-border/50 hover:bg-muted/30">
                          {columns.map((col) => (
                            <td key={col} className="p-2 font-mono max-w-[200px] truncate">
                              {row[col] === null || row[col] === undefined ? (
                                <span className="text-muted-foreground italic">NULL</span>
                              ) : (
                                String(row[col])
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {output?.truncated && (
                    <div className="p-2 text-[10px] text-muted-foreground text-center border-t">
                      Results truncated — showing first 50 of {rowCount} rows
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {viewMode === 'results' && !isCompleted && (
            <div className="p-3 text-xs text-muted-foreground text-center">
              Executing query...
            </div>
          )}
        </div>
      )}
    </div>
  );
}
