---
category: ssr
component: analytics-provider
tags: [nextjs, useSearchParams, suspense, streaming-ssr]
date_resolved: 2026-02-09
related_build: KAI UI Revamp
related_tasks: [P2-15, P3-01]
---

# useSearchParams() Suspense Boundary Pattern

## Problem Symptom

Build failed with error for multiple pages:
```
Error occurred prerendering page "/connections". Read more: https://nextjs.org/docs/messages/missing-suspense-with-csr-bailout
⨯ useSearchParams() should be wrapped in a suspense boundary at page "/connections"
```

All pages using `AnalyticsProvider` or `ServiceWorkerProvider` failed static optimization.

## Investigation Steps

1. **Error Pattern**: All pages failed with useSearchParams() Suspense error
2. **Root Cause**: `AnalyticsProvider` was using `useSearchParams()` in root layout without Suspense
3. **Impact**: Entire app couldn't build, all pages became dynamic

### Affected Code

```typescript
// ❌ BEFORE - Breaks static optimization
export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams(); // This breaks SSR!

  useEffect(() => {
    const fullPath = `${pathname}?${searchParams.toString()}`;
    trackPageView({ path: fullPath });
  }, [pathname, searchParams]);

  return <>{children}</>;
}
```

## Root Cause

In Next.js 14 App Router, `useSearchParams()` causes the entire page to opt out of static optimization. When used in a provider that wraps all pages, it makes every page dynamic. The solution is to wrap `useSearchParams()` usage in a Suspense boundary so the page shell can be static while the dynamic part streams in.

## Working Solution

**Step 1: Extract search params usage to separate component**

```typescript
// src/components/analytics-provider.tsx
function AnalyticsTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!isAnalyticsEnabled()) return;

    const search = searchParams.toString();
    const fullPath = search ? `${pathname}?${search}` : pathname;
    const title = document.title;

    trackPageView({
      path: fullPath,
      title: title,
    });
  }, [pathname, searchParams]);

  return null;
}
```

**Step 2: Wrap in Suspense boundary**

```typescript
export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
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
```

**Step 3: Remove unused useSearchParams() from ServiceWorkerProvider**

```typescript
// src/components/service-worker-provider.tsx
// ❌ BEFORE
const searchParams = useSearchParams(); // Unused!

// ✅ AFTER
// Removed - not actually needed
```

**Result**: Build succeeded, all pages generate successfully

## Prevention Strategies

1. **Never use useSearchParams() in providers** that wrap the entire app
2. **Extract to leaf components** when you need search params
3. **Always wrap in Suspense** when using useSearchParams(), usePathname(), or useRouter()
4. **Use fallback={null}** for Suspense when you don't need loading UI

```typescript
// ✅ Safe pattern - Suspense boundary
export function MyComponent() {
  return (
    <>
      <StaticHeader />
      <Suspense fallback={<Loading />}>
        <DynamicSearchParamsConsumer />
      </Suspense>
    </>
  );
}

// ❌ Unsafe pattern - No Suspense
export function MyComponent() {
  const params = useSearchParams(); // Makes whole page dynamic
  return <div>{params.get('q')}</div>;
}
```

## Test Cases Added

```typescript
// tests/unit/suspense-boundary.test.tsx
describe('useSearchParams() Suspense pattern', () => {
  it('should wrap search params consumer in Suspense', () => {
    const render = () => (
      <AnalyticsProvider>
        <div>Child content</div>
      </AnalyticsProvider>
    );

    // Should not throw
    expect(render).not.toThrow();
  });

  it('should render children while tracker loads', () => {
    const { getByText } = render(
      <AnalyticsProvider>
        <div>Child content</div>
      </AnalyticsProvider>
    );

    // Children render immediately
    expect(getByText('Child content')).toBeInTheDocument();
  });
});
```

## Cross-References

- Related: [ADR-003: Next.js 14 App Router](../adr/adr-003-nextjs-14-app-router-with-server-components.md)
- Pattern: [useSearchParams() Suspense boundary pattern](../patterns/useSearchParams-suspense-boundary.md)
- Affected: `src/components/analytics-provider.tsx`, `src/components/service-worker-provider.tsx`
- Next.js docs: https://nextjs.org/docs/messages/missing-suspense-with-csr-bailout
