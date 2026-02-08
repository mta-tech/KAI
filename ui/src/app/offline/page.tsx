'use client';

/**
 * Offline Page
 *
 * Shown when the user is offline and the requested resource is not cached.
 */
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { WifiOff, RefreshCw } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Redirect to home if we come back online
  useEffect(() => {
    if (isOnline) {
      const timeout = setTimeout(() => {
        window.location.href = '/';
      }, 1000);
      return () => clearTimeout(timeout);
    }
  }, [isOnline]);

  return (
    <div className="flex h-full items-center justify-center p-6 bg-background">
      <Card className="w-full max-w-md border-destructive/20 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <WifiOff className="h-5 w-5" />
            You're Offline
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {isOnline
              ? 'Connection restored! Redirecting...'
              : 'It looks like you\'ve lost your internet connection. Some features may not be available.'}
          </p>

          {!isOnline && (
            <>
              <div className="rounded-lg bg-muted p-4">
                <p className="text-xs text-muted-foreground">
                  <strong>What you can do offline:</strong>
                  <br />• View previously loaded pages
                  <br />• Access cached knowledge base
                  <br />• Review chat history
                </p>
              </div>

              <Button
                onClick={() => window.location.reload()}
                className="w-full"
                variant="default"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
