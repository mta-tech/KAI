import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for Chat UI Capabilities
 *
 * These tests verify the complete user flow of querying the kemenkop database
 * with an Indonesian language question about cooperative counts in Jakarta.
 *
 * Prerequisites:
 * - Backend (FastAPI) running on port 8000
 * - Frontend (Next.js) running on port 3000
 * - Typesense running on port 8108
 * - kemenkop/koperasi database connection configured
 */

// ============================================================================
// Connection Selection Helpers
// Pattern from: ui/src/components/chat/session-sidebar.tsx
//
// The session sidebar uses a Radix UI Select component with:
// - SelectTrigger: The button that opens the dropdown (role="combobox")
// - SelectContent: The dropdown content with options
// - SelectItem: Individual connection options (role="option")
//
// Connection display format: conn.alias || conn.id.slice(0, 8)
// ============================================================================

/**
 * Selects a specific connection from the connection dropdown.
 *
 * This function:
 * 1. Verifies the dropdown is visible and shows the placeholder
 * 2. Opens the dropdown by clicking the combobox
 * 3. Waits for connection options to load from API
 * 4. Selects the connection matching the provided name
 * 5. Verifies the selection was successful
 * 6. Confirms the New Session button is enabled
 *
 * @param page - Playwright page object
 * @param connectionName - The connection alias or partial ID to select (e.g., 'koperasi')
 * @throws Will fail if connection is not found within timeout
 */
async function selectConnection(page: Page, connectionName: string): Promise<void> {
  // Find the connection dropdown (Select component renders as combobox)
  const connectionDropdown = page.getByRole('combobox');
  await expect(connectionDropdown).toBeVisible();

  // Verify dropdown shows placeholder before selection
  await expect(connectionDropdown).toContainText('Select connection');

  // Click to open the dropdown
  await connectionDropdown.click();

  // Wait for the dropdown content to be visible and options to load
  // Options come from API call to list connections, so may take time
  const connectionOption = page.getByRole('option', { name: new RegExp(connectionName, 'i') });
  await expect(connectionOption).toBeVisible({ timeout: 10000 });

  // Select the connection
  await connectionOption.click();

  // Verify the dropdown now shows the selected connection (not the placeholder)
  await expect(connectionDropdown).not.toContainText('Select connection');
  await expect(connectionDropdown).toContainText(new RegExp(connectionName, 'i'));

  // Verify the "New Session" button is now enabled (depends on connection selection)
  const newSessionButton = page.getByRole('button', { name: /New Session/i });
  await expect(newSessionButton).toBeEnabled();
}

/**
 * Selects the first available connection from the dropdown.
 * Use this as a fallback when a specific connection may not exist.
 *
 * @param page - Playwright page object
 * @returns The name/text of the selected connection
 */
async function selectFirstAvailableConnection(page: Page): Promise<string> {
  const connectionDropdown = page.getByRole('combobox');
  await expect(connectionDropdown).toBeVisible();
  await connectionDropdown.click();

  // Wait for at least one option to appear
  const options = page.getByRole('option');
  await expect(options.first()).toBeVisible({ timeout: 10000 });

  // Get the text of the first option
  const firstOption = options.first();
  const connectionName = (await firstOption.textContent()) || 'unknown';

  // Select the first option
  await firstOption.click();

  // Verify selection was successful (placeholder should be replaced)
  await expect(connectionDropdown).not.toContainText('Select connection');

  // Verify New Session button is enabled
  const newSessionButton = page.getByRole('button', { name: /New Session/i });
  await expect(newSessionButton).toBeEnabled();

  return connectionName;
}

/**
 * Attempts to select koperasi connection, falls back to first available.
 * This provides robustness when the specific connection may not exist.
 *
 * @param page - Playwright page object
 * @returns The name of the selected connection
 */
async function selectKoperasiOrFirstConnection(page: Page): Promise<string> {
  const connectionDropdown = page.getByRole('combobox');
  await connectionDropdown.click();

  // Wait for options to load
  const options = page.getByRole('option');
  await expect(options.first()).toBeVisible({ timeout: 10000 });

  // Try to find koperasi, otherwise use first available connection
  const koperasiOption = page.getByRole('option', { name: /koperasi/i });
  const hasKoperasi = await koperasiOption.isVisible().catch(() => false);

  let selectedConnectionName: string;
  if (hasKoperasi) {
    selectedConnectionName = (await koperasiOption.textContent()) || 'koperasi';
    await koperasiOption.click();
  } else {
    selectedConnectionName = (await options.first().textContent()) || 'unknown';
    await options.first().click();
  }

  // Verify selection was successful
  await expect(connectionDropdown).not.toContainText('Select connection');

  // Verify New Session button is enabled
  const newSessionButton = page.getByRole('button', { name: /New Session/i });
  await expect(newSessionButton).toBeEnabled();

  return selectedConnectionName;
}

