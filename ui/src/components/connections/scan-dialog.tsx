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
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';
import { tablesApi } from '@/lib/api/tables';
import { toast } from 'sonner';
import type { DatabaseConnection } from '@/lib/api/types';

interface ScanDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  connection: DatabaseConnection | null;
}

export function ScanDialog({ open, onOpenChange, connection }: ScanDialogProps) {
  const router = useRouter();
  const [withAI, setWithAI] = useState(true);
  const [instruction, setInstruction] = useState('Generate detailed descriptions for all tables and columns');
  const [isLoading, setIsLoading] = useState(false);

  const handleScan = async () => {
    if (!connection) return;

    setIsLoading(true);
    try {
      // Get all tables for this connection first
      const tables = await tablesApi.list(connection.id);
      const tableIds = tables.map(t => t.id);

      if (tableIds.length === 0) {
        toast.error('No tables found in this connection');
        return;
      }

      await tablesApi.scan(tableIds, withAI, withAI ? instruction : undefined);

      toast.success(`Successfully scanned ${tableIds.length} tables${withAI ? ' with AI descriptions' : ''}`);
      onOpenChange(false);

      // Navigate to schema page to view results
      router.push(`/schema?connection=${connection.id}`);
    } catch (error) {
      console.error('Scan error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to scan database');
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
          <Button onClick={handleScan} disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? 'Scanning...' : 'Start Scan'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
