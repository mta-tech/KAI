import { toast } from '@/hooks/use-toast';
import { logger } from '@/lib/logger';
import { trackError } from '@/lib/analytics';

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: unknown;
}

export function handleApiError(error: unknown, context?: string): void {
  logger.error('API error:', error, { context });

  // Track error in analytics
  if (error instanceof Error) {
    trackError(error, { context, type: 'api_error' });
  }

  let title = 'Something went wrong';
  let description = 'An unexpected error occurred. Please try again.';
  const variant: 'default' | 'destructive' = 'destructive';

  if (error instanceof Error) {
    // Try to parse error message
    const message = error.message;

    if (message.includes('Failed to fetch')) {
      title = 'Connection Error';
      description = 'Unable to connect to the server. Please check your connection.';
    } else if (message.includes('401') || message.includes('Unauthorized')) {
      title = 'Authentication Error';
      description = 'You need to log in to perform this action.';
    } else if (message.includes('403') || message.includes('Forbidden')) {
      title = 'Permission Denied';
      description = "You don't have permission to perform this action.";
    } else if (message.includes('404') || message.includes('not found')) {
      title = 'Not Found';
      description = 'The requested resource was not found.';
    } else if (message.includes('409') || message.includes('conflict')) {
      title = 'Conflict';
      description = 'This action conflicts with existing data.';
    } else if (message.includes('422') || message.includes('validation')) {
      title = 'Validation Error';
      description = 'Please check your input and try again.';
    } else if (message.includes('500') || message.includes('server')) {
      title = 'Server Error';
      description = 'The server encountered an error. Please try again later.';
    } else {
      // Use the error message if it's user-friendly
      description = message;
    }
  }

  toast({
    variant,
    title,
    description,
  });
}

export function showSuccessToast(message: string, description?: string): void {
  toast({
    variant: 'default',
    title: 'Success',
    description: message,
  });
}

export function showInfoToast(message: string): void {
  toast({
    variant: 'default',
    title: 'Info',
    description: message,
  });
}

export function showWarningToast(message: string): void {
  toast({
    variant: 'default',
    title: 'Warning',
    description: message,
  });
}