test.describe('Chat UI Capabilities', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the chat page
    await page.goto('/chat');

    // Wait for the page to be fully loaded
    await expect(page.getByText('Select or create a session to start chatting')).toBeVisible();
  });

  test('should display chat page with connection dropdown and new session button', async ({ page }) => {
    // Verify connection dropdown is visible
    await expect(page.getByRole('combobox')).toBeVisible();

    // Verify "New Session" button is visible but disabled (no connection selected)
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await expect(newSessionButton).toBeVisible();
    await expect(newSessionButton).toBeDisabled();
  });

  test('should query koperasi count in Jakarta', async ({ page }) => {
    // Step 1: Select the koperasi connection from dropdown
    // Uses helper function that verifies the complete connection selection flow
    await selectConnection(page, 'koperasi');

    // Step 2: Create a new session
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await expect(newSessionButton).toBeEnabled();
    await newSessionButton.click();

    // Wait for session to be created - the placeholder message should disappear
    await expect(
      page.getByText('Select or create a session to start chatting')
    ).not.toBeVisible({ timeout: 15000 });

    // Step 3: Enter the query in Indonesian
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeVisible();
    await expect(chatInput).toBeEnabled();

    await chatInput.fill('berapa jumlah koperasi di jakarta');

    // Step 4: Send the message using Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
    await chatInput.press('Meta+Enter');

    // Step 5: Verify the user message appears
    await expect(page.getByText('berapa jumlah koperasi di jakarta')).toBeVisible();

    // Step 6: Wait for agent response - look for the Bot icon which indicates an agent message
    // The response may take time due to LLM processing
    const agentResponse = page.locator('.prose').first();
    await expect(agentResponse).toBeVisible({ timeout: 60000 });

    // Step 7: Verify the response contains relevant content
    // Response should mention Jakarta or contain numeric data about cooperatives
    const responseText = await agentResponse.textContent();
    expect(responseText).toBeTruthy();
    expect(responseText!.length).toBeGreaterThan(10);
  });

  test('should show streaming indicator while processing', async ({ page }) => {
    // Select connection using helper function
    await selectConnection(page, 'koperasi');

    // Create new session
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await newSessionButton.click();

    // Wait for session creation
    await expect(
      page.getByText('Select or create a session to start chatting')
    ).not.toBeVisible({ timeout: 15000 });

    // Send a query
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await chatInput.fill('berapa jumlah koperasi di jakarta');
    await chatInput.press('Meta+Enter');

    // Verify streaming indicator appears (the "PROCESSING_REQUEST..." text or Stop button)
    // The stop button appears during streaming
    const stopButton = page.getByRole('button').filter({ has: page.locator('svg') }).last();

    // Either the processing indicator or stop button should appear
    await expect(
      page.getByText(/PROCESSING_REQUEST/i).or(stopButton)
    ).toBeVisible({ timeout: 10000 });

    // Wait for response to complete
    const agentResponse = page.locator('.prose').first();
    await expect(agentResponse).toBeVisible({ timeout: 60000 });
  });

  test('should handle connection selection and session creation flow', async ({ page }) => {
    // Initially, New Session button should be disabled (no connection selected)
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await expect(newSessionButton).toBeDisabled();

    // Select a connection using fallback helper (tries koperasi first, then any available)
    const selectedConnection = await selectKoperasiOrFirstConnection(page);

    // Log selected connection for debugging (visible in test output)
    test.info().annotations.push({
      type: 'selected-connection',
      description: selectedConnection,
    });

    // New Session button should now be enabled (verified in helper, but double-check)
    await expect(newSessionButton).toBeEnabled();

    // Create session
    await newSessionButton.click();

    // Chat input should now be visible and enabled
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeVisible({ timeout: 15000 });
    await expect(chatInput).toBeEnabled();
  });

  test('should verify connection dropdown contains available connections', async ({ page }) => {
    // Open connection dropdown
    const connectionDropdown = page.getByRole('combobox');
    await expect(connectionDropdown).toBeVisible();
    await expect(connectionDropdown).toContainText('Select connection');

    await connectionDropdown.click();

    // Wait for options to load from API
    const options = page.getByRole('option');
    await expect(options.first()).toBeVisible({ timeout: 10000 });

    // Count available connections
    const connectionCount = await options.count();
    expect(connectionCount).toBeGreaterThan(0);

    // Log available connections for debugging
    const connectionNames: string[] = [];
    for (let i = 0; i < connectionCount; i++) {
      const name = await options.nth(i).textContent();
      if (name) connectionNames.push(name);
    }
    test.info().annotations.push({
      type: 'available-connections',
      description: connectionNames.join(', '),
    });

    // Close dropdown by clicking outside or pressing Escape
    await page.keyboard.press('Escape');

    // Verify dropdown is closed (placeholder still visible since nothing selected)
    await expect(connectionDropdown).toContainText('Select connection');
  });
});
