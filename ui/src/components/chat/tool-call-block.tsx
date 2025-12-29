'use client';

import { useState } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AgentEvent } from '@/lib/api/types';

interface ToolCallBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

export function ToolCallBlock({ event, result }: ToolCallBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';

  return (
    <div className="my-2 rounded-md border bg-muted/50">
      <button
        className="flex w-full items-center gap-2 p-2 text-left text-sm"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
        <span className={cn('font-mono', isCompleted ? 'text-green-600' : 'text-blue-600')}>
          {isCompleted ? '✔' : '➜'} {event.tool}
        </span>
      </button>

      {expanded && (
        <div className="border-t p-2 text-xs">
          {event.input && (
            <div className="mb-2">
              <div className="font-medium text-muted-foreground">Input:</div>
              <pre className="mt-1 overflow-x-auto rounded bg-background p-2">
                {JSON.stringify(event.input, null, 2)}
              </pre>
            </div>
          )}
          {result?.output && (
            <div>
              <div className="font-medium text-muted-foreground">Output:</div>
              <pre className="mt-1 max-h-40 overflow-auto rounded bg-background p-2">
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
