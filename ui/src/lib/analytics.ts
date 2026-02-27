/**
 * Analytics Utility
 *
 * Privacy-respecting analytics tracking for the KAI UI.
 * Tracks page views, user actions, and errors without collecting PII.
 *
 * Supports multiple analytics providers:
 * - PostHog (default if configured)
 * - Google Analytics
 * - Custom/Console (for development)
 */

type AnalyticsProvider = 'posthog' | 'google-analytics' | 'custom' | 'none';

interface AnalyticsEvent {
  name: string;
  properties?: Record<string, string | number | boolean | null>;
}

interface PageViewEvent extends Record<string, unknown> {
  path: string;
  title?: string;
  referrer?: string;
}

interface UserActionEvent {
  action: string;
  category: string;
  label?: string;
  value?: number;
}

/**
 * Analytics configuration
 */
const ANALYTICS_ENABLED = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true';
const ANALYTICS_PROVIDER: AnalyticsProvider =
  (process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER as AnalyticsProvider) || 'none';

// PostHog configuration
const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST;

// Google Analytics configuration
const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;

/**
 * Check if analytics is enabled
 */
export function isAnalyticsEnabled(): boolean {
  return ANALYTICS_ENABLED && ANALYTICS_PROVIDER !== 'none' && typeof window !== 'undefined';
}

/**
 * Check if PostHog is configured
 */
export function isPostHogConfigured(): boolean {
  return ANALYTICS_PROVIDER === 'posthog' &&
         !!POSTHOG_KEY &&
         typeof window !== 'undefined' &&
         !!(window as any).posthog;
}

/**
 * Check if Google Analytics is configured
 */
export function isGAConfigured(): boolean {
  return ANALYTICS_PROVIDER === 'google-analytics' &&
         !!GA_MEASUREMENT_ID &&
         typeof window !== 'undefined' &&
         !!(window as any).gtag;
}

/**
 * Initialize analytics
 * Call this once when the app starts
 */
export function initAnalytics(): void {
  if (!isAnalyticsEnabled()) {
    console.log('[Analytics] Disabled - running in development or not configured');
    return;
  }

  console.log('[Analytics] Initializing with provider:', ANALYTICS_PROVIDER);

  // Initialize based on provider
  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      initPostHog();
      break;
    case 'google-analytics':
      initGoogleAnalytics();
      break;
    case 'custom':
      console.log('[Analytics] Custom provider - no initialization needed');
      break;
  }
}

/**
 * Initialize PostHog analytics
 */
function initPostHog(): void {
  if (!POSTHOG_KEY) {
    console.warn('[Analytics] PostHog key not configured');
    return;
  }

  // PostHog should be loaded via script tag
  // This just verifies it's available
  if (typeof window !== 'undefined' && (window as any).posthog) {
    (window as any).posthog.identify();
    console.log('[Analytics] PostHog initialized');
  } else {
    console.warn('[Analytics] PostHog not available');
  }
}

/**
 * Initialize Google Analytics
 */
function initGoogleAnalytics(): void {
  if (!GA_MEASUREMENT_ID) {
    console.warn('[Analytics] GA measurement ID not configured');
    return;
  }

  // Google Analytics should be loaded via script tag
  // This just verifies it's available
  if (typeof window !== 'undefined' && (window as any).gtag) {
    console.log('[Analytics] Google Analytics initialized');
  } else {
    console.warn('[Analytics] Google Analytics not available');
  }
}

/**
 * Track a page view
 */
export function trackPageView(page: PageViewEvent): void {
  if (!isAnalyticsEnabled()) return;

  console.log('[Analytics] Page view:', page.path);

  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      if (isPostHogConfigured()) {
        (window as any).posthog?.capture('$pageview', {
          $current_url: page.path,
          title: page.title,
        });
      }
      break;

    case 'google-analytics':
      if (isGAConfigured()) {
        (window as any).gtag?.('event', 'page_view', {
          page_path: page.path,
          page_title: page.title,
        });
      }
      break;

    case 'custom':
      // Custom implementation - send to your analytics endpoint
      sendCustomEvent('page_view', page);
      break;
  }
}

/**
 * Track a user action
 */
export function trackAction(action: UserActionEvent): void {
  if (!isAnalyticsEnabled()) return;

  const event: AnalyticsEvent = {
    name: `${action.category}_${action.action}`,
    properties: {
      category: action.category,
      label: action.label ?? null,
      value: action.value ?? null,
    },
  };

  console.log('[Analytics] Action:', event.name, event.properties);

  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      if (isPostHogConfigured()) {
        (window as any).posthog?.capture(event.name, event.properties);
      }
      break;

    case 'google-analytics':
      if (isGAConfigured()) {
        (window as any).gtag?.('event', event.name, event.properties);
      }
      break;

    case 'custom':
      sendCustomEvent(event.name, event.properties);
      break;
  }
}

/**
 * Track a generic event
 */
export function trackEvent(name: string, properties?: Record<string, unknown>): void {
  if (!isAnalyticsEnabled()) return;

  console.log('[Analytics] Event:', name, properties);

  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      if (isPostHogConfigured()) {
        (window as any).posthog?.capture(name, properties);
      }
      break;

    case 'google-analytics':
      if (isGAConfigured()) {
        (window as any).gtag?.('event', name, properties);
      }
      break;

    case 'custom':
      sendCustomEvent(name, properties);
      break;
  }
}

/**
 * Track an error
 */
