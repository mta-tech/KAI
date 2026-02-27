/**
 * Dynamic import utilities for code splitting
 *
 * Next.js App Router automatically handles route-based code splitting,
 * but this file provides utilities for splitting heavy client components.
 */

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

/**
 * Create a dynamically imported component with loading fallback
 * Use this for heavy client-side components that don't need SSR
 */
export function createDynamicComponent<T extends object>(
  importFn: () => Promise<{ default: ComponentType<T> }>,
  fallback?: React.ReactElement
) {
  return dynamic(importFn, {
    loading: () => fallback ?? <DefaultLoadingFallback />,
    ssr: false, // Disable SSR for client-only components
  });
}

/**
 * Default loading fallback for dynamic imports
 */
function DefaultLoadingFallback() {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  );
}

/**
 * Dynamically import heavy chart/visualization components
 */
export const ChartComponents = {
  // Add chart components here when needed
  // Example: BarChart: dynamic(() => import('@/components/charts/bar-chart'), { ssr: false }),
};

/**
 * Dynamically import heavy editor components
 */
export const EditorComponents = {
  // Add editor components here when needed
  // Example: CodeEditor: dynamic(() => import('@/components/editor/code-editor'), { ssr: false }),
};
