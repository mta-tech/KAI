import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for Context Asset Promotion Workflow
 *
 * These tests verify the workflow for promoting mission results to reusable
 * context assets in the Agentic Context Platform.
 *
 * Prerequisites:
 * - Backend (FastAPI) running on port 8000
 * - Frontend (Next.js) running on port 3002
 * - Typesense running on port 8108
 * - Context platform models and services implemented
 * - Context asset API endpoints implemented
 * - Asset promotion UI implemented
 *
 * Task: #85 (QA and E2E Tests)
 * Status: SKELETON - Awaiting implementation of blocking tasks #92, #86
 */

// ============================================================================
// Test Constants
// ============================================================================

const ASSET_TYPES = ['instruction', 'verified_sql', 'mission_template', 'benchmark_case', 'semantic_hint'] as const;
type AssetType = typeof ASSET_TYPES[number];

const LIFECYCLE_STATES = ['draft', 'verified', 'published', 'deprecated'] as const;
type LifecycleState = typeof LIFECYCLE_STATES[number];

// ============================================================================
// Helper Functions (to be implemented when asset promotion UI is available)
// ============================================================================

/**
 * Navigate to the knowledge page with context asset management.
 * TODO: Implement when context asset management UI is available
 */
async function goToKnowledgePage(page: Page): Promise<void> {
  // Placeholder: Navigate to knowledge page
  // await page.goto('/knowledge');
  // await expect(page.getByRole('heading', { name: /knowledge/i })).toBeVisible();
}

/**
 * Open the promote to context asset dialog.
 * TODO: Implement when promote dialog is available
 */
async function openPromoteDialog(page: Page, artifactType: string): Promise<void> {
  // Placeholder: Click promote button on artifact
  // await page.getByTestId(`artifact-${artifactType}`).getByRole('button', { name: /promote/i }).click();
  // await expect(page.getByRole('dialog', { name: /promote to context asset/i })).toBeVisible();
}

/**
 * Fill in context asset metadata in the promotion dialog.
 * TODO: Implement when promotion form is available
 */
async function fillAssetMetadata(page: Page, metadata: {
  name: string;
  description: string;
  assetType: AssetType;
  tags?: string[];
}): Promise<void> {
  // Placeholder: Fill in asset metadata
  // await page.getByRole('textbox', { name: /asset name/i }).fill(metadata.name);
  // await page.getByRole('textbox', { name: /description/i }).fill(metadata.description);
  // await page.getByRole('combobox', { name: /asset type/i }).selectOption(metadata.assetType);
  // if (metadata.tags) {
  //   await page.getByRole('textbox', { name: /tags/i }).fill(metadata.tags.join(','));
  // }
}

/**
 * Submit the context asset promotion.
 * TODO: Implement when promotion submit is available
 */
async function submitPromotion(page: Page): Promise<void> {
  // Placeholder: Click submit button
  // await page.getByRole('button', { name: /promote|create asset/i }).click();
}

/**
 * Navigate to context assets tab.
 * TODO: Implement when context assets tab is available
 */
async function goToContextAssetsTab(page: Page): Promise<void> {
  // Placeholder: Switch to context assets tab
  // await page.getByRole('tab', { name: /context assets/i }).click();
  // await expect(page.getByTestId('context-assets-list')).toBeVisible();
}

/**
 * Search for a context asset by name.
 * TODO: Implement when context asset search is available
 */
async function searchContextAsset(page: Page, name: string): Promise<void> {
  // Placeholder: Search for asset
  // await page.getByRole('searchbox', { name: /search assets/i }).fill(name);
  // await page.keyboard.press('Enter');
}

// ============================================================================
// Asset Creation Tests
// ============================================================================

