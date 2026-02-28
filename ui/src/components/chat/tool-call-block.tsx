'use client';

import { useState } from 'react';
import { ChevronRight, ChevronDown, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import type { AgentEvent } from '@/lib/api/types';

interface ToolCallBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

export function ToolCallBlock({ event, result }: ToolCallBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';
  const isStreaming = !isCompleted;

  return (
    <div className={cn(
      "my-2 rounded-md border bg-muted/50",
      "transition-all duration-200",
      isStreaming && "border-blue-500/50 bg-blue-50/50 dark:bg-blue-950/20"
    )}>
      <Button
        variant="ghost"
        className="flex w-full items-center gap-2 p-2 text-left text-xs sm:text-sm h-auto hover:bg-muted"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
        )}
        <span className={cn('font-mono', isCompleted ? 'text-green-600' : 'text-blue-600')}>
          {isCompleted ? '✔' : (
            <>
              <Loader2 className="h-3 w-3 sm:h-3.5 sm:w-3.5 animate-spin inline mr-1" />
              ➜
            </>
          )} {event.tool}
        </span>
      </Button>

      {expanded && (
        <div className="border-t p-2 text-[10px] sm:text-xs">
          {event.input && (
            <div className="mb-2">
              <div className="font-medium text-muted-foreground mb-1">Input:</div>
              <pre className="mt-1 overflow-x-auto rounded bg-background p-2 text-[10px] sm:text-xs">
                {JSON.stringify(event.input, null, 2)}
              </pre>
            </div>
          )}
          {result?.output && (
            <div>
              <div className="font-medium text-muted-foreground mb-1">Output:</div>
              <pre className="mt-1 max-h-32 sm:max-h-40 overflow-auto rounded bg-background p-2 text-[10px] sm:text-xs">
                {typeof result.output === 'string'
                  ? result.output.slice(0, 500)
                  : JSON.stringify(result.output, null, 2).slice(0, 500)}
                {(typeof result.output === 'string' ? result.output.length : JSON.stringify(result.output, null, 2).length) > 500 && '...'}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
