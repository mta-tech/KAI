import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for Knowledge Base UI
 *
 * These tests verify the complete user flow for managing business glossary
 * and custom instructions in the Knowledge Base page.
 *
 * Prerequisites:
 * - Backend (FastAPI) running on port 8000
 * - Frontend (Next.js) running on port 3002
 * - Typesense running on port 8108
 * - At least one database connection configured
 */

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Waits for the Knowledge page to fully load with connections.
 * This handles both the loading state and the final rendered state.
 *
 * @param page - Playwright page object
 */
async function waitForPageReady(page: Page): Promise<void> {
  // First wait for the heading to appear
  await expect(page.getByRole('heading', { name: /Knowledge Base/i })).toBeVisible({ timeout: 30000 });

  // The page should either show the combobox (if connections exist) or the empty state
  const combobox = page.locator('button[role="combobox"]');
  const emptyState = page.getByText(/No database connections available/i);

  // Wait for either to be visible - this indicates the page has loaded
  // Using polling approach since the API call may have already happened
  await expect(async () => {
    const comboboxVisible = await combobox.isVisible();
    const emptyVisible = await emptyState.isVisible();
    expect(comboboxVisible || emptyVisible).toBeTruthy();
  }).toPass({ timeout: 30000, intervals: [500, 1000, 2000] });
}

/**
 * Selects a connection from the connection dropdown on the Knowledge page.
 *
 * @param page - Playwright page object
 * @param connectionName - The connection alias to select (e.g., 'koperasi')
 */
async function selectConnection(page: Page, connectionName: string): Promise<void> {
  const connectionDropdown = page.locator('button[role="combobox"]');
  await expect(connectionDropdown).toBeVisible({ timeout: 15000 });

  await connectionDropdown.click();

  // Wait for options and select the connection
  const connectionOption = page.getByRole('option', { name: new RegExp(connectionName, 'i') });
  await expect(connectionOption).toBeVisible({ timeout: 15000 });
  await connectionOption.click();

  // Verify selection was successful
  await expect(connectionDropdown).toContainText(new RegExp(connectionName, 'i'));
}

/**
 * Selects the first available connection from the dropdown.
 * The Knowledge page auto-selects the first connection, so we just verify it's selected.
 *
 * @param page - Playwright page object
 * @returns The name of the selected connection
 */
async function selectFirstAvailableConnection(page: Page): Promise<string> {
  const connectionDropdown = page.locator('button[role="combobox"]');
  await expect(connectionDropdown).toBeVisible({ timeout: 15000 });

  // The page auto-selects the first connection, so we just read the current value
  const currentValue = await connectionDropdown.textContent();

  // If no connection is selected (shows "Select connection"), click to select one
  if (currentValue?.includes('Select connection')) {
    await connectionDropdown.click();

    // Wait for at least one option to appear
    const options = page.getByRole('option');
    await expect(options.first()).toBeVisible({ timeout: 15000 });

    // Get the text of the first option
    const firstOption = options.first();
    const connectionName = (await firstOption.textContent()) || 'unknown';

    // Select the first option
    await firstOption.click();

    return connectionName;
  }

  return currentValue || 'unknown';
}

/**
 * Clicks on the Instructions tab.
 *
 * @param page - Playwright page object
 */
async function clickInstructionsTab(page: Page): Promise<void> {
  const instructionsTab = page.getByRole('tab', { name: /Instructions/i });
  await expect(instructionsTab).toBeVisible({ timeout: 10000 });
  await instructionsTab.click();

  // Wait for tab content to switch
  await expect(page.getByRole('button', { name: /Add Instruction/i })).toBeVisible({ timeout: 10000 });
}

/**
 * Opens the Add Instruction dialog.
 *
 * @param page - Playwright page object
 */
async function openAddInstructionDialog(page: Page): Promise<void> {
  const addButton = page.getByRole('button', { name: /Add Instruction/i });
  await expect(addButton).toBeVisible();
  await addButton.click();

  // Wait for dialog to open
  await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
  await expect(page.getByRole('heading', { name: /Add Custom Instruction/i })).toBeVisible();
}

/**
 * Fills the instruction form with the provided values.
 *
 * @param page - Playwright page object
 * @param condition - The condition text
 * @param rules - The rules text
 * @param isDefault - Whether to mark as default instruction
 */
async function fillInstructionForm(
  page: Page,
  condition: string,
  rules: string,
  isDefault: boolean = false
): Promise<void> {
  // Fill condition field - find by label
  const conditionInput = page.locator('textarea[id="condition"]');
  await expect(conditionInput).toBeVisible();
  await conditionInput.fill(condition);

  // Fill rules field - find by label
  const rulesInput = page.locator('textarea[id="rules"]');
  await expect(rulesInput).toBeVisible();
  await rulesInput.fill(rules);

  // Check/uncheck default checkbox if needed
  if (isDefault) {
    const checkbox = page.locator('button[role="checkbox"]');
    await checkbox.click();
  }
}

/**
 * Submits the instruction form by clicking the Create button.
 *
 * @param page - Playwright page object
 */
