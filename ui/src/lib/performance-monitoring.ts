/**
 * Performance Monitoring Utility
 *
 * Tracks Core Web Vitals and custom performance metrics.
 * Integrates with analytics services for monitoring.
 */

export interface CoreWebVitals {
  // Largest Contentful Paint - measures loading performance
  LCP: number;
  // First Input Delay - measures interactivity
  FID: number;
  // Cumulative Layout Shift - measures visual stability
  CLS: number;
  // First Contentful Paint - measures when content first appears
  FCP: number;
  // Time to First Byte - measures server response time
  TTFB: number;
}

export interface NavigationTiming {
  // DNS lookup time
  dnsLookup: number;
  // TCP connection time
  tcpConnection: number;
  // Request time
  request: number;
  // Response time
  response: number;
  // DOM processing time
  domProcessing: number;
  // Total page load time
  totalLoadTime: number;
}

/**
 * Get navigation timing metrics
 */
export function getNavigationTiming(): NavigationTiming | null {
  if (typeof window === 'undefined' || !window.performance) {
    return null;
  }

  const timing = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

  if (!timing) {
    return null;
  }

  return {
    dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
    tcpConnection: timing.connectEnd - timing.connectStart,
    request: timing.requestStart - timing.responseStart,
    response: timing.responseEnd - timing.requestStart,
    domProcessing: timing.domComplete - timing.domInteractive,
    totalLoadTime: timing.loadEventEnd - timing.fetchStart,
  };
}

/**
 * Get Core Web Vitals using web-vitals library (if available)
 * or fallback to PerformanceObserver API
 */
export async function getCoreWebVitals(): Promise<CoreWebVitals> {
  return new Promise((resolve) => {
    const vitals: CoreWebVitals = {
      LCP: 0,
      FID: 0,
      CLS: 0,
      FCP: 0,
      TTFB: 0,
    };

    // Check if web-vitals library is available
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      // Largest Contentful Paint (LCP)
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1] as any;
          vitals.LCP = lastEntry?.startTime || 0;
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay (FID)
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const fidEntry = entries[0] as any;
          vitals.FID = fidEntry?.processingStart - fidEntry?.startTime || 0;
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        // Cumulative Layout Shift (CLS)
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries() as any[]) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          vitals.CLS = clsValue;
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });

        // First Contentful Paint (FCP) and Time to First Byte (TTFB)
        const paintObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              vitals.FCP = entry.startTime;
            }
          }
        });
        paintObserver.observe({ entryTypes: ['paint'] });

        // Get TTFB from navigation timing
        const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navEntry) {
          vitals.TTFB = navEntry.responseStart - navEntry.fetchStart;
        }

        // Wait a bit for metrics to be collected
        setTimeout(() => resolve(vitals), 3000);
      } catch (error) {
        console.warn('Error measuring Core Web Vitals:', error);
        resolve(vitals);
      }
    } else {
      resolve(vitals);
    }
  });
}

/**
 * Log performance metrics (can be sent to analytics)
 */
export function logPerformanceMetrics(metrics: CoreWebVitals & { navigationTiming?: NavigationTiming }) {
  // In production, send to analytics service
  if (process.env.NODE_ENV === 'production') {
    // Send to analytics (e.g., Google Analytics, Sentry, etc.)
    // gtag('event', 'core_web_vitals', { ...metrics });
    console.log('Core Web Vitals:', metrics);
  }
}

/**
 * Check if performance metrics meet targets
 */
export function checkPerformanceTargets(metrics: CoreWebVitals): {
  passed: boolean;
  details: Record<string, { value: number; target: number; passed: boolean }>;
} {
  const targets = {
    LCP: 2.5, // Target: < 2.5s
    FID: 100, // Target: < 100ms
    CLS: 0.1, // Target: < 0.1
    FCP: 1.8, // Target: < 1.8s
    TTFB: 0.8, // Target: < 800ms
  };

  const details: Record<string, { value: number; target: number; passed: boolean }> = {};

  for (const [key, value] of Object.entries(metrics)) {
    const target = targets[key as keyof typeof targets] || 0;
    const passed = key === 'LCP' || key === 'FCP' || key === 'TTFB'
      ? value < target
      : value <= target;

    details[key] = { value, target, passed };
  }

  const passed = Object.values(details).every((d) => d.passed);

  return { passed, details };
}

/**
 * Measure custom performance marks
 */
export function measurePerformanceMark(name: string, fn: () => void | Promise<void>) {
  if (typeof window === 'undefined' || !window.performance) {
    return fn();
  }

  const startMark = `${name}-start`;
  const endMark = `${name}-end`;

  performance.mark(startMark);

  const result = fn();

  if (result instanceof Promise) {
    return result.finally(() => {
      performance.mark(endMark);
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name)[0];
      console.log(`${name} took ${measure.duration.toFixed(2)}ms`);
    });
  } else {
    performance.mark(endMark);
    performance.measure(name, startMark, endMark);
    const measure = performance.getEntriesByName(name)[0];
    console.log(`${name} took ${measure.duration.toFixed(2)}ms`);
    return result;
  }
}

/**
 * Get resource timing data for debugging
 */
export function getResourceTiming(): Array<{
  name: string;
  duration: number;
  size: number;
}> {
  if (typeof window === 'undefined' || !window.performance) {
    return [];
  }

  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

  return resources.map((resource) => ({
    name: resource.name,
    duration: resource.duration,
    size: resource.transferSize,
  }));
}

/**
 * Clear performance marks and measures
 */
export function clearPerformanceMarks() {
  if (typeof window === 'undefined' || !window.performance) {
    return;
  }

  performance.clearMarks();
  performance.clearMeasures();
}
