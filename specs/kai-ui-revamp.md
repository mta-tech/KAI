---
title: "KAI UI Revamp - Implementation Plan"
type: feat
date: 2026-02-08
status: ready
priority: high
estimated_duration: 8-12 weeks
source: docs/plans/2026-02-08-feat-kai-ui-revamp-plan.md
---

# Plan: KAI UI Revamp

## Overview

This plan implements a comprehensive UI revamp for KAI (Knowledge Agent for Intelligence Query), addressing 73 identified issues across visual design, accessibility, user experience, and technical architecture. The revamp transforms KAI from a functional prototype into a polished, production-ready application optimized for analytic engineers who value efficiency, data visibility, and keyboard-driven workflows.

**Key Deliverables:**
- Complete design system with Deep Indigo brand identity (#6366f1)
- WCAG 2.1 AA compliant interface (95%+ compliance)
- 80%+ test coverage with E2E tests for critical flows
- 4-phase implementation: Quick Wins → Foundation → Major Features → Polish
- Command palette and keyboard-optimized workflows

**Architecture Note:**
Built on Next.js 14 with App Router, React 18, shadcn/ui, Radix UI primitives, and Tailwind CSS. Uses React Query for server state, Zustand for client state. Targeted at analytic engineers who prefer information-dense, keyboard-driven interfaces.

## Task Description

Comprehensive UI revamp addressing 73 identified issues:
- **Visual Design**: 31 issues (no brand identity, weak hierarchy, mobile responsiveness)
- **Accessibility**: 27 issues (missing ARIA labels, no live regions, 62% WCAG compliance)
- **User Experience**: 12 issues (empty states, no progress indication, poor feedback)
- **Technical Architecture**: 11 issues (console logs in prod, no error boundaries, 0% test coverage)

The revamp follows a 4-phase approach:
1. **Quick Wins** (Week 1): Critical fixes, loading states, basic keyboard nav
2. **Foundation** (Weeks 2-4): Design system, accessibility infrastructure, error management
3. **Major Features** (Weeks 5-10): Chat redesign, knowledge base, settings, performance
4. **Polish** (Weeks 11-12): Micro-interactions, testing suite, documentation, launch prep

## Objective

Transform KAI from a functional prototype (6/10 visual maturity, 62% accessibility) into a production-ready application (9/10 visual maturity, 95%+ accessibility) optimized for analytic engineers.

**Success Metrics:**
| Metric | Current | Target |
|--------|---------|--------|
| Visual Design Maturity | 6/10 | 9/10 |
| WCAG 2.1 AA Compliance | 62% | 95%+ |
| Technical Architecture Grade | B+ | A |
| Test Coverage | 0% | 80%+ |
| Lighthouse Performance | 75 | 95+ |
| Critical Issues | 9 | 0 |

## Problem Statement

KAI's current UI suffers from:
1. **No brand identity** - Generic admin interface appearance
2. **Poor accessibility** - Missing ARIA labels, no keyboard navigation, 62% WCAG compliance
3. **Incomplete feedback** - Missing loading states, empty states, error handling
4. **Technical debt** - Console logs in production, no error boundaries, zero test coverage
5. **Mobile experience** - Non-responsive sidebar, poor touch interactions

Target users (analytic engineers) require:
- Information-dense interfaces with data-first priority
- Full keyboard navigation with visible shortcuts
- Dark mode native design
- Progressive disclosure of complex features
- Predictable patterns across all surfaces

## Proposed Solution

Implement a comprehensive design system with:
- **Brand Identity**: Deep Indigo (#6366f1) primary color
- **Component Library**: 15+ accessible base components built on shadcn/ui
- **Design Tokens**: Centralized colors, spacing, typography
- **Accessibility Infrastructure**: Skip links, landmarks, live regions, focus management
- **Keyboard Shortcuts**: Modal-triggered shortcut system (`?` key)
- **Command Palette**: Cmd+K for power user actions (Phase 4)
- **Error Handling**: Global toast system, error boundaries, retry logic
- **Testing**: Vitest unit tests, Playwright E2E, axe DevTools integration

### Architecture

```
app/
├── components/
│   ├── ui/              # Base shadcn/ui components
│   ├── domain/          # Feature-specific components
│   │   ├── chat/
│   │   ├── knowledge/
│   │   ├── data/
│   │   └── settings/
│   └── layouts/         # Layout components
├── lib/
│   ├── tokens.ts        # Design tokens
│   ├── hooks/           # Custom React hooks
│   ├── utils/           # Helper functions
│   └── constants/       # App constants
└── styles/
    └── globals.css      # Tailwind imports + custom CSS
```

### Dependencies to Add

```json
{
  "dependencies": {
    "@radix-ui/react-dialog": "^1.0.0",
    "@radix-ui/react-toast": "^1.1.0",
    "@radix-ui/react-tooltip": "^1.0.0",
    "cmdk": "^0.2.0",
    "sonner": "^1.4.0",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "@storybook/addon-essentials": "^7.6.0",
    "@storybook/react": "^7.6.0",
    "@axe-core/react": "^4.8.0",
    "@playwright/test": "^1.40.0"
  }
}
```

## Relevant Files

### Existing Files to Modify

**Core Application:**
- `app/main.tsx` - Add error boundary, dark mode provider
- `app/routes/__root.tsx` - Add skip links, landmarks
- `app/components/layout/sidebar.tsx` - Fix mobile responsiveness
- `app/components/layout/header.tsx` - Add ARIA labels
- `app/styles/globals.css` - Add design tokens

**Chat Module:**
- `app/components/domain/chat/chat-interface.tsx` - Redesign layout
- `app/components/domain/chat/message-list.tsx` - Add streaming UI
- `app/components/domain/chat/sql-results.tsx` - Add export, table view

**Knowledge Base:**
- `app/components/domain/knowledge/knowledge-list.tsx` - Add filters
- `app/components/domain/knowledge/knowledge-editor.tsx` - Add preview

**Settings:**
- `app/components/domain/settings/settings-layout.tsx` - Group sections
- `app/components/domain/settings/connection-manager.tsx` - Add test

**Utilities:**
- `app/lib/api/client.ts` - Add retry logic
- All console.log statements - Remove or replace with proper logging

### New Files to Create

**Design System:**
- `app/lib/tokens.ts` - Design token definitions
- `app/components/ui/button.tsx` - Accessible button component
- `app/components/ui/input.tsx` - Accessible input component
- `app/components/ui/card.tsx` - Card component
- `app/components/ui/toast.tsx` - Toast notification system
- `app/components/ui/command-palette.tsx` - Command palette (Phase 4)

**Accessibility:**
- `app/components/accessibility/skip-link.tsx` - Skip links
- `app/components/accessibility/live-region.tsx` - Live region wrapper
- `app/components/accessibility/keyboard-shortcuts-modal.tsx` - Shortcuts modal

**State Management:**
- `app/lib/stores/theme-store.ts` - Theme persistence (Zustand)
- `app/lib/hooks/use-keyboard-shortcuts.ts` - Keyboard shortcuts hook

**Testing:**
- `tests/unit/components/button.test.tsx` - Button component tests
- `tests/unit/components/input.test.tsx` - Input component tests
- `tests/e2e/chat-flow.spec.ts` - Chat E2E tests
- `tests/e2e/knowledge-base-flow.spec.ts` - Knowledge base E2E tests

**Storybook:**
- `.storybook/main.ts` - Storybook configuration
- `app/components/ui/button.stories.tsx` - Button stories
- `app/components/ui/input.stories.tsx` - Input stories

## Implementation Phases

### Phase 1: Quick Wins (Week 1)

**Goal:** Address critical issues and build momentum with visible improvements

**Tasks:**

#### 1.1 Remove console.logs from production builds
- **Task ID:** P1-01
- **Points:** 2
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] All `console.log` statements removed from production code
  - [ ] Production build has zero console statements
  - [ ] Debug logging properly gated behind environment check
- **Implementation Requirements:**
  - Search for all `console.log` in codebase
  - Remove or replace with proper logging library
  - Add ESLint rule to prevent future console.logs
- **Files:**
  - All files with console.log statements
- **Success Criteria:**
  - [ ] Production bundle verified clean

#### 1.2 Add missing ARIA labels to navigation
- **Task ID:** P1-02
- **Points:** 3
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] All navigation links have descriptive aria-label
  - [ ] Sidebar navigation has aria-label="Main navigation"
  - [ ] User menu has aria-label="User menu"
  - [ ] All icons have aria-hidden="true" or proper labels
- **Implementation Requirements:**
  - Audit all navigation components
  - Add aria-label to all nav landmarks
  - Ensure icon-only buttons have aria-label
- **Files:**
  - `app/components/layout/sidebar.tsx`
  - `app/components/layout/header.tsx`
  - `app/components/layout/user-menu.tsx`
- **Success Criteria:**
  - [ ] axe DevTools passes navigation

#### 1.3 Fix sidebar mobile responsiveness
- **Task ID:** P1-03
- **Points:** 4
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Sidebar collapses to hamburger on mobile (< 768px)
  - [ ] Sidebar slides in from left on mobile
  - [ ] Overlay appears when sidebar open on mobile
  - [ ] Touch outside closes sidebar on mobile
  - [ ] Works at 320px minimum width
- **Implementation Requirements:**
  - Use Radix Sheet or Drawer for mobile
  - Add hamburger menu button (visible only on mobile)
  - Implement overlay/backdrop
  - Add close button
- **Files:**
  - `app/components/layout/sidebar.tsx`
  - `app/styles/mobile.css` (if needed)
- **Success Criteria:**
  - [ ] Manual testing on mobile devices passes

#### 1.4 Add loading states to all async actions
- **Task ID:** P1-04
- **Points:** 3
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] All buttons trigger loading state on click
  - [ ] Forms show spinner during submission
  - [ ] Data fetching shows skeleton or spinner
  - [ ] Loading states have proper ARIA attributes
- **Implementation Requirements:**
  - Create LoadingButton component
  - Create Skeleton component
  - Add isLoading props to async components
  - Use React Query's isLoading status
- **Files:**
  - `app/components/ui/loading-button.tsx`
  - `app/components/ui/skeleton.tsx`
  - All async components
- **Success Criteria:**
  - [ ] All async actions have visual feedback

#### 1.5 Implement basic keyboard navigation
- **Task ID:** P1-05
- **Points:** 4
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Tab key follows logical order through page
  - [ ] Focus visible on all interactive elements
  - [ ] Escape key closes modals
  - [ ] Enter/Space activate buttons and links
- **Implementation Requirements:**
  - Add visible focus styles (outline/ring)
  - Ensure proper tab order (DOM order)
  - Add keyboard event handlers to modals
  - Test navigation with keyboard only
- **Files:**
  - `app/styles/globals.css` - focus styles
  - All interactive components
- **Success Criteria:**
  - [ ] Can navigate app with keyboard only

#### 1.6 Add error boundaries to all routes
- **Task ID:** P1-06
- **Points:** 2
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] All routes wrapped in error boundary
  - [ ] Errors show friendly fallback UI
  - [ ] Errors logged to error tracking
  - [ ] User can retry from error state
- **Implementation Requirements:**
  - Create ErrorBoundary component
  - Wrap route components
  - Add error logging
  - Create error fallback UI
- **Files:**
  - `app/components/error-boundary.tsx`
  - `app/routes/__root.tsx`
  - `app/components/error-fallback.tsx`
- **Success Criteria:**
  - [ ] Errors caught and displayed gracefully

#### 1.7 Fix inconsistent button styles
- **Task ID:** P1-07
- **Points:** 3
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] All buttons use consistent Button component
  - [ ] Button variants: primary, secondary, ghost, danger
  - [ ] Button sizes: sm, md, lg
  - [ ] All buttons have proper hover/active/focus states
- **Implementation Requirements:**
  - Audit all button usage
  - Replace with Button component
  - Define consistent variants
- **Files:**
  - `app/components/ui/button.tsx`
  - All files with <button> elements
