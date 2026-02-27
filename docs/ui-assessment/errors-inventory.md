# KAI UI Errors Inventory

**Generated**: February 8, 2026
**Build**: kai-ui-revamp-assessment
**Synthesis of**: Visual Design, UX Research, Accessibility, and Technical Assessments

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Issues** | **73** |
| Critical Severity | 9 |
| High Severity | 24 |
| Medium Severity | 31 |
| Low Severity | 9 |

### By Category

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Visual Design | 3 | 4 | 18 | 6 | 31 |
| UX | 3 | 5 | 4 | 0 | 12 |
| Accessibility | 3 | 9 | 11 | 4 | 27 |
| Technical | 0 | 6 | 2 | 3 | 11 |

### By Affected Component

| Component | Issues |
|-----------|--------|
| Layout (Sidebar/Header) | 12 |
| Chat Page | 11 |
| Connections Page | 10 |
| Empty States (all) | 9 |
| Forms/Dialogs | 8 |
| Dashboard | 7 |
| Schema Page | 6 |
| Knowledge Page | 5 |
| MDL Page | 3 |
| Global/Styles | 2 |

---

## Critical Issues (Blockers)

*Issues that prevent core functionality or violate critical accessibility standards.*

### VIS-001: No Brand Color Identity
**Category**: Visual Design
**Severity**: Critical
**Source**: Visual Design Audit
**Location**: `ui/src/app/globals.css:14-66`

**Description**: The color palette is entirely grayscale with no brand color. The "primary" color is simply black/white variants.

**Impact**:
- No visual differentiation from competitors
- Missing opportunity for brand recognition
- Reduced visual hierarchy
- Generic "yet another admin panel" appearance

**Proposed Solution**: Introduce a signature brand color (deep blue, purple, or teal) for primary actions and accents.

**Effort**: Medium

---

### VIS-002: Weak Brand Presence
**Category**: Visual Design
**Severity**: Critical
**Source**: Visual Design Audit
**Location**: `ui/src/components/layout/sidebar.tsx:32-36`

**Description**: Only branding is small layered icon + "KAI_ADMIN" monospace text. Generic icon, no brand colors or patterns.

**Impact**: UI is visually indistinguishable from any other shadcn/ui admin panel.

**Proposed Solution**: 
1. Design custom logo or wordmark
2. Implement brand color palette
3. Consider subtle AI-themed visual elements (gradients, gentle animations)

**Effort**: High

---

### VIS-003: Mobile-Unresponsive Sidebar
**Category**: Visual Design
**Severity**: Critical
**Source**: Visual Design Audit
**Location**: `ui/src/components/layout/sidebar.tsx:30`

**Description**: Sidebar fixed at 256px width with no mobile adaptation - no collapse, drawer, or bottom nav.

**Impact**: Application breaks on mobile devices.

**Proposed Solution**:
1. Implement collapsible sidebar for desktop
2. Add mobile drawer or bottom navigation
3. Add hamburger menu for mobile

**Effort**: High

---

### UX-001: Chat Page Dead-End Empty State
**Category**: UX
**Severity**: Critical
**Source**: UX Research Audit
**Location**: `/chat` page

**Description**: Empty state shows "Select or create a session to start chatting" with no CTA, guidance, or visual direction.

**Impact**: Complete workflow blockage - users don't know how to proceed.

**Proposed Solution**: Create actionable empty state with "Create Session" CTA, brief explanation, and visual indicator pointing to connection selector.

**Effort**: Low

---

### UX-002: Knowledge Base Connection-Dependent Empty State Without Guidance
**Category**: UX
**Severity**: Critical
**Source**: UX Research Audit
**Location**: `/knowledge` page

**Description**: Empty state when no connections exist doesn't explain why connections are required or how to create them.

**Impact**: User confusion, unclear dependencies.

**Proposed Solution**: Add actionable guidance with "Create Connection" button that navigates to /connections page.

**Effort**: Low

---

### UX-003: Scan Dialog No Progress Indication
**Category**: UX
**Severity**: Critical
**Source**: UX Research Audit
**Location**: `/connections` → Scan Dialog

**Description**: No progress percentage, time estimate, or table count during AI scan. Button changes to "Scanning..." with no feedback.

**Impact**: For large databases (minutes-long scans), users perceive system as broken.

**Proposed Solution**: Implement progress tracking with table count, progress bar, and estimated time remaining.

**Effort**: Medium

---

### A11Y-001: Missing ARIA Labels on Icon-Only Buttons
**Category**: Accessibility
**Severity**: Critical
**Source**: Accessibility Audit
**Location**: Multiple components

**Description**: Icon-only buttons (sidebar links, session delete, close buttons) lack aria-label attributes.

**Impact**: Screen reader users cannot understand button purposes.

**Proposed Solution**: Add descriptive aria-label to all icon-only interactive elements.

