#!/bin/bash

# Script to publish TypeScript SDK to npm
# Usage: ./deploy/publish_typescript.sh [--dry-run]

set -e

DRY_RUN=""
if [[ "$*" == *"--dry-run"* ]]; then
    DRY_RUN="--dry-run"
    echo "🧪 Running in dry-run mode (no actual publish)"
fi

echo "🚀 Publishing BaseAI TypeScript SDK to npm..."

# Check if we're in the right directory
if [ ! -d "typescript" ]; then
    echo "❌ Error: typescript directory not found. Run from repository root."
    exit 1
fi

cd typescript

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    exit 1
fi

# Check if logged in to npm
if ! npm whoami &> /dev/null; then
    echo "⚠️  Not logged in to npm. Please run: npm login"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the package
echo "🔨 Building package..."
npm run build

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ Error: dist directory not found. Build may have failed."
    exit 1
fi

# Publish to npm
if [ -n "$DRY_RUN" ]; then
    echo "🧪 Dry run - checking package..."
    npm publish --dry-run
    echo "✅ Dry run completed successfully!"
else
    echo "📤 Publishing to npm..."
    npm publish --access public
    echo "✅ Published to npm: https://www.npmjs.com/package/@belarabyai/baseai"
fi

echo "🎉 TypeScript SDK published successfully!"

