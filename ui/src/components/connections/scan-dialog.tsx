'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/ui/loading-button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';
import { tablesApi } from '@/lib/api/tables';
import { toast } from 'sonner';
import type { DatabaseConnection } from '@/lib/api/types';
import { logger } from '@/lib/logger';
import { useScanProgress } from '@/lib/stores/scan-progress';

interface ScanDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  connection: DatabaseConnection | null;
}

export function ScanDialog({ open, onOpenChange, connection }: ScanDialogProps) {
  const router = useRouter();
  const { startScan, completeScan } = useScanProgress();
  const [withAI, setWithAI] = useState(true);
  const [instruction, setInstruction] = useState('Generate detailed descriptions for all tables and columns');
  const [isLoading, setIsLoading] = useState(false);

  const handleScan = async () => {
    if (!connection) return;

    setIsLoading(true);

    // Start tracking scan progress
    startScan(connection.id, connection.alias || connection.id.slice(0, 8), withAI);

    // Show initial toast
    const scanToast = toast.loading(
      `Scanning ${connection.alias || 'database'}${withAI ? ' with AI' : ''}...`,
      {
        description: withAI ? 'Generating AI descriptions for tables and columns' : 'Analyzing database schema',
      }
    );

    try {
      // Get all tables for this connection first
      const tables = await tablesApi.list(connection.id);
      const tableIds = tables.map(t => t.id);

      if (tableIds.length === 0) {
        toast.error('No tables found in this connection', { id: scanToast });
        completeScan(connection.id);
        return;
      }

      await tablesApi.scan(tableIds, withAI, withAI ? instruction : undefined);

      // Complete scan tracking
      completeScan(connection.id);

      toast.success(
        `Successfully scanned ${tableIds.length} tables${withAI ? ' with AI descriptions' : ''}`,
        { id: scanToast }
      );
      onOpenChange(false);

      // Navigate to schema page to view results
      router.push(`/schema?connection=${connection.id}`);
    } catch (error) {
      logger.error('Scan error:', error);
      completeScan(connection.id);
      toast.error(error instanceof Error ? error.message : 'Failed to scan database', { id: scanToast });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Scan Database</DialogTitle>
          <DialogDescription>
            Scan {connection?.alias || 'database'} to analyze schema and optionally generate AI descriptions.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="with-ai"
              checked={withAI}
              onCheckedChange={(checked) => setWithAI(checked as boolean)}
            />
            <Label
              htmlFor="with-ai"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Generate AI descriptions for tables and columns
            </Label>
          </div>

          {withAI && (
            <div className="space-y-2">
              <Label htmlFor="instruction">AI Instruction (optional)</Label>
              <Textarea
                id="instruction"
                placeholder="Enter custom instructions for the AI..."
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                rows={3}
              />
              <p className="text-sm text-muted-foreground">
                Customize how the AI should describe your tables and columns
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
            Cancel
          </Button>
          <LoadingButton onClick={handleScan} isLoading={isLoading} loadingText="Scanning...">
            Start Scan
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
