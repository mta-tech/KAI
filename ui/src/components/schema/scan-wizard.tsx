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
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Loader2,
  Database,
  Sparkles,
  Settings,
  CheckCircle2,
  AlertCircle,
  Info,
  ChevronRight,
  ChevronLeft,
} from 'lucide-react';
import { tablesApi } from '@/lib/api/tables';
import { toast } from 'sonner';
import type { DatabaseConnection, TableDescription } from '@/lib/api/types';
import { logger } from '@/lib/logger';
import { useScanProgress } from '@/lib/stores/scan-progress';
import { cn } from '@/lib/utils';

type ScanStep = 'welcome' | 'options' | 'tables' | 'ai-config' | 'progress' | 'complete';

interface ScanWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  connection: DatabaseConnection | null;
}

interface ScanOptions {
  withAI: boolean;
  instruction: string;
  selectedTables: string[];
  scanMode: 'full' | 'incremental' | 'selected';
}

const defaultInstructions = {
  detailed: 'Generate detailed descriptions for all tables and columns, explaining their purpose and relationships.',
  simple: 'Generate concise descriptions focusing on the main purpose of each table and column.',
  business: 'Generate business-focused descriptions that explain the data from a business perspective.',
  technical: 'Generate technical descriptions with data types, constraints, and technical details.',
};

