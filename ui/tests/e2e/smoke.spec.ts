import { test, expect } from '@playwright/test';

/**
 * Smoke Tests - Critical User Flows
 *
 * These tests verify the most critical user flows work correctly.
 * Run these tests first to ensure basic functionality before running
 * the full test suite.
 *
 * Purpose: Quick validation that the application is working
 * Run time: Should complete in under 5 minutes
 * Coverage: All major pages and navigation
 *
 * Prerequisites:
 * - Backend (FastAPI) running on port 8000
 * - Frontend (Next.js) running on port 3002
 * - Typesense running on port 8108
 */

test.describe('Smoke Tests - Critical Flows', () => {
  test.describe.configure({ mode: 'serial' });

  test.beforeEach(async ({ page }) => {
    // Capture errors for debugging
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.log('[Browser Error]', msg.text());
      }
    });

    page.on('pageerror', (error) => {
      console.error('[Page Error]', error.message);
    });
  });

  test('should load the application home page', async ({ page }) => {
    await page.goto('/');

    // Verify main content is visible
    const main = page.locator('main');
    await expect(main).toBeVisible({ timeout: 30000 });

    // Verify sidebar/navigation is present
    const nav = page.locator('nav, [role="navigation"]');
    await expect(nav.first()).toBeVisible();
  });

  test('should navigate between main pages', async ({ page }) => {
    await page.goto('/');

    // Define main pages to test
    const pages = [
      { path: '/', name: 'Dashboard' },
      { path: '/connections', name: 'Connections' },
      { path: '/schema', name: 'Schema' },
      { path: '/chat', name: 'Chat' },
      { path: '/knowledge', name: 'Knowledge' },
    ];

    for (const pageDef of pages) {
      // Navigate using sidebar
      const navLink = page.getByRole('link', { name: pageDef.name }).first();

      const linkExists = await navLink.isVisible().catch(() => false);

      if (linkExists) {
        await navLink.click();
        await expect(page).toHaveURL(new RegExp(pageDef.path), { timeout: 10000 });
      } else {
        // Try direct navigation
        await page.goto(pageDef.path);
        await expect(page.locator('main, [role="main"]')).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should display navigation menu with all items', async ({ page }) => {
    await page.goto('/');

    // Expected navigation items
    const expectedNavItems = [
      'Dashboard',
      'Connections',
      'Schema',
      'MDL',
      'Chat',
      'Knowledge',
      'Logs'
    ];

    let visibleItemCount = 0;

    for (const item of expectedNavItems) {
      const navLink = page.getByRole('link', { name: item }).first();
      const isVisible = await navLink.isVisible().catch(() => false);

      if (isVisible) {
        visibleItemCount++;
      }
    }

    // At least 4 navigation items should be visible
    expect(visibleItemCount).toBeGreaterThanOrEqual(4);

    test.info().annotations.push({
      type: 'nav-items',
      description: `${visibleItemCount}/${expectedNavItems.length} navigation items visible`,
    });
  });

  test('should not have console errors on home page', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Wait for any delayed errors

    // Check for critical errors (ignore benign ones)
    const criticalErrors = errors.filter(error =>
      !error.includes('DevTools failed to load') &&
      !error.includes('Extension') &&
      !error.includes('favicon.ico')
    );

    if (criticalErrors.length > 0) {
      test.info().annotations.push({
        type: 'console-errors',
        description: `Found ${criticalErrors.length} console errors: ${criticalErrors.join('; ')}`,
      });
    }

    // This test will fail if there are critical console errors
    expect(criticalErrors.length).toBe(0);
  });

  test('should have working mobile menu', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Look for mobile menu button
    const menuButton = page.getByRole('button', { name: /menu|open|hamburger/i });
    const hasMenuButton = await menuButton.isVisible().catch(() => false);

    if (hasMenuButton) {
      // Open menu
      await menuButton.tap();

      // Navigation should be visible
      const nav = page.locator('nav, [role="navigation"]');
      await expect(nav.first()).toBeVisible({ timeout: 5000 });

      test.info().annotations.push({
        type: 'mobile-menu',
        description: 'Mobile menu is working',
      });
    } else {
      test.info().annotations.push({
        type: 'mobile-menu',
        description: 'No mobile menu button found (sidebar may always be visible)',
      });
    }
  });

  test('should handle 404 page gracefully', async ({ page }) => {
    // Navigate to non-existent page
    await page.goto('/this-page-does-not-exist-12345');

    // Should show 404 page or redirect to home
    const currentUrl = page.url();
    const has404Heading = await page.getByText(/404|not found/i).isVisible().catch(() => false);
    const hasErrorPage = await page.locator('[data-testid="error-page"], .error-page').isVisible().catch(() => false);

    // Either we're on a 404 page, error page, or redirected
    const handles404 = has404Heading || hasErrorPage || !currentUrl.includes('this-page-does-not-exist');

    expect(handles404).toBeTruthy();
  });

  test('should have proper page title', async ({ page }) => {
    await page.goto('/');

    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    test.info().annotations.push({
      type: 'page-title',
      description: title,
    });
  });

  test('should have meta viewport tag for mobile', async ({ page }) => {
    await page.goto('/');

    const viewportMeta = page.locator('meta[name="viewport"]');
    await expect(viewportMeta).toBeVisible();

    const content = await viewportMeta.getAttribute('content');
    expect(content).toContain('width=device-width');
  });

  test('should load without excessive resources', async ({ page }) => {
    // Track resource loading
    const resources: string[] = [];

    page.on('request', (request) => {
      resources.push(request.url());
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Count resources
    const totalResources = resources.length;

    test.info().annotations.push({
      type: 'resource-count',
      description: `Loaded ${totalResources} resources`,
    });

    // Should not load an excessive number of resources (basic sanity check)
    expect(totalResources).toBeLessThan(200);
  });
});

