'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Sparkles, Loader2, Target, CheckCircle2, AlertCircle } from 'lucide-react';
import { TodoList } from './todo-list';
import { ToolCallBlock } from './tool-call-block';
import { SqlBlock } from './sql-block';
import { InsightsBlock, ChartRecommendationsBlock } from './insights-block';
import type { ChatMessage, StructuredContent } from '@/stores/chat-store';
import type { AgentEvent, MissionStreamEvent } from '@/lib/api/types';

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

// Mission stage display component
function MissionStageBlock({ event }: { event: MissionStreamEvent }) {
  const stageIcon = useMemo(() => {
    switch (event.stage) {
      case 'plan':
        return <Target className="h-4 w-4 text-blue-500" />;
      case 'explore':
        return <Sparkles className="h-4 w-4 text-purple-500" />;
      case 'execute':
        return <Loader2 className="h-4 w-4 text-orange-500 animate-spin" />;
      case 'synthesize':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'finalize':
        return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Loader2 className="h-4 w-4 text-gray-500" />;
    }
  }, [event.stage]);

  const stageLabel = event.stage ? event.stage.charAt(0).toUpperCase() + event.stage.slice(1) : 'Unknown';
  const confidence = event.confidence !== null ? `${Math.round(event.confidence * 100)}%` : null;
  const summary = event.output_summary;
  const artifacts = event.artifacts_produced?.length > 0 ? event.artifacts_produced.length : 0;

  return (
    <div className="rounded-lg border bg-card p-3 shadow-sm">
      <div className="flex items-center gap-2 text-sm font-medium">
        {stageIcon}
        <span>Mission Stage: {stageLabel}</span>
        {confidence && (
          <span className="ml-auto text-xs text-muted-foreground">
            Confidence: {confidence}
          </span>
        )}
      </div>
      {event.sequence_number > 0 && (
        <div className="text-xs text-muted-foreground mt-1">
          Step {event.sequence_number}
        </div>
      )}
      {summary && (
        <div className="text-sm text-muted-foreground mt-2">
          {summary}
        </div>
      )}
      {artifacts > 0 && (
        <div className="text-xs text-muted-foreground mt-2">
          {artifacts} artifact{artifacts !== 1 ? 's' : ''} produced
        </div>
      )}
    </div>
  );
}

export function AgentMessage({ message }: AgentMessageProps) {
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

  // Get the latest mission stage event for display
  const latestMissionEvent = useMemo(() => {
    if (!message.missionEvents || message.missionEvents.length === 0) return null;
    // Return the last mission stage event
    return message.missionEvents.filter(e => e.type === 'mission_stage').pop() || null;
  }, [message.missionEvents]);

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
      <div className="flex justify-end gap-3">
        <div className="max-w-[80%] rounded-2xl rounded-tr-none bg-primary px-5 py-3 text-primary-foreground shadow-sm">
          <p className="leading-relaxed">{message.content}</p>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 border border-primary/20">
            <User className="h-5 w-5 text-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 mt-1">
          <Bot className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
      </div>

      <div className="flex-1 space-y-3 overflow-hidden">
        {/* Mission stage display */}
        {latestMissionEvent && (
          <MissionStageBlock event={latestMissionEvent} />
        )}

        {/* Process status indicator during streaming (when no mission stage) */}
        {message.isStreaming && !latestMissionEvent && structured?.processStatus && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>{structured.processStatus}</span>
          </div>
        )}

        {message.todos && message.todos.length > 0 && (
          <div className="rounded-lg border bg-card p-2 shadow-sm">
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
          <SqlBlock sql={structured.sql} />
        )}

        {/* Summary/Answer Block */}
        {(displayContent || structured?.summary || structured?.reasoning) && (
          <div className="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card/50 px-5 py-4 shadow-sm">
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

        {/* Streaming indicator */}
        {message.isStreaming && !structured?.processStatus && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
            <Sparkles className="h-4 w-4" />
            <span className="font-mono text-xs">PROCESSING_REQUEST...</span>
          </div>
        )}
      </div>
    </div>
  );
}