- **Success Criteria:**
  - [ ] Single Button component used everywhere

#### 1.8 Add empty states with CTAs
- **Task ID:** P1-08
- **Points:** 4
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] All list views show empty state when no data
  - [ ] Empty states have helpful illustrations or icons
  - [ ] Empty states include CTA to add first item
  - [ ] Empty states explain why there's no data
- **Implementation Requirements:**
  - Create EmptyState component
  - Add to all list views (chat, knowledge, connections)
  - Write helpful copy
  - Add CTAs with clear actions
- **Files:**
  - `app/components/ui/empty-state.tsx`
  - `app/components/domain/chat/chat-list.tsx`
  - `app/components/domain/knowledge/knowledge-list.tsx`
  - `app/components/domain/settings/connection-list.tsx`
- **Success Criteria:**
  - [ ] All empty states guide users to next action

#### 1.9 Implement basic focus management
- **Task ID:** P1-09
- **Points:** 3
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Modals trap focus within modal
  - [ ] Focus returns to trigger after modal close
  - [ ] Focus moves to first input after navigation
  - [ ] Skip links visible on focus
- **Implementation Requirements:**
  - Create useFocusTrap hook
  - Create FocusTrap component
  - Add skip links
  - Manage focus on route changes
- **Files:**
  - `app/lib/hooks/use-focus-trap.ts`
  - `app/components/ui/focus-trap.tsx`
  - `app/components/accessibility/skip-link.tsx`
- **Success Criteria:**
  - [ ] Focus management tested and working

**Success Criteria (Phase 1):**
- [ ] All 9 tasks completed
- [ ] Production build clean (no console.logs)
- [ ] Basic WCAG compliance for navigation
- [ ] Mobile-functional sidebar
- [ ] All async actions show loading state
- [ ] Keyboard navigation functional

---

### Phase 2: Foundation (Weeks 2-4)

**Goal:** Establish design system and infrastructure for scalable improvements

**Dependencies:** Requires Phase 1 completion

**Tasks:**

#### 2.1 Create design token system
- **Task ID:** P2-01
- **Points:** 5
- **Dependencies:** P1-01, P1-07
- **Acceptance Criteria:**
  - [ ] Design tokens defined for colors, spacing, typography
  - [ ] Tokens exported from `app/lib/tokens.ts`
  - [ ] Tokens integrated with Tailwind config
  - [ ] Documented in Storybook
- **Implementation Requirements:**
  - Define color palette (primary, secondary, success, warning, danger, neutral)
  - Define spacing scale (0-96, step 4)
  - Define typography (font families, sizes, weights, line heights)
  - Add border radius tokens
  - Add shadow tokens
- **Files:**
  - `app/lib/tokens.ts`
  - `tailwind.config.ts`
  - `.storybook/main.ts`
- **Success Criteria:**
  - [ ] Tokens used throughout app

#### 2.2 Build base component library
- **Task ID:** P2-02
- **Points:** 10
- **Dependencies:** P2-01
- **Acceptance Criteria:**
  - [ ] Button component with variants (primary, secondary, ghost, danger)
  - [ ] Input component with validation states
  - [ ] Card component with variants
  - [ ] Select component with keyboard navigation
  - [ ] Checkbox component with proper ARIA
  - [ ] All components documented in Storybook
  - [ ] All components pass axe DevTools
- **Implementation Requirements:**
  - Build on shadcn/ui base components
  - Add design tokens
  - Ensure full keyboard accessibility
  - Add ARIA attributes
  - Write Storybook stories
  - Export from `app/components/ui/index.ts`
- **Files:**
  - `app/components/ui/button.tsx`
  - `app/components/ui/input.tsx`
  - `app/components/ui/card.tsx`
  - `app/components/ui/select.tsx`
  - `app/components/ui/checkbox.tsx`
  - `app/components/ui/index.ts`
- **Success Criteria:**
  - [ ] 15+ base components available

#### 2.3 Implement dark/light mode toggle
- **Task ID:** P2-03
- **Points:** 5
- **Dependencies:** P2-01
- **Acceptance Criteria:**
  - [ ] Toggle button in header
  - [ ] Mode persists across sessions
  - [ ] Respects system preference on first visit
  - [ ] Smooth transition between modes
  - [ ] All components work in both modes
- **Implementation Requirements:**
  - Create theme store with Zustand
  - Add Tailwind darkMode config
  - Create ThemeToggle component
  - Add to header
  - Ensure color contrast in both modes
- **Files:**
  - `app/lib/stores/theme-store.ts`
  - `app/components/ui/theme-toggle.tsx`
  - `app/components/layout/header.tsx`
  - `tailwind.config.ts`
- **Success Criteria:**
  - [ ] Can toggle between modes seamlessly

#### 2.4 Setup Storybook for component development
- **Task ID:** P2-04
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Storybook running at localhost:6006
  - [ ] All base components have stories
  - [ ] Accessibility addon enabled
  - [ ] Dark mode toggle in Storybook
  - [ ] Auto-docs enabled
- **Implementation Requirements:**
  - Install @storybook/react, @storybook/addon-essentials
  - Configure .storybook/main.ts
  - Create stories for components
  - Add accessibility addon
  - Add dark mode addon
- **Files:**
  - `.storybook/main.ts`
  - `.storybook/preview.ts`
  - `app/components/ui/*.stories.tsx`
- **Success Criteria:**
  - [ ] Storybook fully functional

#### 2.5 Create brand color integration
- **Task ID:** P2-05
- **Points:** 5
- **Dependencies:** P2-01
- **Acceptance Criteria:**
  - [ ] Deep Indigo (#6366f1) used as primary color
  - [ ] Brand color used consistently across app
  - [ ] Logo updated with brand color
  - [ ] Brand color works in dark mode
- **Implementation Requirements:**
  - Update design tokens with brand color
  - Update logo SVG
  - Apply to buttons, links, accents
  - Test contrast ratios
- **Files:**
  - `app/lib/tokens.ts`
  - `app/components/logo.tsx`
  - All component files with hardcoded colors
- **Success Criteria:**
  - [ ] Brand identity visible throughout app

#### 2.6 Implement skip links and landmarks
- **Task ID:** P2-06
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Skip link visible on focus
  - [ ] Skip link jumps to main content
  - [ ] Semantic landmarks (nav, main, aside, footer)
  - [ ] Landmarks have descriptive aria-label
  - [ ] Multiple landmarks distinguishable
- **Implementation Requirements:**
  - Create SkipLink component
  - Add to root layout
  - Wrap content in semantic HTML
  - Add aria-label to landmarks
- **Files:**
  - `app/components/accessibility/skip-link.tsx`
  - `app/routes/__root.tsx`
  - `app/components/layout/sidebar.tsx`
  - `app/components/layout/main.tsx`
- **Success Criteria:**
  - [ ] Can skip to main content with keyboard

#### 2.7 Add live regions for dynamic content
- **Task ID:** P2-07
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Live region wrapper component created
  - [ ] Toast announcements use live region
  - [ ] Error messages use live region
  - [ ] Success messages use live region
  - [ ] Screen readers announce dynamic changes
- **Implementation Requirements:**
  - Create LiveRegion component
  - Wrap dynamic content
  - Use aria-live="polite" or "assertive"
  - Test with screen reader
- **Files:**
  - `app/components/accessibility/live-region.tsx`
  - `app/components/ui/toast.tsx`
  - `app/components/ui/error-message.tsx`
- **Success Criteria:**
  - [ ] Dynamic content announced to screen readers

#### 2.8 Setup axe DevTools CI integration
- **Task ID:** P2-08
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] axe-core installed and configured
  - [ ] CI runs axe on all components
  - [ ] Fail build on critical violations
  - [ ] Accessibility report generated
- **Implementation Requirements:**
  - Install @axe-core/react
  - Add to CI pipeline
  - Configure violation thresholds
  - Add report generation
- **Files:**
  - `.github/workflows/accessibility.yml`
  - `axe.config.js`
- **Success Criteria:**
  - [ ] CI catches accessibility issues

#### 2.9 Keyboard shortcut system
- **Task ID:** P2-09
- **Points:** 10
- **Dependencies:** P1-05
- **Acceptance Criteria:**
  - [ ] Press `?` opens shortcuts modal
  - [ ] Shortcuts documented in modal
  - [ ] Shortcuts work across app
  - [ ] Shortcuts don't conflict with browser
  - [ ] Escape closes modal
- **Implementation Requirements:**
  - Create useKeyboardShortcuts hook
  - Define shortcut map
  - Create KeyboardShortcutsModal component
  - Register global shortcuts
  - Prevent browser conflicts
- **Files:**
  - `app/lib/hooks/use-keyboard-shortcuts.ts`
  - `app/components/accessibility/keyboard-shortcuts-modal.tsx`
  - `app/lib/constants/shortcuts.ts`
- **Success Criteria:**
  - [ ] All major actions have keyboard shortcuts

#### 2.10 Focus trap implementation
- **Task ID:** P2-10
- **Points:** 5
- **Dependencies:** P1-09
- **Acceptance Criteria:**
  - [ ] Modals trap focus within modal
  - [ ] Tab cycles through modal elements
  - [ ] Shift+Tab cycles backwards
  - [ ] Escape closes modal
  - [ ] Focus returns to trigger after close
- **Implementation Requirements:**
  - Create FocusTrap component
  - Add to all modals/dialogs
  - Manage focus on mount/unmount
  - Return focus on close
- **Files:**
  - `app/components/ui/focus-trap.tsx`
  - All modal components
- **Success Criteria:**
  - [ ] Cannot tab outside modal

#### 2.11 Global error toast system
- **Task ID:** P2-11
- **Points:** 5
- **Dependencies:** P2-07
- **Acceptance Criteria:**
  - [ ] Toast component created
  - [ ] Toaster context/provider
  - [ ] API errors show toast
  - [ ] Validation errors show toast
  - [ ] Success messages show toast
  - [ ] Multiple toasts stack
  - [ ] Toasts auto-dismiss
- **Implementation Requirements:**
  - Create Toast component using sonner
  - Create Toaster provider
  - Add to root layout
  - Integrate with API client
  - Create useToast hook
- **Files:**
  - `app/components/ui/toast.tsx`
  - `app/components/ui/toaster.tsx`
  - `app/lib/hooks/use-toast.ts`
  - `app/lib/api/client.ts`
- **Success Criteria:**
  - [ ] All errors show friendly toasts

#### 2.12 Add retry logic to React Query mutations
- **Task ID:** P2-12
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Failed mutations retry with exponential backoff
  - [ ] Retry count configurable
  - [ ] User can trigger manual retry
  - [ ] Max retries prevents infinite loops
- **Implementation Requirements:**
  - Configure React Query mutation retry
  - Add exponential backoff
  - Add retry button to error states
  - Log retry attempts
- **Files:**
  - `app/lib/api/client.ts`
  - All mutation hooks
- **Success Criteria:**
  - [ ] Failed requests retry automatically

#### 2.13 Create error page components
- **Task ID:** P2-13
- **Points:** 5
- **Dependencies:** P2-11
- **Acceptance Criteria:**
  - [ ] 404 page with helpful message
  - [ ] 500 page with error details
  - [ ] Error pages match design system
  - [ ] Error pages have CTAs
  - [ ] Error pages accessible
- **Implementation Requirements:**
  - Create NotFoundPage component
  - Create ServerErrorPage component
  - Add routes
  - Use EmptyState component
- **Files:**
  - `app/routes/404.tsx`
  - `app/routes/500.tsx`
  - `app/components/error-pages/not-found.tsx`
  - `app/components/error-pages/server-error.tsx`
- **Success Criteria:**
  - [ ] Error pages show for appropriate errors

#### 2.14 Implement form validation patterns
- **Task ID:** P2-14
- **Points:** 10
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Validation errors show inline
  - [ ] Errors announce via live region
  - [ ] Submit disabled until valid
  - [ ] Required fields marked
  - [ ] Validation on blur and submit
  - [ ] Reusable validation patterns
