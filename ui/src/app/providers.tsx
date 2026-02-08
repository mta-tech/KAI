'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { Toaster } from '@/components/ui/sonner';
import { ServiceWorkerProvider } from '@/components/service-worker-provider';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { AnalyticsProvider } from '@/components/analytics-provider';

/**
 * Calculate exponential backoff delay for retries
 * @param attemptNumber - The current retry attempt number
 * @returns Delay in milliseconds
 */
function retryDelay(attemptNumber: number): number {
  // Exponential backoff: 1s, 2s, 4s, 8s, max 10s
  const delay = Math.min(1000 * 2 ** (attemptNumber - 1), 10000);
  // Add some jitter to avoid thundering herd
  return delay + Math.random() * 500;
}

/**
 * Check if an error is retryable
 * @param error - The error to check
 * @returns Whether the error should be retried
 */
function isRetryable(error: unknown): boolean {
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    
    // Don't retry client errors (4xx)
    if (message.includes('400') || message.includes('validation')) {
      return false;
    }
    if (message.includes('401') || message.includes('unauthorized')) {
      return false;
    }
    if (message.includes('403') || message.includes('forbidden')) {
      return false;
    }
    if (message.includes('404') || message.includes('not found')) {
      return false;
    }
    if (message.includes('409') || message.includes('conflict')) {
      return false;
    }
    if (message.includes('422')) {
      return false;
    }
    
    // Retry server errors (5xx) and network issues
    if (message.includes('500') || message.includes('server')) {
      return true;
    }
    if (message.includes('502') || message.includes('503') || message.includes('504')) {
      return true;
    }
    if (message.includes('failed to fetch') || message.includes('network')) {
      return true;
    }
  }
  
  // Retry unknown errors up to a point
  return true;
}

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            retry: 1,
          },
          mutations: {
            retry: (failureCount, error) => {
              // Max 3 retries
              if (failureCount >= 3) {
                return false;
              }
              
              // Only retry retryable errors
              return isRetryable(error);
            },
            retryDelay,
            onError: (error) => {
              // Import dynamically to avoid circular dependencies
              import('@/lib/api/errors').then(({ handleApiError }) => {
                handleApiError(error);
              });
            },
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider delayDuration={200} skipDelayDuration={300}>
          <AnalyticsProvider>
            <ServiceWorkerProvider>
              {children}
            </ServiceWorkerProvider>
          </AnalyticsProvider>
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
