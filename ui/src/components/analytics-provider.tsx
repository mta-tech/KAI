'use client';

/**
 * Analytics Provider Component
 *
 * Initializes analytics on app mount and provides page view tracking.
 * Should be placed in the app layout to track all navigation.
 */

import { useEffect, Suspense } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import {
  initAnalytics,
  trackPageView,
  isAnalyticsEnabled,
} from '@/lib/analytics';

function AnalyticsTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Track page views on route changes
  useEffect(() => {
    if (!isAnalyticsEnabled()) return;

    // Construct full URL with search params
    const search = searchParams.toString();
    const fullPath = search ? `${pathname}?${search}` : pathname;

    // Get page title from document
    const title = document.title;

    trackPageView({
      path: fullPath,
      title: title,
    });
  }, [pathname, searchParams]);

  return null;
}

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  // Initialize analytics on mount
  useEffect(() => {
    initAnalytics();
  }, []);

  return (
    <>
      <Suspense fallback={null}>
        <AnalyticsTracker />
      </Suspense>
      {children}
    </>
  );
}

/**
 * Hook to use analytics in components
 */
export function useAnalytics() {
  return {
    isEnabled: isAnalyticsEnabled(),
    trackPageView,
    trackEvent: (name: string, properties?: Record<string, unknown>) => {
      // Dynamically import to avoid SSR issues
      import('@/lib/analytics').then(({ trackEvent }) => {
        trackEvent(name, properties);
      });
    },
    trackAction: (action: { action: string; category: string; label?: string }) => {
      import('@/lib/analytics').then(({ trackAction }) => {
        trackAction(action);
      });
    },
    trackError: (error: Error, context?: Record<string, unknown>) => {
      import('@/lib/analytics').then(({ trackError }) => {
        trackError(error, context);
      });
    },
  };
}
