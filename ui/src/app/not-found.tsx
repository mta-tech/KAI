'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileQuestion } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <Card className="w-full max-w-md border-muted-foreground/20 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <FileQuestion className="h-6 w-6 text-muted-foreground" aria-hidden="true" />
            <span>Page Not Found</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="flex gap-2">
            <Button onClick={() => (window.location.href = '/')}>
              Go to Dashboard
            </Button>
            <Button
              variant="outline"
              onClick={() => window.history.back()}
            >
              Go Back
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
