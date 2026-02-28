---
category: ssr
component: theme-provider
tags: [nextjs, ssr, react-hooks, browser-apis]
date_resolved: 2026-02-09
related_build: KAI UI Revamp
related_tasks: [P2-03, P4-01]
---

# SSR-Safe Theme Provider Pattern

## Problem Symptom

Build failed with error:
```
Error occurred prerendering page "/chat". Read more: https://nextjs.org/docs/messages/prerender-error
ReferenceError: window is not defined
    at Object.getResolvedTheme
    at useTheme
    at ThemeProvider
```

All pages failed to generate static HTML due to theme store accessing `window` during server-side rendering.

## Investigation Steps

1. **Error Location**: Theme provider was accessing `window.matchMedia()` directly
2. **Root Cause**: Next.js 14 App Router renders components on the server first, where `window` doesn't exist
3. **Impact**: All pages failed to build, blocking deployment

### Affected Code

```typescript
// ❌ BEFORE - Breaks SSR
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      setTheme: (theme: Theme) => set({ theme }),
      getResolvedTheme: () => {
        const { theme } = get();
        if (theme === 'system') {
          // This breaks during SSR!
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme;
      },
    }),
    { name: 'kai-theme-storage' }
  )
);

export function useTheme() {
  const store = useThemeStore();
  const resolvedTheme = store.getResolvedTheme(); // Breaks during SSR!
  return { theme: store.theme, resolvedTheme, ... };
}
```

## Root Cause

The `getResolvedTheme()` function accessed `window.matchMedia()` without checking for browser environment. Next.js 14 App Router executes code during server-side rendering where `window`, `document`, and `navigator` are undefined.

## Working Solution

**Step 1: Add browser environment check helper**

```typescript
// src/lib/stores/theme-store.ts
function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
}
```

**Step 2: Make getResolvedTheme() SSR-safe**

```typescript
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      setTheme: (theme: Theme) => set({ theme }),
      getResolvedTheme: () => {
        const { theme } = get();
        if (theme === 'system') {
          // Default to light on server
          if (!isBrowser()) return 'light';
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme;
      },
    }),
    { name: 'kai-theme-storage' }
  )
);
```

**Step 3: Update useTheme hook with SSR fallback**

```typescript
export function useTheme() {
  const store = useThemeStore();
  // Default to 'light' during SSR
  const resolvedTheme = isBrowser() ? store.getResolvedTheme() : 'light';
  return {
    theme: store.theme,
    resolvedTheme,
    setTheme: store.setTheme,
    isDark: resolvedTheme === 'dark',
    isLight: resolvedTheme === 'light',
  };
}
```

**Step 4: Make initializeTheme() client-only**

```typescript
export function initializeTheme() {
  // Only run in browser
  if (!isBrowser()) {
    return () => {}; // No-op cleanup function for SSR
  }

  const store = useThemeStore.getState();
  const root = document.documentElement;
  const resolvedTheme = store.getResolvedTheme();

  // Apply theme class
  if (resolvedTheme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }

  // Listen for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const handleChange = () => {
    const { theme } = useThemeStore.getState();
    if (theme === 'system') {
      const newTheme = mediaQuery.matches ? 'dark' : 'light';
      root.classList.toggle('dark', newTheme === 'dark');
    }
  };

  mediaQuery.addEventListener('change', handleChange);
  return () => mediaQuery.removeEventListener('change', handleChange);
}
```

**Result**: Build succeeded, all pages generated successfully

## Prevention Strategies

1. **Always check browser environment** before accessing `window`, `document`, or `navigator`
2. **Use useEffect for browser-only operations** (runs after hydration)
3. **Provide SSR defaults** for hooks that access browser APIs
4. **Test builds locally** with `npm run build` before deploying

```typescript
// ✅ Safe pattern
function useBrowserFeature() {
  const [feature, setFeature] = useState(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setFeature(window.someFeature);
    }
  }, []);

  return feature;
}

// ❌ Unsafe pattern
function useBrowserFeature() {
  return window.someFeature; // Breaks SSR!
}
```

## Test Cases Added

```typescript
// tests/unit/ssr-safe-theme.test.tsx
describe('SSR-safe theme', () => {
  it('should not access window during SSR', () => {
    // Mock SSR environment
    const originalWindow = global.window;
    // @ts-ignore
    delete global.window;

    expect(() => {
      const { result } = renderHook(() => useTheme());
      expect(result.current.resolvedTheme).toBe('light'); // Default
    }).not.toThrow();

    global.window = originalWindow;
  });

  it('should detect system preference in browser', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.resolvedTheme).toBeDefined();
  });
});
```

## Cross-References

- Related: [ADR-003: Next.js 14 App Router](../adr/adr-003-nextjs-14-app-router-with-server-components.md)
- Pattern: [SSR-safe browser API access](../patterns/ssr-safe-browser-api-access.md)
- Affected: `src/lib/stores/theme-store.ts`, `src/components/providers/theme-provider.tsx`
