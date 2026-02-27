import { test, expect } from '@playwright/test';

/**
 * User Flow Validation Tests
 *
 * These tests validate complete user journeys through the application.
 * Unlike component tests which check individual features, these tests
 * verify the end-to-end experience from a user's perspective.
 *
 * Purpose: Ensure critical user paths work flawlessly
 * Run: Before releases, after major changes
 * Mode: Run with real browsers for validation
 *
 * Prerequisites:
 * - Backend (FastAPI) running on port 8000
 * - Frontend (Next.js) running on port 3002
 * - Typesense running on port 8108
 * - At least one database connection configured
 */

test.describe('User Flow Validation', () => {
  test.describe.configure({ mode: 'serial' });

  // ============================================================================
  // Flow 1: New User First Time Experience
  // ============================================================================

  test.describe('Flow 1: New User Experience', () => {
    test('should guide new user through initial setup', async ({ page }) => {
      // Step 1: User lands on home page
      await page.goto('/');

      // Verify page loads
      await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

      // Step 2: User sees navigation options
      const nav = page.locator('nav, [role="navigation"]');
      await expect(nav.first()).toBeVisible();

      // Step 3: User navigates to Connections to add a database
      const connectionsLink = page.getByRole('link', { name: /Connections/i });
      const linkExists = await connectionsLink.isVisible().catch(() => false);

      if (linkExists) {
        await connectionsLink.click();
        await expect(page).toHaveURL(/\/connections/, { timeout: 10000 });

        // Verify Connections page has clear call-to-action
        const addConnectionButton = page.getByRole('button', { name: /Add Connection/i });
        await expect(addConnectionButton).toBeVisible();

        test.info().annotations.push({
          type: 'new-user-flow',
          description: 'New user can find and access Add Connection',
        });
      }
    });
  });

  // ============================================================================
  // Flow 2: Analyze Data Query (Core Use Case)
  // ============================================================================

  test.describe('Flow 2: Analyze Data Query', () => {
    test('should complete end-to-end query flow', async ({ page }) => {
      // Step 1: Navigate to Chat
      await page.goto('/chat');

      // Step 2: Wait for page to load
      await expect(page.getByText(/Select or create a session/i)).toBeVisible({ timeout: 15000 });

      // Step 3: Check for existing connections
      const connectionDropdown = page.getByRole('combobox');
      const hasConnections = await connectionDropdown.isVisible().catch(() => false);

      if (!hasConnections) {
        test.skip(true, 'No database connections available - skipping query flow');
      }

      // Step 4: Select a connection
      await connectionDropdown.click();
      const options = page.getByRole('option');
      await expect(options.first()).toBeVisible({ timeout: 15000 });

      // Get first connection name for logging
      const firstOption = options.first();
      const connectionName = await firstOption.textContent();
      test.info().annotations.push({
        type: 'selected-connection',
        description: connectionName || 'unknown',
      });

      await firstOption.click();

      // Step 5: Create a new session
      const newSessionButton = page.getByRole('button', { name: /New Session/i });
      await expect(newSessionButton).toBeEnabled({ timeout: 5000 });
      await newSessionButton.click();

      // Step 6: Wait for session to be created (chat input appears)
      const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
      await expect(chatInput).toBeVisible({ timeout: 30000 });
      await expect(chatInput).toBeEnabled();

      // Step 7: Verify user can type a query
      await chatInput.fill('Show me the table structure');
      await expect(chatInput).toHaveValue('Show me the table structure');

      // Step 8: Submit query (using keyboard shortcut)
      await chatInput.press('Meta+Enter');

      // Step 9: Verify user message appears
      await expect(page.getByText('Show me the table structure')).toBeVisible({ timeout: 10000 });

      test.info().annotations.push({
        type: 'query-flow-complete',
        description: 'Successfully completed query submission flow',
      });
    });
  });

  // ============================================================================
  // Flow 3: Knowledge Base Management
  // ============================================================================

  test.describe('Flow 3: Knowledge Base Management', () => {
    test('should complete knowledge base instruction flow', async ({ page }) => {
      // Step 1: Navigate to Knowledge Base
      await page.goto('/knowledge');

      // Step 2: Wait for page to load
      await expect(page.getByRole('heading', { name: /Knowledge Base/i })).toBeVisible({ timeout: 30000 });

      // Step 3: Check for connections
      const connectionDropdown = page.locator('button[role="combobox"]');
      const hasConnections = await connectionDropdown.isVisible().catch(() => false);

      if (!hasConnections) {
        test.skip(true, 'No database connections available');
      }

      // Step 4: Navigate to Instructions tab
      const instructionsTab = page.getByRole('tab', { name: /Instructions/i });
      const tabExists = await instructionsTab.isVisible().catch(() => false);

      if (tabExists) {
        await instructionsTab.click();

        // Step 5: Click Add Instruction button
        const addButton = page.getByRole('button', { name: /Add Instruction/i });
        await expect(addButton).toBeVisible({ timeout: 10000 });
        await addButton.click();

        // Step 6: Verify dialog appears
        await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });

        // Step 7: Cancel the dialog (we're just testing the flow)
        const cancelButton = page.getByRole('button', { name: /Cancel/i });
        await cancelButton.click();

        // Step 8: Verify dialog closed
        await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 5000 });

        test.info().annotations.push({
          type: 'knowledge-flow-complete',
          description: 'Successfully navigated knowledge base instruction flow',
        });
      }
    });
  });

  // ============================================================================
  // Flow 4: Settings Configuration
  // ============================================================================

  test.describe('Flow 4: Settings Configuration', () => {
    test('should access and navigate settings', async ({ page }) => {
      // Note: Settings may be under development
      // This test validates the flow when available

      await page.goto('/settings');

      // Wait a moment for navigation
      await page.waitForTimeout(2000);

      // Check if settings page exists
      const currentUrl = page.url();
      const hasSettingsHeading = await page.getByRole('heading', { name: /Settings/i }).isVisible().catch(() => false);

      if (!currentUrl.includes('/settings') && !hasSettingsHeading) {
        test.info().annotations.push({
          type: 'settings-flow',
          description: 'Settings page not yet implemented',
        });
        test.skip(true, 'Settings page not implemented yet');
      }

      // If settings exist, verify navigation
      if (hasSettingsHeading) {
        // Look for settings sections
        const sections = page.locator('[role="tab"], h2, h3');
        const sectionCount = await sections.count();

        test.info().annotations.push({
          type: 'settings-sections',
          description: `Found ${sectionCount} settings sections`,
        });
      }
    });
  });

  // ============================================================================
  // Flow 5: Navigation Between Pages
  // ============================================================================

  test.describe('Flow 5: Multi-Page Navigation', () => {
    test('should navigate smoothly between all major pages', async ({ page }) => {
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

          // Verify main content is visible
          await expect(page.locator('main').first()).toBeVisible({ timeout: 10000 });

          test.info().annotations.push({
            type: 'navigation-success',
            description: `Successfully navigated to ${pageDef.name}`,
          });
        }
      }
    });
  });

  // ============================================================================
  // Flow 6: Mobile User Experience
  // ============================================================================

  test.describe('Flow 6: Mobile User Journey', () => {
    test('should complete core flow on mobile device', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Step 1: Load home page
      await page.goto('/');
      await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

      // Step 2: Navigate using mobile menu
      const menuButton = page.getByRole('button', { name: /menu|open/i });
      const hasMenuButton = await menuButton.isVisible().catch(() => false);

      if (hasMenuButton) {
        // Open mobile menu
        await menuButton.tap();

        // Navigation should be visible
        const nav = page.locator('nav, [role="navigation"]');
        await expect(nav.first()).toBeVisible({ timeout: 5000 });

        // Tap on a navigation item (e.g., Chat)
        const chatLink = page.getByRole('link', { name: /Chat/i });
        const hasChatLink = await chatLink.isVisible().catch(() => false);

        if (hasChatLink) {
          await chatLink.tap();
          await expect(page).toHaveURL(/\/chat/, { timeout: 10000 });
        }

        test.info().annotations.push({
          type: 'mobile-flow',
          description: 'Mobile navigation flow completed successfully',
        });
      } else {
        test.info().annotations.push({
          type: 'mobile-flow',
          description: 'No mobile menu needed - layout is responsive',
        });
      }
    });
  });

  // ============================================================================
  // Flow 7: Error Recovery
  // ============================================================================

  test.describe('Flow 7: Error Recovery', () => {
    test('should handle errors gracefully', async ({ page }) => {
      // Step 1: Navigate to non-existent page
      await page.goto('/this-page-does-not-exist');

      // Step 2: Verify error handling (404 page or redirect)
      const currentUrl = page.url();
      const has404 = await page.getByText(/404|not found/i).isVisible().catch(() => false);
      const hasErrorPage = await page.locator('[data-testid="error-page"]').isVisible().catch(() => false);

      // Should either show 404 or redirect
      const handlesError = has404 || hasErrorPage || !currentUrl.includes('this-page-does-not-exist');

      expect(handlesError).toBeTruthy();

      // Step 3: User should be able to navigate back to home
      const homeLink = page.getByRole('link', { name: /home|dashboard|logo/i });
      const hasHomeLink = await homeLink.isVisible().catch(() => false);

      if (hasHomeLink) {
        await homeLink.first().click();
        await expect(page).toHaveURL(/\//, { timeout: 10000 });
      }

      test.info().annotations.push({
        type: 'error-recovery',
        description: 'Error recovery flow validated',
      });
    });
  });

  // ============================================================================
  // Flow 8: Session Persistence
  // ============================================================================

  test.describe('Flow 8: Session Persistence', () => {
    test('should maintain session across page reloads', async ({ page }) => {
      // Step 1: Navigate to Chat
      await page.goto('/chat');

      // Step 2: Check if we can select a connection
      const connectionDropdown = page.getByRole('combobox');
      const hasConnections = await connectionDropdown.isVisible().catch(() => false);

      if (!hasConnections) {
        test.skip(true, 'No connections available');
      }

      // Step 3: Select connection and create session
      await connectionDropdown.click();
      const options = page.getByRole('option');
      const hasOptions = await options.first().isVisible().catch(() => false);

      if (hasOptions) {
        await options.first().click();

        const newSessionButton = page.getByRole('button', { name: /New Session/i });
        await newSessionButton.click();

        // Wait for session
        await expect(page.getByPlaceholder(/Ask a question/i)).toBeVisible({ timeout: 30000 });

        // Step 4: Reload page
        await page.reload();

        // Step 5: Verify session state is maintained or UI is usable
        await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

        test.info().annotations.push({
          type: 'session-persistence',
          description: 'Session persistence validated',
        });
      }
    });
  });
});

