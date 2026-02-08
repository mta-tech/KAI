'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import { TodoList } from './todo-list';
import { ToolCallBlock } from './tool-call-block';
import { SqlBlock } from './sql-block';
import { SqlResultsTable, useQueryResults } from './sql-results-table';
import { InsightsBlock, ChartRecommendationsBlock } from './insights-block';
import { Visualizations } from './visualizations';
import { ProcessStatus, StreamingMessage } from './streaming-indicator';
import { MessageActions } from './message-actions';
import type { ChatMessage, StructuredContent } from '@/stores/chat-store';
import type { AgentEvent } from '@/lib/api/types';

interface AgentMessageProps {
  message: ChatMessage;
}

// Helper to format array/object to markdown string
function formatToMarkdown(value: unknown): string {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    return value.map((item) => {
      if (typeof item === 'string') return `- ${item}`;
      if (typeof item === 'object' && item !== null) {
        // Handle objects with title/description or similar structure
        const obj = item as Record<string, unknown>;
        if (obj.title && obj.description) {
          return `**${obj.title}**: ${obj.description}`;
        }
        if (obj.chart_type && obj.reason) {
          return `**${obj.chart_type}**: ${obj.reason}`;
        }
        return `- ${JSON.stringify(item)}`;
      }
      return `- ${String(item)}`;
    }).join('\n');
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

// Parse JSON from content if it's a JSON code block
function parseJsonContent(content: string): { parsed: Record<string, unknown> | null; text: string } {
  // Check for JSON code block pattern: ```json\n{...}\n```
  const jsonBlockMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
  if (jsonBlockMatch) {
    try {
      const parsed = JSON.parse(jsonBlockMatch[1]);
      // Remove the JSON block from content
      const text = content.replace(/```json\s*[\s\S]*?\s*```/, '').trim();
      return { parsed, text };
    } catch {
      // Not valid JSON, return as-is
    }
  }

  // Check if content is just raw JSON
  const trimmed = content.trim();
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      const parsed = JSON.parse(trimmed);
      return { parsed, text: '' };
    } catch {
      // Not valid JSON
    }
  }

  return { parsed: null, text: content };
}

export function AgentMessage({ message }: AgentMessageProps) {
  const queryResults = useQueryResults(message.events);

  const toolPairs = useMemo(() => {
    if (!message.events) return [];

    const pairs: { start: AgentEvent; end?: AgentEvent }[] = [];
    const pending: AgentEvent[] = [];

    for (const event of message.events) {
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
  }, [message.events]);

  // Parse JSON from content and merge with structured content
  const { displayContent, structured } = useMemo(() => {
    const { parsed, text } = parseJsonContent(message.content);

    // Start with existing structured content
    const structured: StructuredContent = { ...message.structured };
    let displayContent = text;

    if (parsed) {
      // Extract structured fields from parsed JSON
      if (parsed.sql && typeof parsed.sql === 'string') {
        structured.sql = parsed.sql;
      }
      if (parsed.summary) {
        structured.summary = formatToMarkdown(parsed.summary);
        displayContent = ''; // Don't show raw content if we have summary
      }
      if (parsed.insights) {
        structured.insights = formatToMarkdown(parsed.insights);
      }
      if (parsed.chart_recommendations) {
        structured.chartRecommendations = formatToMarkdown(parsed.chart_recommendations);
      }
      if (parsed.reasoning) {
        structured.reasoning = formatToMarkdown(parsed.reasoning);
      }
    }

    return { parsedContent: parsed, displayContent, structured };
  }, [message.content, message.structured]);

  if (message.role === 'user') {
    return (
      <div className="flex justify-end gap-2 sm:gap-3 group">
        <div className="max-w-[85%] sm:max-w-[80%] rounded-2xl rounded-tr-none bg-primary px-4 py-3 sm:px-5 sm:py-3 text-primary-foreground shadow-sm relative">
          <p className="text-sm sm:text-base leading-relaxed break-words">{message.content}</p>
          <div className="absolute top-2 right-2">
            <MessageActions message={message} />
          </div>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 border border-primary/20 mt-1">
          <User className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-2 sm:gap-4 group">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 mt-1 relative">
        <Bot className="h-4 w-4 sm:h-5 sm:w-5 text-emerald-600 dark:text-emerald-400" />
        {/* Online indicator for streaming */}
        {message.isStreaming && (
          <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
        )}
      </div>

      <div className="flex-1 space-y-2 sm:space-y-3 overflow-hidden min-w-0 relative">
        {/* Message Actions - positioned in top right */}
        <div className="absolute top-0 right-0 z-10">
          <MessageActions message={message} />
        </div>

        {/* Process status indicator during streaming */}
        {message.isStreaming && structured?.processStatus && (
          <ProcessStatus status={structured.processStatus} />
        )}

        {message.todos && message.todos.length > 0 && (
          <div className="rounded-lg border bg-card p-2 sm:p-3 shadow-sm">
            <TodoList todos={message.todos} />
          </div>
        )}

        {toolPairs.length > 0 && (
          <div className="space-y-2">
            {toolPairs.map((pair, i) => (
              <ToolCallBlock key={i} event={pair.start} result={pair.end} />
            ))}
          </div>
        )}

        {/* SQL Query Block */}
        {structured?.sql && (
          <SqlBlock sql={structured.sql} isStreaming={message.isStreaming} />
        )}

        {/* SQL Results Table */}
        {queryResults && !message.isStreaming && (
          <SqlResultsTable results={queryResults} />
        )}

        {/* Summary/Answer Block */}
        {(displayContent || structured?.summary || structured?.reasoning) && (
          <div className="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card/50 px-3 py-3 sm:px-5 sm:py-4 shadow-sm prose-headings:text-base sm:prose-headings:text-lg prose-p:text-sm sm:prose-p:text-base relative overflow-hidden">
            {/* Streaming shimmer effect */}
            {message.isStreaming && (
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-shimmer" />
              </div>
            )}
            <ReactMarkdown>
              {structured?.summary || displayContent || structured?.reasoning || ''}
            </ReactMarkdown>
          </div>
        )}

        {/* Insights Block */}
        {structured?.insights && (
          <InsightsBlock insights={structured.insights} />
        )}

        {/* Chart Recommendations Block */}
        {structured?.chartRecommendations && (
          <ChartRecommendationsBlock recommendations={structured.chartRecommendations} />
        )}

        {/* Visualizations */}
        {structured?.chartRecommendations && !message.isStreaming && (
          <Visualizations
            recommendations={structured.chartRecommendations}
            data={[]} // Data will be extracted from events by the component
          />
        )}

        {/* Streaming indicator at bottom */}
        {message.isStreaming && !structured?.processStatus && (
          <StreamingMessage message="AI is responding" />
        )}
      </div>
    </div>
  );
}