- **Implementation Requirements:**
  - Create useFormValidation hook
  - Create FieldError component
  - Add validation rules
  - Integrate with forms
- **Files:**
  - `app/lib/hooks/use-form-validation.ts`
  - `app/components/ui/field-error.tsx`
  - All form components
- **Success Criteria:**
  - [ ] All forms have validation

#### 2.15 Add analytics event tracking
- **Task ID:** P2-15
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Analytics initialized on app start
  - [ ] Key user actions tracked
  - [ ] Page views tracked
  - [ ] Errors tracked
  - [ ] Privacy-respecting (no PII)
- **Implementation Requirements:**
  - Setup analytics (PostHog, Plausible, or custom)
  - Create trackEvent function
  - Add tracking to key actions
  - Add page view tracking
  - Ensure privacy compliance
- **Files:**
  - `app/lib/analytics.ts`
  - `app/main.tsx`
  - Key interaction points
- **Success Criteria:**
  - [ ] Analytics capturing data

#### 2.16 Visual regression testing setup
- **Task ID:** P2-16
- **Points:** 5
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Visual regression tests configured with Playwright
  - [ ] Screenshot baseline captured for all pages
  - [ ] CI runs visual tests on every PR
  - [ ] Visual diff viewer available
  - [ ] Threshold configured for acceptable diffs
- **Implementation Requirements:**
  - Setup Playwright screenshot testing
  - Configure visual regression (Percy, Chromatic, or Playwright native)
  - Capture baseline screenshots
  - Add to CI pipeline
  - Create screenshot comparison workflow
- **Files:**
  - `tests/visual/*.spec.ts`
  - `playwright.config.ts`
  - `.github/workflows/visual-regression.yml`
- **Success Criteria:**
  - [ ] Visual changes detected automatically

#### 2.17 Cross-browser testing setup
- **Task ID:** P2-17
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Tests run on Chrome, Firefox, Safari, Edge
  - [ ] Browser matrix configured in CI
  - [ ] Cross-browser issues tracked
  - [ ] Progressive enhancement for older browsers
- **Implementation Requirements:**
  - Configure Playwright browser matrix
  - Identify browser-specific issues
  - Add polyfills if needed
  - Document browser support policy
- **Files:**
  - `playwright.config.ts`
  - `tests/e2e/cross-browser.spec.ts`
  - `docs/browser-support.md`
- **Success Criteria:**
  - [ ] All features work on supported browsers

#### 2.18 Mobile device testing setup
- **Task ID:** P2-18
- **Points:** 5
- **Dependencies:** P1-03
- **Acceptance Criteria:**
  - [ ] Real device testing configured (BrowserStack or local)
  - [ ] Touch gestures tested
  - [ ] Viewport testing (320px - 768px)
  - [ ] Mobile-specific issues tracked
- **Implementation Requirements:**
  - Setup device emulation in Playwright
  - Configure real device testing (BrowserStack/Sauce Labs optional)
  - Test touch interactions
  - Test common mobile viewports
- **Files:**
  - `tests/mobile/*.spec.ts`
  - `playwright.config.ts`
- **Success Criteria:**
  - [ ] Mobile experience validated

**Success Criteria (Phase 2):**
- [ ] All 18 tasks completed
- [ ] Design token system in place
- [ ] 15+ accessible base components
- [ ] Dark mode functional
- [ ] Keyboard shortcut system working
- [ ] WCAG 2.1 AA compliant navigation
- [ ] Global error handling
- [ ] Visual regression tests running
- [ ] Cross-browser tests configured
- [ ] Mobile testing setup complete

---

### Phase 3: Major Features (Weeks 5-10)

**Goal:** Implement complex features and refactor key user flows

**Dependencies:** Requires Phase 2 completion

**Tasks:**

#### 3.1 Redesign chat layout with history sidebar
- **Task ID:** P3-01
- **Points:** 15
- **Dependencies:** P2-02, P2-03
- **Acceptance Criteria:**
  - [ ] Chat list sidebar (left)
  - [ ] Message area (center)
  - [ ] Collapsible history
  - [ ] Active chat highlighted
  - [ ] Search/filter chats
  - [ ] Create new chat button
  - [ ] Works in dark mode
- **Implementation Requirements:**
  - Redesign chat interface layout
  - Add chat history sidebar
  - Implement collapsible panels
  - Add search functionality
  - Maintain responsive design
- **Files:**
  - `app/components/domain/chat/chat-interface.tsx`
  - `app/components/domain/chat/chat-history.tsx`
  - `app/components/domain/chat/chat-main.tsx`
- **Success Criteria:**
  - [ ] Chat interface modern and functional

#### 3.2 Implement message streaming UI
- **Task ID:** P3-02
- **Points:** 10
- **Dependencies:** P3-01
- **Acceptance Criteria:**
  - [ ] Messages appear as they stream
  - [ ] Typing indicator during streaming
  - [ ] Auto-scroll to latest message
  - [ ] Stop generation button
  - [ ] Smooth animations
- **Implementation Requirements:**
  - Implement SSE or streaming response handling
  - Add streaming state to messages
  - Create typing indicator
  - Add auto-scroll logic
  - Add stop generation button
- **Files:**
  - `app/components/domain/chat/message-list.tsx`
  - `app/components/domain/chat/message-bubble.tsx`
  - `app/lib/hooks/use-streaming.ts`
- **Success Criteria:**
  - [ ] Streaming works smoothly

#### 3.3 Add SQL result tables with export
- **Task ID:** P3-03
- **Points:** 10
- **Dependencies:** P3-01
- **Acceptance Criteria:**
  - [ ] Results displayed in table
  - [ ] Virtual scroll for large datasets
  - [ ] Export to CSV
  - [ ] Export to JSON
  - [ ] Column sorting
  - [ ] Responsive on mobile
- **Implementation Requirements:**
  - Create SQLResultsTable component
  - Add virtual scrolling
  - Implement export functions
  - Add sorting logic
  - Make responsive
- **Files:**
  - `app/components/domain/chat/sql-results-table.tsx`
  - `app/lib/utils/export.ts`
- **Success Criteria:**
  - [ ] Can view and export SQL results

#### 3.4 Create visualization card components
- **Task ID:** P3-04
- **Points:** 10
- **Dependencies:** P3-03
- **Acceptance Criteria:**
  - [ ] Chart components (bar, line, pie)
  - [ ] Responsive charts
  - [ ] Dark mode support
  - [ ] Export charts as images
  - [ ] Interactive tooltips
- **Implementation Requirements:**
  - Integrate chart library (Recharts, Chart.js)
  - Create chart components
  - Add dark mode support
  - Add export functionality
  - Add tooltips
- **Files:**
  - `app/components/domain/chat/visualizations.tsx`
  - `app/components/ui/charts/bar-chart.tsx`
  - `app/components/ui/charts/line-chart.tsx`
  - `app/components/ui/charts/pie-chart.tsx`
- **Success Criteria:**
  - [ ] Charts render and interactive

#### 3.5 Implement chat search and filters
- **Task ID:** P3-05
- **Points:** 5
- **Dependencies:** P3-01
- **Acceptance Criteria:**
  - [ ] Search chat messages
  - [ ] Filter by date range
  - [ ] Filter by chat type
  - [ ] Highlight search results
  - [ ] Keyboard shortcut for search (Cmd+K)
- **Implementation Requirements:**
  - Add search input to chat history
  - Implement search logic
  - Add filter controls
  - Highlight matching text
  - Add keyboard shortcut
- **Files:**
  - `app/components/domain/chat/chat-search.tsx`
  - `app/lib/hooks/use-chat-search.ts`
- **Success Criteria:**
  - [ ] Can find messages quickly

#### 3.6 Add message actions
- **Task ID:** P3-06
- **Points:** 5
- **Dependencies:** P3-02
- **Acceptance Criteria:**
  - [ ] Copy message button
  - [ ] Regenerate response button
  - [ ] Share chat button
  - [ ] Delete message button
  - [ ] Actions accessible via keyboard
- **Implementation Requirements:**
  - Add action menu to messages
  - Implement copy to clipboard
  - Implement regenerate
  - Implement share (URL)
  - Implement delete with confirmation
- **Files:**
  - `app/components/domain/chat/message-actions.tsx`
- **Success Criteria:**
  - [ ] All message actions work

#### 3.7 Redesign knowledge base list
- **Task ID:** P3-07
- **Points:** 10
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Grid or list view toggle
  - [ ] Filter by type/tags
  - [ ] Search knowledge bases
  - [ ] Sort by name/date/size
  - [ ] Create new knowledge base button
  - [ ] Empty state with CTA
- **Implementation Requirements:**
  - Redesign knowledge base list layout
  - Add filter controls
  - Implement search
  - Add sorting
  - Add view toggle
- **Files:**
  - `app/components/domain/knowledge/knowledge-list.tsx`
  - `app/components/domain/knowledge/knowledge-grid.tsx`
  - `app/lib/hooks/use-knowledge-filters.ts`
- **Success Criteria:**
  - [ ] Knowledge bases easy to browse

#### 3.8 Create knowledge base editor with preview
- **Task ID:** P3-08
- **Points:** 15
- **Dependencies:** P3-07
- **Acceptance Criteria:**
  - [ ] Markdown editor
  - [ ] Live preview
  - [ ] Split pane view
  - [ ] Save button with loading state
  - [ ] Auto-save indicator
  - [ ] Syntax highlighting
- **Implementation Requirements:**
  - Integrate markdown editor (CodeMirror, Monaco)
  - Add preview pane
  - Implement split pane
  - Add save functionality
  - Add auto-save
  - Add syntax highlighting
- **Files:**
  - `app/components/domain/knowledge/knowledge-editor.tsx`
  - `app/components/domain/knowledge/markdown-preview.tsx`
- **Success Criteria:**
  - [ ] Can edit and preview markdown

#### 3.9 Implement table browser with search
- **Task ID:** P3-09
- **Points:** 10
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] List all tables
  - [ ] Search tables by name
  - [ ] Filter by schema
  - [ ] Table metadata display
  - [ ] Row count preview
- **Implementation Requirements:**
  - Create TableBrowser component
  - Implement search
  - Add filters
  - Show table metadata
  - Add row count
- **Files:**
  - `app/components/domain/data/table-browser.tsx`
  - `app/lib/hooks/use-tables.ts`
- **Success Criteria:**
  - [ ] Can browse and find tables

#### 3.10 Add column details with data types
- **Task ID:** P3-10
- **Points:** 5
- **Dependencies:** P3-09
- **Acceptance Criteria:**
  - [ ] Show column names
  - [ ] Show data types
  - [ ] Show nullable flag
  - [ ] Show constraints
  - [ ] Column search
- **Implementation Requirements:**
  - Create ColumnDetails component
  - Fetch column metadata
  - Display type information
  - Add search
- **Files:**
  - `app/components/domain/data/column-details.tsx`
- **Success Criteria:**
  - [ ] Column information visible

#### 3.11 Create scan wizard with progress
- **Task ID:** P3-11
- **Points:** 10
- **Dependencies:** P2-14
- **Acceptance Criteria:**
  - [ ] Multi-step wizard
  - [ ] Select tables to scan
  - [ ] Progress bar with ETA
  - [ ] Cancel scan button
  - [ ] Scan results summary
  - [ ] Error handling
- **Implementation Requirements:**
  - Create ScanWizard component
  - Implement multi-step form
  - Add progress tracking
  - Show ETA calculation
  - Add cancel functionality
  - Handle errors gracefully
- **Files:**
  - `app/components/domain/data/scan-wizard.tsx`
  - `app/lib/hooks/use-scan-progress.ts`
- **Success Criteria:**
  - [ ] Scanning experience smooth