test.describe('Context Asset Creation', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
  });

  test('should display promote button on mission artifacts', async ({ page }) => {
    // TODO: Navigate to a completed mission and verify promote buttons
    // await page.goto('/chat/session/completed-mission-id');
    // await expect(page.getByTestId('artifact-verified-sql').getByRole('button', { name: /promote/i })).toBeVisible();
  });

  test('should open promotion dialog when promote button is clicked', async ({ page }) => {
    // TODO: Click promote button and verify dialog opens
    // await openPromoteDialog(page, 'verified-sql');
    // await expect(page.getByRole('dialog', { name: /promote to context asset/i })).toBeVisible();
  });

  test('should display all required fields in promotion dialog', async ({ page }) => {
    // TODO: Verify all required fields are present
    // await openPromoteDialog(page, 'verified-sql');
    // await expect(page.getByRole('textbox', { name: /asset name/i })).toBeVisible();
    // await expect(page.getByRole('textbox', { name: /description/i })).toBeVisible();
    // await expect(page.getByRole('combobox', { name: /asset type/i })).toBeVisible();
    // await expect(page.getByRole('textbox', { name: /tags/i })).toBeVisible();
  });

  test('should require asset name to be filled', async ({ page }) => {
    // TODO: Test required validation
    // await openPromoteDialog(page, 'verified-sql');
    // await page.getByRole('textbox', { name: /description/i }).fill('Test description');
    // await page.getByRole('button', { name: /promote/i }).click();
    // await expect(page.getByRole('textbox', { name: /asset name/i })).toHaveAttribute('aria-invalid', 'true');
  });

  test('should require description to be filled', async ({ page }) => {
    // TODO: Test required validation
    // await openPromoteDialog(page, 'verified-sql');
    // await page.getByRole('textbox', { name: /asset name/i }).fill('Test Asset');
    // await page.getByRole('button', { name: /promote/i }).click();
    // await expect(page.getByRole('textbox', { name: /description/i })).toHaveAttribute('aria-invalid', 'true');
  });

  test('should allow selecting asset type', async ({ page }) => {
    // TODO: Test asset type selection
    // await openPromoteDialog(page, 'verified-sql');
    // const typeSelect = page.getByRole('combobox', { name: /asset type/i });
    // await typeSelect.selectOption('verified_sql');
    // await expect(typeSelect).toHaveValue('verified_sql');
  });

  test('should allow adding tags to asset', async ({ page }) => {
    // TODO: Test tag input
    // await openPromoteDialog(page, 'verified-sql');
    // await page.getByRole('textbox', { name: /tags/i }).fill('sales,regional,analysis');
    // await expect(page.getByTestId('tag-sales')).toBeVisible();
    // await expect(page.getByTestId('tag-regional')).toBeVisible();
    // await expect(page.getByTestId('tag-analysis')).toBeVisible();
  });

  test('should allow removing tags', async ({ page }) => {
    // TODO: Test tag removal
    // await page.getByRole('textbox', { name: /tags/i }).fill('sales,regional');
    // await page.getByTestId('tag-sales').getByRole('button', { name: /remove/i }).click();
    // await expect(page.getByTestId('tag-sales')).not.toBeVisible();
  });

  test('should show preview of artifact content', async ({ page }) => {
    // TODO: Verify artifact content preview is displayed
    // await openPromoteDialog(page, 'verified-sql');
    // await expect(page.getByTestId('artifact-preview')).toBeVisible();
    // await expect(page.getByTestId('artifact-preview')).toContainText('SELECT');
  });
});

// ============================================================================
// Asset Submission and Validation Tests
// ============================================================================

