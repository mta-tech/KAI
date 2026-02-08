# Phase 4 (Polish) Preparation Guide

**Prepared by:** builder-polish
**Date:** 2026-02-08
**Purpose:** Preparation guidelines and research for Phase 4 tasks

---

## Overview

Phase 4 focuses on polish details, micro-interactions, testing, documentation, and launch preparation. This document consolidates research, requirements, and implementation guidelines for all Phase 4 tasks assigned to builder-polish.

## Task Matrix

| Task ID | Task Name | Points | Dependencies | Blocker Status |
|---------|-----------|--------|--------------|----------------|
| #60 | Page Transitions | 5 | None | **UNBLOCKED** |
| #62 | Empty State Illustrations | 5 | #17 (Empty States) | Blocked |
| #63 | Toast Notification Polish | 5 | #29 (Global Error Toast) | Blocked |
| #64 | Tooltips for Truncated Content | 5 | #20 (Base Component Library) | Blocked |
| #69 | Component Library Documentation | 10 | #22 (Storybook Setup) | Blocked |
| #70 | User Guide Creation | 5 | #65 (Command Palette) | Blocked |
| #73 | Launch Preparation Checklist | 5 | All previous tasks | Blocked |

---

## Task #60: Page Transitions (UNBLOCKED)

### Requirements
- Smooth route transitions with fade in/out animations
- Respects `prefers-reduced-motion` for accessibility
- No jarring transitions between routes
- Applied to all routes in the app

### Implementation Approach

#### Option 1: Framer Motion (Recommended)
**Pros:**
- Smooth, professional animations
- Built-in `AnimatePresence` for route transitions
- Excellent accessibility support with `reducedMotion` config
- Large community and documentation

**Cons:**
- Additional dependency (~40KB gzipped)
- May be overkill for simple fade transitions

**Installation:**
```bash
npm install framer-motion
```