#### 3.12 Implement bulk table operations
- **Task ID:** P3-12
- **Points:** 10
- **Dependencies:** P3-09
- **Acceptance Criteria:**
  - [ ] Select multiple tables
  - [ ] Bulk scan
  - [ ] Bulk delete
  - [ ] Bulk export metadata
  - [ ] Confirmation dialogs
- **Implementation Requirements:**
  - Add table selection
  - Implement bulk operations
  - Add confirmation dialogs
  - Show progress for bulk ops
- **Files:**
  - `app/components/domain/data/bulk-operations.tsx`
- **Success Criteria:**
  - [ ] Can operate on multiple tables

#### 3.13 Redesign settings with grouped sections
- **Task ID:** P3-13
- **Points:** 10
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Grouped settings sections
  - [ ] Settings navigation (sidebar)
  - [ ] Search settings
  - [ ] Save indicator
  - [ ] Reset to defaults button
  - [ ] Settings organized logically
- **Implementation Requirements:**
  - Redesign settings layout
  - Add sidebar navigation
  - Group related settings
  - Add search
  - Add save/reset
- **Files:**
  - `app/components/domain/settings/settings-layout.tsx`
  - `app/components/domain/settings/settings-nav.tsx`
- **Success Criteria:**
  - [ ] Settings easy to navigate

#### 3.14 Create connection manager with test
- **Task ID:** P3-14
- **Points:** 10
- **Dependencies:** P2-14, P3-13
- **Acceptance Criteria:**
  - [ ] Add new connection form
  - [ ] Test connection button
  - [ ] Connection list
  - [ ] Edit connection
  - [ ] Delete connection
  - [ ] Connection validation
- **Implementation Requirements:**
  - Create ConnectionManager component
  - Add connection form
  - Implement test functionality
  - Add CRUD operations
  - Validate connection strings
- **Files:**
  - `app/components/domain/settings/connection-manager.tsx`
  - `app/lib/hooks/use-connections.ts`
- **Success Criteria:**
  - [ ] Can manage database connections

#### 3.15 Implement LLM configuration cards
- **Task ID:** P3-15
- **Points:** 5
- **Dependencies:** P3-13
- **Acceptance Criteria:**
  - [ ] LLM provider cards
  - [ ] API key input
  - [ ] Model selection
  - [ ] Test API button
  - [ ] Save configuration
- **Implementation Requirements:**
  - Create LLMConfigCard component
  - Add provider options
  - Add API key management
  - Add model selection
  - Test API connection
- **Files:**
  - `app/components/domain/settings/llm-config.tsx`
- **Success Criteria:**
  - [ ] Can configure LLM providers

#### 3.16 Add danger zone with confirmation
- **Task ID:** P3-16
- **Points:** 5
- **Dependencies:** P3-13
- **Acceptance Criteria:**
  - [ ] Danger zone section
  - [ ] Delete account button
  - [ ] Clear all data button
  - [ ] Confirmation dialogs
  - [ ] Warning messages
- **Implementation Requirements:**
  - Create DangerZone component
  - Add destructive actions
  - Require confirmation
  - Show warnings
  - Prevent accidental deletion
- **Files:**
  - `app/components/domain/settings/danger-zone.tsx`
- **Success Criteria:**
  - [ ] Dangerous actions protected

#### 3.17 Implement route-based code splitting
- **Task ID:** P3-17
- **Points:** 10
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Routes split into chunks
  - [ ] Loading states for routes
  - [ ] Reduced initial bundle size
  - [ ] No regression in UX
- **Implementation Requirements:**
  - Use React.lazy for routes
  - Add Suspense boundaries
  - Add loading fallbacks
  - Measure bundle sizes
- **Files:**
  - All route files
  - `app/main.tsx`
- **Success Criteria:**
  - [ ] Initial bundle < 200KB gzipped

#### 3.18 Add virtual scrolling for long lists
- **Task ID:** P3-18
- **Points:** 10
- **Dependencies:** P3-03
- **Acceptance Criteria:**
  - [ ] Lists render 1000+ items smoothly
  - [ ] Virtual scrolling implemented
  - [ ] Smooth scrolling performance
  - [ ] Works with keyboard nav
- **Implementation Requirements:**
  - Integrate react-window or react-virtuoso
  - Apply to long lists
  - Maintain keyboard nav
  - Test performance
- **Files:**
  - `app/components/ui/virtual-list.tsx`
  - All long list components
- **Success Criteria:**
  - [ ] Smooth scrolling with large datasets

#### 3.19 Optimize bundle size
- **Task ID:** P3-19
- **Points:** 5
- **Dependencies:** P3-17
- **Acceptance Criteria:**
  - [ ] Tree shaking enabled
  - [ ] Unused dependencies removed
  - [ ] Bundle analyzer integrated
  - [ ] Bundle size < 200KB gzipped
- **Implementation Requirements:**
  - Run bundle analyzer
  - Remove unused dependencies
  - Enable tree shaking
  - Optimize imports
- **Files:**
  - `package.json`
  - `vite.config.ts` or build config
- **Success Criteria:**
  - [ ] Optimized bundle size

#### 3.20 Add image optimization
- **Task ID:** P3-20
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Images optimized on build
  - [ ] Responsive images
  - [ ] WebP format where supported
  - [ ] Lazy loading images
- **Implementation Requirements:**
  - Configure image optimization
  - Use Next.js Image or similar
  - Generate responsive variants
  - Add lazy loading
- **Files:**
  - All image imports
  - Build configuration
- **Success Criteria:**
  - [ ] Images optimized and responsive

#### 3.21 Implement service worker for caching
- **Task ID:** P3-21
- **Points:** 10
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Service worker registered
  - [ ] Static assets cached
  - [ ] API responses cached (selectively)
  - [ ] Offline fallback page
  - [ ] Cache invalidation strategy
- **Implementation Requirements:**
  - Create service worker
  - Implement caching strategy
  - Add offline page
  - Handle cache updates
- **Files:**
  - `public/sw.js`
  - `app/lib/service-worker-registration.ts`
- **Success Criteria:**
  - [ ] App works offline

#### 3.22 User flow validation with real browsers
- **Task ID:** P3-22
- **Points:** 10
- **Dependencies:** P3-01, P3-07, P3-13
- **Acceptance Criteria:**
  - [ ] Complete user flows tested in real browsers
  - [ ] Chat flow tested (create chat, send message, view results)
  - [ ] Knowledge base flow tested (create, edit, delete)
  - [ ] Settings flow tested (connections, LLM config)
  - [ ] Data flow tested (browse tables, scan)
  - [ ] Edge cases documented
  - [ ] Screenshots captured for documentation
- **Implementation Requirements:**
  - Create comprehensive E2E scenarios
  - Test with real browsers (not just headless)
  - Document user flows
  - Capture screenshots/videos
  - Test error paths
  - Test keyboard-only workflows
- **Files:**
  - `tests/e2e/flows/chat-flow.spec.ts`
  - `tests/e2e/flows/knowledge-flow.spec.ts`
  - `tests/e2e/flows/settings-flow.spec.ts`
  - `tests/e2e/flows/data-flow.spec.ts`
  - `docs/user-flows.md`
- **Success Criteria:**
  - [ ] All critical user flows validated

**Success Criteria (Phase 3):**
- [ ] All 22 tasks completed
- [ ] Chat interface modern and functional
- [ ] Knowledge base management improved
- [ ] Data management tools working
- [ ] Settings organized
- [ ] Performance optimized (50% faster LCP)
- [ ] Service worker caching enabled
- [ ] User flows validated in real browsers

---

### Phase 4: Polish (Weeks 11-12)

**Goal:** Refine details, add delight, ensure production readiness

**Dependencies:** Requires Phase 3 completion

**Tasks:**

#### 4.1 Add micro-interactions
- **Task ID:** P4-01
- **Points:** 10
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Hover states on all interactive elements
  - [ ] Focus states visible and clear
  - [ ] Active states for pressed elements
  - [ ] Smooth transitions (200-300ms)
  - [ ] Respects prefers-reduced-motion
- **Implementation Requirements:**
  - Add hover styles to components
  - Add focus rings
  - Add active states
  - Add transitions
  - Check reduced motion preference
- **Files:**
  - `app/styles/globals.css`
  - All component files
- **Success Criteria:**
  - [ ] All interactions have feedback

#### 4.2 Implement page transitions
- **Task ID:** P4-02
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Smooth route transitions
  - [ ] Fade in/out animations
  - [ ] Respects prefers-reduced-motion
  - [ ] No jarring transitions
- **Implementation Requirements:**
  - Add transition component
  - Apply to routes
  - Check reduced motion
- **Files:**
  - `app/components/page-transition.tsx`
  - `app/routes/__root.tsx`
- **Success Criteria:**
  - [ ] Smooth page transitions

#### 4.3 Add skeleton loaders
- **Task ID:** P4-03
- **Points:** 10
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Skeleton components for all content types
  - [ ] Skeletons match final layout
  - [ ] Smooth loading experience
  - [ ] Used throughout app
- **Implementation Requirements:**
  - Create skeleton components
  - Apply to loading states
  - Match final content layout
- **Files:**
  - `app/components/ui/skeleton.tsx`
  - All content components
- **Success Criteria:**
  - [ ] No layout shift on load

#### 4.4 Create empty state illustrations
- **Task ID:** P4-04
- **Points:** 5
- **Dependencies:** P1-08
- **Acceptance Criteria:**
  - [ ] Custom illustrations for empty states
  - [ ] Consistent art style
  - [ ] Works in light/dark mode
  - [ ] Lightweight (SVG)
- **Implementation Requirements:**
  - Create SVG illustrations
  - Add to EmptyState component
  - Ensure dark mode support
- **Files:**
  - `app/components/illustrations/`
  - `app/components/ui/empty-state.tsx`
- **Success Criteria:**
  - [ ] Empty states visually appealing

#### 4.5 Polish toast notifications
- **Task ID:** P4-05
- **Points:** 5
- **Dependencies:** P2-11
- **Acceptance Criteria:**
  - [ ] Icons for each toast type
  - [ ] Color-coded (success, error, warning, info)
  - [ ] Smooth animations
  - [ ] Dismiss button visible
- **Implementation Requirements:**
  - Add icons to toasts
  - Add color variants
  - Add animations
  - Add dismiss button
- **Files:**
  - `app/components/ui/toast.tsx`
- **Success Criteria:**
  - [ ] Toasts polished and clear

#### 4.6 Add tooltips to truncated content
- **Task ID:** P4-06
- **Points:** 5
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] Tooltips on truncated text
  - [ ] Tooltips show full content
  - [ ] Keyboard accessible
  - [ ] Proper delay/positioning
- **Implementation Requirements:**
  - Create Tooltip component
  - Add to truncated elements
  - Ensure keyboard access
- **Files:**
  - `app/components/ui/tooltip.tsx`
  - All truncated content
- **Success Criteria:**
  - [ ] Can see full content on hover

#### 4.7 Implement command palette
- **Task ID:** P4-07
- **Points:** 10
- **Dependencies:** P2-09
- **Acceptance Criteria:**
  - [ ] Cmd+K opens command palette
  - [ ] Search through commands
  - [ ] Keyboard navigation
  - [ ] Covers 90% of actions
  - [ ] Shows keyboard shortcuts
- **Implementation Requirements:**
  - Create CommandPalette using cmdk
  - Register all commands
  - Add keyboard nav
  - Document shortcuts
- **Files:**
  - `app/components/ui/command-palette.tsx`
  - `app/lib/commands.ts`
- **Success Criteria:**
  - [ ] Power users love command palette

#### 4.8 Write unit tests (80% coverage)
- **Task ID:** P4-08
- **Points:** 15
- **Dependencies:** P2-02
- **Acceptance Criteria:**
  - [ ] 80%+ code coverage
  - [ ] All components tested
  - [ ] All hooks tested
  - [ ] All utilities tested
  - [ ] Tests pass in CI
- **Implementation Requirements:**
  - Write tests for components
  - Write tests for hooks
  - Write tests for utilities
  - Use Testing Library
  - Add to CI pipeline
