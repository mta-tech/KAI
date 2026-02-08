# Browser Testing Matrix

This document defines the browser and device testing strategy for the KAI UI application.

## Testing Targets

### Desktop Browsers (Priority Order)
1. **Chromium** (Chrome/Edge) - Primary testing target
   - Market share: ~65%
   - Most consistent behavior
   - Fastest test execution

2. **Firefox** - Secondary testing target
   - Market share: ~15%
   - Gecko rendering engine differences
   - Important for open-source users

3. **WebKit** (Safari) - Tertiary testing target
   - Market share: ~20%
   - WebKit rendering engine
   - Critical for Mac/iOS users

### Mobile Devices

#### iOS Devices (Safari)
- **iPhone 13** - Standard iPhone viewport (390x844)
- **iPad Pro** - Tablet viewport (1024x1366)
- **iPhone SE** - Small viewport (375x667) - Minimum supported size

#### Android Devices (Chrome)
- **Pixel 5** - Standard Android viewport (393x851)

## Test Projects

The Playwright configuration includes the following test projects:

| Project Name | Device | Viewport | Purpose |
|-------------|--------|----------|---------|
| chromium | Desktop Chrome | 1280x720 | Primary testing |
| firefox | Desktop Firefox | 1280x720 | Cross-browser compatibility |
| webkit | Desktop Safari | 1280x720 | Safari compatibility |
| Mobile Safari - iPhone | iPhone 13 | 390x844 | iOS mobile testing |
| Mobile Safari - iPad | iPad Pro | 1024x1366 | Tablet testing |
| Mobile Chrome - Android | Pixel 5 | 393x851 | Android mobile testing |
| Mobile Small | iPhone SE | 375x667 | Minimum viewport testing |

## Running Tests

### Run All Tests Across All Browsers
```bash
npm run test:e2e
```

### Run Tests on Specific Browser
```bash
# Chrome/Chromium only
npm run test:e2e:chromium

# Firefox only
npm run test:e2e:firefox

# Safari (WebKit) only
npm run test:e2e:webkit
```

### Run Mobile Tests
```bash
# All mobile devices
npm run test:e2e:mobile

# iOS only
npm run test:e2e:mobile-ios

# Android only
npm run test:e2e:mobile-android
```

### Debug Tests
```bash
# Run with headed mode and debugger
npm run test:e2e:debug

# Run with UI mode
npm run test:e2e:ui
```

## Test Coverage Strategy

### Priority 1: Chromium (Always)
- All E2E tests run on Chromium
- Fastest feedback loop during development
- Primary browser for most users

### Priority 2: Firefox & WebKit (Pre-commit/CI)
- Full test suite on Firefox and WebKit
- Catches cross-browser compatibility issues
- Runs before merging to main

### Priority 3: Mobile Devices (Pre-release)
- Mobile-specific tests on iOS and Android
- Responsive design validation
- Touch interaction testing

## Known Browser Differences

### Firefox
- May have different scroll behavior
- Flexbox/Grid rendering nuances
- Font rendering differences

### WebKit (Safari)
- Stricter CORS policies
- Different form validation behavior
- Unique scrollbar styling
- Touch event handling differences

### Mobile
- Viewport meta tag behavior
- Touch vs click event handling
- Virtual keyboard interactions
- Orientation change handling

## CI/CD Integration

### Local Development
Run Chromium only for fast feedback:
```bash
npm run test:e2e:chromium
```

### Pre-commit Hook
Run desktop browsers (Chromium, Firefox, WebKit):
```bash
npm run test:e2e --project=chromium --project=firefox --project=webkit
```

### Pre-deploy (CI)
Run full matrix including mobile:
```bash
npm run test:e2e
```

## Browser-Specific Test Patterns

### Testing Mobile Features
Use `test.describe.configure({ mode: 'serial' })` for mobile-specific tests:

```typescript
test.describe('Mobile Features', () => {
  test.describe.configure({ mode: 'serial' });

  test('should show mobile navigation on small screens', async ({ page }) => {
    // Test mobile-specific behavior
  });
});
```

### Testing Touch Interactions
```typescript
test('should handle tap events', async ({ page }) => {
  await page.tap('selector');
});
```

### Testing Orientation Changes
```typescript
test('should handle orientation change', async ({ page }) => {
  await page.setViewportSize({ width: 844, height: 390 });
  // Test landscape
});
```

## Troubleshooting

### Firefox-specific Issues
1. Check for geolocation permission prompts
2. Verify scroll handling
3. Test form validation

### WebKit-specific Issues
1. Check CORS headers
2. Verify form validation behavior
3. Test Safari-specific features

### Mobile Issues
1. Verify viewport meta tag
2. Test touch targets (minimum 44x44px)
3. Check virtual keyboard handling
4. Test orientation changes

## Future Enhancements

- Add visual regression testing with Percy or Chromatic
- Add accessibility testing with axe-core
- Add performance testing with Lighthouse
- Add network throttling for slow connection testing
- Add geolocation testing
- Add clipboard API testing

## References

- [Playwright Devices](https://playwright.dev/docs/emulation)
- [Playwright Test Configuration](https://playwright.dev/docs/test-configuration)
- [Mobile Testing Best Practices](https://playwright.dev/docs/emulation#devices)
