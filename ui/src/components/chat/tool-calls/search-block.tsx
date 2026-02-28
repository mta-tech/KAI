'use client';

import { useState } from 'react';
import { Search, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { AgentEvent } from '@/lib/api/types';

interface SearchBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

interface SearchOutput {
  results?: unknown[];
  count?: number;
  items?: unknown[];
  matches?: unknown[];
}

function parseOutput(raw: AgentEvent['output']): SearchOutput | null {
  if (!raw) return null;
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw) as SearchOutput;
    } catch {
      return null;
    }
  }
  return raw as SearchOutput;
}

export function SearchBlock({ event, result }: SearchBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';
  const query = (event.input?.query ?? event.input?.pattern ?? event.input?.term ?? '') as string;
  const output = parseOutput(result?.output);
  const resultItems = output?.results ?? output?.items ?? output?.matches ?? [];
  const resultCount = output?.count ?? resultItems.length;

  return (
    <div
      className={cn(
        'my-2 rounded-md border bg-muted/50',
        'transition-all duration-200',
        !isCompleted && 'border-blue-500/50 bg-blue-50/50 dark:bg-blue-950/20',
        isCompleted && 'border-blue-500/30',
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2">
        {isCompleted ? (
          <Search className="h-3.5 w-3.5 shrink-0 text-blue-600" />
        ) : (
          <Loader2 className="h-3.5 w-3.5 shrink-0 text-blue-500 animate-spin" />
        )}
        <span className="text-xs sm:text-sm font-mono flex-1 truncate">
          <span className={isCompleted ? 'text-green-600' : 'text-blue-600'}>
            {isCompleted ? '✔ Searched' : '➜ Searching'}
          </span>
          {query && (
            <code className="ml-1 text-[10px] bg-background/50 px-1 py-0.5 rounded">
              {query.length > 50 ? query.slice(0, 50) + '...' : query}
            </code>
          )}
        </span>

        <div className="flex items-center gap-1 shrink-0">
          {isCompleted && resultCount > 0 && (
            <Badge variant="secondary" className="text-[10px] h-5">
              {resultCount} results
            </Badge>
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

      {expanded && (
        <div className="border-t p-2 text-[10px] sm:text-xs">
          {result?.output ? (
            <pre className="max-h-40 overflow-auto rounded bg-background p-2">
              {typeof result.output === 'string'
                ? result.output.slice(0, 500)
                : JSON.stringify(result.output, null, 2).slice(0, 500)}
              {(typeof result.output === 'string'
                ? result.output.length
                : JSON.stringify(result.output, null, 2).length) > 500 && '...'}
            </pre>
          ) : (
            <div className="text-muted-foreground text-center py-2">
              {isCompleted ? 'No output' : 'Searching...'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