export function ScanWizard({ open, onOpenChange, connection }: ScanWizardProps) {
  const router = useRouter();
  const { startScan, completeScan } = useScanProgress();

  // Wizard state
  const [currentStep, setCurrentStep] = useState<ScanStep>('welcome');
  const [options, setOptions] = useState<ScanOptions>({
    withAI: true,
    instruction: defaultInstructions.detailed,
    selectedTables: [],
    scanMode: 'full',
  });

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [isTablesLoading, setIsTablesLoading] = useState(false);
  const [tables, setTables] = useState<TableDescription[]>([]);
  const [scanProgress, setScanProgress] = useState({ current: 0, total: 0 });
  const [scanResults, setScanResults] = useState({ scanned: 0, failed: 0, skipped: 0 });

  const steps: { id: ScanStep; title: string; icon: typeof Database }[] = [
    { id: 'welcome', title: 'Welcome', icon: Database },
    { id: 'options', title: 'Scan Options', icon: Settings },
    { id: 'tables', title: 'Select Tables', icon: Database },
    { id: 'ai-config', title: 'AI Configuration', icon: Sparkles },
    { id: 'progress', title: 'Scanning', icon: Loader2 },
    { id: 'complete', title: 'Complete', icon: CheckCircle2 },
  ];

  const currentStepIndex = steps.findIndex(s => s.id === currentStep);
  const canGoBack = currentStepIndex > 0 && currentStep !== 'progress' && currentStep !== 'complete';
  const canGoNext = currentStepIndex < steps.length - 1 && currentStep !== 'progress' && currentStep !== 'complete';

  const loadTables = async () => {
    if (!connection) return;

    setIsTablesLoading(true);
    try {
      const tablesData = await tablesApi.list(connection.id);
      setTables(tablesData);
      // By default, select all tables that haven't been scanned
      const unscannedTables = tablesData.filter(t => t.sync_status === 'NOT_SCANNED');
      setOptions(prev => ({
        ...prev,
        selectedTables: unscannedTables.map(t => t.id)
      }));
    } catch (error) {
      logger.error('Failed to load tables:', error);
      toast.error('Failed to load tables');
    } finally {
      setIsTablesLoading(false);
    }
  };

  const handleNext = async () => {
    if (currentStep === 'tables' && tables.length === 0) {
      await loadTables();
    }

    if (currentStep === 'ai-config') {
      await executeScan();
    } else {
      setCurrentStep(steps[currentStepIndex + 1].id);
    }
  };

  const handleBack = () => {
    if (canGoBack) {
      setCurrentStep(steps[currentStepIndex - 1].id);
    }
  };

  const executeScan = async () => {
    if (!connection) return;

    setIsLoading(true);
    setCurrentStep('progress');

    // Start tracking scan progress
    startScan(connection.id, connection.alias || connection.id.slice(0, 8), options.withAI);

    try {
      // Determine which tables to scan
      let tablesToScan: string[] = [];

      if (options.scanMode === 'selected') {
        tablesToScan = options.selectedTables;
      } else if (options.scanMode === 'incremental') {
        tablesToScan = tables.filter(t => t.sync_status === 'NOT_SCANNED').map(t => t.id);
      } else {
        tablesToScan = tables.map(t => t.id);
      }

      if (tablesToScan.length === 0) {
        toast.error('No tables to scan');
        setCurrentStep('options');
        setIsLoading(false);
        completeScan(connection.id);
        return;
      }

      setScanProgress({ current: 0, total: tablesToScan.length });

      // Show initial toast
      const scanToast = toast.loading(
        `Scanning ${tablesToScan.length} tables${options.withAI ? ' with AI' : ''}...`,
        {
          description: options.withAI ? 'Generating AI descriptions for tables and columns' : 'Analyzing database schema',
        }
      );

      await tablesApi.scan(tablesToScan, options.withAI, options.withAI ? options.instruction : undefined);

      // Simulate progress updates
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.floor(Math.random() * 10) + 5;
        if (progress > tablesToScan.length) progress = tablesToScan.length;
        setScanProgress({ current: progress, total: tablesToScan.length });

        if (progress >= tablesToScan.length) {
          clearInterval(progressInterval);
        }
      }, 500);

      // Wait a bit to show progress
      await new Promise(resolve => setTimeout(resolve, 2000));
      clearInterval(progressInterval);

      // Complete scan
      completeScan(connection.id);
      setScanResults({
        scanned: tablesToScan.length,
        failed: 0,
        skipped: tables.length - tablesToScan.length
      });

      toast.success(
        `Successfully scanned ${tablesToScan.length} tables${options.withAI ? ' with AI descriptions' : ''}`,
        { id: scanToast }
      );

      setCurrentStep('complete');
    } catch (error) {
      logger.error('Scan error:', error);
      completeScan(connection.id);
      toast.error(error instanceof Error ? error.message : 'Failed to scan database');
      setCurrentStep('options');
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = () => {
    onOpenChange(false);
    // Reset wizard state
    setCurrentStep('welcome');
    setOptions({
      withAI: true,
      instruction: defaultInstructions.detailed,
      selectedTables: [],
      scanMode: 'full',
    });
    setScanProgress({ current: 0, total: 0 });
    setScanResults({ scanned: 0, failed: 0, skipped: 0 });

    // Navigate to schema page to view results
    if (connection) {
      router.push(`/schema?connection=${connection.id}`);
    }
  };

  const toggleTableSelection = (tableId: string) => {
    setOptions(prev => ({
      ...prev,
      selectedTables: prev.selectedTables.includes(tableId)
        ? prev.selectedTables.filter(id => id !== tableId)
        : [...prev.selectedTables, tableId]
    }));
  };

  const toggleAllTables = () => {
    if (options.selectedTables.length === tables.length) {
      setOptions(prev => ({ ...prev, selectedTables: [] }));
    } else {
      setOptions(prev => ({ ...prev, selectedTables: tables.map(t => t.id) }));
    }
  };

  const getStepContent = () => {
    switch (currentStep) {
      case 'welcome':
        return <WelcomeStep connection={connection} />;
      case 'options':
        return <OptionsStep options={options} setOptions={setOptions} />;
      case 'tables':
        return (
          <TablesStep
            tables={tables}
            isLoading={isTablesLoading}
            selectedTables={options.selectedTables}
            onToggleTable={toggleTableSelection}
            onToggleAll={toggleAllTables}
            scanMode={options.scanMode}
          />
        );
      case 'ai-config':
        return <AIConfigStep options={options} setOptions={setOptions} />;
      case 'progress':
        return <ProgressStep progress={scanProgress} withAI={options.withAI} />;
      case 'complete':
        return <CompleteStep results={scanResults} connection={connection} />;
    }
  };

  const isNextDisabled = () => {
    if (currentStep === 'tables' && options.scanMode === 'selected') {
      return options.selectedTables.length === 0;
    }
    return false;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Database Scan Wizard
          </DialogTitle>
          <DialogDescription>
            Scan your database to analyze schema and optionally generate AI descriptions
          </DialogDescription>
        </DialogHeader>

        {/* Progress Steps */}
        <div className="flex items-center justify-between px-4 py-2">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            const isCompleted = index < currentStepIndex;
            const isCurrent = index === currentStepIndex;

            return (
              <div key={step.id} className="flex items-center">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex items-center justify-center">
                        <div
                          className={cn(
                            'flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors',
                            isCompleted && 'bg-primary border-primary text-primary-foreground',
                            isCurrent && 'border-primary text-primary',
                            !isCompleted && !isCurrent && 'border-muted text-muted-foreground'
                          )}
                        >
                          {isCompleted ? (
                            <CheckCircle2 className="h-4 w-4" />
                          ) : (
                            <StepIcon className="h-4 w-4" />
                          )}
                        </div>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{step.title}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      'w-8 h-0.5 mx-1 transition-colors',
                      isCompleted ? 'bg-primary' : 'bg-muted'
                    )}
                  />
                )}
              </div>
            );
          })}
        </div>

        <Separator />

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto max-h-[400px]">
          {getStepContent()}
        </div>

        {/* Footer */}
        <DialogFooter className="flex justify-between">
          <div className="flex gap-2">
            {canGoBack && (
              <Button variant="outline" onClick={handleBack} disabled={isLoading}>
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading || currentStep === 'progress' || currentStep === 'complete'}
            >
              Cancel
            </Button>

            {currentStep === 'complete' ? (
              <Button onClick={handleComplete}>
                View Results
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : canGoNext ? (
              <Button
                onClick={handleNext}
                disabled={isNextDisabled() || isLoading}
              >
                {currentStep === 'ai-config' ? 'Start Scan' : 'Next'}
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : null}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Step Components

function WelcomeStep({ connection }: { connection: DatabaseConnection | null }) {
  return (
    <div className="space-y-4 py-4">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10">
          <Database className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold">Welcome to the Scan Wizard</h3>
        <p className="text-sm text-muted-foreground">
          This wizard will guide you through scanning your database schema
        </p>
      </div>

      <Separator />

      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
          <div>
            <p className="font-medium">Analyze Database Structure</p>
            <p className="text-sm text-muted-foreground">
              Automatically discover tables, columns, and relationships
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Sparkles className="h-5 w-5 text-purple-600 mt-0.5" />
          <div>
            <p className="font-medium">Generate AI Descriptions</p>
            <p className="text-sm text-muted-foreground">
              Get intelligent explanations of your data structures
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Settings className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <p className="font-medium">Customizable Options</p>
            <p className="text-sm text-muted-foreground">
              Choose scan mode, tables, and AI instructions
            </p>
          </div>
        </div>
      </div>

      {connection && (
        <>
          <Separator />
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium">Target Connection</p>
            <p className="text-sm text-muted-foreground">{connection.alias || connection.id}</p>
          </div>
        </>
      )}
    </div>
  );
}

function OptionsStep({
  options,
  setOptions
}: {
  options: ScanOptions;
  setOptions: (options: ScanOptions) => void
}) {
  return (
    <div className="space-y-6 py-4">
      <div className="space-y-3">
        <Label>Scan Mode</Label>
        <div className="space-y-2">
          <div
            className={cn(
              'flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
              options.scanMode === 'full' ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
            )}
            onClick={() => setOptions({ ...options, scanMode: 'full' })}
          >
            <Checkbox
              checked={options.scanMode === 'full'}
              onChange={() => setOptions({ ...options, scanMode: 'full' })}
            />
            <div className="flex-1">
              <p className="font-medium">Full Scan</p>
              <p className="text-sm text-muted-foreground">
                Scan all tables in the database, regardless of previous scan status
              </p>
            </div>
          </div>

          <div
            className={cn(
              'flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
              options.scanMode === 'incremental' ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
            )}
            onClick={() => setOptions({ ...options, scanMode: 'incremental' })}
          >
            <Checkbox
              checked={options.scanMode === 'incremental'}
              onChange={() => setOptions({ ...options, scanMode: 'incremental' })}
            />
            <div className="flex-1">
              <p className="font-medium">Incremental Scan</p>
              <p className="text-sm text-muted-foreground">
                Only scan tables that haven't been scanned before
              </p>
            </div>
          </div>

          <div
            className={cn(
              'flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
              options.scanMode === 'selected' ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
            )}
            onClick={() => setOptions({ ...options, scanMode: 'selected' })}
          >
            <Checkbox
              checked={options.scanMode === 'selected'}
              onChange={() => setOptions({ ...options, scanMode: 'selected' })}
            />
            <div className="flex-1">
              <p className="font-medium">Selected Tables</p>
              <p className="text-sm text-muted-foreground">
                Choose specific tables to scan on the next step
              </p>
            </div>
          </div>
        </div>
      </div>

      <Separator />

      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label>Generate AI Descriptions</Label>
          <p className="text-sm text-muted-foreground">
            Use AI to generate intelligent table and column descriptions
          </p>
        </div>
        <Checkbox
          checked={options.withAI}
          onCheckedChange={(checked) => setOptions({ ...options, withAI: checked as boolean })}
        />
      </div>

      {!options.withAI && (
        <div className="p-3 bg-muted rounded-lg">
          <div className="flex items-start gap-2">
            <Info className="h-4 w-4 text-blue-600 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Without AI, the scan will only collect basic schema information (table names, column names, data types)
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function TablesStep({
  tables,
  isLoading,
  selectedTables,
  onToggleTable,
  onToggleAll,
  scanMode,
}: {
  tables: TableDescription[];
  isLoading: boolean;
  selectedTables: string[];
  onToggleTable: (tableId: string) => void;
  onToggleAll: () => void;
  scanMode: 'full' | 'incremental' | 'selected';
}) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
        <p className="text-sm text-muted-foreground">Loading tables...</p>
      </div>
    );
  }

  if (tables.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <Database className="h-12 w-12 text-muted-foreground mb-2" />
        <p className="text-sm text-muted-foreground">No tables found in this connection</p>
      </div>
    );
  }

  const allSelected = selectedTables.length === tables.length;
  const someSelected = selectedTables.length > 0 && !allSelected;

  if (scanMode !== 'selected') {
    return (
      <div className="text-center py-8">
        <Info className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground">
          {scanMode === 'full'
            ? 'Full scan will process all tables automatically'
            : 'Incremental scan will process unscanned tables automatically'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 py-4">
      <div className="flex items-center justify-between">
        <Label>Select Tables to Scan</Label>
        <Button variant="outline" size="sm" onClick={onToggleAll}>
          {allSelected ? 'Deselect All' : someSelected ? 'Select All' : 'Select All'}
        </Button>
      </div>

      <div className="text-sm text-muted-foreground">
        {selectedTables.length} of {tables.length} tables selected
      </div>

      <div className="border rounded-lg max-h-[300px] overflow-y-auto">
        {tables.map((table) => {
          const isSelected = selectedTables.includes(table.id);
          const wasScanned = table.sync_status === 'SCANNED';

          return (
            <div
              key={table.id}
              className={cn(
                'flex items-center gap-3 p-3 border-b last:border-b-0 cursor-pointer transition-colors',
                isSelected ? 'bg-primary/5' : 'hover:bg-muted/50'
              )}
              onClick={() => onToggleTable(table.id)}
            >
              <Checkbox checked={isSelected} />
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{table.table_name}</p>
                <p className="text-xs text-muted-foreground">
                  {table.db_schema || 'public'} • {table.columns.length} columns
                </p>
              </div>
              {wasScanned && (
                <Badge variant="secondary" className="text-xs">
                  Scanned
                </Badge>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AIConfigStep({
  options,
  setOptions
}: {
  options: ScanOptions;
  setOptions: (options: ScanOptions) => void
}) {
  return (
    <div className="space-y-4 py-4">
      <div className="space-y-2">
        <Label>AI Instruction Preset</Label>
        <Select
          value={Object.keys(defaultInstructions).find(
            key => defaultInstructions[key as keyof typeof defaultInstructions] === options.instruction
          ) || 'custom'}
          onValueChange={(value) => {
            if (value !== 'custom') {
              setOptions({
                ...options,
                instruction: defaultInstructions[value as keyof typeof defaultInstructions]
              });
            }
          }}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="detailed">Detailed Descriptions</SelectItem>
            <SelectItem value="simple">Simple Descriptions</SelectItem>
            <SelectItem value="business">Business-Focused</SelectItem>
            <SelectItem value="technical">Technical Details</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="instruction">Custom Instruction (optional)</Label>
        <Textarea
          id="instruction"
          placeholder="Enter custom instructions for the AI..."
          value={options.instruction}
          onChange={(e) => setOptions({ ...options, instruction: e.target.value })}
          rows={4}
          className="text-sm"
        />
        <p className="text-xs text-muted-foreground">
          Customize how the AI should describe your tables and columns. Leave empty for default behavior.
        </p>
      </div>

      <div className="p-3 bg-muted rounded-lg">
        <div className="flex items-start gap-2">
          <Sparkles className="h-4 w-4 text-purple-600 mt-0.5" />
          <div className="text-sm text-muted-foreground">
            <p className="font-medium mb-1">AI Description Tips</p>
            <ul className="space-y-1 text-xs">
              <li>• Be specific about what information you want</li>
              <li>• Mention your domain or industry for better context</li>
              <li>• Specify the level of detail (simple vs technical)</li>
              <li>• Include any business terms or concepts to focus on</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProgressStep({
  progress,
  withAI
}: {
  progress: { current: number; total: number };
  withAI: boolean;
}) {
  const percentage = progress.total > 0 ? (progress.current / progress.total) * 100 : 0;

  return (
    <div className="space-y-6 py-8">
      <div className="flex flex-col items-center justify-center">
        <Loader2 className="h-16 w-16 animate-spin text-primary mb-4" />
        <h3 className="text-lg font-semibold mb-2">
          {withAI ? 'Generating AI Descriptions' : 'Scanning Database'}
        </h3>
        <p className="text-sm text-muted-foreground text-center">
          This may take a few moments depending on the size of your database
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Progress</span>
          <span>{progress.current} / {progress.total} tables</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300 ease-out"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground text-center">
          {Math.round(percentage)}% complete
        </p>
      </div>

      {withAI && (
        <div className="p-3 bg-muted rounded-lg">
          <div className="flex items-start gap-2">
            <Sparkles className="h-4 w-4 text-purple-600 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              AI is analyzing your database schema and generating intelligent descriptions for each table and column
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function CompleteStep({
  results,
  connection
}: {
  results: { scanned: number; failed: number; skipped: number };
  connection: DatabaseConnection | null;
}) {
  return (
    <div className="space-y-6 py-4">
      <div className="flex flex-col items-center justify-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
          <CheckCircle2 className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Scan Complete!</h3>
        <p className="text-sm text-muted-foreground text-center">
          Your database has been successfully scanned
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-600">{results.scanned}</p>
          <p className="text-xs text-muted-foreground">Scanned</p>
        </div>

        {results.failed > 0 && (
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <p className="text-2xl font-bold text-red-600">{results.failed}</p>
            <p className="text-xs text-muted-foreground">Failed</p>
          </div>
        )}

        {results.skipped > 0 && (
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-600">{results.skipped}</p>
            <p className="text-xs text-muted-foreground">Skipped</p>
          </div>
        )}
      </div>

      <div className="space-y-2 text-sm text-muted-foreground">
        <p>• Tables and columns are now available in the schema browser</p>
        <p>• You can start asking questions about your data</p>
        <p>• Descriptions will help the AI understand your database better</p>
      </div>

      {connection && (
        <div className="p-3 bg-muted rounded-lg">
          <p className="text-sm font-medium">Next Steps</p>
          <p className="text-sm text-muted-foreground">
            Click "View Results" to explore your database schema in the Schema Browser
          </p>
        </div>
      )}
    </div>
  );
}