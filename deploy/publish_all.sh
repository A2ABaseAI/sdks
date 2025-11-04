#!/bin/bash

# Script to publish both Python and TypeScript SDKs
# Usage: ./deploy/publish_all.sh [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "🚀 Publishing BaseAI SDKs..."
echo ""

# Publish Python SDK
echo "📦 Publishing Python SDK..."
"$SCRIPT_DIR/publish_python.sh" pypi
echo ""

# Publish TypeScript SDK
echo "📦 Publishing TypeScript SDK..."
if [[ "$*" == *"--dry-run"* ]]; then
    "$SCRIPT_DIR/publish_typescript.sh" --dry-run
else
    "$SCRIPT_DIR/publish_typescript.sh"
fi

echo ""
echo "🎉 All SDKs published successfully!"

