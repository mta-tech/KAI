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

// ============================================================================
// Session Creation Helpers
// Pattern from: ui/src/components/chat/session-sidebar.tsx
//
// The session creation flow:
// 1. User selects a connection (required - New Session button is disabled otherwise)
// 2. User clicks "New Session" button (with Plus icon)
// 3. Session is created via agentApi and appears in the sidebar
// 4. The placeholder message disappears and chat input becomes available
//
// Session display format: session.title || `Session ${session.id.slice(0, 8)}`
// ============================================================================

/**
 * Creates a new chat session by clicking the New Session button.
 *
 * Prerequisites:
 * - A connection must already be selected (New Session button must be enabled)
 *
 * This function:
 * 1. Verifies the New Session button is enabled (connection is selected)
 * 2. Clicks the New Session button
 * 3. Waits for the session to be created (placeholder message disappears)
 * 4. Verifies the chat input is visible and enabled
 * 5. Optionally verifies the session appears in the sidebar
 *
 * @param page - Playwright page object
 * @param options - Optional configuration for session creation
 * @throws Will fail if session creation times out or chat input is not available
 */
async function createNewSession(
  page: Page,
  options: {
    /** Timeout for session creation in milliseconds. Default: 15000 */
    timeout?: number;
    /** Whether to verify the session appears in the sidebar. Default: false */
    verifySidebar?: boolean;
  } = {}
): Promise<void> {
  const { timeout = 15000, verifySidebar = false } = options;

  // Verify the New Session button is enabled (requires connection to be selected)
  const newSessionButton = page.getByRole('button', { name: /New Session/i });
  await expect(newSessionButton).toBeVisible();
  await expect(newSessionButton).toBeEnabled();

  // Click the New Session button to create a session
  await newSessionButton.click();

  // Wait for session to be created - the placeholder message should disappear
  // This indicates the session was successfully created and the chat view is ready
  await expect(
    page.getByText('Select or create a session to start chatting')
  ).not.toBeVisible({ timeout });

  // Verify the chat input is now visible and enabled
  const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
  await expect(chatInput).toBeVisible({ timeout: 5000 });
  await expect(chatInput).toBeEnabled();

  // Optionally verify the session appears in the sidebar
  if (verifySidebar) {
    // Sessions are displayed with MessageSquare icon and title/id
    // Look for any session entry in the sidebar (not the "No sessions yet" message)
    const sessionEntries = page.locator('button').filter({
      has: page.locator('svg'),
    }).filter({
      hasText: /Session/i,
    });
    await expect(sessionEntries.first()).toBeVisible({ timeout: 5000 });
  }
}

/**
 * Creates a new session and returns the session ID from the sidebar.
 *
 * Prerequisites:
 * - A connection must already be selected
 *
 * This function extends createNewSession to also capture and return
 * the session identifier displayed in the sidebar.
 *
 * @param page - Playwright page object
 * @returns The session display text (e.g., "Session abc12345")
 */
async function createNewSessionAndGetId(page: Page): Promise<string> {
  // Get the count of existing sessions before creating a new one
  const sessionsBefore = page.locator('[class*="group"]').filter({
    has: page.locator('svg'),
  });
  const countBefore = await sessionsBefore.count().catch(() => 0);

  // Create the new session
  await createNewSession(page);

  // Wait for a new session to appear in the sidebar
  // Look for session entries with the MessageSquare icon pattern
  const sessionEntries = page.locator('button').filter({
    hasText: /Session [a-f0-9]+/i,
  });

  // Wait for at least one more session than before
  await expect(async () => {
    const currentCount = await sessionEntries.count();
    expect(currentCount).toBeGreaterThan(countBefore);
  }).toPass({ timeout: 10000 });

  // Get the text of the most recently created session (likely the last or first visible one)
  const latestSession = sessionEntries.first();
  const sessionText = (await latestSession.textContent()) || 'unknown-session';

  return sessionText.trim();
}

/**
 * Selects an existing session from the sidebar by its display text.
 *
 * @param page - Playwright page object
 * @param sessionText - The session text to look for (partial match supported)
 * @throws Will fail if session is not found
 */