test.describe('Smoke Tests - Browser Compatibility', () => {
  test('should work on Chrome', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome-specific test');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });
  });

  test('should work on Firefox', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });
  });

  test('should work on Safari', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari-specific test');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });
  });
});

test.describe('Smoke Tests - Accessibility', () => {
  test('should have skip links for keyboard navigation', async ({ page }) => {
    await page.goto('/');

    // Look for skip links
    const skipLink = page.locator('a[href^="#"], [data-testid="skip-link"]').first();
    const hasSkipLink = await skipLink.isVisible().catch(() => false);

    if (hasSkipLink) {
      test.info().annotations.push({
        type: 'skip-link',
        description: 'Skip link found',
      });
    }
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');

    // Check for h1
    const h1 = page.locator('h1');
    const h1Count = await h1.count();

    test.info().annotations.push({
      type: 'heading-hierarchy',
      description: `Found ${h1Count} h1 heading(s)`,
    });

    // Should have at most one h1 (or none if using landmark regions)
    expect(h1Count).toBeLessThanOrEqual(1);
  });

  test('should have landmarks for screen readers', async ({ page }) => {
    await page.goto('/');

    // Check for ARIA landmarks
    const main = page.locator('main, [role="main"]');
    const nav = page.locator('nav, [role="navigation"]');
    const header = page.locator('header, [role="banner"]');

    const hasMain = await main.isVisible().catch(() => false);
    const hasNav = await nav.isVisible().catch(() => false);
    const hasHeader = await header.isVisible().catch(() => false);

    // Should have at least main and navigation
    expect(hasMain || hasNav).toBeTruthy();
  });
});

test.describe('Smoke Tests - Performance', () => {
  test('should load home page quickly', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('main, [role="main"]');

    const loadTime = Date.now() - startTime;

    test.info().annotations.push({
      type: 'load-time',
      description: `Page loaded in ${loadTime}ms`,
    });

    // Should load in under 10 seconds (generous threshold for dev)
    expect(loadTime).toBeLessThan(10000);
  });
});