- **Files:**
  - `tests/unit/components/*.test.tsx`
  - `tests/unit/hooks/*.test.ts`
  - `tests/unit/utils/*.test.ts`
- **Success Criteria:**
  - [ ] 80%+ coverage achieved

#### 4.9 Create E2E test suite
- **Task ID:** P4-09
- **Points:** 10
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] Critical flows covered
  - [ ] Chat flow tested
  - [ ] Knowledge base flow tested
  - [ ] Settings flow tested
  - [ ] Tests pass in CI
- **Implementation Requirements:**
  - Setup Playwright
  - Write E2E tests
  - Add to CI
  - Test on multiple browsers
- **Files:**
  - `tests/e2e/chat-flow.spec.ts`
  - `tests/e2e/knowledge-base-flow.spec.ts`
  - `tests/e2e/settings-flow.spec.ts`
  - `playwright.config.ts`
- **Success Criteria:**
  - [ ] E2E tests passing

#### 4.10 Run full accessibility audit
- **Task ID:** P4-10
- **Points:** 5
- **Dependencies:** P2-08
- **Acceptance Criteria:**
  - [ ] Axe DevTools shows 0 violations
  - [ ] Manual keyboard navigation test
  - [ ] Screen reader test
  - [ ] Color contrast check
  - [ ] WCAG 2.1 AA compliant
- **Implementation Requirements:**
  - Run axe DevTools on all pages
  - Test with keyboard only
  - Test with screen reader
  - Check color contrast
  - Fix all violations
- **Files:**
  - All pages and components
- **Success Criteria:**
  - [ ] 95%+ WCAG compliance

#### 4.11 Document component library
- **Task ID:** P4-11
- **Points:** 10
- **Dependencies:** P2-04
- **Acceptance Criteria:**
  - [ ] All components documented in Storybook
  - [ ] Usage examples
  - [ ] Props documented
  - [ ] Accessibility notes
  - [ ] Design guidelines
- **Implementation Requirements:**
  - Write Storybook docs
  - Add examples
  - Document props
  - Add a11y notes
  - Add design guidelines
- **Files:**
  - `app/components/ui/*.stories.tsx`
  - Storybook docs
- **Success Criteria:**
  - [ ] Component library documented

#### 4.12 Create user guide
- **Task ID:** P4-12
- **Points:** 5
- **Dependencies:** P4-07
- **Acceptance Criteria:**
  - [ ] Getting started guide
  - [ ] Keyboard shortcuts reference
  - [ ] Feature guides
  - [ ] Screenshots/videos
  - [ ] Targeted at analytic engineers
- **Implementation Requirements:**
  - Write user documentation
  - Add screenshots
  - Create videos for complex flows
  - Publish to docs site
- **Files:**
  - `docs/user-guide/`
  - `docs/keyboard-shortcuts.md`
- **Success Criteria:**
  - [ ] User guide comprehensive

#### 4.13 Performance audit and optimization
- **Task ID:** P4-13
- **Points:** 5
- **Dependencies:** P3-17
- **Acceptance Criteria:**
  - [ ] Lighthouse score > 95
  - [ ] LCP < 2s
  - [ ] FID < 100ms
  - [ ] CLS < 0.1
  - [ ] Bundle size optimized
- **Implementation Requirements:**
  - Run Lighthouse audit
  - Fix performance issues
  - Optimize critical path
  - Reduce bundle size
- **Files:**
  - All performance-critical files
- **Success Criteria:**
  - [ ] Lighthouse score > 95

#### 4.14 Security review and fixes
- **Task ID:** P4-14
- **Points:** 5
- **Dependencies:** none
- **Acceptance Criteria:**
  - [ ] No console.logs in production
  - [ ] No exposed API keys
  - [ ] Proper error handling (no data leakage)
  - [ ] CSP headers configured
  - [ ] Dependencies audited
- **Implementation Requirements:**
  - Run security audit
  - Remove sensitive data
  - Add CSP headers
  - Audit dependencies
  - Fix vulnerabilities
- **Files:**
  - All source files
  - `app/server/config.py` (for CSP)
- **Success Criteria:**
  - [ ] Security issues resolved

#### 4.15 Launch preparation checklist
- **Task ID:** P4-15
- **Points:** 5
- **Dependencies:** All previous tasks
- **Acceptance Criteria:**
  - [ ] Feature flags configured
  - [ ] Rollback plan documented
  - [ ] Monitoring configured
  - [ ] Error tracking setup
  - [ ] Support channels ready
  - [ ] Documentation complete
- **Implementation Requirements:**
  - Configure feature flags
  - Document rollback
  - Setup monitoring
  - Setup error tracking
  - Prepare support
- **Files:**
  - `docs/deployment/`
  - Monitoring dashboards
- **Success Criteria:**
  - [ ] Ready for production launch

#### 4.16 Manual accessibility testing with real users
- **Task ID:** P4-16
- **Points:** 5
- **Dependencies:** P4-10
- **Acceptance Criteria:**
  - [ ] Screen reader testing completed (NVDA, JAWS, VoiceOver)
  - [ ] Keyboard-only navigation validated
  - [ ] High contrast mode tested
  - [ ] Zoom testing (200%, 400%)
  - [ ] Real user with disabilities testing
  - [ ] Accessibility issues documented and fixed
- **Implementation Requirements:**
  - Recruit users with disabilities for testing
  - Test with actual screen readers
  - Test keyboard-only workflows
  - Test browser zoom functionality
  - Document and fix all issues found
- **Files:**
  - `docs/accessibility-testing-report.md`
  - All components requiring fixes
- **Success Criteria:**
  - [ ] Real-world accessibility validated

#### 4.17 Production smoke tests with real browsers
- **Task ID:** P4-17
- **Points:** 5
- **Dependencies:** P4-15
- **Acceptance Criteria:**
  - [ ] Smoke tests run on production-like environment
  - [ ] All critical paths tested before launch
  - [ ] Real browser testing (not emulated)
  - [ ] Performance validated in production
  - [ ] Error tracking verified
  - [ ] Rollback tested
- **Implementation Requirements:**
  - Create smoke test suite
  - Deploy to staging
  - Run tests with real browsers
  - Validate all critical paths
  - Test rollback procedure
  - Measure production performance
- **Files:**
  - `tests/smoke/production-smoke.spec.ts`
  - `docs/pre-launch-checklist.md`
- **Success Criteria:**
  - [ ] Production validated before launch

**Success Criteria (Phase 4):**
- [ ] All 17 tasks completed
- [ ] Micro-interactions polished
- [ ] Command palette functional
- [ ] 80%+ test coverage
- [ ] Full WCAG 2.1 AA compliance
- [ ] Lighthouse score > 95
- [ ] Documentation complete
- [ ] Production-ready
- [ ] Manual accessibility testing complete
- [ ] Production smoke tests passed

---

## Alternative Approaches Considered

### 1. Incremental Rollout vs Big Bang
**Decision:** Phased approach with phase gates
**Rationale:** Allows for feedback, reduces risk, maintains momentum

### 2. Custom Design System vs Existing Library
**Decision:** Build on shadcn/ui
**Rationale:** Proven patterns, faster implementation, full customization

### 3. Full TypeScript Migration
**Decision:** Already using TypeScript, ensuring strict mode
**Rationale:** Type safety catches bugs early, better DX

### 4. Client-Side vs Server-Side Routing
**Decision:** Next.js App Router (server-side)
**Rationale:** Better SEO, faster initial load, simpler data fetching

### 5. Component Library: Radix vs Headless UI
**Decision:** Radix UI
**Rationale:** Better accessibility, more primitives, active development

## Team Orchestration

As the team lead, you have access to powerful tools for coordinating work across multiple agents. You NEVER write code directly - you orchestrate team members using these tools.

### Task Management Tools

**TaskCreate** - Create tasks in the shared task list:

```typescript
TaskCreate({
  subject: "Implement user authentication",
  description: "Create login/logout endpoints with JWT tokens. See specs/kai-ui-revamp.md for details.",
  activeForm: "Implementing authentication" // Shows in UI spinner when in_progress
})
// Returns: taskId (e.g., "1")
```

**TaskUpdate** - Update task status, assignment, or dependencies:

```typescript
TaskUpdate({
  taskId: "1",
  status: "in_progress", // pending → in_progress → completed
  owner: "builder-auth" // Assign to specific team member
})
```

**TaskList** - View all tasks and their status:

```typescript
TaskList({})
// Returns: Array of tasks with id, subject, status, owner, blockedBy
```

**TaskGet** - Get full details of a specific task:

```typescript
TaskGet({ taskId: "1" })
// Returns: Full task including description
```

### Task Dependencies

Use `addBlockedBy` to create sequential dependencies - blocked tasks cannot start until dependencies complete:

```typescript
// Task 2 depends on Task 1
TaskUpdate({
  taskId: "2",
  addBlockedBy: ["1"] // Task 2 blocked until Task 1 completes
})

// Task 3 depends on both Task 1 and Task 2
TaskUpdate({
  taskId: "3",
  addBlockedBy: ["1", "2"]
})
```

Dependency chain example:
```
Task 1: Setup foundation → no dependencies
Task 2: Implement feature → blockedBy: ["1"]
Task 3: Write tests → blockedBy: ["2"]
Task 4: Final validation → blockedBy: ["1", "2", "3"]
```

### Owner Assignment

Assign tasks to specific team members for clear accountability:

```typescript
// Assign task to a specific builder
TaskUpdate({
  taskId: "1",
  owner: "builder-api"
})

// Team members check for their assignments
TaskList({}) // Filter by owner to find assigned work
```

### Agent Deployment with Task Tool

**Task** - Deploy an agent to do work:

```typescript
Task({
  description: "Implement auth endpoints",
  prompt: "Implement the authentication endpoints as specified in Task 1...",
  subagent_type: "general-purpose",
  model: "sonnet", // or "opus" for complex work, "haiku" for VERY simple
  run_in_background: false // true for parallel execution
})
// Returns: agentId (e.g., "a1b2c3")
```

### Resume Pattern

Store the agentId to continue an agent's work with preserved context:

```typescript
// First deployment - agent works on initial task
Task({
  description: "Build user service",
  prompt: "Create the user service with CRUD operations...",
  subagent_type: "general-purpose"
})
// Returns: agentId: "abc123"

// Later - resume SAME agent with full context preserved
Task({
  description: "Continue user service",
  prompt: "Now add input validation to the endpoints you created...",
  subagent_type: "general-purpose",
  resume: "abc123" // Continues with previous context
})
```

**When to resume vs start fresh:**
- **Resume**: Continuing related work, agent needs prior context
- **Fresh**: Unrelated task, clean slate preferred

### Parallel Execution

Run multiple agents simultaneously with `run_in_background: true`:

```typescript
// Launch multiple agents in parallel
Task({
  description: "Build API endpoints",
  prompt: "...",
  subagent_type: "general-purpose",
  run_in_background: true
})
// Returns immediately with agentId and output_file path

Task({
  description: "Build frontend components",
  prompt: "...",
  subagent_type: "general-purpose",
  run_in_background: true
})

// Both agents now working simultaneously

// Check on progress
TaskOutput({
  task_id: "agentId",
  block: false, // non-blocking check
  timeout: 5000
})

// Wait for completion
TaskOutput({
  task_id: "agentId",
  block: true, // blocks until done
  timeout: 300000
})
```

### Orchestration Workflow

1. **Create tasks** with `TaskCreate` for each step in the plan
2. **Set dependencies** with `TaskUpdate` + `addBlockedBy`
3. **Assign owners** with `TaskUpdate` + `owner`
4. **Deploy agents** with `Task` to execute assigned work
5. **Monitor progress** with `TaskList` and `TaskOutput`
6. **Resume agents** with `Task` + `resume` for follow-up work
7. **Mark complete** with `TaskUpdate` + `status: "completed"`

### Team Members