test.describe('Asset Submission and Validation', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
  });

  test('should successfully create context asset on submit', async ({ page }) => {
    // TODO: Test successful asset creation
    // await openPromoteDialog(page, 'verified-sql');
    // await fillAssetMetadata(page, {
    //   name: 'Sales by Region',
    //   description: 'Quarterly sales breakdown by region',
    //   assetType: 'verified_sql',
    //   tags: ['sales', 'regional']
    // });
    // await submitPromotion(page);
    // await expect(page.getByRole('alert', { name: /asset created successfully/i })).toBeVisible();
  });

  test('should display created asset in context assets list', async ({ page }) => {
    // TODO: Verify asset appears in list
    // await openPromoteDialog(page, 'verified-sql');
    // await fillAssetMetadata(page, {
    //   name: 'Sales by Region',
    //   description: 'Quarterly sales breakdown',
    //   assetType: 'verified_sql'
    // });
    // await submitPromotion(page);
    // await goToContextAssetsTab(page);
    // await searchContextAsset(page, 'Sales by Region');
    // await expect(page.getByRole('link', { name: /sales by region/i })).toBeVisible();
  });

  test('should validate asset name uniqueness', async ({ page }) => {
    // TODO: Test uniqueness validation
    // Try to create asset with existing name
    // await openPromoteDialog(page, 'verified-sql');
    // await fillAssetMetadata(page, {
    //   name: 'Existing Asset Name',
    //   description: 'Test',
    //   assetType: 'verified_sql'
    // });
    // await submitPromotion(page);
    // await expect(page.getByText(/asset with this name already exists/i)).toBeVisible();
  });

  test('should validate tag format', async ({ page }) => {
    // TODO: Test tag format validation
    // Try to add invalid tag (special characters)
    // await openPromoteDialog(page, 'verified-sql');
    // await page.getByRole('textbox', { name: /tags/i }).fill('sales,regional@#$,analysis');
    // await expect(page.getByText(/invalid tag format/i)).toBeVisible();
  });

  test('should limit description length', async ({ page }) => {
    // TODO: Test description length limit
    // await openPromoteDialog(page, 'verified-sql');
    // const longDescription = 'a'.repeat(5001);
    // await page.getByRole('textbox', { name: /description/i }).fill(longDescription);
    // await expect(page.getByText(/description too long/i })).toBeVisible();
  });

  test('should handle submission errors gracefully', async ({ page }) => {
    // TODO: Test error handling
    // Simulate network error or server error
    // await openPromoteDialog(page, 'verified-sql');
    // await fillAssetMetadata(page, {
    //   name: 'Test Asset',
    //   description: 'Test',
    //   assetType: 'verified_sql'
    // });
    // Mock API error response
    // await submitPromotion(page);
    // await expect(page.getByRole('alert', { name: /error creating asset/i })).toBeVisible();
  });
});

// ============================================================================
// Asset Display and Visibility Tests
// ============================================================================

test.describe('Asset Display and Visibility', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
    await goToContextAssetsTab(page);
  });

  test('should display context assets list', async ({ page }) => {
    // TODO: Verify context assets list is displayed
    // await expect(page.getByTestId('context-assets-list')).toBeVisible();
  });

  test('should display asset metadata in list item', async ({ page }) => {
    // TODO: Verify asset metadata is displayed
    // const assetItem = page.getByTestId('context-asset-item').first();
    // await expect(assetItem.getByTestId('asset-name')).toBeVisible();
    // await expect(assetItem.getByTestId('asset-type')).toBeVisible();
    // await expect(assetItem.getByTestId('asset-lifecycle-state')).toBeVisible();
    // await expect(assetItem.getByTestId('asset-tags')).toBeVisible();
  });

  test('should display asset lifecycle state badge', async ({ page }) => {
    // TODO: Verify lifecycle state badge is displayed
    // const assetItem = page.getByTestId('context-asset-item').first();
    // await expect(assetItem.getByTestId('asset-lifecycle-state')).toBeVisible();
    // await expect(assetItem.getByTestId('asset-lifecycle-state')).toContainText(/draft|verified|published|deprecated/i);
  });

  test('should allow filtering assets by type', async ({ page }) => {
    // TODO: Test filtering by asset type
    // await page.getByRole('combobox', { name: /filter by type/i }).selectOption('verified_sql');
    // await expect(page.getByTestId('context-assets-list')).getByTestId('asset-type').filter({ hasText: 'verified_sql' });
  });

  test('should allow filtering assets by lifecycle state', async ({ page }) => {
    // TODO: Test filtering by lifecycle state
    // await page.getByRole('combobox', { name: /filter by state/i }).selectOption('published');
    // await expect(page.getByTestId('context-assets-list')).getByTestId('asset-lifecycle-state').filter({ hasText: 'published' });
  });

  test('should allow searching assets by name', async ({ page }) => {
    // TODO: Test search functionality
    // await page.getByRole('searchbox', { name: /search assets/i }).fill('sales');
    // await page.keyboard.press('Enter');
    // await expect(page.getByTestId('context-assets-list')).getByTestId('asset-name').filter({ hasText: /sales/i });
  });

  test('should allow searching assets by tags', async ({ page }) => {
    // TODO: Test tag search
    // await page.getByRole('searchbox', { name: /search assets/i }).fill('tag:regional');
    // await page.keyboard.press('Enter');
    // await expect(page.getByTestId('context-assets-list').getByTestId('asset-tags')).filter({ hasText: 'regional' });
  });

  test('should display empty state when no assets match filter', async ({ page }) => {
    // TODO: Test empty state
    // await page.getByRole('searchbox', { name: /search assets/i }).fill('nonexistent');
    // await page.keyboard.press('Enter');
    // await expect(page.getByText(/no context assets found/i)).toBeVisible();
  });
});

