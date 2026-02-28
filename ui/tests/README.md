# KAI UI Testing Guide

This guide covers the complete testing setup for the KAI UI application, including E2E testing, cross-browser testing, and mobile device testing.

## Quick Start

### Run All Tests (All Browsers & Devices)
```bash
npm run test:e2e
```

### Run Tests on Specific Browser
```bash
npm run test:e2e:chromium    # Chrome/Edge (fastest)
npm run test:e2e:firefox     # Firefox
npm run test:e2e:webkit      # Safari
```

### Run Mobile Tests
```bash
npm run test:e2e:mobile           # All mobile devices
npm run test:e2e:mobile-ios       # iOS (iPhone/iPad)
npm run test:e2e:mobile-android   # Android
```

### Debug Tests
```bash
npm run test:e2e:ui        # Interactive UI mode
npm run test:e2e:debug     # Step-by-step debugging
npm run test:e2e:headed    # Run with visible browser
```

### Visual Regression Tests
```bash
npm run test:visual        # Run Chromatic visual tests locally
npm run test:visual:ci     # Run Chromatic in CI mode
```

### Production Smoke Tests
```bash
# Run against staging
BASE_URL=https://staging.example.com npm run test:e2e --grep "Production Smoke"

# Run against production
BASE_URL=https://app.example.com npm run test:e2e --grep "Production Smoke"
```

## Testing Stack

| Tool | Purpose | Documentation |
|------|---------|---------------|
| **Playwright** | E2E testing framework | [docs](https://playwright.dev) |
| **Vitest** | Unit testing | [docs](https://vitest.dev) |
| **Storybook** | Component testing & visual regression | [docs](https://storybook.js.org) |
| **Chromatic** | Visual regression testing (via Storybook) | [docs](https://www.chromatic.com) |

## Test Structure

```
ui/
├── tests/
│   ├── e2e/                    # Playwright E2E tests
│   │   ├── smoke.spec.ts       # Smoke tests (critical flows)
│   │   ├── dashboard.spec.ts   # Dashboard page tests
│   │   ├── connections.spec.ts # Connection management tests
│   │   ├── schema.spec.ts      # Schema browser tests
│   │   ├── chat-query.spec.ts  # Chat functionality tests
│   │   ├── knowledge.spec.ts   # Knowledge base tests
│   │   ├── settings.spec.ts    # Settings page tests
│   │   ├── user-flows.spec.ts  # User flow validation tests
│   │   └── production-smoke.spec.ts  # Production smoke tests
│   └── README.md               # This file
├── playwright.config.ts        # Playwright configuration
├── BROWSER_TESTING_MATRIX.md   # Cross-browser testing guide
└── MOBILE_TESTING_GUIDE.md     # Mobile testing patterns
```

## Browser & Device Coverage

### Desktop Browsers
| Browser | Project Name | Priority |
|---------|--------------|----------|
| Chrome/Edge | `chromium` | Primary (fastest) |
| Firefox | `firefox` | Secondary |
| Safari | `webkit` | Tertiary |

### Mobile Devices
| Device | Project Name | Viewport | Platform |
|--------|--------------|----------|----------|
| iPhone 13 | `Mobile Safari - iPhone` | 390x844 | iOS |
| iPad Pro | `Mobile Safari - iPad` | 1024x1366 | iOS |
| Pixel 5 | `Mobile Chrome - Android` | 393x851 | Android |
| iPhone SE | `Mobile Small` | 375x667 | iOS (min) |

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    // Arrange
    await page.goto('/chat');

    // Act
    await page.getByRole('button', { name: 'Submit' }).click();

    // Assert
    await expect(page.getByText('Success')).toBeVisible();
  });
});
```

### Mobile-Specific Tests

```typescript
test.describe('Mobile Features', () => {
  test('should show mobile menu on small screens', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Test mobile-specific behavior
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
  });
});
```

### Touch Interactions

```typescript
test('should handle tap events', async ({ page }) => {
  // Use tap for mobile instead of click
  await page.tap('button[type="submit"]');
});
```

### Helper Functions

The test suite includes reusable helper functions in `chat-query.spec.ts`:

```typescript
// Select a connection
await selectConnection(page, 'koperasi');

// Create a new session
await createNewSession(page);

// Submit a query
await submitQuery(page, 'What is the count?');