Based on the tech stack (Next.js, React, TypeScript, Tailwind CSS) and project scope, the team consists of:

#### Builder: Frontend Foundation
- **Name:** `builder-foundation`
- **Role:** Frontend Architecture
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Design token system (P2-01)
  - Base component library (P2-02)
  - Dark/light mode (P2-03)
  - Storybook setup (P2-04)
  - Brand color integration (P2-05)

#### Builder: Accessibility
- **Name:** `builder-a11y`
- **Role:** Accessibility Specialist
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - ARIA labels (P1-02)
  - Skip links and landmarks (P2-06)
  - Live regions (P2-07)
  - axe DevTools CI (P2-08)
  - Keyboard shortcuts (P2-09)
  - Focus trap (P2-10)
  - Accessibility audit (P4-10)

#### Builder: UI Components
- **Name:** `builder-ui`
- **Role:** Frontend Developer
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Button consistency (P1-07)
  - Empty states (P1-08)
  - Loading states (P1-04)
  - Error boundaries (P1-06)
  - Error toasts (P2-11)
  - Form validation (P2-14)
  - Micro-interactions (P4-01)
  - Skeleton loaders (P4-03)

#### Builder: Features
- **Name:** `builder-features`
- **Role:** Frontend Developer
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Chat redesign (P3-01, P3-02, P3-03, P3-04)
  - Knowledge base (P3-07, P3-08)
  - Data management (P3-09, P3-10, P3-11, P3-12)
  - Settings (P3-13, P3-14, P3-15, P3-16)
  - Command palette (P4-07)

#### Builder: Performance
- **Name:** `builder-perf`
- **Role:** Performance Engineer
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Remove console.logs (P1-01)
  - Code splitting (P3-17)
  - Virtual scrolling (P3-18)
  - Bundle optimization (P3-19)
  - Image optimization (P3-20)
  - Service worker (P3-21)
  - Performance audit (P4-13)

#### Builder: Testing
- **Name:** `builder-tests`
- **Role:** QA Engineer
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Unit tests (P4-08)
  - E2E tests (P4-09)
  - Security review (P4-14)

#### Builder: Mobile
- **Name:** `builder-mobile`
- **Role:** Frontend Developer (Mobile Focus)
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Sidebar mobile responsiveness (P1-03)
  - Touch interactions
  - Mobile testing

#### Builder: Polish
- **Name:** `builder-polish`
- **Role:** Frontend Developer
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Page transitions (P4-02)
  - Empty state illustrations (P4-04)
  - Toast polish (P4-05)
  - Tooltips (P4-06)
  - Documentation (P4-11, P4-12)
  - Launch prep (P4-15)

#### Builder: UI Tester (Browser)
- **Name:** `builder-ui-tester`
- **Role:** QA Engineer (Browser Testing)
- **Agent Type:** `general-purpose`
- **Resume:** true
- **Responsibilities:**
  - Real scenario testing (continuous)
  - Visual regression testing (P2-16)
  - Cross-browser testing (P2-17)
  - Mobile device testing (P2-18)
  - User flow validation (P3-22)
  - Accessibility manual testing (P4-16)
  - Production smoke tests (P4-17)
  - Uses Playwright and real browsers for all testing

## Step by Step Tasks

### Phase 1: Quick Wins (Week 1)

#### 1. Remove console.logs from production builds
- **Task ID:** P1-01
- **Depends On:** none
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Search for all `console.log` statements in the codebase and remove them. Replace with proper logging library if needed. Add ESLint rule to prevent future console.logs.

#### 2. Add missing ARIA labels to navigation
- **Task ID:** P1-02
- **Depends On:** none
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01)
- Audit all navigation components and add descriptive ARIA labels. Ensure all icons have aria-hidden="true" or proper labels.

#### 3. Fix sidebar mobile responsiveness
- **Task ID:** P1-03
- **Depends On:** none
- **Assigned To:** `builder-mobile`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02)
- Implement responsive sidebar that collapses to hamburger menu on mobile (< 768px). Use Radix Sheet or Drawer for mobile slide-in behavior.

#### 4. Add loading states to all async actions
- **Task ID:** P1-04
- **Depends On:** none
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02, P1-03)
- Create LoadingButton and Skeleton components. Add loading states to all async actions using React Query's isLoading status.

#### 5. Implement basic keyboard navigation
- **Task ID:** P1-05
- **Depends On:** none
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02, P1-03, P1-04)
- Add visible focus styles and ensure proper tab order. Add keyboard event handlers to modals (Escape to close).

#### 6. Add error boundaries to all routes
- **Task ID:** P1-06
- **Depends On:** none
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02, P1-03, P1-04, P1-05)
- Create ErrorBoundary component and wrap all route components. Add error logging and create friendly error fallback UI.

#### 7. Fix inconsistent button styles
- **Task ID:** P1-07
- **Depends On:** none
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02, P1-03, P1-04, P1-05, P1-06)
- Audit all button usage and replace with consistent Button component. Define variants: primary, secondary, ghost, danger.

#### 8. Add empty states with CTAs
- **Task ID:** P1-08
- **Depends On:** none
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02, P1-03, P1-04, P1-05, P1-06, P1-07)
- Create EmptyState component and add to all list views (chat, knowledge, connections). Write helpful copy and add CTAs with clear actions.

#### 9. Implement basic focus management
- **Task ID:** P1-09
- **Depends On:** none
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P1-01, P1-02, P1-03, P1-04, P1-05, P1-06, P1-07, P1-08)
- Create useFocusTrap hook and FocusTrap component. Add skip links. Manage focus on route changes (move to first input).

### Phase 2: Foundation (Weeks 2-4)

#### 10. Create design token system
- **Task ID:** P2-01
- **Depends On:** P1-01, P1-07
- **Assigned To:** `builder-foundation`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Define design tokens for colors (Deep Indigo #6366f1 as primary), spacing, typography, border radius, and shadows. Export from `app/lib/tokens.ts` and integrate with Tailwind config.

#### 11. Build base component library
- **Task ID:** P2-02
- **Depends On:** P2-01
- **Assigned To:** `builder-foundation`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Build 15+ accessible base components on shadcn/ui: Button, Input, Card, Select, Checkbox, Radio, Switch, Slider, Tabs, Dialog, Dropdown, Popover, Tooltip, Toast. All must pass axe DevTools and be documented in Storybook.

#### 12. Implement dark/light mode toggle
- **Task ID:** P2-03
- **Depends On:** P2-01
- **Assigned To:** `builder-foundation`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-02)
- Create theme store with Zustand. Add ThemeToggle component to header. Ensure mode persists across sessions and respects system preference on first visit.

#### 13. Setup Storybook for component development
- **Task ID:** P2-04
- **Depends On:** none
- **Assigned To:** `builder-foundation`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Install and configure @storybook/react. Add accessibility and dark mode addons. Create stories for all base components.

#### 14. Create brand color integration
- **Task ID:** P2-05
- **Depends On:** P2-01
- **Assigned To:** `builder-foundation`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-02)
- Update design tokens with Deep Indigo (#6366f1) as primary color. Update logo SVG and apply brand color consistently across app.

#### 15. Implement skip links and landmarks
- **Task ID:** P2-06
- **Depends On:** none
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create SkipLink component and add to root layout. Wrap content in semantic HTML landmarks (nav, main, aside, footer) with descriptive aria-label.

#### 16. Add live regions for dynamic content
- **Task ID:** P2-07
- **Depends On:** none
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create LiveRegion component. Wrap toast notifications, error messages, and success messages. Use aria-live="polite" or "assertive" appropriately.

#### 17. Setup axe DevTools CI integration
- **Task ID:** P2-08
- **Depends On:** none
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Install @axe-core/react and configure CI pipeline to run axe on all components. Fail build on critical violations and generate accessibility report.

#### 18. Keyboard shortcut system
- **Task ID:** P2-09
- **Depends On:** P1-05
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create useKeyboardShortcuts hook and KeyboardShortcutsModal component. Define shortcut map and register global shortcuts. Press `?` to open modal.

#### 19. Focus trap implementation
- **Task ID:** P2-10
- **Depends On:** P1-09
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create FocusTrap component using Radix primitives. Add to all modals/dialogs. Ensure Tab cycles through modal elements and Escape closes.

#### 20. Global error toast system
- **Task ID:** P2-11
- **Depends On:** P2-07
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create Toast component using sonner. Create Toaster provider and useToast hook. Add to root layout and integrate with API client for automatic error toasts.

#### 21. Add retry logic to React Query mutations
- **Task ID:** P2-12
- **Depends On:** none
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Configure React Query mutation retry with exponential backoff. Add manual retry button to error states. Prevent infinite loops with max retries.

#### 22. Create error page components
- **Task ID:** P2-13
- **Depends On:** P2-11
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create NotFoundPage and ServerErrorPage components. Add routes for 404 and 500. Use EmptyState component with helpful CTAs.

#### 23. Implement form validation patterns
- **Task ID:** P2-14
- **Depends On:** P2-02
- **Assigned To:** `builder-ui`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Create useFormValidation hook and FieldError component. Add validation rules and integrate with all forms. Show errors inline and announce via live region.

#### 24. Add analytics event tracking
- **Task ID:** P2-15
- **Depends On:** none
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Setup analytics (PostHog or custom). Create trackEvent function. Track page views, key user actions, and errors. Ensure privacy compliance (no PII).

#### 25. Visual regression testing setup
- **Task ID:** P2-16
- **Depends On:** P2-02
- **Assigned To:** `builder-ui-tester`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P2-02)
- Setup Playwright screenshot testing. Configure visual regression (Percy, Chromatic, or Playwright native). Capture baseline screenshots. Add to CI pipeline.

#### 26. Cross-browser testing setup
- **Task ID:** P2-17
- **Depends On:** none
- **Assigned To:** `builder-ui-tester`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P2-01)
- Configure Playwright browser matrix (Chrome, Firefox, Safari, Edge). Identify browser-specific issues. Add polyfills if needed. Document browser support policy.

#### 27. Mobile device testing setup
- **Task ID:** P2-18
- **Depends On:** P1-03
- **Assigned To:** `builder-ui-tester`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P1-03)
- Setup device emulation in Playwright. Configure real device testing (BrowserStack/Sauce Labs optional). Test touch interactions. Test common mobile viewports.

### Phase 3: Major Features (Weeks 5-10)

#### 28. Redesign chat layout with history sidebar
- **Task ID:** P3-01
- **Depends On:** P2-02, P2-03
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Redesign chat interface with collapsible history sidebar (left), message area (center), and input area (bottom). Add search/filter chats and create new chat button.

#### 29. Implement message streaming UI
- **Task ID:** P3-02
- **Depends On:** P3-01
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Implement SSE or streaming response handling. Messages appear as they stream with typing indicator. Add auto-scroll to latest message and stop generation button.

#### 30. Add SQL result tables with export
- **Task ID:** P3-03
- **Depends On:** P3-01
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Create SQLResultsTable component with virtual scrolling for large datasets. Add export to CSV and JSON. Implement column sorting and responsive design.

#### 31. Create visualization card components
- **Task ID:** P3-04
- **Depends On:** P3-03
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Integrate chart library (Recharts or Chart.js). Create bar, line, and pie chart components. Add dark mode support, export as images, and interactive tooltips.

#### 32. Implement chat search and filters
- **Task ID:** P3-05
- **Depends On:** P3-01
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P3-02)
- Add search functionality to chat history. Implement filters by date range and chat type. Highlight search results and add Cmd+K keyboard shortcut.

#### 33. Add message actions
- **Task ID:** P3-06
- **Depends On:** P3-02
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** true (with P3-03)
- Add action menu to messages with copy, regenerate, share, and delete buttons. Ensure all actions accessible via keyboard.

#### 34. Redesign knowledge base list
- **Task ID:** P3-07
- **Depends On:** P2-02
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-04)
- Redesign knowledge base list with grid/list view toggle. Add filters by type/tags, search, and sort by name/date/size. Include create new knowledge base button and empty state.