// ============================================================================
// Asset Reuse Tests
// ============================================================================

test.describe('Asset Reuse in New Queries', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
  });

  test('should allow attaching context asset to new query', async ({ page }) => {
    // TODO: Test asset attachment to query
    // await page.goto('/chat');
    // await page.getByRole('button', { name: /attach context/i }).click();
    // await page.getByRole('dialog', { name: /select context assets/i }).getByRole('option', { name: /sales by region/i }).click();
    // await page.getByRole('button', { name: /attach/i }).click();
    // await expect(page.getByTestId('attached-context-assets')).toContainText('sales by region');
  });

  test('should display asset usage count', async ({ page }) => {
    // TODO: Verify usage count is displayed
    // await goToContextAssetsTab(page);
    // const assetItem = page.getByTestId('context-asset-item').filter({ hasText: 'sales by region' });
    // await expect(assetItem.getByTestId('asset-usage-count')).toContainText(/\d+ uses/);
  });

  test('should increment usage count when asset is reused', async ({ page }) => {
    // TODO: Verify usage count increments
    // const initialCount = await getUsageCount('sales by region');
    // Attach asset to query
    // const newCount = await getUsageCount('sales by region');
    // expect(newCount).toBe(initialCount + 1);
  });

  test('should recommend relevant assets based on query', async ({ page }) => {
    // TODO: Test asset recommendation
    // await page.goto('/chat');
    // await page.getByRole('textbox', { name: /query/i }).fill('Show sales by region');
    // await expect(page.getByTestId('recommended-assets')).toBeVisible();
    // await expect(page.getByTestId('recommended-assets')).toContainText('sales by region');
  });

  test('should display asset compatibility warning for incompatible databases', async ({ page }) => {
    // TODO: Test compatibility warning
    // await page.goto('/chat');
    // Select connection that doesn't match asset's database
    // Try to attach asset
    // await expect(page.getByText(/this asset is from a different database/i)).toBeVisible();
  });
});

// ============================================================================
// Asset Editing Tests
// ============================================================================

test.describe('Asset Editing', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
    await goToContextAssetsTab(page);
  });

  test('should allow editing asset metadata', async ({ page }) => {
    // TODO: Test asset editing
    // await page.getByTestId('context-asset-item').first().getByRole('button', { name: /edit/i }).click();
    // await expect(page.getByRole('dialog', { name: /edit context asset/i })).toBeVisible();
  });

  test('should update asset name', async ({ page }) => {
    // TODO: Test name update
    // await page.getByRole('textbox', { name: /asset name/i }).fill('Updated Asset Name');
    // await page.getByRole('button', { name: /save/i }).click();
    // await expect(page.getByTestId('asset-name')).toContainText('Updated Asset Name');
  });

  test('should update asset description', async ({ page }) => {
    // TODO: Test description update
    // await page.getByRole('textbox', { name: /description/i }).fill('Updated description');
    // await page.getByRole('button', { name: /save/i }).click();
    // await expect(page.getByTestId('asset-description')).toContainText('Updated description');
  });

  test('should allow adding tags to existing asset', async ({ page }) => {
    // TODO: Test adding tags
    // await page.getByRole('textbox', { name: /tags/i }).fill('new-tag');
    // await page.getByRole('button', { name: /save/i }).click();
    // await expect(page.getByTestId('asset-tags')).toContainText('new-tag');
  });

  test('should create new version on edit', async ({ page }) => {
    // TODO: Test versioning
    // Edit asset and verify new version is created
    // await expect(page.getByTestId('asset-version')).toContainText('v2');
  });

  test('should display version history', async ({ page }) => {
    // TODO: Test version history display
    // await page.getByTestId('context-asset-item').first().getByRole('button', { name: /version history/i }).click();
    // await expect(page.getByRole('dialog', { name: /version history/i })).toBeVisible();
    // await expect(page.getByTestId('version-list')).toBeVisible();
  });

  test('should allow reverting to previous version', async ({ page }) => {
    // TODO: Test version revert
    // await page.getByTestId('version-item', { exact: true }).filter({ hasText: 'v1' }).getByRole('button', { name: /revert/i }).click();
    // await expect(page.getByText(/reverted to version/i)).toBeVisible();
  });
});

