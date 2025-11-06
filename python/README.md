# BaseAI Python SDK

> **One SDK. Unlimited Tools. Build AI Agents in Minutes.**

Official Python SDK for building powerful AI agents with access to 50+ built-in tools, 300+ integrations, and all major LLMs—all through a single, unified platform.

📹 **Watch the Demo**: [YouTube Video](https://youtu.be/bxJvMlVs2Mg)

## 🚀 Why BaseAI?

**Stop juggling multiple tools, APIs, and accounts.** BaseAI consolidates everything you need into one simple SDK.

### The Problem You're Solving

Building AI agents today means:
- ❌ Managing 10+ different API keys and accounts
- ❌ Integrating multiple libraries and SDKs
- ❌ Searching for the right tools and benchmarking
- ❌ Building custom integrations from scratch
- ❌ Dealing with authentication and security concerns
- ❌ Paying multiple subscription fees

### The BaseAI Solution

**One SDK. One API key. Everything you need.**

- ✅ **50+ built-in tools** - Everything from web search to image editing to web development
- ✅ **300+ MCP integrations** - Access 200+ Composio integrations (Gmail, Slack, GitHub, etc.) plus custom MCP servers
- ✅ **All LLMs in one place** - Unified access to multiple language models
- ✅ **Isolated sandboxes** - Secure execution environments built-in
- ✅ **Pay-as-you-go pricing** - 80% cheaper than alternatives
- ✅ **Type-safe SDK** - Full IDE support for Python

**Install one SDK. Access everything. Build a working prototype in minutes.**

## 💰 Pricing

### Pay-As-You-Go Model

BaseAI uses transparent, pay-as-you-go pricing with **no hidden fees**.

**80% Cheaper Than Alternatives**

Unlike traditional platforms that require:
- Multiple subscription fees for different services
- Per-user licensing costs
- Minimum monthly commitments
- Platform lock-in fees

BaseAI charges you only for what you use, when you use it. No minimums. Just simple, transparent pricing that scales with your needs.

### What You Get

- **Access to all tools** - No per-tool pricing
- **All LLMs** - Unified access without separate accounts
- **300+ integrations** - No per-integration fees
- **Isolated sandboxes** - Included at no extra cost
- **Full SDK support** - Python SDK included

**Get started today**: [Get your API key](https://a2abase.ai/settings/api-keys)

## Installation

```bash
pip install a2abase-sdk
```

📦 **Published on PyPI**: [https://pypi.org/project/a2abase-sdk/](https://pypi.org/project/a2abase-sdk/)

Or install directly from GitHub:

```bash
pip install git+https://github.com/A2ABaseAI/sdks.git#subdirectory=python
```

## Requirements

- Python 3.11+
- See [requirements.txt](./requirements.txt) for dependencies

## 🚀 Quick Start

```python
import asyncio
import os
from baseai import BaseAI
from baseai.tools import BaseAITool

async def main():
    api_key = os.getenv("BASEAI_API_KEY")
    if not api_key:
        raise ValueError("Please set BASEAI_API_KEY environment variable")
    
    client = BaseAI(api_key=api_key, api_url="https://a2abase.ai/api")
    
    thread = await client.Thread.create()
    agent = await client.Agent.create(
        name="My Assistant",
        system_prompt="You are a helpful AI assistant.",
        mcp_tools=[BaseAITool.WEB_SEARCH_TOOL],
    )
    
    run = await agent.run("Hello, how are you?", thread)
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="")

asyncio.run(main())
```

## 🔑 Getting Your API Key

1. Sign up at [BaseAI](https://a2abase.ai/settings/api-keys)
2. Get your API key from the dashboard
3. Set it as an environment variable:

```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
```

That's it! You're ready to build.

## 🛠️ Available Tools

The SDK provides access to the same comprehensive set of tools through the `BaseAITool` enum:

### File Management
- `FILES_TOOL` - Read, write, and edit files in the sandbox
- `UPLOAD_FILE_TOOL` - Upload files to the sandbox workspace

### Development & Automation
- `SHELL_TOOL` - Execute shell commands in isolated sandboxes
- `WEB_DEV_TOOL` - Create and manage modern web applications (Next.js, React, Vite, shadcn/ui)
- `DEPLOY_TOOL` - Deploy web applications to production
- `EXPOSE_TOOL` - Expose local services to the internet
- Project templates - Scaffold projects from predefined templates

### Image & Vision
- `VISION_TOOL` - Analyze and understand images with AI
- `IMAGE_SEARCH_TOOL` - Search for images on the web
- `IMAGE_EDIT_TOOL` - Edit and manipulate images
- `DESIGN_TOOL` - Design and create visual content

### Content Creation
- `DOCS_TOOL` - Create and manage documents (HTML, Markdown formats)
- `SHEETS_TOOL` - Create and manage spreadsheets with data analysis, visualization, and formatting
- `PRESENTATION_TOOL` - Create and manage presentations
- `PRESENTATION_OUTLINE_TOOL` - Create presentation outlines

### Search & Browser
- `WEB_SEARCH_TOOL` - Search the web for information
- `BROWSER_TOOL` - Browse websites and interact with web pages (navigate, click, fill forms, scroll)

### Research & Intelligence
- People search - Search for people and enrich profiles
- Company search - Search for companies and business information
- Paper search - Search academic papers and research documents
- Web search - General web search capabilities

### Knowledge & Data
- `KB_TOOL` - Access and manage knowledge base (local and global sync)
- `DATA_PROVIDERS_TOOL` - Access structured data from providers:
  - LinkedIn - Professional network data
  - Yahoo Finance - Financial market data
  - Amazon - Product and marketplace data
  - Zillow - Real estate data
  - Twitter - Social media data
  - ActiveJobs - Job listings data

### Agent Management
- Agent creation - Create and configure AI agents
- Agent configuration - Manage agent settings and versions
- Workflow management - Create and manage agent workflows
- Trigger management - Set up automated triggers
- Credential profiles - Manage API credentials

### Task Management
- Task list - Create, update, and manage tasks organized by sections
- Task tracking - Track completion status and progress
- Batch operations - Manage multiple tasks at once

### Communication
- Message tool - Ask questions, inform users, and mark completion
- Message expansion - Expand truncated messages from previous conversations

### Automation
- Computer use - Control sandbox browser and GUI (mouse, keyboard, screenshots)
- Document parser - Parse and extract data from documents

### Templates & Scaffolding
- Project templates - Generate projects from predefined templates
- Template search - Search and discover available templates

## 🔌 MCP Integrations

BaseAI supports **300+ MCP (Model Context Protocol) integrations** through Composio and custom MCP servers, allowing you to connect any MCP-compatible server. MCPs can be connected via:

- HTTP/HTTPS endpoints
- SSE (Server-Sent Events)
- stdio (standard input/output)

### Composio MCP Integrations (200+)

BaseAI integrates with [Composio.dev](https://composio.dev) to provide access to **200+ pre-configured MCP servers** including:

**Productivity & Communication**
- Gmail, Google Calendar, Slack, Microsoft Teams, Notion, Linear, Asana, Jira, Trello, Airtable

**Code & Development**
- GitHub, GitLab, Bitbucket, Docker Hub, AWS, Google Cloud Platform, Azure

**CRM & Sales**
- Salesforce, HubSpot, Pipedrive, Zoho CRM, Intercom

**Data & Analytics**
- Google Sheets, Google Drive, Dropbox, Airtable, MongoDB, PostgreSQL, MySQL

**Marketing & Social**
- Twitter/X, LinkedIn, Facebook, Instagram, Mailchimp, SendGrid

**E-commerce & Payments**
- Shopify, Stripe, PayPal, WooCommerce, Square

**And 150+ more integrations** including project management tools, databases, cloud services, APIs, and business applications.

### Custom MCP Servers

You can also connect any custom MCP-compatible server by providing the MCP endpoint URL. This enables integration with any tool, API, or service that follows the Model Context Protocol standard.

## Usage

### Creating an Agent

```python
from baseai import BaseAI
from baseai.tools import BaseAITool

client = BaseAI(api_key="your-api-key", api_url="https://a2abase.ai/api")

# Create an agent with tools
agent = await client.Agent.create(
    name="My Agent",
    system_prompt="You are a helpful assistant.",
    mcp_tools=[BaseAITool.WEB_SEARCH_TOOL, BaseAITool.FILES_TOOL],
)
```

### Running an Agent

```python
# Create a thread
thread = await client.Thread.create()

# Run the agent
run = await agent.run("Your task here", thread)

# Stream the response
stream = await run.get_stream()
async for chunk in stream:
    print(chunk, end="")
```

### Finding an Existing Agent

```python
# Find agent by name
agent = await client.Agent.find_by_name("My Agent")
if agent:
    # Use the existing agent
    pass
```

## 📚 Examples

Comprehensive examples are available in the [`example/`](./example/) directory, demonstrating:

- **Tool-Specific Examples**: Each tool from `BaseAITool` enum with practical use cases
- **Common Use Cases**: Real-world scenarios like research, content creation, automation, and more

See the [examples README](./example/README.md) for a complete list of available examples.

### Running Examples

**Python:**
- Run scripts: `cd python && PYTHONPATH=. python3 example/<name>.py`
- Run in Google Colab: See [Running Examples in Google Colab](#running-examples-in-google-colab) for instructions

### Running All Examples

```bash
cd python
PYTHONPATH=. python3 example/run_all_examples.py
```

### Running Examples in Google Colab

To run examples in Google Colab:

**Option 1: Open from GitHub**
1. Go to [Google Colab](https://colab.research.google.com/)
2. Click "File" → "Open notebook"
3. Select the "GitHub" tab
4. Enter: `A2ABaseAI/sdks`
5. Navigate to `python/example/quick_start.ipynb` or any `.py` file

**Option 2: Manual Setup**
1. Open [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Copy the code from any example file
4. Adapt it for notebook use (remove `if __name__ == "__main__"` and use `await` directly)

**Quick Start in Colab:**

```python
# Install the SDK
!pip install a2abase-sdk

import os
from baseai import BaseAI
from baseai.tools import BaseAITool

# Set your API key (use Colab's secrets or environment variables)
os.environ['BASEAI_API_KEY'] = 'pk_xxx:sk_xxx'

# Create client
client = BaseAI(api_key=os.getenv("BASEAI_API_KEY"), api_url="https://a2abase.ai/api")

# Create thread and agent
thread = await client.Thread.create()
agent = await client.Agent.create(
    name="My Assistant",
    system_prompt="You are a helpful AI assistant.",
    mcp_tools=[BaseAITool.WEB_SEARCH_TOOL],
)

# Run the agent
run = await agent.run("Hello, how are you?", thread)
stream = await run.get_stream()

# Stream and display results
async for chunk in stream:
    print(chunk, end="")
```

**Note:** In Google Colab, you can use `await` directly in cells without `asyncio.run()`.

## 📖 Documentation

- **PyPI Package**: [https://pypi.org/project/a2abase-sdk/](https://pypi.org/project/a2abase-sdk/)
- **GitHub Repository**: [https://github.com/A2ABaseAI/sdks](https://github.com/A2ABaseAI/sdks)
- **Full Documentation**: See the [repository](https://github.com/A2ABaseAI/sdks) for more examples and API reference.

## 💬 Support

Need help? Join our Discord community for support and discussions:

- **Discord**: [https://discord.gg/qAncfHmYUm](https://discord.gg/qAncfHmYUm)

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines.

## 📄 License

MIT License - see LICENSE file for details.
