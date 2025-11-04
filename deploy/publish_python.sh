#!/bin/bash

# Script to publish Python SDK to PyPI
# Usage: ./deploy/publish_python.sh [testpypi|pypi]

set -e

REPOSITORY=${1:-pypi}

echo "🚀 Publishing BaseAI Python SDK to $REPOSITORY..."

# Check if we're in the right directory
if [ ! -d "python" ]; then
    echo "❌ Error: python directory not found. Run from repository root."
    exit 1
fi

cd python

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "📦 Installing twine..."
    pip install twine build
fi

# Check if build is installed
if ! python -m build --version &> /dev/null; then
    echo "📦 Installing build..."
    pip install build
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Build the package
echo "📦 Building package..."
python -m build

# Check the package
echo "✅ Checking package..."
twine check dist/*

# Upload to PyPI
if [ "$REPOSITORY" = "testpypi" ]; then
    echo "📤 Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Published to Test PyPI: https://test.pypi.org/project/baseai/"
else
    echo "📤 Uploading to PyPI..."
    twine upload --repository pypi dist/*
    echo "✅ Published to PyPI: https://pypi.org/project/baseai/"
fi

echo "🎉 Python SDK published successfully!"

