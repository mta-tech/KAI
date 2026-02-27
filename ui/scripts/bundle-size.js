#!/usr/bin/env node

/**
 * Bundle size measurement script
 *
 * Run after build to check bundle sizes against budgets
 * Usage: node scripts/bundle-size.js
 */

const fs = require('fs');
const path = require('path');

// Bundle size budgets (in bytes)
const BUDGETS = {
  initialJs: 200 * 1024, // 200KB gzipped
  pageJs: 100 * 1024, // 100KB per page
  totalJs: 500 * 1024, // 500KB total JS
};

const BUILDS_DIR = path.join(__dirname, '../.next/analyze');

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

function getGzippedSize(filePath) {
  const zlib = require('zlib');
  const content = fs.readFileSync(filePath);
  return zlib.gzipSync(content).length;
}

function analyzeBundles() {
  if (!fs.existsSync(BUILDS_DIR)) {
    console.log('No bundle analysis found. Run with ANALYZE=true next build');
    process.exit(1);
  }

  const clientDir = path.join(BUILDS_DIR, 'client');
  if (!fs.existsSync(clientDir)) {
    console.log('Client bundles not found');
    process.exit(1);
  }

  console.log('\n📊 Bundle Size Analysis\n');

  let totalJs = 0;
  let passed = true;

  // Analyze client JS bundles
  const jsFiles = fs.readdirSync(clientDir).filter(f => f.endsWith('.js'));

  for (const file of jsFiles) {
    const filePath = path.join(clientDir, file);
    const stat = fs.statSync(filePath);
    const gzipped = getGzippedSize(filePath);
    totalJs += gzipped;

    const isOverBudget = gzipped > BUDGETS.pageJs;
    if (isOverBudget) passed = false;

    console.log(
      `${isOverBudget ? '❌' : '✅'} ${file.padEnd(30)} ${formatBytes(gzipped).padEnd(10)}${
        isOverBudget ? ` (over ${formatBytes(BUDGETS.pageJs)})` : ''
      }`
    );
  }

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Total JS: ${formatBytes(totalJs)}${totalJs > BUDGETS.totalJs ? ` ❌ (over ${formatBytes(BUDGETS.totalJs)})` : ' ✅'}`);

  if (passed) {
    console.log('\n✨ All bundles within budget!\n');
  } else {
    console.log('\n⚠️  Some bundles exceed budget. Consider code splitting.\n');
    process.exit(1);
  }
}

analyzeBundles();
