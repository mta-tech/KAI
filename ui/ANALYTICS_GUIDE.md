# Analytics Implementation Guide

## Overview

The KAI UI includes privacy-respecting analytics tracking that captures user interactions, page views, and errors without collecting personally identifiable information (PII).

## Setup

### 1. Environment Configuration

Add the following to your `.env` file:

```bash
# Enable analytics
NEXT_PUBLIC_ANALYTICS_ENABLED=true

# Choose your provider
NEXT_PUBLIC_ANALYTICS_PROVIDER=posthog

# PostHog configuration
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

### 2. Provider Setup

#### PostHog (Recommended)

1. Add PostHog script to `app/layout.tsx`:
```tsx
import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        {process.env.NEXT_PUBLIC_ANALYTICS_ENABLED && (
          <Script
            src="https://cdn.jsdelivr.net/npm/posthog-js/dist/posthog.min.js"
            strategy="afterInteractive"
          />
        )}
      </head>
      <body>{children}</body>
    </html>
  );
}
```

2. Initialize PostHog:
```tsx
if (typeof window !== 'undefined' && window.posthog) {
  window.posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
  });
}
```

#### Google Analytics

Add GA script to `app/layout.tsx`:
```tsx
<Script
  src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}`}
  strategy="afterInteractive"
/>
<Script id="google-analytics" strategy="afterInteractive">
  {`
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}');
  `}
</Script>
```

## Usage

### Using the Analytics Provider

The `AnalyticsProvider` is already integrated in `app/providers.tsx` and automatically:
- Initializes analytics on app start
- Tracks page views on route changes

### Using the useAnalytics Hook

```tsx
import { useAnalytics } from '@/components/analytics-provider';

function MyComponent() {
  const { trackEvent, trackAction, trackError } = useAnalytics();

  const handleClick = () => {
    trackEvent('button_clicked', {
      button: 'submit',
      location: 'homepage',
    });
  };

  return <button onClick={handleClick}>Submit</button>;
}
```

### Using Analytics Actions

Pre-configured actions for common KAI UI events:

```tsx
import { analyticsActions } from '@/lib/analytics';

// Connection events
analyticsActions.connectionCreated('postgresql');
analyticsActions.connectionTested(true);

// Chat events
analyticsActions.chatStarted();
analyticsActions.chatMessageSent();
analyticsActions.chatSQLGenerated();

// Knowledge base events
analyticsActions.knowledgeCreated('glossary');

// Table events
analyticsActions.tablesScanned(5);
analyticsActions.tableSchemaViewed();

// MDL events
analyticsActions.mdlCreated();
analyticsActions.mdlExported('json');

// Navigation events
analyticsActions.navigationClicked('dashboard');

// Settings events
analyticsActions.settingChanged('theme');

// Error events
analyticsActions.errorOccurred('connection_failed');
```

### Tracking Errors

Errors are automatically tracked in `handleApiError`, but you can manually track errors:

```tsx
import { trackError } from '@/lib/analytics';

try {
  // Some operation
} catch (error) {
  trackError(error as Error, {
    context: 'user_action',
    action: 'save_settings'
  });
}
```

### Tracking Page Views

Page views are automatically tracked by the `AnalyticsProvider`, but you can manually track:

```tsx
import { trackPageView } from '@/lib/analytics';

trackPageView({
  path: '/settings/profile',
  title: 'Profile Settings',
});
```

## Privacy Features

### PII Protection

The analytics system automatically:
- Removes or hashes potential PII (emails, phone numbers, etc.)
- Sanitizes error messages
- Truncates stack traces
- Filters sensitive property names

### Disabled in Development

Analytics is automatically disabled in development mode. Events are only logged to console.

### Opt-Out Support

Analytics can be completely disabled by:
1. Setting `NEXT_PUBLIC_ANALYTICS_ENABLED=false`
2. Setting `NEXT_PUBLIC_ANALYTICS_PROVIDER=none`

## Events Tracked

### Page Views
- All route changes tracked automatically
- Includes path, title, and referrer

### User Actions
- Connection management (create, test, delete)
- Chat interactions (start, message, SQL generation)
- Knowledge base CRUD
- Table scanning and schema viewing
- MDL creation and export
- Navigation clicks
- Settings changes

### Errors
- API errors with context
- Validation errors
- Network errors
- Application errors

## Testing

### Verify Analytics is Working

1. Enable analytics in development:
```bash
NEXT_PUBLIC_ANALYTICS_ENABLED=true npm run dev
```

2. Check browser console for `[Analytics]` logs

3. Use browser DevTools Network tab to verify events are sent

### Testing Without Analytics

Analytics is disabled by default in development, so no special setup is needed.

## Best Practices

1. **Always use analytics actions** when available instead of raw trackEvent
2. **Never include PII** in event properties
3. **Use descriptive event names** that make sense in analytics dashboards
4. **Group related events** with consistent naming (category_action format)
5. **Test analytics** in staging before production deployment

## Monitoring

### Key Metrics to Track

1. **User Engagement**
   - Page views per session
   - Time on page
   - Return user rate

2. **Feature Usage**
   - Chat usage frequency
   - Connection creation rate
   - Knowledge base adoption

3. **Performance**
   - Error rates by feature
   - API failure rates
   - Page load times

4. **Conversion**
   - Scan completion rate
   - MDL creation rate
   - Query success rate

## Troubleshooting

### Events Not Appearing

1. Check analytics is enabled: `NEXT_PUBLIC_ANALYTICS_ENABLED=true`
2. Check provider is configured correctly
3. Check browser console for errors
4. Verify API keys are valid

### Page Views Not Tracked

1. Verify `AnalyticsProvider` is in the component tree
2. Check for JavaScript errors
3. Ensure routes are using Next.js router

## Resources

- [PostHog Documentation](https://posthog.com/docs)
- [Google Analytics Documentation](https://developers.google.com/analytics)
- [Privacy-first Analytics](https://posthog.com/blog/privacy-first-analytics)
