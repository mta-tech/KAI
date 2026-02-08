'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';
import { logger } from '@/lib/logger';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    logger.error('Application error:', error);
  }, [error]);

  return (
    <div 
      className="flex h-full items-center justify-center p-6"
      role="main"
      aria-label="Error page"
    >
      <Card className="w-full max-w-md border-destructive/20 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" aria-hidden="true" />
            <span>System Error</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            An error occurred while loading this page. This has been logged and we'll look into it.
          </p>
          {error.message && (
            <details className="rounded bg-muted p-2 text-xs">
              <summary className="cursor-pointer font-medium">Error details</summary>
              <pre className="mt-2 overflow-x-auto">
                {error.message}
              </pre>
            </details>
          )}
          <div className="flex gap-2">
            <Button onClick={reset} aria-label="Try reloading this page">
              Try again
            </Button>
            <Button 
              variant="outline" 
              onClick={() => (window.location.href = '/')}
              aria-label="Go to dashboard home page"
            >
              Go to Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