**Implementation Pattern:**
```tsx
// app/components/ui/page-transition.tsx
"use client"

import { motion, AnimatePresence } from "framer-motion"
import { usePathname } from "next/navigation"

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.2, ease: "easeInOut" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

**Usage in layout.tsx:**
```tsx
// Wrap the children in layout.tsx
<PageTransition>{children}</PageTransition>
```

#### Option 2: CSS Transitions (Lightweight)
**Pros:**
- No additional dependencies
- Minimal bundle size impact
- Good for simple fade transitions

**Cons:**
- Less flexibility for complex animations
- Manual coordination of enter/exit states

**Implementation Pattern:**
```tsx
// app/components/ui/page-transition.tsx
"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [displayChildren, setDisplayChildren] = useState(children)

  useEffect(() => {
    setIsTransitioning(true)
    const timer = setTimeout(() => {
      setDisplayChildren(children)
      setIsTransitioning(false)
    }, 200) // Match CSS transition duration

    return () => clearTimeout(timer)
  }, [pathname, children])

  return (
    <div
      className={`transition-opacity duration-200 ${
        isTransitioning ? "opacity-0" : "opacity-100"
      }`}
    >
      {displayChildren}
    </div>
  )
}
```

#### Option 3: React Transition Group
**Pros:**
- Lightweight compared to Framer Motion
- Specifically designed for route transitions
- Good React ecosystem integration

**Cons:**
- Less feature-rich than Framer Motion
- Requires more manual configuration

### Accessibility Considerations
```css
/* Must respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .page-transition {
    transition: none !important;
  }
}
```

### Recommended Decision
**Use Option 1 (Framer Motion)** if the bundle size budget allows. The professional feel and accessibility support are worth the size cost for a polished production application. If bundle size is critical, fall back to Option 2 (CSS Transitions).

---

## Task #62: Empty State Illustrations (BLOCKED by #17)

### Requirements
- Custom SVG illustrations for empty states
- Consistent art style across all empty states
- Works in both light and dark mode
- Lightweight (SVG format)
- Contextually relevant to each empty state scenario

### Empty State Scenarios to Illustrate

Based on the codebase analysis, we need illustrations for:

| Context | Illustration Concept | Location |
|---------|---------------------|----------|
| No chat messages | Empty chat bubble or conversation icon | Chat interface |
| No knowledge base entries | Book/document icon with plus | Knowledge list |
| No connections | Database/connection icon | Connection manager |
| No tables | Grid/table icon | Table browser |
| No query results | Search/magnifying glass icon | SQL results |
| No schema items | Schema/structure icon | Schema browser |
| Error state | Warning/error icon | Various error states |
| Loading state | Spinner or loading dots | Various loading states |

### Illustration Style Guidelines

#### Design Principles
1. **Minimalist**: Clean lines, simple shapes
2. **Brand-Aligned**: Use Deep Indigo (#6366f1) as primary accent color
3. **Color Mode Support**: Use CSS custom properties for colors
4. **Scalable**: SVG format for crisp rendering at any size
5. **Consistent**: Unified stroke width, corner radius, and spacing

#### Color Strategy
```tsx
// Use CSS custom properties for theme support
const illustrationColors = {
  primary: "hsl(var(--primary))",
  secondary: "hsl(var(--muted))",
  accent: "hsl(var(--accent))",
  foreground: "hsl(var(--foreground))",
  muted: "hsl(var(--muted-foreground))",
}
```

#### Size Specifications
- Small: 120x120px (inline empty states)
- Medium: 200x200px (page-level empty states)
- Large: 320x320px (full-page empty states)

### Implementation Pattern
```tsx
// app/components/illustrations/empty-chat.tsx
export function EmptyChatIllustration({
  size = "medium",
}: {
  size?: "small" | "medium" | "large"
}) {
  const sizes = {
    small: 120,
    medium: 200,
    large: 320,
  }

  return (
    <svg
      width={sizes[size]}
      height={sizes[size]}
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* SVG paths for illustration */}
    </svg>
  )
}
```

### Empty State Component Pattern
```tsx
// app/components/ui/empty-state.tsx
interface EmptyStateProps {
  illustration: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({
  illustration,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="mb-4">{illustration}</div>
      <h3 className="text-lg font-semibold">{title}</h3>
      {description && (
        <p className="mt-2 text-sm text-muted-foreground">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
```

### External Illustration Resources
If creating custom SVGs is time-intensive, consider:
1. **undraw.co** - Open source illustrations (MIT license)
2. **storyset.com** - Customizable illustrations (free for personal/commercial)
3. **hueman.undraw.co** - Skin tone customizable illustrations

---

## Task #63: Toast Notification Polish (BLOCKED by #29)

### Current State Analysis
The codebase already has:
- `sonner` library installed for toast notifications
- Custom styling in `/ui/src/components/ui/sonner.tsx`
- Basic toast configuration with theme support

### Required Polish
1. **Icons for Each Toast Type**
   - Success: Checkmark icon (✓)
   - Error: X or alert icon
   - Warning: Exclamation icon
   - Info: Info icon (i)

2. **Color-Coded Variants**
   - Success: Green/teal tones
   - Error: Red tones
   - Warning: Yellow/amber tones
   - Info: Blue tones

3. **Smooth Animations**
   - Slide in from top/bottom
   - Fade in/out
   - Swipe to dismiss (already supported by sonner)

4. **Visible Dismiss Button**
   - X icon in top-right corner
   - Always visible, not just on hover

### Implementation Pattern
```tsx
// Enhanced sonner configuration
const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast: "group toast border-border shadow-lg",
          title: "font-semibold",
          description: "text-sm text-muted-foreground",
          actionButton: "bg-primary text-primary-foreground",
          cancelButton: "bg-muted text-muted-foreground",
          success: "border-green-500 bg-green-50 dark:bg-green-950",
          error: "border-red-500 bg-red-50 dark:bg-red-950",
          warning: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950",
          info: "border-blue-500 bg-blue-50 dark:bg-blue-950",
        },
        icons: {
          success: <CheckCircle className="text-green-500" />,
          error: <XCircle className="text-red-500" />,
          warning: <AlertTriangle className="text-yellow-500" />,
          info: <Info className="text-blue-500" />,
        },
      }}
      closeButton
      {...props}
    />
  )
}
```

---

## Task #64: Tooltips for Truncated Content (BLOCKED by #20)

### Requirements
- Tooltips on all truncated text elements
- Shows full content on hover/focus
- Keyboard accessible (Enter/Space to show)
- Proper delay (≈500ms) and positioning
- Respects `prefers-reduced-motion`

### Implementation Pattern (Radix UI Tooltip)
```tsx
// app/components/ui/tooltip.tsx
"use client"

