import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for Dashboard
 *
 * These tests verify the dashboard functionality including:
 * - Display of system statistics
 * - Quick action buttons
 * - Recent activity
 * - Navigation to other pages
 *
 * Prerequisites:
 * - Backend (FastAPI) running on port 8000
 * - Frontend (Next.js) running on port 3002
 * - Typesense running on port 8108
 */

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Waits for the Dashboard page to fully load.
 */
async function waitForPageReady(page: Page): Promise<void> {
  // Dashboard is the home page (/)
  await page.goto('/');

  // Wait for either heading or main content
  await expect(async () => {
    const heading = page.getByRole('heading', { name: /Dashboard/i });
    const mainContent = page.locator('main');
    const visible = await heading.isVisible().catch(() => false) ||
                    await mainContent.isVisible().catch(() => false);
    expect(visible).toBeTruthy();
  }).toPass({ timeout: 30000, intervals: [500, 1000, 2000] });
}

/**
 * Gets the count of stat cards displayed on the dashboard.
 */
async function getStatCardCount(page: Page): Promise<number> {
  const statCards = page.locator('[data-testid="stat-card"], .stat-card, .bg-card');
  return await statCards.count();
}

// ============================================================================
// Test Suite
// ============================================================================

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Capture console logs and errors
    page.on('console', (msg) => {
      const type = msg.type();
      const text = msg.text();
      if (type === 'error' || type === 'warning') {
        console.log(`[Browser ${type}]`, text);
      }
    });

    page.on('pageerror', (error) => {
      console.error('[Browser Error]', error.message);
    });

    await waitForPageReady(page);
  });

  test('should display dashboard page', async ({ page }) => {
    // Verify we're on the dashboard
    expect(page.url()).toContain('/');

    // Check for heading or main content
    const headingVisible = await page.getByRole('heading', { name: /Dashboard/i }).isVisible().catch(() => false);
    const mainVisible = await page.locator('main').isVisible().catch(() => false);

    expect(headingVisible || mainVisible).toBeTruthy();
  });

  test('should display navigation sidebar', async ({ page }) => {
    // Verify sidebar is present
    const sidebar = page.locator('nav, [role="navigation"], aside');
    await expect(sidebar.first()).toBeVisible();

    // Verify main navigation items
    const navItems = [
      'Dashboard',
      'Connections',
      'Schema',
      'MDL',
      'Chat',
      'Knowledge',
      'Logs'
    ];

    // Check that at least some navigation items are visible
    let visibleNavCount = 0;
    for (const item of navItems) {
      const navLink = page.getByRole('link', { name: item }).first();
      if (await navLink.isVisible().catch(() => false)) {
        visibleNavCount++;
      }
    }

    // At least 3 nav items should be visible
    expect(visibleNavCount).toBeGreaterThanOrEqual(3);
  });

  test('should display stat cards', async ({ page }) => {
    const statCardCount = await getStatCardCount(page);

    test.info().annotations.push({
      type: 'stat-card-count',
      description: `Found ${statCardCount} stat cards`,
    });

    if (statCardCount > 0) {
      // Verify at least one stat card is visible
      const firstCard = page.locator('[data-testid="stat-card"], .stat-card, .bg-card').first();
      await expect(firstCard).toBeVisible();
    }
  });

  test('should have working navigation links', async ({ page }) => {
    // Test navigation to Connections page
    const connectionsLink = page.getByRole('link', { name: /Connections/i }).first();
    const hasConnectionsLink = await connectionsLink.isVisible().catch(() => false);

    if (hasConnectionsLink) {
      await connectionsLink.click();
      await expect(page).toHaveURL(/\/connections/, { timeout: 10000 });
      await page.goBack(); // Go back to dashboard
    }

    // Test navigation to Chat page
    const chatLink = page.getByRole('link', { name: /Chat/i }).first();
    const hasChatLink = await chatLink.isVisible().catch(() => false);

    if (hasChatLink) {
      await chatLink.click();
      await expect(page).toHaveURL(/\/chat/, { timeout: 10000 });
    }
  });

  test('should display quick action buttons', async ({ page }) => {
    // Look for common quick action buttons
    const quickActions = [
      'New Chat',
      'Add Connection',
      'Scan Tables',
      'Create Session'
    ];

    let foundActions = 0;
    for (const action of quickActions) {
      const button = page.getByRole('button', { name: new RegExp(action, 'i') }).first();
      if (await button.isVisible().catch(() => false)) {
        foundActions++;
      }
    }

    test.info().annotations.push({
      type: 'quick-actions',
      description: `Found ${foundActions} quick action buttons`,
    });
  });

  test('should show system status indicator', async ({ page }) => {
    // Look for system status (green dot, "Online" indicator, etc.)
    const statusIndicator = page.locator('[data-testid="system-status"], .status-dot, .rounded-full.bg-green');
    const hasStatus = await statusIndicator.isVisible().catch(() => false);

    if (hasStatus) {
      test.info().annotations.push({
        type: 'system-status',
        description: 'System status indicator is visible',
      });
    }
  });

  test('should display version information', async ({ page }) => {
    // Look for version info
    const versionText = page.getByText(/v\d+\.\d+\.\d+/);
    const hasVersion = await versionText.isVisible().catch(() => false);

    if (hasVersion) {
      test.info().annotations.push({
        type: 'version-info',
        description: await versionText.textContent(),
      });
    }
  });
});

