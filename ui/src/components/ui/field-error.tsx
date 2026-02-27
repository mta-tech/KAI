'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle } from 'lucide-react';

export interface FieldErrorProps extends React.HTMLAttributes<HTMLParagraphElement> {
  /**
   * The error message to display
   */
  error?: string;
  
  /**
   * Unique ID for the error element
   */
  id?: string;
  
  /**
   * Whether to show the error with reduced visual emphasis
   */
  variant?: 'default' | 'subtle';
}

export const FieldError = React.forwardRef<HTMLParagraphElement, FieldErrorProps>(
  ({ error, id, variant = 'default', className, ...props }, ref) => {
    if (!error) {
      return null;
    }
    
    return (
      <p
        ref={ref}
        id={id}
        role="alert"
        aria-live="polite"
        aria-atomic="true"
        className={cn(
          'flex items-center gap-1.5 text-sm font-medium',
          variant === 'default' 
            ? 'text-destructive' 
            : 'text-muted-foreground',
          className
        )}
        {...props}
      >
        {variant === 'default' && (
          <AlertCircle className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        )}
        <span>{error}</span>
      </p>
    );
  }
);

FieldError.displayName = 'FieldError';