// ============================================================================
// Asset Deletion Tests
// ============================================================================

test.describe('Asset Deletion', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
    await goToContextAssetsTab(page);
  });

  test('should display delete button on asset', async ({ page }) => {
    // TODO: Verify delete button is displayed
    // await expect(page.getByTestId('context-asset-item').first().getByRole('button', { name: /delete/i })).toBeVisible();
  });

  test('should show confirmation dialog on delete', async ({ page }) => {
    // TODO: Test delete confirmation
    // await page.getByTestId('context-asset-item').first().getByRole('button', { name: /delete/i }).click();
    // await expect(page.getByRole('dialog', { name: /delete context asset/i })).toBeVisible();
  });

  test('should confirm deletion before deleting', async ({ page }) => {
    // TODO: Test deletion confirmation
    // await page.getByRole('button', { name: /delete/i }).click();
    // await page.getByRole('dialog', { name: /delete context asset/i }).getByRole('button', { name: /confirm|delete/i }).click();
    // await expect(page.getByRole('alert', { name: /asset deleted successfully/i })).toBeVisible();
  });

  test('should cancel deletion on cancel', async ({ page }) => {
    // TODO: Test deletion cancel
    // await page.getByRole('button', { name: /delete/i }).click();
    // await page.getByRole('dialog', { name: /delete context asset/i }).getByRole('button', { name: /cancel/i }).click();
    // await expect(page.getByRole('dialog', { name: /delete context asset/i })).not.toBeVisible();
    // await expect(page.getByTestId('context-asset-item')).toBeVisible();
  });

  test('should warn if asset is used in active missions', async ({ page }) => {
    // TODO: Test active mission warning
    // Try to delete asset that's in use
    // await expect(page.getByText(/this asset is being used in active missions/i)).toBeVisible();
  });

  test('should support soft delete with recovery option', async ({ page }) => {
    // TODO: Test soft delete and recovery
    // Delete asset
    // Go to trash/deleted assets
    // Restore asset
    // await expect(page.getByRole('button', { name: /restore/i })).toBeVisible();
  });
});

// ============================================================================
// Asset Lifecycle State Tests
// ============================================================================

test.describe('Asset Lifecycle States', () => {
  test.beforeEach(async ({ page }) => {
    await goToKnowledgePage(page);
    await goToContextAssetsTab(page);
  });

  test('should create asset in draft state by default', async ({ page }) => {
    // TODO: Verify default state
    // After promotion, asset should be in 'draft' state
    // await expect(page.getByTestId('asset-lifecycle-state')).toContainText('draft');
  });

  test('should allow transitioning from draft to verified', async ({ page }) => {
    // TODO: Test state transition
    // await page.getByRole('button', { name: /verify/i }).click();
    // await expect(page.getByTestId('asset-lifecycle-state')).toContainText('verified');
  });

  test('should require permission to publish asset', async ({ page }) => {
    // TODO: Test publish permission
    // Non-maintainer role should not see publish button
    // await expect(page.getByRole('button', { name: /publish/i })).not.toBeVisible();
  });

  test('should allow maintainer to publish verified asset', async ({ page }) => {
    // TODO: Test publish action (as maintainer)
    // Login as maintainer
    // await page.getByRole('button', { name: /publish/i }).click();
    // await expect(page.getByTestId('asset-lifecycle-state')).toContainText('published');
  });

  test('should allow deprecating published asset', async ({ page }) => {
    // TODO: Test deprecation
    // await page.getByRole('button', { name: /deprecate/i }).click();
    // await expect(page.getByTestId('asset-lifecycle-state')).toContainText('deprecated');
  });

  test('should display state transition history', async ({ page }) => {
    // TODO: Test transition history
    // await page.getByTestId('context-asset-item').first().getByRole('button', { name: /history/i }).click();
    // await expect(page.getByTestId('state-transition-history')).toBeVisible();
    // await expect(page.getByTestId('state-transition-history')).toContainText(/draft -> verified/i);
  });
});