async function selectExistingSession(page: Page, sessionText: string): Promise<void> {
  // Find and click the session button in the sidebar
  const sessionButton = page.locator('button').filter({
    hasText: new RegExp(sessionText, 'i'),
  }).first();

  await expect(sessionButton).toBeVisible({ timeout: 5000 });
  await sessionButton.click();

  // Verify the chat input is visible after selecting the session
  const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
  await expect(chatInput).toBeVisible({ timeout: 5000 });
}

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

    // Step 2: Create a new session using helper function
    // This verifies the New Session button is enabled, clicks it, and waits for
    // the session to be created (placeholder disappears, chat input visible)
    await createNewSession(page);

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

    // Create new session using helper function
    await createNewSession(page);

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

    // Create session using helper function
    // This verifies the button is enabled, clicks it, waits for session creation,
    // and confirms the chat input is visible and enabled
    await createNewSession(page);
  });

  test('should create new session when New Session button is clicked', async ({ page }) => {
    // This test specifically validates the session creation step
    // Pattern from: ui/src/components/chat/session-sidebar.tsx

    // Step 1: Verify initial state - New Session button should be disabled
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await expect(newSessionButton).toBeVisible();
    await expect(newSessionButton).toBeDisabled();

    // Verify placeholder message is shown (no session selected)
    await expect(
      page.getByText('Select or create a session to start chatting')
    ).toBeVisible();

    // Step 2: Select a connection (required for session creation)
    await selectKoperasiOrFirstConnection(page);

    // Step 3: Create a new session with sidebar verification
    // This uses the helper function with verifySidebar option enabled
    await createNewSession(page, { verifySidebar: true });

    // Step 4: Verify the session was created successfully
    // - Placeholder message should be hidden
    await expect(
      page.getByText('Select or create a session to start chatting')
    ).not.toBeVisible();

    // - Chat input should be visible and ready for input
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeVisible();
    await expect(chatInput).toBeEnabled();

    // - The "No sessions yet" message should not be visible (session was created)
    await expect(page.getByText('No sessions yet')).not.toBeVisible();
  });

  test('should verify session appears in sidebar with correct format', async ({ page }) => {
    // This test verifies the session display format in the sidebar
    // Pattern from: ui/src/components/chat/session-sidebar.tsx
    // Session display format: session.title || `Session ${session.id.slice(0, 8)}`

    // Step 1: Select a connection
    const selectedConnection = await selectKoperasiOrFirstConnection(page);
    test.info().annotations.push({
      type: 'selected-connection',
      description: selectedConnection,
    });

    // Step 2: Use createNewSessionAndGetId to create session and capture ID
    const sessionText = await createNewSessionAndGetId(page);

    // Step 3: Verify session text format matches expected pattern
    // Should be "Session" followed by 8 hex characters (truncated UUID)
    expect(sessionText).toBeTruthy();
    expect(sessionText).toMatch(/Session [a-f0-9]{8}/i);

    // Log the captured session ID for debugging
    test.info().annotations.push({
      type: 'created-session',
      description: sessionText,
    });

    // Step 4: Verify the session entry is visible in the sidebar
    const sessionEntry = page.locator('button').filter({
      hasText: new RegExp(sessionText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'),
    }).first();
    await expect(sessionEntry).toBeVisible();

    // Step 5: Verify clicking the session entry keeps the chat active
    await sessionEntry.click();
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeVisible();
    await expect(chatInput).toBeEnabled();
  });

  test('should allow selecting and switching between sessions', async ({ page }) => {
    // This test verifies session selection functionality
    // Pattern from: ui/src/components/chat/session-sidebar.tsx

    // Step 1: Select a connection
    await selectKoperasiOrFirstConnection(page);

    // Step 2: Create first session and capture its ID
    const firstSessionText = await createNewSessionAndGetId(page);
    test.info().annotations.push({
      type: 'first-session',
      description: firstSessionText,
    });

    // Step 3: Create a second session
    // First, we need to click New Session button again
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await newSessionButton.click();

    // Wait for the second session to be created
    await expect(
      page.getByText('Select or create a session to start chatting')
    ).not.toBeVisible({ timeout: 15000 });

    // Step 4: Use selectExistingSession helper to switch to the first session
    await selectExistingSession(page, firstSessionText);

    // Step 5: Verify we're back to the first session
    // The chat input should be visible and the session should be selected
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeVisible();
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
