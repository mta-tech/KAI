'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Square, Mic } from 'lucide-react';
import { useKeyboardShortcuts } from '@/lib/hooks/use-keyboard-shortcuts';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled: boolean;
}

export function ChatInput({ onSend, onStop, isStreaming, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea based on content
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      // Reset height to auto to get the correct scrollHeight
      textareaRef.current.style.height = 'auto';
      // Set new height based on scrollHeight, with max height constraint
      const newHeight = Math.min(textareaRef.current.scrollHeight, 150);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    if (!isStreaming) {
      textareaRef.current?.focus();
    }
  }, [isStreaming]);

  // Register keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'Enter',
      description: 'Send message',
      action: handleSubmit,
      metaKey: true,
      category: 'Chat',
    },
    {
      key: 'c',
      description: 'Focus chat input',
      action: () => textareaRef.current?.focus(),
      metaKey: true,
      category: 'Chat',
    },
    {
      key: 'Escape',
      description: 'Stop generation',
      action: onStop,
      category: 'Chat',
    },
  ], true);

  return (
    <div className="flex gap-2 items-end">
      <div className="flex-1 relative">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your data... (Cmd+Enter to send)"
          className={cn(
            "min-h-[48px] max-h-[150px] resize-none overflow-y-auto",
            "py-3 px-4 text-base",
            "touch-manipulation" // Improves touch responsiveness
          )}
          disabled={disabled}
          rows={1}
          style={{
            height: 'auto',
          } as React.CSSProperties}
        />
      </div>
      <div className="flex gap-1 shrink-0">
        {/* Voice input button - placeholder for future implementation */}
        <Button
          variant="ghost"
          size="icon"
          className="h-11 w-11 shrink-0 sm:hidden"
          aria-label="Voice input"
          type="button"
          tabIndex={-1}
        >
          <Mic className="h-5 w-5" />
        </Button>

        {isStreaming ? (
          <Button
            variant="destructive"
            size="icon"
            onClick={onStop}
            aria-label="Stop generation"
            className="h-11 w-11 shrink-0 sm:h-10 sm:w-10"
            type="button"
          >
            <Square className="h-4 w-4 sm:h-4 sm:w-4" aria-hidden="true" />
          </Button>
        ) : (
          <Button
            size="icon"
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            aria-label="Send message"
            className="h-11 w-11 shrink-0 sm:h-10 sm:w-10"
            type="submit"
          >
            <Send className="h-4 w-4 sm:h-4 sm:w-4" aria-hidden="true" />
          </Button>
        )}
      </div>
    </div>
  );
}
