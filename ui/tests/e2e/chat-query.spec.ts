import { test, expect } from '@playwright/test';

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
    const connectionDropdown = page.getByRole('combobox');
    await connectionDropdown.click();

    // Wait for dropdown options to appear and select koperasi
    // The connection may show as 'koperasi' alias or partial connection ID
    const koperasiOption = page.getByRole('option', { name: /koperasi/i });
    await expect(koperasiOption).toBeVisible({ timeout: 10000 });
    await koperasiOption.click();

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
    // Select connection and create session
    const connectionDropdown = page.getByRole('combobox');
    await connectionDropdown.click();
    await page.getByRole('option', { name: /koperasi/i }).click();

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
    // Initially, New Session button should be disabled
    const newSessionButton = page.getByRole('button', { name: /New Session/i });
    await expect(newSessionButton).toBeDisabled();

    // Select a connection
    const connectionDropdown = page.getByRole('combobox');
    await connectionDropdown.click();

    // Get available connections and select the first one (or koperasi if available)
    const options = page.getByRole('option');
    await expect(options.first()).toBeVisible({ timeout: 10000 });

    // Try to find koperasi, otherwise use first available connection
    const koperasiOption = page.getByRole('option', { name: /koperasi/i });
    const hasKoperasi = await koperasiOption.isVisible().catch(() => false);

    if (hasKoperasi) {
      await koperasiOption.click();
    } else {
      await options.first().click();
    }

    // New Session button should now be enabled
    await expect(newSessionButton).toBeEnabled();

    // Create session
    await newSessionButton.click();

    // Chat input should now be visible and enabled
    const chatInput = page.getByPlaceholder(/Ask a question about your data/i);
    await expect(chatInput).toBeVisible({ timeout: 15000 });
    await expect(chatInput).toBeEnabled();
  });
});
