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

// ============================================================================
// Query Submission Helpers
// Pattern from: ui/src/components/chat/chat-input.tsx
//
// The chat input component handles message submission with:
// - Textarea with placeholder "Ask a question about your data... (Cmd+Enter to send)"
// - Keyboard shortcut: Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
// - Send button (icon button) as alternative submission method
// - Input is disabled when no session is selected or while streaming
//
// Submission flow:
// 1. User types message in textarea
// 2. User presses Cmd+Enter or clicks Send button
// 3. Message appears in chat as user message
// 4. Agent processes and streams response
// 5. Response appears with bot icon and markdown rendering
// ============================================================================

/**
 * Submits a query to the chat using the keyboard shortcut.
 *
 * This function:
 * 1. Verifies the chat input is visible and enabled
 * 2. Clears any existing input and fills with the new query
 * 3. Sends the message using Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
 * 4. Verifies the user message appears in the chat
 *
 * @param page - Playwright page object
 * @param query - The query text to submit
 * @param options - Optional configuration for query submission
 * @returns Promise that resolves when query is submitted and user message is visible
 */
async function submitQuery(
  page: Page,
  query: string,
  options: {
    /** Use button click instead of keyboard shortcut. Default: false */
    useButton?: boolean;
    /** Timeout for user message to appear in milliseconds. Default: 10000 */
    timeout?: number;
    /** Whether to verify user message appears. Default: true */
    verifyUserMessage?: boolean;
  } = {}
): Promise<void> {
  const { useButton = false, timeout = 10000, verifyUserMessage = true } = options;

  // Find and verify the chat input is ready
  const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
  await expect(chatInput).toBeVisible();
  await expect(chatInput).toBeEnabled();

  // Clear any existing input and fill with the query
  await chatInput.fill('');
  await chatInput.fill(query);

  // Verify the query text was entered
  await expect(chatInput).toHaveValue(query);

  if (useButton) {
    // Submit using the Send button (icon button with Send icon)
    // The Send button is the last button in the input group when not streaming
    const sendButton = page.getByRole('button').filter({
      has: page.locator('svg'),
    }).last();
    await expect(sendButton).toBeVisible();
    await expect(sendButton).toBeEnabled();
    await sendButton.click();
  } else {
    // Submit using keyboard shortcut (Cmd+Enter on Mac, Ctrl+Enter on Windows/Linux)
    // Playwright's Meta key works as Cmd on Mac and Windows key on Windows
    await chatInput.press('Meta+Enter');
  }

  // Verify the user message appears in the chat
  if (verifyUserMessage) {
    await expect(page.getByText(query)).toBeVisible({ timeout });
  }

  // Input should be cleared after submission
  await expect(chatInput).toHaveValue('');
}

/**
 * Submits a query and waits for the agent response.
 *
 * This function extends submitQuery to also wait for and validate the agent response.
 *
 * @param page - Playwright page object
 * @param query - The query text to submit
 * @param options - Optional configuration for query and response handling
 * @returns Promise that resolves with the response element
 */
async function submitQueryAndWaitForResponse(
  page: Page,
  query: string,
  options: {
    /** Use button click instead of keyboard shortcut. Default: false */
    useButton?: boolean;
    /** Timeout for response to appear in milliseconds. Default: 60000 */
    responseTimeout?: number;
    /** Minimum expected response length in characters. Default: 10 */
    minResponseLength?: number;
  } = {}
): Promise<{ responseText: string; responseElement: ReturnType<typeof page.locator> }> {
  const { useButton = false, responseTimeout = 60000, minResponseLength = 10 } = options;

  // Submit the query
  await submitQuery(page, query, { useButton });

  // Wait for agent response - look for the prose class which indicates markdown-rendered response
  // The response may take time due to LLM processing and streaming
  const agentResponse = page.locator('.prose').first();
  await expect(agentResponse).toBeVisible({ timeout: responseTimeout });

  // Get the response text and verify it has content
  const responseText = (await agentResponse.textContent()) || '';
  expect(responseText).toBeTruthy();
  expect(responseText.length).toBeGreaterThan(minResponseLength);

  return { responseText, responseElement: agentResponse };
}