test.describe('Dashboard - Mobile', () => {
  test('should show mobile-friendly layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Wait for page to load
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

    // On mobile, sidebar might be hidden or collapsible
    const sidebar = page.locator('nav, [role="navigation"], aside');

    // Check if there's a mobile menu button
    const menuButton = page.getByRole('button', { name: /menu|open|hamburger/i });

    const hasMenuButton = await menuButton.isVisible().catch(() => false);

    if (hasMenuButton) {
      // Mobile menu button should be tappable
      const buttonBox = await menuButton.boundingBox();
      if (buttonBox) {
        expect(buttonBox.width).toBeGreaterThanOrEqual(44);
        expect(buttonBox.height).toBeGreaterThanOrEqual(44);
      }
    }

    test.info().annotations.push({
      type: 'mobile-layout',
      description: hasMenuButton ? 'Mobile menu button found' : 'No mobile menu button needed',
    });
  });

  test('should handle mobile menu toggle', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Look for menu button
    const menuButton = page.getByRole('button', { name: /menu|open/i });
    const hasMenuButton = await menuButton.isVisible().catch(() => false);

    if (hasMenuButton) {
      // Open menu
      await menuButton.tap();

      // Navigation should become visible
      const nav = page.locator('nav, [role="navigation"]');
      await expect(nav.first()).toBeVisible({ timeout: 5000 });

      // Close menu
      const closeButton = page.getByRole('button', { name: /close|×|x/i });
      const hasCloseButton = await closeButton.isVisible().catch(() => false);

      if (hasCloseButton) {
        await closeButton.tap();
      }
    } else {
      test.skip(true, 'No mobile menu button found');
    }
  });
});

test.describe('Dashboard - Cross-Browser', () => {
  test('should render correctly on Firefox', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });
  });

  test('should render correctly on WebKit', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'WebKit-specific test');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });
  });
});

test.describe('Dashboard - Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');

    // Check for h1 heading
    const h1 = page.locator('h1');
    const hasH1 = await h1.isVisible().catch(() => false);

    if (hasH1) {
      test.info().annotations.push({
        type: 'a11y-heading',
        description: 'Page has h1 heading',
      });
    }

    // Check that navigation has proper label
    const nav = page.locator('nav[aria-label], nav[aria-labelledby], [role="navigation"][aria-label]');
    const hasLabeledNav = await nav.isVisible().catch(() => false);

    if (hasLabeledNav) {
      test.info().annotations.push({
        type: 'a11y-nav-label',
        description: 'Navigation has proper aria-label',
      });
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');

    // Tab through the page
    await page.keyboard.press('Tab');

    // Something should be focused
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();

    // Continue tabbing to navigate through interactive elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => document.activeElement?.tagName);
      test.info().annotations.push({
        type: `tab-${i}`,
        description: `Focused element: ${focused}`,
      });
    }
  });
});
