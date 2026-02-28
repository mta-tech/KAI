'use client';

import { useState } from 'react';
import { FlaskConical, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import type { AgentEvent } from '@/lib/api/types';

interface DataAnalysisBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

export function DataAnalysisBlock({ event, result }: DataAnalysisBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';
  const toolLabel = event.tool === 'create_python_execute_tool'
    ? 'Python analysis'
    : 'Data analysis';

  return (
    <div
      className={cn(
        'my-2 rounded-md border bg-muted/50',
        'transition-all duration-200',
        !isCompleted && 'border-amber-500/50 bg-amber-50/50 dark:bg-amber-950/20',
        isCompleted && 'border-amber-500/30',
      )}
    >
      <div className="flex items-center gap-2 px-3 py-2">
        {isCompleted ? (
          <FlaskConical className="h-3.5 w-3.5 shrink-0 text-amber-600" />
        ) : (
          <Loader2 className="h-3.5 w-3.5 shrink-0 text-amber-500 animate-spin" />
        )}
        <span className="text-xs sm:text-sm font-mono flex-1 truncate">
          <span className={isCompleted ? 'text-green-600' : 'text-amber-600'}>
            {isCompleted ? '✔' : '➜'} {isCompleted ? 'Ran' : 'Running'} {toolLabel}
          </span>
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
              <div className="font-medium text-muted-foreground mb-1">Input:</div>
              <pre className="overflow-x-auto rounded bg-background p-2">
                {JSON.stringify(event.input, null, 2)}
              </pre>
            </div>
          )}
          {result?.output && (
            <div>
              <div className="font-medium text-muted-foreground mb-1">Output:</div>
              <pre className="max-h-40 overflow-auto rounded bg-background p-2">
                {typeof result.output === 'string'
                  ? result.output.slice(0, 500)
                  : JSON.stringify(result.output, null, 2).slice(0, 500)}
                {(typeof result.output === 'string'
                  ? result.output.length
                  : JSON.stringify(result.output, null, 2).length) > 500 && '...'}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
