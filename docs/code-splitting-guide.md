# Code Splitting Implementation

## Overview

This document describes the code splitting implementation for the KAI UI application.

## Route-Based Code Splitting

Next.js App Router automatically implements route-based code splitting. Each route in `/app` is automatically split into its own chunk.

### Loading States

Each route has a `loading.tsx` file that provides a skeleton UI while the route is loading:

- `/app/loading.tsx` - Dashboard
- `/app/chat/loading.tsx` - Chat page
- `/app/connections/loading.tsx` - Connections page
- `/app/schema/loading.tsx` - Schema browser
- `/app/knowledge/loading.tsx` - Knowledge base
- `/app/mdl/loading.tsx` - MDL manifests
- `/app/mdl/[id]/loading.tsx` - MDL detail

### Suspense Boundaries

The root layout includes a Suspense boundary that wraps all page content:

```tsx
<main>
  <Suspense fallback={<PageLoadingFallback />}>
    {children}
  </Suspense>
</main>
```

This ensures that async components have proper loading fallbacks.

## Component-Level Code Splitting

For heavy client-side components, use the `createDynamicComponent` utility from `/lib/dynamic-imports.tsx`:

```tsx
import { createDynamicComponent } from '@/lib/dynamic-imports';

const HeavyChart = createDynamicComponent(
  () => import('@/components/charts/heavy-chart'),
  <div>Loading chart...</div>
);
```

## Bundle Analysis

### Analyze Bundle Sizes

Run the bundle analyzer to see the size of each chunk:

```bash
npm run analyze
```

This will open a browser showing the bundle sizes and dependencies.

### Check Bundle Budgets

After a build, check if bundles are within budget:

```bash
npm run bundle-size
```

Current budgets:
- Initial JS: 200KB gzipped
- Page JS: 100KB per page
- Total JS: 500KB total

## Best Practices

1. **Keep page chunks small**: Each page should ideally be under 100KB gzipped
2. **Use dynamic imports for heavy components**: Charts, editors, and other large components should be dynamically imported
3. **Provide good loading states**: Use skeleton UIs that match the final layout
4. **Measure regularly**: Run the bundle analyzer after significant changes

## Monitoring

The bundle size script runs in CI to catch regressions. If bundles exceed budget, the build will fail.

To update budgets, edit `/ui/scripts/bundle-size.js`.
