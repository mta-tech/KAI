import { useMemo } from 'react';
import type { AgentEvent } from '@/lib/api/types';
import { parseQueryResults } from './sql-results-utils';
import type { QueryResult } from './sql-results-utils';

export type { QueryResult };

/** Extract the last sql_execute tool result from a list of agent events. */
export function useQueryResults(events: AgentEvent[] = []): QueryResult | null {
  return useMemo(() => {
    for (let i = events.length - 1; i >= 0; i--) {
      const event = events[i];
      if (event.type === 'tool_end' && event.tool === 'sql_execute') {
        return parseQueryResults(event);
      }
    }
    return null;
  }, [events]);
}
