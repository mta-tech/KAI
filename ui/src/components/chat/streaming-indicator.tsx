'use client';

import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface StreamingIndicatorProps {
  status?: string;
  className?: string;
}

export function StreamingIndicator({ status, className }: StreamingIndicatorProps) {
  return (
    <div className={cn('flex items-center gap-2 text-muted-foreground', className)}>
      <div className="flex items-center gap-1">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
        </span>
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75 delay-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-primary delay-75"></span>
        </span>
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75 delay-150"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-primary delay-150"></span>
        </span>
      </div>
      {status && (
        <span className="text-xs sm:text-sm font-medium">{status}</span>
      )}
    </div>
  );
}

interface ProcessStatusProps {
  status: string;
  className?: string;
}

export function ProcessStatus({ status, className }: ProcessStatusProps) {
  return (
    <div className={cn(
      'inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs sm:text-sm',
      'bg-primary/5 border-primary/20 text-primary',
      className
    )}>
      <Loader2 className="h-3 w-3 sm:h-3.5 sm:w-3.5 animate-spin" />
      <span className="font-medium">{status}</span>
    </div>
  );
}

interface StreamingDotsProps {
  className?: string;
}

export function StreamingDots({ className }: StreamingDotsProps) {
  return (
    <div className={cn('flex items-center gap-1', className)}>
      <span className="h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]"></span>
      <span className="h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.15s]"></span>
      <span className="h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-primary animate-bounce"></span>
    </div>
  );
}

interface StreamingMessageProps {
  message: string;
  className?: string;
}

export function StreamingMessage({ message, className }: StreamingMessageProps) {
  return (
    <div className={cn(
      'flex items-center gap-2 rounded-lg border bg-muted/50 px-3 py-2',
      'text-xs sm:text-sm text-muted-foreground',
      className
    )}>
      <StreamingDots />
      <span className="font-mono text-[10px] sm:text-xs">{message}</span>
    </div>
  );
}