import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"
import { cn } from "@/lib/utils"

const TooltipProvider = TooltipPrimitive.Provider
const Tooltip = TooltipPrimitive.Root
const TooltipTrigger = TooltipPrimitive.Trigger
const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      "z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
      className
    )}
    {...props}
  />
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
```

### Truncated Text Component with Tooltip
```tsx
// app/components/ui/truncated-text.tsx
"use client"

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip"

interface TruncatedTextProps {
  text: string
  maxLength?: number
  className?: string
}

export function TruncatedText({
  text,
  maxLength = 50,
  className = "",
}: TruncatedTextProps) {
  const isTruncated = text.length > maxLength
  const displayText = isTruncated ? `${text.slice(0, maxLength)}...` : text

  if (!isTruncated) {
    return <span className={className}>{displayText}</span>
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={className}>{displayText}</span>
        </TooltipTrigger>
        <TooltipContent>
          <p>{text}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
```

---

## Task #69: Component Library Documentation (BLOCKED by #22)

### Requirements
- All components documented in Storybook
- Usage examples for each component
- Props documented with TypeScript types
- Accessibility notes for each component
- Design guidelines and best practices

### Storybook Documentation Template
```tsx
// app/components/ui/button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './button'

const meta = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
    },
  },
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

// Variants
export const Default: Story = {
  args: {
    children: 'Button',
  },
}

export const Destructive: Story = {
  args: {
    variant: 'destructive',
    children: 'Delete',
  },
}

// Accessibility
export const WithAccessibilityNotes: Story = {
  args: {
    children: 'Accessible Button',
  },
  parameters: {
    docs: {
      description: {
        story: 'This button demonstrates accessibility best practices. It includes proper ARIA labels, keyboard navigation support, and focus indicators.',
      },
    },
  },
}
```

### Documentation Checklist per Component
- [ ] Component description and purpose
- [ ] Import statement example
- [ ] Basic usage example
- [ ] All variants demonstrated
- [ ] All sizes demonstrated
- [ ] Props table with types
- [ ] Accessibility notes
- [ ] Keyboard interactions documented
- [ ] Design tokens used (colors, spacing)
- [ ] Related components linked

---

## Task #70: User Guide Creation (BLOCKED by #65)

### Requirements
- Getting started guide
- Keyboard shortcuts reference
- Feature guides for major functionality
- Screenshots/videos for complex flows
- Targeted at analytic engineers

### Proposed Documentation Structure
```
docs/user-guide/
├── getting-started.md
├── keyboard-shortcuts.md
├── chat/
│   ├── natural-language-queries.md
│   ├── understanding-results.md
│   └── exporting-data.md
├── knowledge-base/
│   ├── creating-entries.md
│   ├── managing-glossaries.md
│   └── using-skills.md
├── data/
│   ├── browsing-tables.md
│   ├── scanning-schema.md
│   └── managing-connections.md
└── settings/
    ├── theme-preferences.md
    ├── llm-configuration.md
    └── security-settings.md
```

### Content Templates

#### Getting Started Guide Template
```markdown
# Getting Started with KAI

