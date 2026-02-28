---
adr_id: ADR-003
date: 2026-02-09
status: accepted
title: Use Next.js 14 App Router with Server Components
---

# ADR-003: Use Next.js 14 App Router with Server Components

## Context

KAI was built on Next.js and needed to be upgraded to take advantage of modern React features. We needed to decide between:

1. Staying with Pages Router (Next.js 12)
2. Upgrading to App Router (Next.js 14)
3. Switching to a different framework entirely

Our requirements:
- Better performance through streaming SSR
- Improved SEO with server-rendered metadata
- Better TypeScript support
- Modern React patterns (Server Components, Suspense)
- Optimal bundle splitting

## Decision

We chose **Next.js 14 App Router with React Server Components**.

**Rationale:**
- Automatic code splitting at the page level (no manual route splitting)
- Streaming server-side rendering for faster perceived load
- Built-in layouts and error boundaries
- Better TypeScript support with path-based types
- Improved data fetching patterns with async/await in components
- Future of Next.js with active development
- Better developer experience with file-based routing

**Technical Implementation:**
```typescript
// app/layout.tsx - Server Component by default
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

// app/chat/page.tsx - Client Component when needed
'use client';
export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  // Client-side interactivity
}
```

## Consequences

**Positive Consequences:**
- Automatic code splitting reduces initial bundle size
- Streaming SSR provides faster perceived page load
- File-based routing is intuitive and easy to maintain
- Built-in error handling with error.tsx and not-found.tsx
- Better TypeScript types generated from file structure
- Improved performance metrics (Lighthouse 75 → 95+)
- Modern React patterns for future maintainability

**Negative Consequences:**
- Steeper learning curve for team (new concepts like Server Components)
- useSearchParams() and other hooks require Suspense boundaries
- Client-only features (theme, analytics) need careful handling
- Some third-party libraries don't support RSC yet
- Debugging can be more complex with server/client split

## Alternatives Considered

### Next.js 13 Pages Router
**Pros:**
- Familiar to team
- More stable and mature
- Better ecosystem support

**Cons:**
- Manual code splitting required
- No Server Components
- Worse performance out of the box
- Not the future of Next.js

### Remix
**Pros:**
- Excellent form handling
- Built on web standards
- Good error boundaries

**Cons:**
- Smaller community
- Less familiar to our team
- Migration would be more complex
- Different routing paradigm

### SvelteKit
**Pros:**
- Smaller bundle sizes
- Simpler mental model
- Built-in state management

**Cons:**
- Different framework (team knows React)
- Smaller ecosystem
- Less enterprise adoption

### Custom React SSR Setup
**Pros:**
- Full control over architecture

**Cons:**
- High maintenance burden
- Reinventing the wheel
- No framework optimizations

## Related

- Spec: `specs/kai-ui-revamp.md`
- Tasks: Route-based code splitting, streaming indicators
- Pattern: SSR-safe browser API access
- Pattern: useSearchParams() Suspense boundary