#### 35. Create knowledge base editor with preview
- **Task ID:** P3-08
- **Depends On:** P3-07
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Integrate markdown editor (CodeMirror or Monaco). Create split pane view with live preview. Add save button with loading state, auto-save indicator, and syntax highlighting.

#### 36. Implement table browser with search
- **Task ID:** P3-09
- **Depends On:** P2-02
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-08)
- Create TableBrowser component. List all tables with search by name and filter by schema. Show table metadata and row count preview.

#### 37. Add column details with data types
- **Task ID:** P3-10
- **Depends On:** P3-09
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Create ColumnDetails component. Show column names, data types, nullable flag, and constraints. Add column search functionality.

#### 38. Create scan wizard with progress
- **Task ID:** P3-11
- **Depends On:** P2-14
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-10)
- Create ScanWizard component with multi-step form. Select tables to scan, show progress bar with ETA, add cancel button, and display scan results summary.

#### 39. Implement bulk table operations
- **Task ID:** P3-12
- **Depends On:** P3-09
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-11)
- Add table selection functionality. Implement bulk scan, bulk delete, and bulk export metadata. Add confirmation dialogs and show progress for bulk operations.

#### 40. Redesign settings with grouped sections
- **Task ID:** P3-13
- **Depends On:** P2-02
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-12)
- Redesign settings layout with grouped sections and sidebar navigation. Add settings search, save indicator, and reset to defaults button.

#### 41. Create connection manager with test
- **Task ID:** P3-14
- **Depends On:** P2-14, P3-13
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Create ConnectionManager component. Add new connection form, test connection button, connection list, edit/delete functionality, and connection validation.

#### 42. Implement LLM configuration cards
- **Task ID:** P3-15
- **Depends On:** P3-13
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Create LLMConfigCard component. Add LLM provider cards, API key input, model selection, test API button, and save configuration.

#### 43. Add danger zone with confirmation
- **Task ID:** P3-16
- **Depends On:** P3-13
- **Assigned To:** `builder-features`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-15)
- Create DangerZone component. Add delete account and clear all data buttons. Require confirmation dialogs and show warning messages.

#### 44. Implement route-based code splitting
- **Task ID:** P3-17
- **Depends On:** none
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 2)
- Use React.lazy for all routes. Add Suspense boundaries with loading fallbacks. Measure bundle sizes and ensure initial bundle < 200KB gzipped.

#### 45. Add virtual scrolling for long lists
- **Task ID:** P3-18
- **Depends On:** P3-03
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Integrate react-window or react-virtuoso. Apply to long lists (chat history, table browser). Maintain keyboard navigation and test with 1000+ items.

#### 46. Optimize bundle size
- **Task ID:** P3-19
- **Depends On:** P3-17
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Run bundle analyzer. Remove unused dependencies, enable tree shaking, optimize imports. Ensure bundle size < 200KB gzipped.

#### 47. Add image optimization
- **Task ID:** P3-20
- **Depends On:** none
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-19)
- Configure image optimization. Use Next.js Image or similar. Generate responsive variants, convert to WebP, and add lazy loading.

#### 48. Implement service worker for caching
- **Task ID:** P3-21
- **Depends On:** none
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-20)
- Create service worker with caching strategy. Cache static assets and selective API responses. Add offline fallback page and cache invalidation strategy.

#### 49. User flow validation with real browsers
- **Task ID:** P3-22
- **Depends On:** P3-01, P3-07, P3-13
- **Assigned To:** `builder-ui-tester`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P3-01, P3-07, P3-13)
- Create comprehensive E2E scenarios. Test with real browsers (not just headless). Document user flows. Capture screenshots/videos. Test error paths and keyboard-only workflows.

### Phase 4: Polish (Weeks 11-12)

#### 50. Add micro-interactions
- **Task ID:** P4-01
- **Depends On:** P2-02
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Add hover, focus, and active states to all interactive elements. Use smooth transitions (200-300ms) and respect prefers-reduced-motion.

#### 51. Implement page transitions
- **Task ID:** P4-02
- **Depends On:** none
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Add page transition component with fade in/out animations. Ensure respects prefers-reduced-motion and no jarring transitions.

#### 52. Add skeleton loaders
- **Task ID:** P4-03
- **Depends On:** P2-02
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-01)
- Create skeleton components for all content types. Apply to loading states, ensure match final layout, and eliminate layout shift.

#### 53. Create empty state illustrations
- **Task ID:** P4-04
- **Depends On:** P1-08
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-02)
- Create custom SVG illustrations for empty states. Ensure consistent art style, works in light/dark mode, and lightweight.

#### 54. Polish toast notifications
- **Task ID:** P4-05
- **Depends On:** P2-11
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-03)
- Add icons for each toast type. Color-code (success, error, warning, info). Add smooth animations and visible dismiss button.

#### 55. Add tooltips to truncated content
- **Task ID:** P4-06
- **Depends On:** P2-02
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-04)
- Create Tooltip component. Add to all truncated text. Show full content on hover, ensure keyboard accessible, proper delay/positioning.

#### 56. Implement command palette
- **Task ID:** P4-07
- **Depends On:** P2-09
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-05)
- Create CommandPalette using cmdk. Register all commands, add keyboard navigation, cover 90% of actions, show keyboard shortcuts.

#### 57. Write unit tests (80% coverage)
- **Task ID:** P4-08
- **Depends On:** P2-02
- **Assigned To:** `builder-tests`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Write tests for all components, hooks, and utilities. Use Testing Library. Achieve 80%+ coverage and ensure tests pass in CI.

#### 58. Create E2E test suite
- **Task ID:** P4-09
- **Depends On:** none
- **Assigned To:** `builder-tests`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Setup Playwright. Write E2E tests for chat, knowledge base, and settings flows. Test on multiple browsers and ensure tests pass in CI.

#### 59. Run full accessibility audit
- **Task ID:** P4-10
- **Depends On:** P2-08
- **Assigned To:** `builder-a11y`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Run axe DevTools on all pages. Test with keyboard only and screen reader. Check color contrast. Fix all violations and achieve 95%+ WCAG compliance.

#### 60. Document component library
- **Task ID:** P4-11
- **Depends On:** P2-04
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-07)
- Document all components in Storybook. Add usage examples, props documentation, accessibility notes, and design guidelines.

#### 61. Create user guide
- **Task ID:** P4-12
- **Depends On:** P4-07
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-10)
- Write getting started guide, keyboard shortcuts reference, and feature guides. Add screenshots/videos. Target at analytic engineers. Publish to docs site.

#### 62. Performance audit and optimization
- **Task ID:** P4-13
- **Depends On:** P3-17
- **Assigned To:** `builder-perf`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Run Lighthouse audit. Fix performance issues. Optimize critical path. Achieve Lighthouse score > 95, LCP < 2s, FID < 100ms, CLS < 0.1.

#### 63. Security review and fixes
- **Task ID:** P4-14
- **Depends On:** none
- **Assigned To:** `builder-tests`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after Phase 3)
- Run security audit. Remove console.logs, exposed API keys, and ensure proper error handling. Add CSP headers, audit dependencies, fix vulnerabilities.

#### 64. Launch preparation checklist
- **Task ID:** P4-15
- **Depends On:** All previous tasks
- **Assigned To:** `builder-polish`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after all other tasks)
- Configure feature flags, document rollback plan, setup monitoring, setup error tracking, prepare support channels, complete documentation.

#### 65. Manual accessibility testing with real users
- **Task ID:** P4-16
- **Depends On:** P4-10
- **Assigned To:** `builder-ui-tester`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-10)
- Recruit users with disabilities for testing. Test with actual screen readers (NVDA, JAWS, VoiceOver). Test keyboard-only workflows, high contrast mode, and browser zoom (200%, 400%). Document and fix all issues found.

#### 66. Production smoke tests with real browsers
- **Task ID:** P4-17
- **Depends On:** P4-15
- **Assigned To:** `builder-ui-tester`
- **Agent Type:** `general-purpose`
- **Parallel:** false (after P4-15)
- Create smoke test suite and deploy to staging. Run tests with real browsers (not emulated). Validate all critical paths, test rollback procedure, and measure production performance.

## Acceptance Criteria

### Functional Requirements

#### Phase 1 (Quick Wins)
- [ ] Production build has zero console.log statements
- [ ] All navigation elements have descriptive ARIA labels
- [ ] Sidebar works on mobile (320px - 768px)
- [ ] All async actions show loading state
- [ ] All routes have error boundaries
- [ ] Tab navigation follows logical order
- [ ] Empty states guide users to next actions
- [ ] All buttons use consistent Button component
- [ ] Modals trap focus, Escape closes

