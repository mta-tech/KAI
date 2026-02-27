import { useMemo } from 'react';
import type { AgentEvent } from '@/lib/api/types';

export interface ToolPair {
  start: AgentEvent;
  end?: AgentEvent;
}

export function useToolPairs(events: AgentEvent[] | undefined): ToolPair[] {
  return useMemo(() => {
    if (!events) return [];

    const pairs: ToolPair[] = [];
    const pending: AgentEvent[] = [];

    for (const event of events) {
      if (event.type === 'tool_start') {
        pending.push(event);
      } else if (event.type === 'tool_end') {
        const start = pending.find((p) => p.tool === event.tool);
        if (start) {
          pairs.push({ start, end: event });
          pending.splice(pending.indexOf(start), 1);
        }
      }
    }

    for (const start of pending) {
      pairs.push({ start });
    }

    return pairs;
  }, [events]);
}
