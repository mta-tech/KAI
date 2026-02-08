'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertTriangle, Trash2, Download, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useRouter } from 'next/navigation';

export function DangerZone() {
  const { toast } = useToast();
  const router = useRouter();
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [isClearingData, setIsClearingData] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [clearConfirmation, setClearConfirmation] = useState('');

  const handleExportData = async () => {
    setIsExporting(true);
    try {
      const response = await api.get<Blob>('/user/export');
      const blob = response instanceof Blob ? response : new Blob([JSON.stringify(response)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kai-data-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast({
        title: 'Data exported',
        description: 'Your data has been exported successfully.',
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleClearData = async () => {
    if (clearConfirmation !== 'DELETE ALL DATA') {
      return;
    }

    setIsClearingData(true);
    try {
      await api.post('/user/clear-data');
      toast({
        title: 'Data cleared',
        description: 'All your data has been deleted.',
      });
      setClearConfirmation('');
      // Reload to show cleared state
      setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
      toast({
        title: 'Clear failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsClearingData(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== 'DELETE ACCOUNT') {
      return;
    }

    setIsDeletingAccount(true);
    try {
      await api.delete('/user/account');
      toast({
        title: 'Account deleted',
        description: 'Your account has been permanently deleted.',
      });
      // Redirect to home or logout
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } catch (error) {
      toast({
        title: 'Deletion failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsDeletingAccount(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Data Management</CardTitle>
          <CardDescription>Export or clear your data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <p className="font-medium">Export your data</p>
              <p className="text-sm text-muted-foreground">
                Download all your data including connections, queries, and settings
              </p>
            </div>
            <Button variant="outline" onClick={handleExportData} disabled={isExporting}>
              {isExporting ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </>
              )}
            </Button>
          </div>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <div className="flex items-center justify-between p-4 border border-destructive/50 rounded-lg hover:bg-destructive/5 cursor-pointer transition-colors">
                <div>
                  <p className="font-medium text-destructive">Clear all data</p>
                  <p className="text-sm text-muted-foreground">
                    Delete all your data including connections, queries, and settings
                  </p>
                </div>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear all data?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete all your data including:
                  <ul className="list-disc list-inside mt-2 text-sm">
                    <li>Database connections</li>
                    <li>Query history and saved queries</li>
                    <li>Knowledge base entries</li>
                    <li>Settings and preferences</li>
                  </ul>
                </AlertDialogDescription>
              </AlertDialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="clear-confirm">
                    Type <span className="font-mono font-bold">DELETE ALL DATA</span> to confirm
                  </Label>
                  <Input
                    id="clear-confirm"
                    value={clearConfirmation}
                    onChange={(e) => setClearConfirmation(e.target.value)}
                    placeholder="Type confirmation"
                  />
                </div>
                <AlertDialogFooter>
                  <AlertDialogCancel onClick={() => setClearConfirmation('')}>
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleClearData}
                    disabled={clearConfirmation !== 'DELETE ALL DATA' || isClearingData}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    {isClearingData ? 'Clearing...' : 'Clear all data'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </div>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-base text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible and destructive actions for your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Dialog>
            <DialogTrigger asChild>
              <div className="flex items-center justify-between p-4 border border-destructive rounded-lg hover:bg-destructive/5 cursor-pointer transition-colors">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-5 w-5 text-destructive" />
                  <div>
                    <p className="font-medium">Delete your account</p>
                    <p className="text-sm text-muted-foreground">
                      Permanently delete your account and all data
                    </p>
                  </div>
                </div>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete your account?</DialogTitle>
                <DialogDescription>
                  This action cannot be undone. This will permanently delete:
                  <ul className="list-disc list-inside mt-2 text-sm">
                    <li>Your account and all data</li>
                    <li>Database connections</li>
                    <li>Query history and saved queries</li>
                    <li>Knowledge base entries</li>
                    <li>MDL manifests and configurations</li>
                  </ul>
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="delete-confirm">
                    Type <span className="font-mono font-bold">DELETE ACCOUNT</span> to confirm
                  </Label>
                  <Input
                    id="delete-confirm"
                    value={deleteConfirmation}
                    onChange={(e) => setDeleteConfirmation(e.target.value)}
                    placeholder="Type confirmation"
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setDeleteConfirmation('');
                      // Close dialog
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDeleteAccount}
                    disabled={deleteConfirmation !== 'DELETE ACCOUNT' || isDeletingAccount}
                  >
                    {isDeletingAccount ? 'Deleting...' : 'Delete account'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            Important Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>
            <strong>Data retention:</strong> Your data is stored locally and on connected databases. Clearing
            data will remove local KAI data but won't affect your databases.
          </p>
          <p>
            <strong>Account deletion:</strong> Deleting your account removes your KAI user data but doesn't
            affect the databases you've connected to.
          </p>
          <p>
            <strong>Export first:</strong> We recommend exporting your data before taking any destructive
            actions.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
