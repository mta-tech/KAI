'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { LoadingButton } from '@/components/ui/loading-button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Plus, Pencil, Trash2, Database as DatabaseIcon, TestTube, Check, X, Eye, EyeOff } from 'lucide-react';
import { useConnections } from '@/hooks/use-connections';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import type { DatabaseConnection } from '@/lib/api/types';

interface ConnectionFormData {
  alias: string;
  connection_string: string;
}

export function ConnectionManager() {
  const { data: connections = [], isLoading } = useConnections();
  const { toast } = useToast();

  const [isOpen, setIsOpen] = useState(false);
  const [editConnection, setEditConnection] = useState<DatabaseConnection | null>(null);
  const [formData, setFormData] = useState<ConnectionFormData>({
    alias: '',
    connection_string: '',
  });
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const resetForm = () => {
    setFormData({ alias: '', connection_string: '' });
    setEditConnection(null);
    setTestResult(null);
    setShowPassword(false);
  };

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) resetForm();
  };

  const handleEdit = (connection: DatabaseConnection) => {
    setEditConnection(connection);
    setFormData({
      alias: connection.alias || '',
      connection_string: '', // Don't pre-fill connection string for security
    });
    setIsOpen(true);
  };

  const handleTest = async () => {
    if (!formData.connection_string) {
      toast({
        title: 'Connection string required',
        description: 'Please enter a connection string to test.',
        variant: 'destructive',
      });
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      await api.post('/connections/test', {
        connection_string: formData.connection_string,
      });
      setTestResult('success');
      toast({
        title: 'Connection successful',
        description: 'The connection string is valid.',
      });
    } catch (error) {
      setTestResult('error');
      toast({
        title: 'Connection failed',
        description: 'The connection string is invalid or the database is unreachable.',
        variant: 'destructive',
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editConnection) {
        await api.put(`/connections/${editConnection.id}`, {
          alias: formData.alias,
        });
        toast({
          title: 'Connection updated',
          description: `Connection "${formData.alias}" has been updated.`,
        });
      } else {
        await api.post('/connections', {
          alias: formData.alias,
          connection_string: formData.connection_string,
        });
        toast({
          title: 'Connection created',
          description: `Connection "${formData.alias}" has been added.`,
        });
      }
      handleOpenChange(false);
      // Refresh connections
      window.location.reload();
    } catch (error) {
      toast({
        title: 'Operation failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: string, alias: string) => {
    if (!confirm(`Are you sure you want to delete connection "${alias}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await api.delete(`/connections/${id}`);
      toast({
        title: 'Connection deleted',
        description: `Connection "${alias}" has been removed.`,
      });
      // Refresh connections
      window.location.reload();
    } catch (error) {
      toast({
        title: 'Delete failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    }
  };

  const maskConnectionString = (str: string) => {
    if (!str) return '';
    // Mask password in connection string
    return str.replace(/:([^:@]+)@/, ':****@');
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Database Connections</CardTitle>
          <CardDescription>Manage your database connections</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">Loading connections...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Database Connections</CardTitle>
              <CardDescription>Manage your database connections</CardDescription>
            </div>
            <Dialog open={isOpen} onOpenChange={handleOpenChange}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Connection
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editConnection ? 'Edit Connection' : 'Add New Connection'}</DialogTitle>
                  <DialogDescription>
                    {editConnection
                      ? 'Update the connection alias. Connection string cannot be modified.'
                      : 'Add a new database connection.'}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="alias">Connection Alias</Label>
                    <Input
                      id="alias"
                      placeholder="My Database"
                      value={formData.alias}
                      onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
                      required
                    />
                    <p className="text-xs text-muted-foreground">
                      A friendly name to identify this connection
                    </p>
                  </div>

                  {!editConnection && (
                    <div className="space-y-2">
                      <Label htmlFor="connection_string">Connection String</Label>
                      <div className="relative">
                        <Textarea
                          id="connection_string"
                          placeholder="postgresql://user:password@host:port/database"
                          value={formData.connection_string}
                          onChange={(e) => setFormData({ ...formData, connection_string: e.target.value })}
                          className="font-mono text-sm pr-20"
                          rows={3}
                          required
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-2 top-2 h-8 px-2"
                          onClick={() => setShowPassword(!showPassword)}
                          aria-label={showPassword ? 'Hide connection string' : 'Show connection string'}
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        PostgreSQL connection string. The password will be encrypted.
                      </p>
                    </div>
                  )}

                  {!editConnection && (
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={handleTest}
                      disabled={isTesting || !formData.connection_string}
                    >
                      <TestTube className="h-4 w-4 mr-2" />
                      {isTesting ? 'Testing...' : 'Test Connection'}
                    </Button>
                  )}

                  {testResult === 'success' && (
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <Check className="h-4 w-4" />
                      Connection successful! You can now save.
                    </div>
                  )}

                  {testResult === 'error' && (
                    <div className="flex items-center gap-2 text-sm text-red-600">
                      <X className="h-4 w-4" />
                      Connection failed. Please check your connection string.
                    </div>
                  )}

                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                      Cancel
                    </Button>
                    <LoadingButton type="submit" loadingText="Saving...">
                      {editConnection ? 'Update' : 'Create'}
                    </LoadingButton>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {connections.length === 0 ? (
            <div className="text-center py-8">
              <DatabaseIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-semibold mb-2">No connections yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Add a database connection to get started with KAI
              </p>
              <Button onClick={() => setIsOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Connection
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Host</TableHead>
                  <TableHead>Database</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {connections.map((conn) => {
                  const connectionString = conn.connection_string || '';
                  const hostMatch = connectionString.match(/@([^:]+)/);
                  const host = hostMatch ? hostMatch[1] : 'Unknown';
                  const dbMatch = connectionString.match(/\/([^?]+)/);
                  const database = dbMatch ? dbMatch[1] : 'Unknown';

                  return (
                    <TableRow key={conn.id}>
                      <TableCell className="font-medium">{conn.alias || conn.id.slice(0, 8)}</TableCell>
                      <TableCell className="font-mono text-sm">{host}</TableCell>
                      <TableCell className="font-mono text-sm">{database}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          Active
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" onClick={() => handleEdit(conn)}>
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(conn.id, conn.alias || conn.id.slice(0, 8))}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Connection Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>• Use PostgreSQL connection strings: <code className="font-mono">postgresql://user:password@host:port/database</code></p>
          <p>• The connection string will be encrypted and stored securely.</p>
          <p>• Test your connection before saving to ensure it's working.</p>
          <p>• You can create multiple connections to different databases.</p>
        </CardContent>
      </Card>
    </div>
  );
}
