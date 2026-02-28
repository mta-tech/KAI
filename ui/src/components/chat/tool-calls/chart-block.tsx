'use client';

import { useState } from 'react';
import { BarChart2, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import type { AgentEvent } from '@/lib/api/types';

interface ChartBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

export function ChartBlock({ event, result }: ChartBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';
  const chartType = (event.input?.chart_type ?? event.input?.type ?? 'chart') as string;
  const title = (event.input?.title ?? '') as string;

  return (
    <div
      className={cn(
        'my-2 rounded-md border bg-muted/50',
        'transition-all duration-200',
        !isCompleted && 'border-purple-500/50 bg-purple-50/50 dark:bg-purple-950/20',
        isCompleted && 'border-purple-500/30',
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2">
        <BarChart2
          className={cn(
            'h-3.5 w-3.5 shrink-0',
            isCompleted ? 'text-purple-600' : 'text-purple-500',
          )}
        />
        <span className="text-xs sm:text-sm font-mono flex-1 truncate">
          <span className={isCompleted ? 'text-green-600' : 'text-purple-600'}>
            {isCompleted ? '✔' : '➜'} {isCompleted ? 'Generated' : 'Generating'} chart
          </span>
          {(chartType || title) && (
            <span className="ml-1 text-muted-foreground">
              {chartType}{title ? `: ${title}` : ''}
            </span>
          )}
        </span>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 shrink-0"
          onClick={() => setExpanded(!expanded)}
          aria-label={expanded ? 'Collapse' : 'Expand'}
        >
          {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </Button>
      </div>

      {expanded && (
        <div className="border-t p-2 text-[10px] sm:text-xs">
          {event.input && (
            <div className="mb-2">
              <div className="font-medium text-muted-foreground mb-1">Chart Config:</div>
              <pre className="overflow-x-auto rounded bg-background p-2">
                {JSON.stringify(event.input, null, 2)}
              </pre>
            </div>
          )}
          {result?.output && (
            <div>
              <div className="font-medium text-muted-foreground mb-1">Result:</div>
              <pre className="max-h-32 overflow-auto rounded bg-background p-2">
                {typeof result.output === 'string'
                  ? result.output.slice(0, 300)
                  : JSON.stringify(result.output, null, 2).slice(0, 300)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
