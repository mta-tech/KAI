# Mobile Testing Guide

This guide covers mobile device testing strategies for the KAI UI application.

## Mobile Test Configuration

The Playwright configuration includes the following mobile device emulations:

| Device | Viewport | User Agent | Purpose |
|--------|----------|------------|---------|
| iPhone 13 | 390x844 | Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) | Standard iOS testing |
| iPad Pro | 1024x1366 | Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) | Tablet testing |
| Pixel 5 | 393x851 | Mozilla/5.0 (Linux; Android 11) | Standard Android testing |
| iPhone SE | 375x667 | Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) | Minimum viewport testing |

## Mobile-Specific Test Patterns

### 1. Responsive Navigation Testing

```typescript
test.describe('Mobile Navigation', () => {
  test('should show hamburger menu on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Mobile menu button should be visible
    const menuButton = page.getByRole('button', { name: /menu/i });
    await expect(menuButton).toBeVisible();
  });

  test('should open sidebar when menu is tapped', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Tap menu button
    await page.tap('[data-testid="mobile-menu-button"]');

    // Sidebar should be visible
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toBeVisible();
  });
});
```

### 2. Touch Interaction Testing

```typescript
test.describe('Touch Interactions', () => {
  test('should handle tap events correctly', async ({ page }) => {
    await page.goto('/chat');

    // Use tap instead of click for mobile
    const sendButton = page.getByRole('button', { name: /send/i });
    await page.tap(sendButton);
  });

  test('should handle pinch to zoom (if applicable)', async ({ page }) => {
    await page.goto('/visualization');

    // Pinch zoom gesture
    await page.touchscreen.tap(100, 100);
    // Note: Actual pinch zoom requires more complex gesture handling
  });
});
```

### 3. Virtual Keyboard Testing

```typescript
test.describe('Virtual Keyboard', () => {
  test('should handle virtual keyboard appearance', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/chat');

    // Focus on input field
    const input = page.getByPlaceholder(/Ask a question/i);
    await input.tap();

    // Wait for keyboard to appear (viewport may shrink)
    // Most mobile browsers reduce viewport height when keyboard appears
    await page.waitForTimeout(500);

    // Input should still be visible
    await expect(input).toBeVisible();
  });

  test('should scroll input into view when keyboard appears', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/chat');

    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Focus input
    const input = page.getByPlaceholder(/Ask a question/i);
    await input.tap();

    // Input should be visible even with keyboard
    await expect(input).toBeInViewport();
  });
});
```

### 4. Orientation Change Testing

```typescript
test.describe('Orientation Changes', () => {
  test('should handle portrait to landscape rotation', async ({ page }) => {
    // Start in portrait
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Rotate to landscape
    await page.setViewportSize({ width: 667, height: 375 });

    // Layout should adjust
    const content = page.locator('main');
    await expect(content).toBeVisible();
  });

  test('should maintain state during rotation', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/chat');

    // Create a session
    await page.getByRole('button', { name: /New Session/i }).tap();

    // Rotate
    await page.setViewportSize({ width: 667, height: 375 });

    // Session should still be active
    const chatInput = page.getByPlaceholder(/Ask a question/i);
    await expect(chatInput).toBeVisible();
  });
});
```

### 5. Swipe Gesture Testing

```typescript
test.describe('Swipe Gestures', () => {
  test('should handle swipe to close sidebar', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Open sidebar
    await page.tap('[data-testid="mobile-menu-button"]');

    // Swipe from left edge to close
    await page.touchscreen.tap(50, 300);
    await page.touchscreen.tap(300, 300);

    // Sidebar should close
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).not.toBeVisible();
  });
});
```

## Mobile-Specific Assertions

### Touch Target Size (WCAG 2.5.5)

```typescript
test('should have adequate touch targets', async ({ page }) => {
  await page.goto('/');

  // All interactive elements should be at least 44x44 CSS pixels
  const buttons = await page.locator('button, a, [role="button"]').all();

  for (const button of buttons) {
    const box = await button.boundingBox();
    if (box) {
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
    }
  }
});
```

### Text Readability

```typescript
test('should have readable text on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/');

  // Body text should be at least 16px to prevent iOS zoom
  const bodyStyles = await page.locator('body').evaluate((el) => {
    const styles = window.getComputedStyle(el);
    return {
      fontSize: styles.fontSize,
      lineHeight: styles.lineHeight,
    };
  });

  expect(parseInt(bodyStyles.fontSize)).toBeGreaterThanOrEqual(16);
});
```

### Viewport Meta Tag

```typescript
test('should have correct viewport meta tag', async ({ page }) => {
  await page.goto('/');

  const viewportMeta = page.locator('meta[name="viewport"]');
  const content = await viewportMeta.getAttribute('content');

  expect(content).toContain('width=device-width');
  expect(content).toContain('initial-scale=1');
});
```

## Mobile Performance Testing

### Network Throttling

```typescript
test.describe('Mobile Performance', () => {
  test('should load quickly on slow mobile connections', async ({ page }) => {
    // Simulate slow 3G connection
    await page.route('**/*', (route) => {
      route.continue({
        // Throttle to 3G speeds: 1.6 Mbps down, 750 Kbps up, 100ms RTT
        latency: 100,
      });
    });

    const startTime = Date.now();
    await page.goto('/');
    const loadTime = Date.now() - startTime;

    // Page should load in under 5 seconds even on 3G
    expect(loadTime).toBeLessThan(5000);
  });
});
```

## Running Mobile Tests

### All Mobile Devices
```bash
npm run test:e2e:mobile
```

### iOS Only
```bash
npm run test:e2e:mobile-ios
```

### Android Only
```bash
npm run test:e2e:mobile-android
```

### Specific Device
```bash
npx playwright test --project="Mobile Safari - iPhone"
```

## Mobile Testing Checklist

- [ ] Navigation works on mobile viewport
- [ ] Touch targets are minimum 44x44px
- [ ] Text is readable without zoom (min 16px)
- [ ] Virtual keyboard doesn't hide important content
- [ ] Orientation changes are handled gracefully
- [ ] Swipe gestures work as expected
- [ ] Performance is acceptable on slow connections
- [ ] Forms work with virtual keyboard
- [ ] Scroll behavior is natural
- [ ] All interactive elements are accessible via touch

## Known Mobile Browser Issues

### iOS Safari
- `position: fixed` elements can behave oddly during scrolling
- Virtual keyboard can cause layout shifts
- 100vh includes the address bar (use 100dvh instead)
- Back/forward cache can cause state issues

### Android Chrome
- Different touch event behavior
- Virtual keyboard handling varies by Android version
- Address bar behavior differs from iOS

### Solutions

Use CSS dynamic viewport units for mobile:
```css
height: 100dvh; /* Dynamic viewport height */
```

Handle virtual keyboard:
```typescript
// Detect keyboard appearance
const visualViewport = window.visualViewport;
visualViewport?.addEventListener('resize', () => {
  // Keyboard appeared/disappeared
});
```

## References

- [Playwright Mobile Emulation](https://playwright.dev/docs/emulation#devices)
- [WCAG 2.5.5: Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [Mobile Web Best Practices](https://web.dev/mobile/)
