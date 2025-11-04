# BaseAI Python SDK

Python SDK for the BaseAI platform.

## Installation

```bash
pip install baseai-sdk
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/A2ABaseAI/sdks.git#subdirectory=python
```

## Requirements

- Python 3.8+
- See [requirements.txt](./requirements.txt) for dependencies

## Quick Start

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

## Getting Your API Key

Get your API key from https://a2abase.ai/settings/api-keys

Set it as an environment variable:

```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
```

## Examples

Comprehensive examples are available in the [`example/`](./example/) directory, demonstrating:

- **Tool-Specific Examples**: Each tool from `BaseAITool` enum with practical use cases
- **Common Use Cases**: Real-world scenarios like research, content creation, automation, and more

See the [examples README](./example/README.md) for a complete list of available examples.

### Running Examples

```bash
# Set your API key
export BASEAI_API_KEY="pk_xxx:sk_xxx"

# Run an example
cd python
PYTHONPATH=. python3 example/customer_support_triage.py
```

### Running All Examples

```bash
cd python
PYTHONPATH=. python3 example/run_all_examples.py
```

## Available Tools

The SDK provides access to various tools through the `BaseAITool` enum:

- **File Management**: `FILES_TOOL`, `UPLOAD_FILE_TOOL`
- **Development**: `SHELL_TOOL`, `WEB_DEV_TOOL`, `DEPLOY_TOOL`, `EXPOSE_TOOL`
- **Image Tools**: `VISION_TOOL`, `IMAGE_SEARCH_TOOL`, `IMAGE_EDIT_TOOL`
- **Content Creation**: `DOCS_TOOL`, `SHEETS_TOOL`, `PRESENTATION_TOOL`, `PRESENTATION_OUTLINE_TOOL`, `DESIGN_TOOL`
- **Knowledge & Data**: `KB_TOOL`, `DATA_PROVIDERS_TOOL`
- **Search & Browser**: `WEB_SEARCH_TOOL`, `BROWSER_TOOL`

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

## Documentation

See the [full documentation](https://github.com/A2ABaseAI/sdks) for more examples and API reference.

## License

MIT License - see LICENSE file for details.