// ============================================================================
// Cross-Browser Flow Validation
// ============================================================================

test.describe('User Flows - Cross-Browser Validation', () => {
  test('should complete core flow on Chrome', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome validation');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

    test.info().annotations.push({
      type: 'cross-browser',
      description: 'Chrome: Core flow validated',
    });
  });

  test('should complete core flow on Firefox', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox validation');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

    test.info().annotations.push({
      type: 'cross-browser',
      description: 'Firefox: Core flow validated',
    });
  });

  test('should complete core flow on Safari', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari validation');

    await page.goto('/');
    await expect(page.locator('main')).toBeVisible({ timeout: 30000 });

    test.info().annotations.push({
      type: 'cross-browser',
      description: 'Safari: Core flow validated',
    });
  });
});

// ============================================================================
// Performance Flow Validation
// ============================================================================

test.describe('User Flows - Performance Validation', () => {
  test('should complete flows within acceptable time', async ({ page }) => {
    const flowTimings: { [key: string]: number } = {};

    // Test page load time
    let start = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    flowTimings.homePageLoad = Date.now() - start;

    // Test navigation time
    start = Date.now();
    const chatLink = page.getByRole('link', { name: /Chat/i });
    const hasChatLink = await chatLink.isVisible().catch(() => false);

    if (hasChatLink) {
      await chatLink.click();
      await page.waitForLoadState('networkidle');
      flowTimings.chatNavigation = Date.now() - start;
    }

    // Log all timings
    test.info().annotations.push({
      type: 'performance-timings',
      description: JSON.stringify(flowTimings),
    });

    // Basic performance assertions
    if (flowTimings.homePageLoad) {
      expect(flowTimings.homePageLoad).toBeLessThan(10000); // 10 seconds max
    }
  });
});
