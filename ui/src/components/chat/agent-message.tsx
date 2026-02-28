'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { TodoList } from './todo-list';
import { ToolCallBlock, useToolPairs } from './tool-calls';
import { SqlBlock } from './sql-block';
import { SqlResultsTable, useQueryResults } from './sql-results-table';
import { InsightsBlock, ChartRecommendationsBlock } from './insights-block';
import { Visualizations } from './visualizations';
import { ProcessStatus, StreamingMessage } from './streaming-indicator';
import { MessageActions } from './message-actions';
import { FollowUpSuggestions } from './follow-up-suggestions';
import { useChat } from '@/hooks/use-chat';
import type { ChatMessage, StructuredContent } from '@/stores/chat-store';
import { formatToMarkdown, parseJsonContent } from './chat-message-utils';

interface AgentMessageProps {
  message: ChatMessage;
}

export function AgentMessage({ message }: AgentMessageProps) {
  const queryResults = useQueryResults(message.events);
  const toolPairs = useToolPairs(message.events);
  const { sendMessage } = useChat();

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
      <div className="flex justify-end group">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl bg-primary/10 px-4 py-3 text-foreground relative">
          <p className="text-sm sm:text-base leading-relaxed break-words">{message.content}</p>
          <div className="absolute top-1.5 right-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <MessageActions message={message} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="group">
      <div
        className="space-y-3 overflow-hidden min-w-0 relative"
        aria-live="polite"
        aria-busy={message.isStreaming}
        aria-label={message.isStreaming ? 'AI is responding' : 'AI response'}
      >
        {/* Message Actions - positioned in top right */}
        <div className="absolute top-0 right-0 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
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
          <div
            className={`prose prose-sm dark:prose-invert max-w-none rounded-xl border border-border/50 bg-card/50 px-3 py-3 sm:px-5 sm:py-4 shadow-sm prose-headings:text-base sm:prose-headings:text-lg prose-p:text-sm sm:prose-p:text-base relative overflow-hidden${message.isStreaming ? ' streaming-cursor' : ''}`}
          >
            {/* Streaming shimmer effect */}
            {message.isStreaming && (
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-foreground/5 to-transparent animate-shimmer" />
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

        {/* Follow-up suggestions (shown after streaming completes) */}
        {!message.isStreaming && structured?.followUpSuggestions && structured.followUpSuggestions.length > 0 && (
          <FollowUpSuggestions
            suggestions={structured.followUpSuggestions.slice(0, 4)}
            onSelect={sendMessage}
          />
        )}
      </div>
    </div>
  );
}
