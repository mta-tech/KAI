---
adr_id: ADR-001
date: 2026-02-09
status: accepted
title: Use shadcn/ui + Radix UI + Tailwind CSS for Design System
---

# ADR-001: Use shadcn/ui + Radix UI + Tailwind CSS for Design System

## Context

KAI's UI needed a complete redesign to address visual design, accessibility, and user experience issues. The application had no brand identity, weak visual hierarchy, and poor accessibility (62% WCAG compliance). We needed a design system that could:

1. Provide accessible, customizable components out of the box
2. Support our target users (analytic engineers who value information-dense interfaces)
3. Enable rapid development with consistent design patterns
4. Support dark/light mode theming
5. Work seamlessly with Next.js 14 App Router and React 18

## Decision

We chose **shadcn/ui** built on **Radix UI** primitives with **Tailwind CSS** for styling.

**Rationale:**
- shadcn/ui provides accessible, customizable components that can be copied into our codebase
- Radix UI primitives are WCAG compliant and include proper ARIA attributes
- Tailwind CSS enables rapid UI development with utility-first approach
- Design tokens can be centralized and reused via Tailwind theme configuration
- Strong TypeScript support with proper type definitions
- Large community and ecosystem support

**Technical Implementation:**
```typescript
// tailwind.config.ts
import { designTokens } from "./src/lib/tokens";

export default {
  theme: {
    extend: {
      colors: designTokens.colors,
      spacing: designTokens.spacing,
      fontFamily: designTokens.typography.fontFamily,
      // ... more tokens
    }
  }
}
```

## Consequences

**Positive Consequences:**
- Components are fully customizable since they're copied into our codebase
- Built-in accessibility with ARIA attributes and keyboard navigation
- Design tokens ensure consistency across the application
- Easy to implement dark/light mode with theme switching
- Reduced development time with pre-built, tested components
- Better visual design maturity (6/10 → 9/10)

**Negative Consequences:**
- Initial setup requires understanding multiple technologies (shadcn, Radix, Tailwind)
- Component copies need manual updates when shadcn/ui releases updates
- Additional build complexity with Tailwind compilation
- Team learning curve for utility-first CSS approach

## Alternatives Considered

### Custom Component Library from Scratch
**Pros:**
- Full control over component API and implementation
- No dependency on external library updates

**Cons:**
- High development cost to build accessible components from scratch
- Accessibility requires extensive testing and expertise
- Longer time to market

### Material-UI (MUI)
**Pros:**
- Large ecosystem and community support
- Comprehensive component library

**Cons:**
- Heavy bundle size impact
- Difficult to customize beyond Material Design
- Not ideal for information-dense analytic interfaces

### Chakra UI
**Pros:**
- Good accessibility support
- Easy theming system

**Cons:**
- Smaller community than MUI
- Less flexible than shadcn/ui's copy-paste approach
- Components are pre-packaged (harder to customize)

### Mantine
**Pros:**
- Good TypeScript support
- Comprehensive component library

**Cons:**
- Less familiar to our team
- Heavier than our chosen stack

## Related

- Spec: `specs/kai-ui-revamp.md`
- Tasks: Design system implementation (Phase 2)
- Pattern: Design token integration with Tailwind