// Submit and wait for response
const { responseText } = await submitQueryAndWaitForResponse(page, query);
```

## Test Suites

### Smoke Tests (`smoke.spec.ts`)
**Purpose**: Quick validation of critical user flows
**Run Time**: ~2-3 minutes
**Tests**:
- Application home page loads
- Navigation between main pages
- Mobile menu functionality
- Console error detection
- 404 page handling
- Browser compatibility (Chrome, Firefox, Safari)
- Basic accessibility checks
- Performance baseline

**When to run**: Before committing code, as a quick sanity check

### Dashboard Tests (`dashboard.spec.ts`)
**Purpose**: Validate dashboard functionality
**Tests**:
- Dashboard page rendering
- Navigation sidebar
- Stat cards display
- Quick action buttons
- System status indicator
- Mobile layout
- Keyboard navigation

### Connection Tests (`connections.spec.ts`)
**Purpose**: Test database connection management
**Tests**:
- Connection list display
- Add connection dialog
- Connection form validation
- Connection status indicators
- Test connection functionality
- Empty state handling
- Search/filter connections

### Schema Tests (`schema.spec.ts`)
**Purpose**: Validate schema browsing functionality
**Tests**:
- Schema page loading
- Table list display
- Column details view
- Search/filter tables
- Table relationships

### Chat Tests (`chat-query.spec.ts`)
**Purpose**: Test chat/query functionality
**Tests**:
- Connection selection
- Session creation
- Query submission
- Response validation
- Streaming indicators
- Multiple queries in session
- Session switching

### Knowledge Tests (`knowledge.spec.ts`)
**Purpose**: Test knowledge base management
**Tests**:
- Instructions tab
- Add/edit/delete instructions
- Default instruction handling
- Form validation
- Empty states

### Settings Tests (`settings.spec.ts`)
**Purpose**: Test settings and configuration
**Tests**:
- Settings page display
- Settings sections
- Form inputs
- Save/apply functionality
- Settings persistence

### User Flow Tests (`user-flows.spec.ts`)
**Purpose**: Validate complete user journeys from end-to-end
**Tests**:
- Flow 1: New user first time experience
- Flow 2: Analyze data query (core use case)
- Flow 3: Knowledge base management
- Flow 4: Settings configuration
- Flow 5: Multi-page navigation
- Flow 6: Mobile user journey
- Flow 7: Error recovery
- Flow 8: Session persistence
- Cross-browser flow validation
- Performance flow validation

**When to run**: Before releases, after major changes, with real browsers

## Test Best Practices

### 1. Use Data Test IDs
```html
<button data-testid="submit-button">Submit</button>
```
```typescript
await page.getByTestId('submit-button').click();
```

### 2. Wait for Elements Properly
```typescript
// Good - waits for element to be visible
await expect(page.getByText('Loaded')).toBeVisible();

// Bad - arbitrary timeout
await page.waitForTimeout(5000);
```

### 3. Use Role-Based Selectors
```typescript
// Accessible and semantic
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByLabel('Email').fill('test@example.com');
```

### 4. Test User Flows, Not Implementation
```typescript
// Good - tests what the user sees
await expect(page.getByText('Success')).toBeVisible();

// Bad - tests internal state
expect(await page.evaluate(() => window.localStorage.getItem('token'))).toBeTruthy();
```

## CI/CD Integration

### Local Development
Run Chromium only for fast feedback:
```bash
npm run test:e2e:chromium
```

### Pre-commit Hook
Run desktop browsers:
```bash
npm run test:e2e --project=chromium --project=firefox --project=webkit
```

### CI Pipeline
Run full matrix:
```bash
npm run test:e2e
```

## Debugging Failed Tests

### View Test Reports
```bash
# HTML report
npm run test:e2e
open playwright-report/index.html

# View last test results
npx playwright show-report
```

### Debug Mode
```bash
# Run with debugger
npm run test:e2e:debug

# Run with UI mode (step through tests)
npm run test:e2e:ui
```

### Screenshots & Traces
Failed tests automatically capture:
- Screenshots (`test-results/`)
- Trace files (for debugging)
- Video recordings (if configured)

## Known Issues & Troubleshooting

### Firefox-specific
- Geolocation permission prompts may appear
- Different scroll behavior than Chrome
- Stricter form validation

### Safari (WebKit) Issues
- CORS policies are stricter
- Different scrollbar styling
- Unique touch event handling

### Mobile Issues
- Virtual keyboard can hide content
- Orientation changes may cause layout shifts
- Touch targets must be 44x44px minimum

## Test Coverage Goals

| Test Type | Current Coverage | Goal |
|-----------|------------------|------|
| E2E Tests | ✅ 7 test suites covering all major flows | All critical paths |
| Cross-Browser | ✅ Chrome, Firefox, Safari configured | All major browsers |
| Mobile | ✅ iOS, Android configured | All mobile devices |
| Visual Regression | ⏳ Not yet implemented (Task #34) | Component library |

## Future Testing Enhancements

- [ ] Visual regression testing with Chromatic (Task #34)
- [ ] User flow validation (Task #58)
- [ ] Accessibility testing with axe-core
- [ ] Performance testing with Lighthouse
- [ ] Network throttling tests
- [ ] Geolocation testing
- [ ] Manual accessibility testing (Task #74)
- [ ] Production smoke tests (Task #75)

## Additional Documentation

- **Browser Testing Matrix**: `BROWSER_TESTING_MATRIX.md` - Detailed browser testing strategy
- **Mobile Testing Guide**: `MOBILE_TESTING_GUIDE.md` - Mobile-specific test patterns
- **Playwright Config**: `playwright.config.ts` - Test configuration
- **Existing Tests**: `tests/e2e/` - Example tests to reference

## Getting Help

1. Check existing tests for patterns
2. Refer to Playwright documentation: https://playwright.dev
3. Review the browser testing matrix for cross-browser issues
4. Check mobile testing guide for device-specific patterns

## Running Tests in Different Contexts

### Docker/CI Environment
```bash
# Install browsers
npx playwright install --with-deps

# Run tests
npm run test:e2e
```

### With Backend Running
The Playwright config automatically starts the dev server. If you have it running:
```bash
# Set env to skip server start
EXISTING_SERVER=true npm run test:e2e
```

### Against Staging/Production
```bash
# Override base URL
BASE_URL=https://staging.example.com npm run test:e2e
```
