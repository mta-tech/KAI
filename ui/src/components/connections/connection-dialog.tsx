'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/ui/loading-button';
import { FieldError } from '@/components/ui/field-error';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Eye, EyeOff } from 'lucide-react';
import { useCreateConnection } from '@/hooks/use-connections';
import { useFormValidation } from '@/lib/hooks/use-form-validation';
import type { DatabaseConnection } from '@/lib/api/types';

interface ConnectionDialogProps {
  connection?: DatabaseConnection;
  trigger?: React.ReactNode;
}

export function ConnectionDialog({ connection, trigger }: ConnectionDialogProps) {
  const [open, setOpen] = useState(false);
  const [showUri, setShowUri] = useState(false);
  const createMutation = useCreateConnection();

  const form = useFormValidation({
    initialValues: {
      alias: connection?.alias || '',
      connection_uri: '',
      schemas: connection?.schemas?.join(', ') || '',
    },
    validationRules: {
      alias: {
        required: 'Alias is required',
        minLength: { value: 2, message: 'Alias must be at least 2 characters' },
        pattern: { value: /^[a-zA-Z0-9_-]+$/, message: 'Alias can only contain letters, numbers, hyphens, and underscores' },
      },
      connection_uri: {
        required: 'Connection URI is required',
        pattern: {
          value: /^[\w-]+:\/\/[\w-]+:[\w-]+@[\w.-]+:\d+\/[\w-]+$/,
          message: 'Invalid connection URI format. Expected: dialect://user:pass@host:port/database'
        },
      },
    },
    onSubmit: async (values) => {
      await createMutation.mutateAsync({
        alias: values.alias,
        connection_uri: values.connection_uri,
        schemas: values.schemas ? values.schemas.split(',').map(s => s.trim()) : undefined,
      });

      setOpen(false);
      form.resetForm();
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Connection
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {connection ? 'Edit Connection' : 'Add Database Connection'}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={form.handleSubmit} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label htmlFor="alias">Alias <span className="text-destructive">*</span></Label>
            <Input
              id="alias"
              placeholder="my-database"
              value={form.values.alias}
              onChange={(e) => form.handleChange('alias', e.target.value)}
              onBlur={() => form.handleBlur('alias')}
              aria-invalid={!!form.fieldsMeta.alias?.error}
              aria-describedby={form.fieldsMeta.alias?.error ? 'alias-error' : undefined}
            />
            <FieldError id="alias-error" error={form.fieldsMeta.alias?.error} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="uri">Connection URI <span className="text-destructive">*</span></Label>
            <div className="relative">
              <Input
                id="uri"
                type={showUri ? 'text' : 'password'}
                placeholder="postgresql://user:pass@host:5432/db"
                value={form.values.connection_uri}
                onChange={(e) => form.handleChange('connection_uri', e.target.value)}
                onBlur={() => form.handleBlur('connection_uri')}
                aria-invalid={!!form.fieldsMeta.connection_uri?.error}
                aria-describedby={form.fieldsMeta.connection_uri?.error ? 'uri-error' : undefined}
                className="pr-20"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowUri(!showUri)}
                aria-label={showUri ? 'Hide connection URI' : 'Show connection URI'}
              >
                {showUri ? <EyeOff className="h-4 w-4" aria-hidden="true" /> : <Eye className="h-4 w-4" aria-hidden="true" />}
              </Button>
            </div>
            <FieldError id="uri-error" error={form.fieldsMeta.connection_uri?.error} />
            <p className="text-xs text-muted-foreground">
              Format: dialect://user:password@host:port/database
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="schemas">Schemas (optional)</Label>
            <Input
              id="schemas"
              placeholder="public, sales, analytics"
              value={form.values.schemas}
              onChange={(e) => form.handleChange('schemas', e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated list of schemas to include
            </p>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <LoadingButton 
              type="submit" 
              isLoading={form.isSubmitting || createMutation.isPending} 
              loadingText="Creating..."
              disabled={!form.isFormValid}
            >
              Create
            </LoadingButton>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