async function submitInstructionForm(page: Page): Promise<void> {
  const createButton = page.getByRole('button', { name: /Create/i });
  await expect(createButton).toBeVisible();

  // Wait for the button to be enabled (not in pending state)
  await expect(createButton).toBeEnabled({ timeout: 5000 });

  // Click the Create button
  await createButton.click();

  // Wait for dialog to close (success) - use longer timeout as API might be slow
  await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 30000 });
}

/**
 * Verifies an instruction exists in the list.
 *
 * @param page - Playwright page object
 * @param condition - The condition text to verify
 * @param rules - The rules text to verify (partial match - uses first 30 chars if longer)
 */
async function verifyInstructionExists(
  page: Page,
  condition: string,
  rules: string
): Promise<void> {
  // Verify condition is displayed (use first() as there may be multiple matches from previous test runs)
  await expect(page.getByText(condition).first()).toBeVisible({ timeout: 5000 });

  // Verify rules are displayed - use partial match for long rules (may be truncated in UI)
  // Take first 30 characters of rules to avoid truncation issues
  // Use first() as there may be multiple instructions with similar rules from previous test runs
  const rulesPrefix = rules.length > 30 ? rules.substring(0, 30) : rules;
  await expect(page.getByText(rulesPrefix, { exact: false }).first()).toBeVisible({ timeout: 5000 });
}

/**
 * Deletes an instruction by clicking its delete button.
 *
 * @param page - Playwright page object
 * @param instructionIndex - The 1-based index of the instruction to delete
 */
async function deleteInstruction(page: Page, instructionIndex: number = 1): Promise<void> {
  // Find the instruction card by its heading (Instruction #N)
  const instructionCard = page.locator(`text=Instruction #${instructionIndex}`).locator('..');

  // Find and click the delete button within the card
  const deleteButton = instructionCard.locator('button').filter({
    has: page.locator('svg.lucide-trash-2'),
  });

  // Set up dialog handler for confirmation
  page.once('dialog', async (dialog) => {
    await dialog.accept();
  });

  await deleteButton.click();

  // Wait for the instruction to be removed
  await expect(page.getByText(`Instruction #${instructionIndex}`)).not.toBeVisible({ timeout: 10000 });
}

// ============================================================================
// Test Suite
// ============================================================================

