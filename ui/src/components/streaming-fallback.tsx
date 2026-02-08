/**
 * StreamingFallback component
 *
 * Used as a fallback for Suspense boundaries when components
 * are loading data or waiting for streaming responses.
 */

import { Loader2 } from 'lucide-react';

interface StreamingFallbackProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function StreamingFallback({ message = 'Loading...', size = 'md' }: StreamingFallbackProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <div className="flex items-center justify-center gap-2 p-4 text-muted-foreground">
      <Loader2 className={`animate-spin ${sizeClasses[size]}`} />
      {message && <span className="text-sm">{message}</span>}
    </div>
  );
}

/**
 * Page-level loading fallback with skeleton
 */
export function PageLoadingFallback() {
  return (
    <div className="flex items-center justify-center h-full">
      <StreamingFallback message="Loading page..." size="lg" />
    </div>
  );
}