/**
 * Verifies that a stop button appears during streaming.
 *
 * Pattern from: ui/src/components/chat/chat-input.tsx
 * During streaming, the Send button is replaced with a Stop button (destructive variant)
 *
 * @param page - Playwright page object
 * @param timeout - Timeout for stop button to appear in milliseconds. Default: 10000
 */
async function verifyStreamingIndicator(
  page: Page,
  timeout: number = 10000
): Promise<void> {
  // During streaming, either the processing indicator or stop button should appear
  // The stop button is a destructive button with a Square icon
  const stopButton = page.getByRole('button').filter({
    has: page.locator('svg'),
  }).last();

  // Either the processing indicator text or stop button should be visible
  await expect(
    page.getByText(/PROCESSING_REQUEST/i).or(stopButton)
  ).toBeVisible({ timeout });
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

    // Step 3-6: Submit query and wait for response using helper function
    // This handles: filling input, keyboard submission, verifying user message,
    // waiting for agent response, and validating response content
    const query = 'berapa jumlah koperasi di jakarta';
    const { responseText } = await submitQueryAndWaitForResponse(page, query, {
      responseTimeout: 60000,
      minResponseLength: 10,
    });

    // Step 7: Log response for debugging (visible in test output)
    test.info().annotations.push({
      type: 'agent-response',
      description: responseText.substring(0, 200) + (responseText.length > 200 ? '...' : ''),
    });
  });

  test('should submit query using Send button', async ({ page }) => {
    // This test verifies the alternative submission method using the Send button
    // Pattern from: ui/src/components/chat/chat-input.tsx

    // Step 1: Select connection and create session
    await selectKoperasiOrFirstConnection(page);
    await createNewSession(page);

    // Step 2: Submit query using button instead of keyboard shortcut
    const query = 'berapa jumlah koperasi di jakarta';
    const { responseText } = await submitQueryAndWaitForResponse(page, query, {
      useButton: true,
      responseTimeout: 60000,
    });

    // Step 3: Verify response was received
    expect(responseText).toBeTruthy();
    expect(responseText.length).toBeGreaterThan(10);
  });

  test('should show streaming indicator while processing', async ({ page }) => {
    // Select connection using helper function
    await selectConnection(page, 'koperasi');

    // Create new session using helper function
    await createNewSession(page);

    // Submit query without waiting for response (to catch streaming indicator)
    const query = 'berapa jumlah koperasi di jakarta';
    await submitQuery(page, query, { verifyUserMessage: true });

    // Verify streaming indicator appears using helper function
    // Pattern from: ui/src/components/chat/chat-input.tsx
    // During streaming, either PROCESSING_REQUEST text or Stop button should appear
    await verifyStreamingIndicator(page, 10000);

    // Wait for response to complete
    const agentResponse = page.locator('.prose').first();
    await expect(agentResponse).toBeVisible({ timeout: 60000 });

    // Verify the input is re-enabled after streaming completes
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeEnabled({ timeout: 5000 });
  });

  test('should submit multiple queries in same session', async ({ page }) => {
    // This test verifies that multiple queries can be submitted in the same session
    // Pattern from: ui/src/components/chat/chat-input.tsx

    // Step 1: Setup - select connection and create session
    await selectKoperasiOrFirstConnection(page);
    await createNewSession(page);

    // Step 2: Submit first query and wait for response
    const query1 = 'berapa jumlah koperasi di jakarta';
    await submitQueryAndWaitForResponse(page, query1, { responseTimeout: 60000 });

    // Step 3: Submit second query (follow-up question)
    const query2 = 'bagaimana trennya dalam 5 tahun terakhir';
    await submitQueryAndWaitForResponse(page, query2, { responseTimeout: 60000 });

    // Step 4: Verify both user messages are visible in the chat history
    await expect(page.getByText(query1)).toBeVisible();
    await expect(page.getByText(query2)).toBeVisible();

    // Step 5: Verify there are multiple prose elements (multiple responses)
    const responses = page.locator('.prose');
    const responseCount = await responses.count();
    expect(responseCount).toBeGreaterThanOrEqual(2);
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