test.describe('Knowledge Base - Instructions', () => {
  // Run tests serially to avoid state interference between tests
  test.describe.configure({ mode: 'serial' });

  test.beforeEach(async ({ page }) => {
    // Capture console logs and errors for debugging
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

    // Navigate to the knowledge page
    await page.goto('/knowledge');

    // Wait for the page to be fully loaded with connections data
    await waitForPageReady(page);
  });

  test('should display Knowledge Base page with tabs', async ({ page }) => {
    // Check if connections are available (combobox visible means connections exist)
    const combobox = page.locator('button[role="combobox"]');
    const emptyState = page.getByText(/No database connections available/i);

    // Either we have connections (combobox) or empty state
    const hasConnections = await combobox.isVisible();

    if (hasConnections) {
      // Verify tabs are visible when connections exist
      await expect(page.getByRole('tab', { name: /Business Glossary/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /Instructions/i })).toBeVisible();
    } else {
      // Verify empty state message
      await expect(emptyState).toBeVisible();
      test.skip(true, 'No database connections available');
    }
  });

  test('should switch to Instructions tab', async ({ page }) => {
    // Check if we have connections
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Select a connection first (page auto-selects, but verify)
    await selectFirstAvailableConnection(page);

    // Click on Instructions tab
    await clickInstructionsTab(page);

    // Verify the tab is active and content is shown
    await expect(page.getByRole('button', { name: /Add Instruction/i })).toBeVisible();
  });

  test('should open Add Instruction dialog', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup: select connection and navigate to Instructions tab
    await selectFirstAvailableConnection(page);
    await clickInstructionsTab(page);

    // Open the dialog
    await openAddInstructionDialog(page);

    // Verify dialog elements are visible
    await expect(page.getByRole('heading', { name: /Add Custom Instruction/i })).toBeVisible();
    await expect(page.locator('textarea[id="condition"]')).toBeVisible();
    await expect(page.locator('textarea[id="rules"]')).toBeVisible();
    await expect(page.locator('button[role="checkbox"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /Cancel/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Create/i })).toBeVisible();
  });

  test('should create a new instruction', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup: select connection and navigate to Instructions tab
    const selectedConnection = await selectFirstAvailableConnection(page);
    test.info().annotations.push({
      type: 'selected-connection',
      description: selectedConnection,
    });

    await clickInstructionsTab(page);

    // Open the dialog
    await openAddInstructionDialog(page);

    // Fill the form
    const testCondition = `Test condition ${Date.now()}`;
    const testRules = 'Always exclude cancelled orders from calculations. Show results in IDR currency.';

    await fillInstructionForm(page, testCondition, testRules, false);

    // Submit the form
    await submitInstructionForm(page);

    // Wait for toast notification (success) - use exact text to avoid matching aria-live region
    await expect(page.getByText('Instruction added', { exact: true })).toBeVisible({ timeout: 10000 });

    // Verify the instruction appears in the list
    await verifyInstructionExists(page, testCondition, testRules);

    // Log success
    test.info().annotations.push({
      type: 'created-instruction',
      description: `Condition: ${testCondition}, Rules: ${testRules}`,
    });
  });

  test('should create instruction with default flag', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup
    await selectFirstAvailableConnection(page);
    await clickInstructionsTab(page);
    await openAddInstructionDialog(page);

    // Fill the form with default flag
    const testCondition = `Default condition ${Date.now()}`;
    const testRules = 'Always format currency values with thousand separators.';

    await fillInstructionForm(page, testCondition, testRules, true);

    // Submit the form
    await submitInstructionForm(page);

    // Wait for success - use exact text to avoid matching aria-live region
    await expect(page.getByText('Instruction added', { exact: true })).toBeVisible({ timeout: 10000 });

    // Verify the instruction shows the "Default" badge (use first() to avoid multiple matches)
    await expect(page.locator('span:text("Default")').first()).toBeVisible({ timeout: 5000 });
  });

  test('should cancel instruction creation', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup
    await selectFirstAvailableConnection(page);
    await clickInstructionsTab(page);

    // Get initial instruction count from tab
    const instructionsTab = page.getByRole('tab', { name: /Instructions/i });
    const initialTabText = await instructionsTab.textContent();

    // Open the dialog
    await openAddInstructionDialog(page);

    // Fill the form partially
    await page.locator('textarea[id="condition"]').fill('Test condition');

    // Click Cancel
    const cancelButton = page.getByRole('button', { name: /Cancel/i });
    await cancelButton.click();

    // Verify dialog is closed
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 5000 });

    // Verify tab count didn't change (instruction was not created)
    await expect(instructionsTab).toHaveText(initialTabText || '');
  });

  test('should show empty state message when no instructions exist', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup: select connection and navigate to Instructions tab
    await selectFirstAvailableConnection(page);
    await clickInstructionsTab(page);

    // Check if empty state is shown (only if no instructions exist)
    // Note: This test might pass or fail depending on existing data
    const emptyMessage = page.getByText(/No custom instructions defined yet/i);
    const hasInstructions = !(await emptyMessage.isVisible().catch(() => false));

    if (!hasInstructions) {
      await expect(emptyMessage).toBeVisible();
      await expect(
        page.getByText(/Add instructions to guide how the AI interprets and responds to queries/i)
      ).toBeVisible();
    }
  });

  test('should display instruction with condition and rules', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup: select connection and navigate to Instructions tab
    await selectFirstAvailableConnection(page);
    await clickInstructionsTab(page);

    // Check if there are existing instructions
    const instructionHeading = page.locator('text=/Instruction #\\d+/');
    const hasInstructions = await instructionHeading.first().isVisible().catch(() => false);

    if (hasInstructions) {
      // Verify the instruction card structure
      await expect(page.getByText(/Condition:/i).first()).toBeVisible();
      await expect(page.getByText(/Rules:/i).first()).toBeVisible();
      await expect(page.getByText(/Created:/i).first()).toBeVisible();

      // Verify edit and delete buttons are present
      const instructionCard = page.locator('text=/Instruction #1/').locator('../..');
      await expect(instructionCard.locator('svg.lucide-pencil').first()).toBeVisible();
      await expect(instructionCard.locator('svg.lucide-trash-2').first()).toBeVisible();
    } else {
      // If no instructions, create one first
      await openAddInstructionDialog(page);
      await fillInstructionForm(page, 'Test condition', 'Test rules');
      await submitInstructionForm(page);

      // Now verify the structure
      await expect(page.getByText(/Condition:/i).first()).toBeVisible();
      await expect(page.getByText(/Rules:/i).first()).toBeVisible();
    }
  });

  test('should validate required fields before submission', async ({ page }) => {
    const combobox = page.locator('button[role="combobox"]');
    const hasConnections = await combobox.isVisible();

    if (!hasConnections) {
      test.skip(true, 'No database connections available');
    }

    // Setup
    await selectFirstAvailableConnection(page);
    await clickInstructionsTab(page);
    await openAddInstructionDialog(page);

    // Try to submit without filling fields
    const createButton = page.getByRole('button', { name: /Create/i });

    // Get the condition input and verify it exists
    const conditionInput = page.locator('textarea[id="condition"]');
    const rulesInput = page.locator('textarea[id="rules"]');

    // HTML5 validation should prevent submission
    // The form should not submit if required fields are empty
    await createButton.click();

    // Dialog should still be open (form didn't submit)
    await expect(page.getByRole('dialog')).toBeVisible();

    // Fill only condition
    await conditionInput.fill('Test condition');
    await createButton.click();

    // Dialog should still be open (rules is empty)
    await expect(page.getByRole('dialog')).toBeVisible();

    // Now fill rules too
    await rulesInput.fill('Test rules');
    await createButton.click();

    // Now it should submit successfully
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 15000 });
  });
});