## What is KAI?
KAI (Knowledge Agent for Intelligence Query) is an AI-powered database intelligence and analysis tool...

## Prerequisites
- Database connection (PostgreSQL, MySQL, Snowflake, etc.)
- LLM API key (OpenAI, Google, or Ollama for local)

## Quick Start
1. Connect your database
2. Start a chat session
3. Ask questions in natural language
4. View and export results

## Next Steps
- [ ] Create your first knowledge base entry
- [ ] Set up keyboard shortcuts
- [ ] Configure your preferences
```

#### Keyboard Shortcuts Reference Template
```markdown
# Keyboard Shortcuts

## Global Shortcuts
| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open command palette |
| `?` | Show keyboard shortcuts modal |
| `Cmd/Ctrl + /` | Focus search |

## Chat Shortcuts
| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `↑ / ↓` | Navigate message history |
| `Cmd/Ctrl + N` | New chat |

## Knowledge Base Shortcuts
| Shortcut | Action |
|----------|--------|
| `n` | Create new entry |
| `f` | Focus search |
| `e` | Edit selected entry |
| `Delete` | Delete selected entry |
```

---

## Task #73: Launch Preparation Checklist (BLOCKED by all)

### Requirements
- Feature flags configured
- Rollback plan documented
- Monitoring configured
- Error tracking setup
- Support channels ready
- Documentation complete

### Launch Checklist Template
```markdown
# Launch Preparation Checklist

## Feature Flags
- [ ] All new features behind feature flags
- [ ] Feature flag system tested
- [ ] Rollout strategy documented
- [ ] Canary deployment plan ready

## Monitoring & Observability
- [ ] Application metrics configured (Prometheus/Grafana)
- [ ] Log aggregation setup (ELK/Loki)
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring (Lighthouse CI)
- [ ] Uptime monitoring configured

## Security
- [ ] Security audit completed
- [ ] CSP headers configured
- [ ] API keys secured
- [ ] Dependency vulnerabilities resolved
- [ ] Rate limiting configured

## Documentation
- [ ] User guide published
- [ ] API documentation updated
- [ ] Deployment guide finalized
- [ ] Troubleshooting guide complete
- [ ] Accessibility statement published

## Support
- [ ] Support channels established
- [ ] Escalation path defined
- [ ] Bug triage process ready
- [ ] User feedback mechanism configured

## Rollback Plan
- [ ] Database migration rollback tested
- [ ] Feature flag rollback procedure
- [ ] Previous version restoration tested
- [ ] Data backup verification

## Smoke Tests
- [ ] Critical path E2E tests passing
- [ ] Production-like environment tested
- [ ] Real browser testing completed
- [ ] Performance benchmarks met

## Communication
- [ ] Release notes prepared
- [ ] User notification plan ready
- [ ] Stakeholder communication scheduled
- [ ] Marketing materials prepared
```

---

## Summary & Next Steps

### Immediate Actions (Can Start Now)
1. **Research page transition libraries** - Decision matrix ready for implementation
2. **Document empty state requirements** - Scenarios and guidelines defined
3. **Create component doc templates** - Storybook patterns ready to apply

### When Dependencies Clear
1. **Start with #60 (Page Transitions)** - No dependencies, can begin immediately
2. **Watch for #17 completion** - Triggers #62 (Empty State Illustrations)
3. **Watch for #29 completion** - Triggers #63 (Toast Polish)
4. **Watch for #22 completion** - Triggers #69 (Component Docs)

### Estimated Timeline
- Task #60: 1-2 days
- Task #62: 2-3 days (illustration creation)
- Task #63: 1 day
- Task #64: 1-2 days
- Task #69: 3-4 days (documentation)
- Task #70: 2-3 days
- Task #73: 1-2 days

**Total Estimated Effort**: 11-17 days for all Phase 4 polish tasks

---

**Document Status**: Ready for review and implementation
**Prepared by**: builder-polish
**Last Updated**: 2026-02-08
