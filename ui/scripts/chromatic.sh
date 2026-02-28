#!/bin/bash

# Chromatic Visual Regression Testing Script
# Run this script to execute visual regression tests locally

set -e

echo "🎨 Chromatic Visual Regression Testing"
echo "======================================"
echo ""

# Check if project token is set
if [ -z "$CHROMATIC_PROJECT_TOKEN" ]; then
  echo "❌ Error: CHROMATIC_PROJECT_TOKEN environment variable is not set"
  echo ""
  echo "Please set your Chromatic project token:"
  echo "  export CHROMATIC_PROJECT_TOKEN=your_token_here"
  echo ""
  echo "Or add it to your .env file"
  exit 1
fi

echo "✅ Project token found"
echo ""

# Build Storybook
echo "📚 Building Storybook..."
npm run build-storybook

echo ""
echo "🚀 Running Chromatic..."
npx chromatic --project-token="$CHROMATIC_PROJECT_TOKEN" --exitZeroOnChanges

echo ""
echo "✅ Visual regression tests complete!"
echo ""
echo "View results at: https://www.chromatic.com"
