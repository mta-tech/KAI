---
adr_id: ADR-002
date: 2026-02-09
status: accepted
title: Use Zustand for Client State Management
---

# ADR-002: Use Zustand for Client State Management

## Context

KAI needed to manage UI state for:
- Sidebar open/closed state
- Theme preference (light/dark/system)
- Keyboard shortcuts registry
- Command palette state
- Modal/dialog states

We needed a state management solution that:
- Works seamlessly with Next.js 14 App Router and React 18
- Has minimal boilerplate and learning curve
- Provides good TypeScript support
- Has small bundle size impact
- Supports persistent state (localStorage)

## Decision

We chose **Zustand** for client state management.

**Rationale:**
- Simple API with hooks-based usage (`useStore()` pattern)
- No providers needed, reducing component nesting
- Built-in TypeScript support with proper type inference
- Small bundle size (~1KB minzipped)
- Built-in middleware for persistence (zustand/middleware)
- Easy to test and debug
- Works well with React Server Components

**Technical Implementation:**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    { name: 'kai-theme-storage' }
  )
);
```

## Consequences

**Positive Consequences:**
- Simple API reduces boilerplate code
- No provider nesting simplifies component tree
- Persistent state works out of the box with middleware
- Easy to add actions and computed values
- Excellent DevTools support
- Fast performance with minimal re-renders

**Negative Consequences:**
- Less ecosystem support compared to Redux
- Fewer middleware options for complex state logic
- Less suitable for very complex state interactions
- Smaller community means fewer third-party integrations

## Alternatives Considered

### Redux Toolkit
**Pros:**
- Large ecosystem and community support
- Excellent DevTools
- Predictable state updates
- Good for complex state logic

**Cons:**
- More boilerplate than Zustand
- Requires provider setup
- Heavier bundle size
- Overkill for our UI state needs

### Jotai
**Pros:**
- Atomic state approach
- No providers needed
- Good TypeScript support

**Cons:**
- Less familiar to our team
- More complex atom management
- Smaller community

### Valtio
**Pros:**
- Proxy-based state management
- No actions needed
- Simple API

**Cons:**
- Less mature than Zustand
- Different paradigm may confuse team
- Potential performance issues with large state trees

### React Context Only
**Pros:**
- Built into React
- No additional dependencies

**Cons:**
- Provider nesting leads to prop drilling
- Performance issues with frequent updates
- No built-in persistence
- More boilerplate for derived state

## Related

- Spec: `specs/kai-ui-revamp.md`
- Tasks: Theme toggle, sidebar state, keyboard shortcuts
- Implementation: `src/lib/stores/theme-store.ts`, `src/stores/sidebar-store.ts`
