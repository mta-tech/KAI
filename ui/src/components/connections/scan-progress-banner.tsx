'use client';

import { useScanProgress } from '@/lib/stores/scan-progress';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Sparkles } from 'lucide-react';
import { LiveRegion } from '@/components/ui/live-region';

export function ScanProgressBanner() {
  const { getAllScans } = useScanProgress();
  const activeScans = getAllScans();

  if (activeScans.length === 0) {
    return null;
  }

  const announcement = activeScans.length === 1 
    ? `Database scan in progress for ${activeScans[0].connectionAlias}`
    : `${activeScans.length} database scans in progress: ${activeScans.map(s => s.connectionAlias).join(', ')}`;

  return (
    <>
      <LiveRegion politeness="polite" role="status">
        {announcement}
      </LiveRegion>
      <Card className="border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950">
        <CardContent className="py-3">
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-blue-600 dark:text-blue-400" aria-hidden="true" />
            <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
              {activeScans.length === 1 ? 'Database scan in progress' : `${activeScans.length} database scans in progress`}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {activeScans.map((scan) => (
              <Badge
                key={scan.connectionId}
                variant="outline"
                className="gap-1 border-blue-300 bg-white text-blue-700 dark:border-blue-700 dark:bg-blue-900 dark:text-blue-100"
              >
                {scan.withAI && <Sparkles className="h-3 w-3" aria-hidden="true" />}
                {scan.connectionAlias}
                {scan.withAI && ' (AI)'}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </>
  );
}
