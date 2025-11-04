# Deployment Guide

This directory contains scripts and configuration for publishing the BaseAI SDKs to their respective package registries.

## Prerequisites

### Python SDK (PyPI)
- Python 3.11+
- `pip` and `twine` installed
- PyPI credentials configured

### TypeScript SDK (npm)
- Node.js 18+
- npm credentials configured
- npm account with access to publish `@belarabyai/baseai` (scoped package)

## Quick Start - Publishing Both SDKs

### Step-by-Step Guide

#### 1. Python SDK (PyPI)

**Get PyPI API Token:**
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Copy the token (starts with `pypi-`)

**Set credentials and publish:**
```bash
# Set environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your_token_here

# Navigate to Python directory
cd python

# Build the package
python3 -m build

# Check the package
python3 -m twine check dist/*

# Publish to PyPI
python3 -m twine upload dist/*
```

**Or use the script:**
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your_token_here
./deploy/publish_python.sh pypi
```

#### 2. TypeScript SDK (npm)

**Login to npm:**
```bash
cd typescript
npm login
```
When prompted, enter:
- **Username**: `belarabyai`
- **Password**: (your npm password)
- **Email**: (your email address)

**Publish:**
```bash
# Build (automatically runs before publish)
npm run build

# Publish to npm (scoped packages need --access public)
npm publish --access public
```

**Or use the script:**
```bash
./deploy/publish_typescript.sh
```

---

## Manual Deployment (Detailed)

### Python SDK

1. **Update version in `python/pyproject.toml`**
   ```toml
   version = "0.1.0"  # Update version
   ```

2. **Get PyPI API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create a new token
   - Copy it (starts with `pypi-`)

3. **Set environment variables**
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your_token_here
   ```

4. **Build the package**
   ```bash
   cd python
   python3 -m build
   ```

5. **Test the package**
   ```bash
   python3 -m twine check dist/*
   ```

6. **Upload to PyPI**
   ```bash
   # Production PyPI
   python3 -m twine upload dist/*
   ```

Or use the deployment script:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your_token_here
./deploy/publish_python.sh pypi
```

### TypeScript SDK

1. **Update version in `typescript/package.json`**
   ```json
   "version": "0.1.0"  // Update version
   ```

2. **Login to npm**
   ```bash
   cd typescript
   npm login
   ```
   When prompted, enter:
   - **Username**: `belarabyai`
   - **Password**: (your npm password)
   - **Email**: (your email address)

3. **Verify login**
   ```bash
   npm whoami
   ```

4. **Build the package**
   ```bash
   npm run build
   ```

5. **Test publish (dry-run)**
   ```bash
   npm publish --dry-run
   ```

6. **Publish to npm**
   ```bash
   npm publish --access public
   ```
   
   **Note:** The package name is `@belarabyai/baseai` (scoped). You need to own the `@belarabyai` scope on npm.

Or use the deployment script:
```bash
./deploy/publish_typescript.sh
```

## Automated Deployment

### GitHub Actions

GitHub Actions workflows are available in `.github/workflows/` for automated publishing:

- **Python**: Publishes to PyPI on tag push
- **TypeScript**: Publishes to npm on tag push

To trigger a release:
1. Update version in `python/pyproject.toml` and `typescript/package.json`
2. Commit and push changes
3. Create and push a git tag:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

## Version Management

Versions should be kept in sync across both SDKs:
- Python: `python/pyproject.toml`
- TypeScript: `typescript/package.json`

Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Environment Variables

### Python (PyPI)

#### Getting a PyPI API Token

1. **Create/Login to PyPI account**
   - Go to https://pypi.org/account/register/ (if new account)
   - Or login at https://pypi.org/account/login/

2. **Generate API Token**
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Enter a name (e.g., "baseai-sdk-deployment")
   - Choose scope:
     - **Entire account**: Can publish to all projects
     - **Project-specific**: Only for specific project
   - Click "Add token"
   - **IMPORTANT**: Copy the token immediately (you won't see it again!)
   - Format: `pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

3. **Set Environment Variables**

   **Option 1: Export in current session**
   ```bash
   export TWINE_USERNAME=__token__
   ```
   
   **Option 2: Add to your shell profile** (permanent)
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   echo 'export TWINE_USERNAME=' >> ~/.zshrc
   source ~/.zshrc
   ```
   
   **Option 3: Use a .env file** (recommended for security)
   ```bash
   # Create .env file in deploy/ directory
   cat > deploy/.env << EOF
   TWINE_USERNAME=__token__
   TWINE_PASSWORD=pypi-your_actual_token_here
   EOF
   
   # Source it before deploying
   source deploy/.env
   ```
   
   **Option 4: Use twine config file** (alternative)
   ```bash
   # Create ~/.pypirc
   cat > ~/.pypirc << EOF
   [pypi]
   username = __token__
   password = pypi-your_actual_token_here
   EOF
   chmod 600 ~/.pypirc  # Secure the file
   ```

#### Using the Token

```bash
# Verify token is set
echo $TWINE_USERNAME
echo $TWINE_PASSWORD

# Upload to PyPI
cd python
python3 -m twine upload dist/*
```

#### Security Best Practices

- ✅ **Use API tokens** instead of passwords (more secure, revocable)
- ✅ **Store tokens in environment variables** or secure config files
- ✅ **Never commit tokens** to git (add `.env` to `.gitignore`)
- ✅ **Use project-specific tokens** when possible (limited scope)
- ✅ **Revoke old tokens** if compromised or no longer needed

### TypeScript (npm)

#### Getting an npm Token

1. **Login to npm**
   ```bash
   npm login
   ```
   Enter your username, password, and email

2. **Generate Access Token** (for CI/CD)
   - Go to https://www.npmjs.com/settings/YOUR_USERNAME/tokens
   - Click "Generate New Token"
   - Choose token type:
     - **Automation**: For CI/CD (recommended)
     - **Publish**: For publishing packages
     - **Read-only**: For reading packages
   - Copy the token

3. **Set Environment Variable**
   ```bash
   export NPM_TOKEN=npm_your_actual_token_here
   ```

### GitHub Secrets (for Automated Deployment)

Add these as secrets in your GitHub repository:

1. Go to: `Settings` → `Secrets and variables` → `Actions`
2. Click "New repository secret"
3. Add:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Your PyPI API token (starts with `pypi-`)
   
   - **Name**: `NPM_TOKEN`
   - **Value**: Your npm token (starts with `npm_`)

Then the GitHub Actions workflows will automatically use these tokens.

