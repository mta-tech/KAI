import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';

import { playwright } from '@vitest/browser-playwright';

const dirname =
  typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

// More info at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(dirname, './src'),
    },
  },
  esbuild: {
    jsx: 'automatic',
    jsxImportSource: undefined, // Use default React import for Next.js compatibility
  },
  // Optimize for Next.js compatibility
  optimizeDeps: {
    include: ['react', 'react-dom', '@testing-library/react', '@testing-library/jest-dom'],
  },
  test: {
    // Coverage configuration at root level for Vitest 4.x
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.{js,ts,tsx}'],
      exclude: [
        'src/**/*.stories.tsx',
        'src/**/*.d.ts',
        'src/**/__tests__/**',
        'node_modules/**',
      ],
    },
    projects: [
      // Unit tests (node environment, faster)
      {
        resolve: {
          alias: {
            '@': path.resolve(dirname, './src'),
          },
        },
        test: {
          name: 'unit',
          environment: 'jsdom',
          include: ['tests/unit/**/*.{test,spec}.{js,ts,tsx}'],
          exclude: ['tests/e2e/**', 'tests/**/*.stories.tsx'],
          setupFiles: ['./tests/unit/setup.ts'],
          globals: true,
        },
      },
      // Storybook tests (browser environment)
      {
        extends: true,
        plugins: [
          // The plugin will run tests for the stories defined in your Storybook config
          // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
          storybookTest({ configDir: path.join(dirname, '.storybook') }),
        ],
        test: {
          name: 'storybook',
          browser: {
            enabled: true,
            headless: true,
            provider: playwright({}),
            instances: [{ browser: 'chromium' }],
          },
          setupFiles: ['.storybook/vitest.setup.ts'],
        },
      },
    ],
  },
});
