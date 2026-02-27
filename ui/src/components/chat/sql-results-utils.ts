import type { AgentEvent } from '@/lib/api/types';

export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  executionTime?: number;
}

/** Parse a tool_end event output into a QueryResult, or return null if not parseable. */
export function parseQueryResults(event: AgentEvent): QueryResult | null {
  if (event.type !== 'tool_end' || !event.output) return null;

  const output = typeof event.output === 'string'
    ? JSON.parse(event.output)
    : event.output;

  if (output.results && Array.isArray(output.results)) {
    return {
      columns: output.columns || Object.keys(output.results[0] || {}),
      rows: output.results,
      rowCount: output.row_count || output.results.length,
      executionTime: output.execution_time,
    };
  }

  if (Array.isArray(output) && output.length > 0) {
    return {
      columns: Object.keys(output[0]),
      rows: output,
      rowCount: output.length,
    };
  }

  return null;
}

/** Format a table cell value for display. Returns a string or null/boolean sentinel. */
export function formatCellValue(value: unknown): React.ReactNode {
  if (value === null || value === undefined) {
    return null; // caller renders as NULL
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

/** Generate a CSV string from the given data and columns. */
export function generateCSV(rows: Record<string, unknown>[], columns: string[]): string {
  const csvRows = rows.map((row) =>
    columns.map((col) => {
      const val = String(row[col] ?? '');
      if (val.includes(',') || val.includes('"') || val.includes('\n')) {
        return `"${val.replace(/"/g, '""')}"`;
      }
      return val;
    })
  );
  return [columns.join(','), ...csvRows.map((r) => r.join(','))].join('\n');
}

/** Trigger a browser download for the given content. */
export function downloadFile(content: string, filename: string, type: string): void {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
