'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Sparkles } from 'lucide-react';
import { TodoList } from './todo-list';
import { ToolCallBlock } from './tool-call-block';
import type { ChatMessage } from '@/stores/chat-store';
import type { AgentEvent } from '@/lib/api/types';

interface AgentMessageProps {
  message: ChatMessage;
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

        {message.content && (
          <div className="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card/50 px-5 py-4 shadow-sm">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {message.isStreaming && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
            <Sparkles className="h-4 w-4" />
            <span className="font-mono text-xs">PROCESSING_REQUEST...</span>
          </div>
        )}
      </div>
    </div>
  );
}