#### Phase 2 (Foundation)
- [ ] Design tokens defined and integrated
- [ ] 15+ accessible base components built
- [ ] Dark mode persists across sessions
- [ ] Storybook running at localhost:6006
- [ ] Deep Indigo (#6366f1) used consistently
- [ ] Skip links visible on focus
- [ ] Live regions announce dynamic changes
- [ ] CI runs axe on all components
- [ ] Press `?` opens shortcuts modal
- [ ] Cannot tab outside modal
- [ ] Errors show as toasts
- [ ] Failed mutations retry
- [ ] Error pages for 404/500
- [ ] All forms have validation
- [ ] Analytics tracking enabled

#### Phase 3 (Major Features)
- [ ] Chat interface with history sidebar
- [ ] Messages stream with typing indicator
- [ ] SQL results export to CSV/JSON
- [ ] Charts render and interactive
- [ ] Can search and filter chats
- [ ] Message actions work (copy, regenerate, share)
- [ ] Knowledge base grid/list views
- [ ] Markdown editor with preview
- [ ] Can browse and search tables
- [ ] Column details visible
- [ ] Scan wizard shows progress/ETA
- [ ] Bulk operations work
- [ ] Settings grouped and navigable
- [ ] Can manage connections
- [ ] Can configure LLM providers
- [ ] Dangerous actions protected
- [ ] Initial bundle < 200KB gzipped
- [ ] Tables render 1000+ rows smoothly
- [ ] Images optimized and responsive
- [ ] Service worker caching enabled

#### Phase 4 (Polish)
- [ ] All interactions have hover/focus/active states
- [ ] Smooth page transitions
- [ ] Skeleton loaders prevent layout shift
- [ ] Empty states have illustrations
- [ ] Toasts polished with icons
- [ ] Tooltips on truncated content
- [ ] Cmd+K opens command palette
- [ ] 80%+ test coverage
- [ ] E2E tests pass
- [ ] Axe DevTools shows 0 violations
- [ ] Component library documented
- [ ] User guide complete
- [ ] Lighthouse score > 95
- [ ] Security issues resolved
- [ ] Ready for production launch

### Non-Functional Requirements

#### Performance
- [ ] Lighthouse Performance score > 95
- [ ] LCP < 2s
- [ ] FID < 100ms
- [ ] CLS < 0.1
- [ ] Bundle size < 200KB gzipped
- [ ] Images optimized (WebP, lazy loading)
- [ ] Virtual scrolling for 1000+ items

#### Accessibility
- [ ] WCAG 2.1 AA compliance > 95%
- [ ] All interactive elements keyboard accessible
- [ ] Focus visible on all interactive elements
- [ ] ARIA labels on all navigation
- [ ] Live regions for dynamic content
- [ ] Color contrast AA compliant
- [ ] Screen reader friendly
- [ ] Respects prefers-reduced-motion

#### Quality
- [ ] 80%+ test coverage
- [ ] E2E tests for critical flows
- [ ] No console.logs in production
- [ ] Error boundaries on all routes
- [ ] TypeScript strict mode
- [ ] ESLint/Prettier configured
- [ ] CI/CD pipeline passing

#### Security
- [ ] No exposed API keys
- [ ] Proper error handling (no data leakage)
- [ ] CSP headers configured
- [ ] Dependencies audited
- [ ] HTTPS only
- [ ] Input validation on all forms

### Quality Gates

#### Phase 1 Gate
- [ ] All Phase 1 tasks complete
- [ ] Production build clean
- [ ] Basic WCAG compliance
- [ ] Mobile functional

#### Phase 2 Gate
- [ ] All Phase 2 tasks complete
- [ ] Design system documented
- [ ] Accessibility infrastructure in place
- [ ] Beta release ready

#### Phase 3 Gate
- [ ] All Phase 3 tasks complete
- [ ] All major features working
- [ ] Performance optimized
- [ ] E2E tests passing

#### Phase 4 Gate
- [ ] All Phase 4 tasks complete
- [ ] 80%+ test coverage
- [ ] Full WCAG 2.1 AA compliance
- [ ] Lighthouse > 95
- [ ] Documentation complete
- [ ] Production ready

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Visual Design Maturity | 6/10 | 9/10 | Design review |
| WCAG 2.1 AA Compliance | 62% | 95%+ | axe DevTools |
| Lighthouse Performance | 75 | 95+ | Lighthouse audit |
| Lighthouse Accessibility | 62 | 95+ | Lighthouse audit |
| Bundle Size (gzipped) | ~250KB | <200KB | Bundle analyzer |
| Test Coverage | 0% | 80%+ | Vitest coverage |
| Time to Interactive | ~4s | <2s | Lighthouse |
| Critical Issues | 9 | 0 | Manual verification |

## Dependencies & Prerequisites

### External Dependencies

| Dependency | Version | Purpose | Risk |
|------------|---------|---------|------|
| Next.js | 14+ | Framework | Low |
| React | 18+ | UI library | Low |
| TypeScript | 5+ | Type safety | Low |
| Tailwind CSS | 3+ | Styling | Low |
| shadcn/ui | Latest | Component primitives | Low |
| Radix UI | Latest | Accessible primitives | Low |
| React Query | Latest | Server state | Low |
| Zustand | 4+ | Client state | Low |
| Vitest | Latest | Unit testing | Low |
| Playwright | Latest | E2E testing | Low |
| @axe-core/react | Latest | Accessibility testing | Low |
| cmdk | Latest | Command palette | Low |
| sonner | Latest | Toast notifications | Low |
| Recharts/Chart.js | Latest | Charts | Medium |

### Internal Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Phase 1 completion | Pending | Required for Phase 2 |
| Phase 2 completion | Pending | Required for Phase 3 |
| Phase 3 completion | Pending | Required for Phase 4 |
| Design tokens | Pending | Required for components |
| Base components | Pending | Required for features |

## Risk Analysis & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep beyond 12 weeks | Medium | High | Strict adherence to phase gates, defer nice-to-haves |
| Breaking existing functionality | Medium | High | Comprehensive E2E tests before each phase |
| Accessibility standards complexity | High | Medium | Engage accessibility specialist for Phase 2 |
| Performance regressions | Low | Medium | Regular Lighthouse audits in CI |
| Design system iteration time | Medium | Medium | Start with proven shadcn/ui patterns |
| Dark mode color contrast issues | Medium | Low | Automated contrast ratio checks |
| Browser compatibility (older Safari) | Low | Low | Target evergreen browsers only |
| Chart library complexity | Medium | Medium | Choose library with good docs and examples |
| Test coverage not reaching 80% | Medium | Low | Focus on critical paths first |
| Service worker caching issues | Medium | Medium | Comprehensive testing, cache versioning |

## Resource Requirements

### Development Time Estimate

| Phase | Complexity | Estimate | Team |
|-------|------------|----------|------|
| Phase 1 | Simple | 5 days | 3 builders (parallel) |
| Phase 2 | Medium | 15 days | 4 builders (parallel) |
| Phase 3 | Complex | 30 days | 4 builders (parallel) |
| Phase 4 | Medium | 10 days | 4 builders (parallel) |
| **Total** | | **60 days** | **Can compress to ~12 weeks with dedicated team** |

### Team Composition

- **1 Senior Frontend Developer** (40 hrs/week): Primary implementation
- **1 UI/UX Designer** (10 hrs/week): Design system and review
- **1 Accessibility Specialist** (5 hrs/week): Phase 2 consultation and audit
- **1 QA Engineer** (10 hrs/week): E2E test writing and validation

### Budget Estimate

| Phase | Development | Design | QA | Total Days |
|-------|-------------|--------|----|------------|
| Phase 1 | 5 | 1 | 1 | 7 |
| Phase 2 | 15 | 3 | 3 | 21 |
| Phase 3 | 30 | 5 | 5 | 40 |
| Phase 4 | 10 | 2 | 8 | 20 |
| **Total** | **60** | **11** | **17** | **88 days (~18 weeks at 5 days/week)** |

*Note: Can be compressed to ~12 weeks with dedicated full-time team*

## Documentation Plan

| Document | Location | When |
|----------|----------|------|
| Component Library | Storybook | Phase 2 |
| User Guide | docs/user-guide/ | Phase 4 |
| Keyboard Shortcuts | docs/keyboard-shortcuts.md | Phase 4 |
| API Documentation | docs/api/ | Ongoing |
| Deployment Guide | docs/deployment/ | Phase 4 |
| Accessibility Statement | docs/accessibility.md | Phase 4 |

## Validation Commands

### Development

```bash
# Install dependencies
uv sync

# Run development server
uv run python -m app.main

# Run with hot reload
APP_ENABLE_HOT_RELOAD=1 uv run python -m app.main
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run E2E tests
npx playwright test

# Run accessibility tests
npx axe . --exit
```

### Build

```bash
# Production build
npm run build

# Bundle analysis
npm run build:analyze

# Lighthouse audit
npx lighthouse http://localhost:3000 --view
```

### Deployment

```bash
# Build LangGraph container
uv run langgraph build -t kai-langgraph:latest

# Start full stack
docker compose -f docker-compose.langgraph.yml up -d

# Health check
curl http://localhost:8123/ok
```

## Notes

### Design Principles

1. **Data-First Priority**: Information hierarchy prioritizes data visibility over decorative elements
2. **Keyboard-Optimized**: Full keyboard navigation with visible shortcuts
3. **Progressive Disclosure**: Complex features revealed on-demand, reducing cognitive load
4. **Density Over Whitespace**: Analytic engineers prefer information-dense interfaces
5. **System Feedback**: Every action produces clear, immediate feedback
6. **Predictable Patterns**: Consistent interaction patterns across all surfaces
7. **Dark Mode Native**: Design for dark mode first, light mode secondary

### Target Persona: Analytic Engineers

- Technical users who value efficiency
- Prefer data visibility over decoration
- Heavy keyboard users
- Appreciate information density
- Need predictable patterns
- Value dark mode
- Want clear system feedback

### Brand Color: Deep Indigo (#6366f1)

- Professional and trustworthy
- Excellent contrast and accessibility
- Distinguishes from generic admin interfaces
- Appeals to technical users

---

## Checklist Summary

### Phase 1: Quick Wins 🟡
- [ ] P1-01: Remove console.logs from production
- [ ] P1-02: Add missing ARIA labels
- [ ] P1-03: Fix sidebar mobile responsiveness
- [ ] P1-04: Add loading states
- [ ] P1-05: Implement basic keyboard navigation
- [ ] P1-06: Add error boundaries
- [ ] P1-07: Fix inconsistent button styles
- [ ] P1-08: Add empty states with CTAs
- [ ] P1-09: Implement basic focus management

### Phase 2: Foundation ⬜
- [ ] P2-01: Create design token system
- [ ] P2-02: Build base component library
- [ ] P2-03: Implement dark/light mode toggle
- [ ] P2-04: Setup Storybook
- [ ] P2-05: Create brand color integration
- [ ] P2-06: Implement skip links and landmarks
- [ ] P2-07: Add live regions
- [ ] P2-08: Setup axe DevTools CI
- [ ] P2-09: Keyboard shortcut system
- [ ] P2-10: Focus trap implementation
- [ ] P2-11: Global error toast system
- [ ] P2-12: Add retry logic
- [ ] P2-13: Create error page components
- [ ] P2-14: Implement form validation
- [ ] P2-15: Add analytics tracking
- [ ] P2-16: Visual regression testing setup
- [ ] P2-17: Cross-browser testing setup
- [ ] P2-18: Mobile device testing setup

### Phase 3: Major Features ⬜
- [ ] P3-01: Redesign chat layout
- [ ] P3-02: Implement message streaming UI
- [ ] P3-03: Add SQL result tables with export
- [ ] P3-04: Create visualization card components
- [ ] P3-05: Implement chat search and filters
- [ ] P3-06: Add message actions
- [ ] P3-07: Redesign knowledge base list
- [ ] P3-08: Create knowledge base editor
- [ ] P3-09: Implement table browser
- [ ] P3-10: Add column details
- [ ] P3-11: Create scan wizard
- [ ] P3-12: Implement bulk table operations
- [ ] P3-13: Redesign settings
- [ ] P3-14: Create connection manager
- [ ] P3-15: Implement LLM configuration
- [ ] P3-16: Add danger zone
- [ ] P3-17: Implement route-based code splitting
- [ ] P3-18: Add virtual scrolling
- [ ] P3-19: Optimize bundle size
- [ ] P3-20: Add image optimization
- [ ] P3-21: Implement service worker
- [ ] P3-22: User flow validation with real browsers

### Phase 4: Polish ⬜
- [ ] P4-01: Add micro-interactions
- [ ] P4-02: Implement page transitions
- [ ] P4-03: Add skeleton loaders
- [ ] P4-04: Create empty state illustrations
- [ ] P4-05: Polish toast notifications
- [ ] P4-06: Add tooltips to truncated content
- [ ] P4-07: Implement command palette
- [ ] P4-08: Write unit tests (80% coverage)
- [ ] P4-09: Create E2E test suite
- [ ] P4-10: Run full accessibility audit
- [ ] P4-11: Document component library
- [ ] P4-12: Create user guide
- [ ] P4-13: Performance audit and optimization
- [ ] P4-14: Security review and fixes
- [ ] P4-15: Launch preparation checklist
- [ ] P4-16: Manual accessibility testing with real users
- [ ] P4-17: Production smoke tests with real browsers

**Legend:** 🟡 In Progress | ✅ Complete | ⬜ Pending | ❌ Blocked

## Compounded

- [x] Last compounded: 2026-02-09
- [x] ADRs created: 3
- [x] Solutions documented: 2
- [x] Deployment changes: 1
- [x] Patterns added: 10

**Generated Documents:**

### Architecture Decisions (ADRs)
- [docs/adr/adr-001-use-shadcn-ui-radix-ui-tailwind.md](../docs/adr/adr-001-use-shadcn-ui-radix-ui-tailwind.md) - Design system architecture
- [docs/adr/adr-002-zustand-for-client-state.md](../docs/adr/adr-002-zustand-for-client-state.md) - State management strategy
- [docs/adr/adr-003-nextjs-14-app-router-with-server-components.md](../docs/adr/adr-003-nextjs-14-app-router-with-server-components.md) - Framework choice

### Mistakes & Solutions
- [docs/solutions/ssr-issues/ssr-safe-theme-provider.md](../docs/solutions/ssr-issues/ssr-safe-theme-provider.md) - SSR-safe theme handling
- [docs/solutions/ssr-issues/useSearchParams-suspense-boundary.md](../docs/solutions/ssr-issues/useSearchParams-suspense-boundary.md) - Suspense boundary pattern

### Deployment
- [docs/deployment/launch-checklist.md](../docs/deployment/launch-checklist.md) - Updated with changelog and lessons learned

### Reusable Patterns
- SSR-safe browser API access
- useSearchParams() Suspense boundary pattern
- Provider component composition for client features
- Non-mutating array operations
- API client with type-safe methods
- Error boundary composition
- Design token integration with Tailwind
- Suspense for code splitting
- Type-safe environment variables
- Accessibility-first component design