**Effort**: Low

---

### A11Y-002: No Live Regions for Dynamic Content
**Category**: Accessibility
**Severity**: Critical
**Source**: Accessibility Audit
**Location**: Chat, Scan progress

**Description**: Chat messages and scan progress changes are not announced to screen readers. No aria-live regions.

**Impact**: Screen reader users miss real-time updates.

**Proposed Solution**: Wrap dynamic content in aria-live="polite" regions.

**Effort**: Low

---

### A11Y-003: No Semantic Landmarks
**Category**: Accessibility
**Severity**: Critical
**Source**: Accessibility Audit
**Location**: `ui/src/app/layout.tsx`

**Description**: No `<main>`, `<nav>`, `<aside>` landmarks in layout structure.

**Impact**: Screen reader users cannot navigate by regions.

**Proposed Solution**: Add semantic HTML5 landmarks to layout structure.

**Effort**: Medium

---

## High Priority Issues (Serious Impact)

*Issues that significantly impact user experience or accessibility compliance.*

### VIS-004: Inconsistent Hover States
**Category**: Visual Design
**Severity**: High
**Source**: Visual Design Audit
**Location**: Multiple components

**Description**: Different hover patterns across components (translate, shadow, bg color) create disjointed interaction feel.

**Proposed Solution**: Establish clear hover state patterns - navigational (bg + translate), cards (shadow + border), buttons (opacity/brightness).

**Effort**: Medium

---

### VIS-005: Weak Visual Hierarchy (Page Titles Too Small)
**Category**: Visual Design
**Severity**: High
**Source**: Visual Design Audit
**Location**: `ui/src/components/layout/header.tsx:30`

**Description**: Page titles use text-lg (1.125rem), only slightly larger than body text.

**Proposed Solution**: Use text-2xl or text-3xl for page titles.

**Effort**: Low

---

### VIS-006: Boring Empty States (No Illustrations)
**Category**: Visual Design
**Severity**: High
**Source**: Visual Design Audit
**Location**: Multiple pages

**Description**: Empty states use only text, no illustrations or visual interest.

**Proposed Solution**: Add illustrations or icons to empty states.

**Effort**: Medium

---

### VIS-007: Inconsistent Border Styles
**Category**: Visual Design
**Severity**: High
**Source**: Visual Design Audit
**Location**: Multiple components

**Description**: Mix of solid and dashed borders without system. Quick actions use dashed-to-solid transition unique to that component.

**Proposed Solution**: Use subtle solid borders consistently; reserve dashed for "add new" states only.

**Effort**: Low

---

### VIS-008: No Visual Differentiation from Generic Admin Panels
**Category**: Visual Design
**Severity**: High
**Source**: Visual Design Audit
**Location**: Throughout

**Description**: Heavy reliance on shadcn/ui defaults results in generic appearance. AI-powered features not reflected visually.

**Proposed Solution**: Consider subtle gradient accents, animated elements (pulses, glows), "AI" indicators with visual interest.

**Effort**: High

---

### UX-004: Session Sidebar Unclear Session Management
**Category**: UX
**Severity**: High
**Source**: UX Research Audit
**Location**: `/chat` → Session Sidebar

**Description**: Sessions show minimal information - no content/topic indication, no last activity timestamp, no connection badge.

**Proposed Solution**: Enhanced session cards with metadata (connection badge, last activity time).

**Effort**: Medium

---

### UX-005: Schema Page No Context on Empty Table Selection
**Category**: UX
**Severity**: High
**Source**: UX Research Audit
**Location**: `/schema` page

**Description**: "Select a table to view details" doesn't explain what information will be shown or which connection is selected.

**Proposed Solution**: Add context card explaining table details (columns, relationships, AI descriptions).

**Effort**: Low

---

### UX-006: Connection Deletion Unsafe Confirmation
**Category**: UX
**Severity**: High
**Source**: UX Research Audit
**Location**: `/connections` → Connection Table

**Description**: Uses browser confirm() dialog, doesn't show affected resources (MDL, knowledge, sessions), no undo.

**Proposed Solution**: Implement proper confirmation dialog showing cascading effects.

**Effort**: Medium

---

