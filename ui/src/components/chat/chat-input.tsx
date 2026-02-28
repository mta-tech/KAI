'use client';

import { useState, useRef, useEffect } from 'react';
import { ArrowUp, Square } from 'lucide-react';
import { useKeyboardShortcuts } from '@/lib/hooks/use-keyboard-shortcuts';
import { cn } from '@/lib/utils';
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupAddon,
  InputGroupButton,
} from '@/components/ui/input-group';
import { ModelSelector } from './model-selector';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled: boolean;
  selectedModel?: string;
  onModelChange?: (model: string) => void;
}

export function ChatInput({ onSend, onStop, isStreaming, disabled, selectedModel, onModelChange }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 256);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    if (!isStreaming) {
      textareaRef.current?.focus();
    }
  }, [isStreaming]);

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
    <InputGroup className="min-h-[52px]">
      <InputGroupTextarea
        ref={textareaRef}
        value={input}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your data..."
        className={cn(
          'min-h-[52px] max-h-64 touch-manipulation',
          'placeholder:text-muted-foreground/60'
        )}
        disabled={disabled}
        rows={1}
        style={{ height: 'auto' }}
      />

      {/* Bottom bar with model selector and send button */}
      <InputGroupAddon align="inline-start" className="absolute bottom-2 left-2">
        {selectedModel !== undefined && onModelChange && (
          <ModelSelector
            value={selectedModel}
            onChange={onModelChange}
            disabled={isStreaming || disabled}
          />
        )}
        <span className="text-[10px] text-muted-foreground/40 hidden sm:inline ml-1">
          Enter to send
        </span>
      </InputGroupAddon>

      <InputGroupAddon align="inline-end" className="absolute bottom-2 right-2">
        {isStreaming ? (
          <InputGroupButton
            variant="destructive"
            size="icon-xs"
            onClick={onStop}
            aria-label="Stop generation"
            type="button"
          >
            <Square className="h-3.5 w-3.5" aria-hidden="true" />
          </InputGroupButton>
        ) : (
          <InputGroupButton
            size="icon-xs"
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            aria-label="Send message"
            type="submit"
          >
            <ArrowUp className="h-4 w-4" aria-hidden="true" />
          </InputGroupButton>
        )}
      </InputGroupAddon>
    </InputGroup>
  );
}
