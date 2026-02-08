import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

interface ErrorDisplayProps {
  error: unknown;
  onRetry?: () => void;
  title?: string;
  description?: string;
  showRetry?: boolean;
  isRetrying?: boolean;
}

/**
 * Error display component with optional retry button
 * 
 * Provides consistent error UI with:
 * - User-friendly error messages
 * - Optional manual retry button
 * - Loading state during retry
 * 
 * @example
 * ```tsx
 * <ErrorDisplay 
 *   error={error} 
 *   onRetry={() => mutation.manualRetry()} 
 *   isRetrying={mutation.isPending} 
 * />
 * ```
 */
export function ErrorDisplay({
  error,
  onRetry,
  title,
  description,
  showRetry = true,
  isRetrying = false,
}: ErrorDisplayProps) {
  // Generate user-friendly error message
  const getErrorDetails = (err: unknown): { title: string; description: string } => {
    if (error instanceof Error) {
      const message = error.message.toLowerCase();
      
      if (message.includes('failed to fetch') || message.includes('network')) {
        return {
          title: 'Connection Error',
          description: 'Unable to connect to the server. Please check your internet connection.',
        };
      }
      if (message.includes('401') || message.includes('unauthorized')) {
        return {
          title: 'Authentication Error',
          description: 'Your session has expired. Please log in again.',
        };
      }
      if (message.includes('403') || message.includes('forbidden')) {
        return {
          title: 'Permission Denied',
          description: "You don't have permission to perform this action.",
        };
      }
      if (message.includes('404') || message.includes('not found')) {
        return {
          title: 'Not Found',
          description: 'The requested resource was not found.',
        };
      }
      if (message.includes('409') || message.includes('conflict')) {
        return {
          title: 'Conflict',
          description: 'This action conflicts with existing data. Please refresh and try again.',
        };
      }
      if (message.includes('422') || message.includes('validation')) {
        return {
          title: 'Validation Error',
          description: 'Please check your input and try again.',
        };
      }
      if (message.includes('500') || message.includes('server')) {
        return {
          title: 'Server Error',
          description: 'The server encountered an error. Please try again later.',
        };
      }
      if (message.includes('502') || message.includes('503')) {
        return {
          title: 'Service Unavailable',
          description: 'The service is temporarily unavailable. Please try again later.',
        };
      }
    }
    
    // Default error message
    return {
      title: title || 'Something went wrong',
      description: description || (error instanceof Error ? error.message : 'An unexpected error occurred.'),
    };
  };

  const { title: errorTitle, description: errorDescription } = getErrorDetails(error);

  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{errorTitle}</AlertTitle>
      <AlertDescription>{errorDescription}</AlertDescription>
      {showRetry && onRetry && (
        <div className="mt-4 flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            disabled={isRetrying}
          >
            {isRetrying ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Retrying...
              </>
            ) : (
              'Try Again'
            )}
          </Button>
        </div>
      )}
    </Alert>
  );
}

function AlertCircle({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}
