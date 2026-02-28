import { useMutation, UseMutationResult, UseMutationOptions } from '@tanstack/react-query';
import { useState } from 'react';

/**
 * Extended mutation result with retry capability
 */
export type MutationResult<TData, TError, TVariables, TContext> =
  UseMutationResult<TData, TError, TVariables, TContext> & {
    retryCount: number;
    manualRetry: () => void;
  };

/**
 * Enhanced useMutation hook with manual retry support
 *
 * Provides:
 * - Automatic retry with exponential backoff (configured in QueryClient)
 * - Manual retry button capability
 * - Retry count tracking
 *
 * @example
 * ```tsx
 * const mutation = useMutationWithRetry({
 *   mutationFn: async (data) => {
 *     return api.create(data);
 *   },
 *   onSuccess: (data) => {
 *     toast.success('Created successfully');
 *   },
 * });
 *
 * return (
 *   <div>
 *     <button onClick={() => mutation.mutate(data)}} disabled={mutation.isPending}>
 *       Submit
 *     </button>
 *     {mutation.error && (
 *       <ErrorDisplay error={mutation.error} onRetry={mutation.manualRetry} />
 *     )}
 *   </div>
 * );
 * ```
 */
export function useMutationWithRetry<
  TData = unknown,
  TError = unknown,
  TVariables = void,
  TContext = unknown
>(
  options: UseMutationOptions<TData, TError, TVariables, TContext>
): MutationResult<TData, TError, TVariables, TContext> {
  const [retryCount, setRetryCount] = useState(0);

  const mutation = useMutation(options);

  return {
    ...mutation,
    retryCount,
    manualRetry: () => {
      setRetryCount(0);
      mutation.mutate(mutation.variables as TVariables);
    },
  };
}