### UX-007: Dashboard Missing Quick Start for New Users
**Category**: UX
**Severity**: High
**Source**: UX Research Audit
**Location`: `/` (Dashboard)

**Description**: When no connections exist, no guidance on what to do first. Missing onboarding for first-time setup.

**Proposed Solution**: Add first-time user welcome card with "Get Started" CTA and explanation.

**Effort**: Low

---

### UX-008: Scan Progress No Visibility into Active Scans
**Category**: UX
**Severity**: High
**Source**: UX Research Audit
**Location**: `/connections` page

**Description**: During scan, badge shows "Scanning with AI..." with no progress details, table count, or cancel option.

**Proposed Solution**: Enhanced progress banner with table count, progress bar, current table, and cancel button.

**Effort**: Medium

---

### A11Y-004: No Skip Navigation Link
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `layout.tsx`

**Description**: No skip link to bypass sidebar for keyboard users.

**Proposed Solution**: Add "Skip to main content" link at top of page.

**Effort**: Low

---

### A11Y-005: Session List Lacks Proper List Semantics
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `session-sidebar.tsx`

**Description**: Session list not using `<ul>`/`<li>` structure.

**Proposed Solution**: Convert to semantic list structure.

**Effort**: Low

---

### A11Y-006: Table Scope Attributes Missing
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `connection-table.tsx`

**Description**: Table headers lack scope="col" attributes.

**Proposed Solution**: Add scope="col" to all table headers.

**Effort**: Low

---

### A11Y-007: Empty States Lack aria-live
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: Multiple pages

**Description**: Empty state messages not announced to screen readers.

**Proposed Solution**: Wrap empty states in aria-live regions.

**Effort**: Low

---

### A11Y-008: Chat Messages Lack ARIA Labels
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `agent-message.tsx`

**Description**: Messages lack aria-label or role attributes for screen readers.

**Proposed Solution**: Add appropriate ARIA attributes to message components.

**Effort**: Low

---

### A11Y-009: Missing Heading Hierarchy (No h1)
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: All pages

**Description**: No `<h1>` on pages - hierarchy starts at h2 or h3.

**Proposed Solution**: Ensure each page has exactly one `<h1>`.

**Effort**: Low

---

### A11Y-010: Nav Region Missing aria-label
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `sidebar.tsx`

**Description**: Navigation sidebar lacks aria-label.

**Proposed Solution**: Add aria-label="Main navigation" to sidebar.

**Effort**: Low

---

### A11Y-011: Main Content Not Properly Marked
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `layout.tsx`

**Description**: Main content area not wrapped in `<main>` landmark.

**Proposed Solution**: Wrap content in `<main>` element.

**Effort**: Low

---

### A11Y-012: Delete Button Only Visible on Hover
**Category**: Accessibility
**Severity**: High
**Source**: Accessibility Audit
**Location**: `session-sidebar.tsx`

**Description**: Delete button uses opacity-0 group-hover:opacity-100 pattern - invisible to keyboard navigation.

**Proposed Solution**: Remove hover-only visibility; make button always visible.

**Effort**: Low

---

### TECH-001: Console Logging in Production
**Category**: Technical
**Severity**: High
**Source**: Technical Assessment
**Location**: `chat-store.ts`

**Description**: Debug console.log statements present in production code.

**Impact**: Performance impact, potential information leakage.

**Proposed Solution**: Remove or conditionally compile (NODE_ENV === 'development').

**Effort**: Low

---

### TECH-002: Missing Error Boundaries
**Category**: Technical
**Severity**: High
**Source**: Technical Assessment
**Location**: Major routes

**Description**: Error boundary component exists but not consistently applied to routes.

**Impact**: Unhandled errors crash entire sections without graceful degradation.

**Proposed Solution**: Add error boundaries to each major route (chat, connections, schema, etc.).

**Effort**: Medium

---

### TECH-003: No Loading States for Queries
**Category**: Technical
**Severity**: High
**Source**: Technical Assessment
**Location**: Multiple components

**Description**: Many React Query queries don't have proper loading UI/skeletons.

**Impact**: Poor perceived performance, user uncertainty.

**Proposed Solution**: Implement consistent skeleton loading patterns using shadcn/ui Skeleton component.

**Effort**: Medium

---

### TECH-004: Zero Unit Test Coverage
**Category**: Technical
**Severity**: High
**Source**: Technical Assessment
**Location**: Test suite

**Description**: No unit tests configured (only E2E Playwright tests).

**Impact**: No regression prevention for component logic, hooks, utilities.

**Proposed Solution**: Set up Vitest + Testing Library for unit/component tests.

**Effort**: High

---

### TECH-005: Missing State Persistence
**Category**: Technical
**Severity**: High
**Source**: Technical Assessment
**Location**: Chat state

**Description**: Chat state not persisted to localStorage - sessions lost on refresh.

**Impact**: Poor user experience, data loss.

**Proposed Solution**: Add localStorage persistence middleware to Zustand chat store.

**Effort**: Medium

---

### TECH-006: No Bundle Size Monitoring
**Category**: Technical
**Severity**: High
**Source**: Technical Assessment
**Location**: Build configuration

**Description**: No bundle analysis or size limits configured.

**Impact**: Bundle size can grow untracked, performance degradation.

**Proposed Solution**: Add @next/bundle-analyzer and set size budgets.

**Effort**: Medium

---

## Medium Priority Issues

*Improvements for efficiency, polish, and compliance.*

### Visual Design (18 Medium Issues)

- VIS-009: Limited animation/motion - missing micro-interactions and page transitions
- VIS-010: Generic component styling - heavy shadcn/ui reliance
- VIS-011: Dark mode lacks atmosphere - purely functional, no depth
- VIS-012: Icon sizing inconsistency - mix of 16px and 20px
- VIS-013: Monospace font inconsistency - used arbitrarily
- VIS-014: Chart color misalignment - colors don't match theme
- VIS-015: Inconsistent card padding
- VIS-016: Tight spacing in sidebar navigation
- VIS-017: Border radius inconsistency - mix of values
- VIS-018: Stats card label readability - small + muted color
- VIS-019: Button hierarchy not strategic
- VIS-020: No loading state personality
- VIS-021: Limited visual feedback on actions
- VIS-022: Accent color underutilization
- VIS-023: Type scale lacks harmonious progression
- VIS-024: Line height and readability issues in long-form content
- VIS-025: Chart palette unused/wasted
- VIS-026: Logo proportion awkward

### UX (4 Medium Issues)

- UX-009: Chat input limited keyboard shortcuts documentation
- UX-010: MDL page empty state lacks value proposition context
- UX-011: Connection select dropdowns lack visual hierarchy
- UX-012: Generic error handling without actionable details

### Accessibility (11 Medium Issues)

- A11Y-013: Expandable tree lacks keyboard indicators
- A11Y-014: Tab key trapped in modal during scan
- A11Y-015: Muted foreground color contrast unverified
- A11Y-016: Status badge contrast unverified
- A11Y-017: Focus ring contrast needs verification
- A11Y-018: No focus restoration after modal close
- A11Y-019: Chat input auto-focus may interrupt
- A11Y-020: No focus trap in dialogs (unverified)
- A11Y-021: Button groups lack role="group"
- A11Y-022: Status indicators lack role="status"
- A11Y-023: Required fields not clearly indicated to screen readers

### Technical (2 Medium Issues)

- TECH-007: Component extraction needed - some components too complex
- TECH-008: No request debouncing on user input

---

## Low Priority Issues (Polish)

*Minor improvements and technical debt.*

### Visual Design (6 Low Issues)

- VIS-027: Various minor spacing inconsistencies
- VIS-028: Minor hover state refinements needed
- VIS-029: Dark mode temperature could be more distinct
- VIS-030: Shadow consistency improvements
- VIS-031: Minor animation timing adjustments
- VIS-032: Edge case visual fixes

### Accessibility (4 Low Issues)

- A11Y-024: Keyboard shortcuts not documented globally
- A11Y-025: Footer landmark missing
- A11Y-026: Form validation announcements not implemented
- A11Y-027: Select dropdowns need label verification

### Technical (3 Low Issues)

- TECH-009: Unused type alias (DatabaseConnection) to remove
- TECH-010: Some functions lack explicit return types
- TECH-011: Duplicate stores/ directory (lib/stores vs stores/)

---

## Quick Reference Index

### By Component

**Dashboard** (7 issues):
- VIS-005, VIS-006, VIS-018, VIS-019, UX-007, TECH-003, TECH-006

**Chat Page** (11 issues):
- VIS-021, UX-001, UX-004, UX-009, A11Y-002, A11Y-008, A11Y-013, A11Y-019, TECH-003, TECH-005

**Connections Page** (10 issues):
- UX-003, UX-006, UX-008, A11Y-006, A11Y-009, TECH-002, TECH-003

**Layout** (Sidebar/Header) (12 issues):
- VIS-002, VIS-003, VIS-016, A11Y-003, A11Y-004, A11Y-010, A11Y-011, TECH-003

**Forms/Dialogs** (8 issues):
- A11Y-009, A11Y-012, A11Y-020, A11Y-021, A11Y-023, A11Y-027

**Empty States** (9 issues):
- VIS-006, UX-001, UX-002, UX-005, UX-010, A11Y-007

**Schema Page** (6 issues):
- UX-005, A11Y-013

**Knowledge Page** (5 issues):
- UX-002, A11Y-027

**MDL Page** (3 issues):
- UX-010

**Global/Styles** (2 issues):
- VIS-001, VIS-004, A11Y-015

---

## Implementation Priority Matrix

| Priority | Issues | Est. Effort |
|----------|--------|-------------|
| **P1 - Critical** | 9 | 2-3 weeks |
| **P2 - High** | 24 | 4-6 weeks |
| **P3 - Medium** | 31 | 6-8 weeks |
| **P4 - Low** | 9 | 2-3 weeks |
| **Total** | **73** | **14-20 weeks** |

---

**End of Errors Inventory**

Next: See `aesthetic-direction.md` for design system recommendations and `implementation-roadmap.md` for phased execution plan.
