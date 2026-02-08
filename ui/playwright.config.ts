import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for E2E testing of the KAI Chat UI
 *
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directory where tests are located
  testDir: './tests/e2e',

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],

  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: 'http://localhost:3002',

    // Collect trace when retrying the failed test
    trace: 'on-first-retry',

    // Take screenshot on failure
    screenshot: 'only-on-failure',
  },

  // Global timeout for each test - 90 seconds to account for LLM response times
  timeout: 90000,

  // Timeout for each assertion - 60 seconds for LLM responses
  expect: {
    timeout: 60000,
  },

  // Configure projects for major browsers and devices
  // Cross-browser testing matrix: Chrome, Firefox, Safari (webkit)
  // Mobile device testing: iPhone, iPad, Android phones
  projects: [
    // Desktop browsers - Primary testing targets
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile devices - iOS testing (Safari on iPhone/iPad)
    {
      name: 'Mobile Safari - iPhone',
      use: { ...devices['iPhone 13'] },
    },
    {
      name: 'Mobile Safari - iPad',
      use: { ...devices['iPad Pro'] },
    },

    // Mobile devices - Android testing (Chrome on Android)
    {
      name: 'Mobile Chrome - Android',
      use: { ...devices['Pixel 5'] },
    },

    // Mobile viewport testing for responsiveness validation
    {
      name: 'Mobile Small',
      use: {
        ...devices['iPhone SE'],
        viewport: { width: 375, height: 667 },
      },
    },
  ],

  // Run your local dev server before starting the tests
  // Automatically starts the Next.js dev server when running tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3002',
    reuseExistingServer: !process.env.CI,
    timeout: 120000, // 2 minutes to start the dev server
  },

  // Output folder for test artifacts
  outputDir: 'test-results/',
});