export function trackError(error: Error, context?: Record<string, unknown>): void {
  if (!isAnalyticsEnabled()) return;

  const errorProperties = {
    name: error.name,
    message: error.message,
    stack: error.stack?.substring(0, 500), // Limit stack trace length
    ...context,
  };

  console.log('[Analytics] Error:', errorProperties);

  // Never include PII in error tracking
  const sanitizedProperties = sanitizePII(errorProperties);

  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      if (isPostHogConfigured()) {
        (window as any).posthog?.capture('error', sanitizedProperties);
      }
      break;

    case 'google-analytics':
      if (isGAConfigured()) {
        (window as any).gtag?.('event', 'exception', {
          description: error.message,
          fatal: false,
        });
      }
      break;

    case 'custom':
      sendCustomEvent('error', sanitizedProperties);
      break;
  }
}

/**
 * Identify a user (optional, for user-specific analytics)
 * Only use this if you have explicit user consent
 */
export function identifyUser(userId: string, traits?: Record<string, unknown>): void {
  if (!isAnalyticsEnabled()) return;

  const sanitizedTraits = sanitizePII(traits || {});

  console.log('[Analytics] Identify user:', userId);

  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      if (isPostHogConfigured()) {
        (window as any).posthog?.identify(userId, sanitizedTraits);
      }
      break;

    case 'google-analytics':
      if (isGAConfigured()) {
        (window as any).gtag?.('set', 'user_id', userId);
      }
      break;

    case 'custom':
      sendCustomEvent('identify', { userId, ...sanitizedTraits });
      break;
  }
}

/**
 * Reset user identification (logout)
 */
export function resetUser(): void {
  if (!isAnalyticsEnabled()) return;

  console.log('[Analytics] Reset user');

  switch (ANALYTICS_PROVIDER) {
    case 'posthog':
      if (isPostHogConfigured()) {
        (window as any).posthog?.reset();
      }
      break;

    case 'google-analytics':
      if (isGAConfigured()) {
        (window as any).gtag?.('set', 'user_id', undefined);
      }
      break;
  }
}

/**
 * Sanitize PII from properties
 * Removes or hashes personally identifiable information
 */
function sanitizePII(properties: Record<string, unknown>): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {};
  const piiPatterns = [
    /email/i,
    /name/i,
    /phone/i,
    /address/i,
    /ssn/i,
    /credit/i,
    /password/i,
    /token/i,
    /key/i,
    /secret/i,
  ];

  for (const [key, value] of Object.entries(properties)) {
    // Check if key might contain PII
    const mightBePII = piiPatterns.some(pattern => pattern.test(key));

    if (mightBePII) {
      // Hash the value instead of storing it
      sanitized[key] = hashValue(String(value));
    } else if (typeof value === 'string') {
      // Check if value looks like PII
      sanitized[key] = sanitizeValue(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}

/**
 * Simple hash function for PII values
 */
function hashValue(value: string): string {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    const char = value.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return `hashed_${Math.abs(hash)}`;
}

/**
 * Sanitize a single value
 */
function sanitizeValue(value: string): string {
  // Remove email addresses
  if (/@/.test(value)) {
    return '[email]';
  }

  // Remove phone numbers
  if (/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/.test(value)) {
    return '[phone]';
  }

  // Remove credit card numbers
  if (/\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/.test(value)) {
    return '[card]';
  }

  return value;
}

/**
 * Send custom event to analytics endpoint
 */
function sendCustomEvent(eventName: string, properties?: Record<string, unknown>): void {
  // In production, send to your analytics endpoint
  if (process.env.NODE_ENV === 'production') {
    // Example: fetch('/api/analytics', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ event: eventName, properties }),
    // });
    console.log('[Analytics] Custom event:', eventName, properties);
  }
}

/**
 * Analytics hooks for React components
 */
export const analyticsActions = {
  // Connection actions
  connectionCreated: (connectionType: string) =>
    trackAction({ action: 'created', category: 'connection', label: connectionType }),

  connectionDeleted: (connectionType: string) =>
    trackAction({ action: 'deleted', category: 'connection', label: connectionType }),

  connectionTested: (success: boolean) =>
    trackAction({ action: 'tested', category: 'connection', label: success ? 'success' : 'failed' }),

  // Chat actions
  chatStarted: () =>
    trackAction({ action: 'started', category: 'chat' }),

  chatMessageSent: () =>
    trackAction({ action: 'message_sent', category: 'chat' }),

  chatSQLGenerated: () =>
    trackAction({ action: 'sql_generated', category: 'chat' }),

  // Knowledge base actions
  knowledgeCreated: (type: 'glossary' | 'instruction' | 'skill') =>
    trackAction({ action: 'created', category: 'knowledge', label: type }),

  knowledgeDeleted: (type: 'glossary' | 'instruction' | 'skill') =>
    trackAction({ action: 'deleted', category: 'knowledge', label: type }),

  // Table actions
  tablesScanned: (tableCount: number) =>
    trackAction({ action: 'scanned', category: 'tables', value: tableCount }),

  tableSchemaViewed: () =>
    trackAction({ action: 'schema_viewed', category: 'table' }),

  // MDL actions
  mdlCreated: () =>
    trackAction({ action: 'created', category: 'mdl' }),

  mdlExported: (format: string) =>
    trackAction({ action: 'exported', category: 'mdl', label: format }),

  // Navigation actions
  navigationClicked: (destination: string) =>
    trackAction({ action: 'navigated', category: 'navigation', label: destination }),

  // Settings actions
  settingChanged: (setting: string) =>
    trackAction({ action: 'changed', category: 'settings', label: setting }),

  // Error actions
  errorOccurred: (errorType: string) =>
    trackAction({ action: 'occurred', category: 'error', label: errorType }),
};
