#!/usr/bin/env node

/**
 * Check for unused dependencies
 *
 * This script analyzes the codebase and identifies dependencies
 * that may not be used.
 */

const fs = require('fs');
const path = require('path');

const packageJson = require('../package.json');
const srcDir = path.join(__dirname, '../src');

// Get all dependencies from package.json
const allDeps = {
  ...packageJson.dependencies,
  ...packageJson.devDependencies,
};

// Track which packages are imported
const usedPackages = new Set();

function getFileImports(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const imports = [];

  // Match ES6 imports
  const es6ImportRegex = /import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]/g;
  let match;
  while ((match = es6ImportRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }

  // Match require() calls
  const requireRegex = /require\(['"]([^'"]+)['"]\)/g;
  while ((match = requireRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }

  return imports;
}

function scanDirectory(dir) {
  const files = fs.readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = path.join(dir, file.name);

    if (file.isDirectory()) {
      // Skip node_modules and .next
      if (file.name !== 'node_modules' && file.name !== '.next') {
        scanDirectory(fullPath);
      }
    } else if (file.name.match(/\.(ts|tsx|js|jsx)$/)) {
      const imports = getFileImports(fullPath);
      imports.forEach(imp => {
        // Extract package name from import path
        const packageName = imp.match(/^(@?[^/]+)/)?.[1];
        if (packageName && allDeps[packageName]) {
          usedPackages.add(packageName);
        }
      });
    }
  }
}

// Scan the src directory
if (fs.existsSync(srcDir)) {
  scanDirectory(srcDir);
}

// Find potentially unused dependencies
const unusedPackages = Object.keys(allDeps).filter(
  dep => !usedPackages.has(dep)
);

// Filter out known build/dev tools that may not be directly imported
const alwaysUsed = [
  'next',
  'react',
  'react-dom',
  'typescript',
  'eslint',
  'tailwindcss',
  'postcss',
];

const potentiallyUnused = unusedPackages.filter(
  dep => !alwaysUsed.includes(dep)
);

console.log('\n📦 Dependency Analysis\n');
console.log(`Total dependencies: ${Object.keys(allDeps).length}`);
console.log(`Used in code: ${usedPackages.size}`);
console.log(`Potentially unused: ${potentiallyUnused.length}\n`);

if (potentiallyUnused.length > 0) {
  console.log('Potentially unused packages:');
  potentiallyUnused.forEach(dep => {
    console.log(`  - ${dep}`);
  });
  console.log('\n⚠️  Review these packages before removing. Some may be used for:\n' +
    '   - Build configuration\n' +
    '   - TypeScript types\n' +
    '   - Peer dependencies\n');
} else {
  console.log('✅ All dependencies appear to be in use!\n');
}

// Export for use in CI
if (process.env.CI === 'true' && potentiallyUnused.length > 0) {
  process.exit(1);
}
