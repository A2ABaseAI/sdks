#!/bin/bash

# Script to publish A2ABase CLI tool to PyPI
# Usage: ./deploy/publish_cli.sh [testpypi|pypi]

set -e

REPOSITORY=${1:-pypi}

echo "🚀 Publishing A2ABase CLI to $REPOSITORY..."

# Check if we're in the right directory
if [ ! -d "a2abase_cli" ]; then
    echo "❌ Error: a2abase_cli directory not found. Run from repository root."
    exit 1
fi

cd a2abase_cli

# Check if twine is installed
if ! python3 -m twine --version &> /dev/null; then
    echo "📦 Installing twine..."
    python3 -m pip install twine build
fi

# Check if build is installed
if ! python3 -m build --version &> /dev/null; then
    echo "📦 Installing build..."
    python3 -m pip install build
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Build the package
echo "📦 Building package..."
python3 -m build

# Check the package
echo "✅ Checking package..."
twine check dist/*

# Upload to PyPI
if [ "$REPOSITORY" = "testpypi" ]; then
    echo "📤 Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Published to Test PyPI: https://test.pypi.org/project/a2abase-cli/"
else
    echo "📤 Uploading to PyPI..."
    twine upload --repository pypi dist/*
    echo "✅ Published to PyPI: https://pypi.org/project/a2abase-cli/"
fi

echo "🎉 CLI tool published successfully!"

