# BaseAI SDKs

Multi-language SDKs for interacting with the BaseAI platform. This repository contains official SDKs for Python and TypeScript/JavaScript.

## 📦 Available SDKs

- **[Python](./python/)** - `pip install baseai-sdk` | [PyPI Package](https://pypi.org/project/baseai-sdk/)
- **[TypeScript/JavaScript](./typescript/)** - `npm install @belarabyai/baseai` | [npm Package](https://www.npmjs.com/package/@belarabyai/baseai)

## 🚀 Quick Start

### Python

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

### TypeScript/JavaScript

```typescript
import { BaseAI } from '@belarabyai/baseai';
import { BaseAITool } from '@belarabyai/baseai';

async function main() {
  const apiKey = process.env.BASEAI_API_KEY;
  if (!apiKey) {
    throw new Error('Please set BASEAI_API_KEY environment variable');
  }

  const client = new BaseAI({
    apiKey,
    apiUrl: 'https://a2abase.ai/api',
  });

  const thread = await client.Thread.create();
  const agent = await client.Agent.create({
    name: 'My Assistant',
    systemPrompt: 'You are a helpful AI assistant.',
    mcpTools: [BaseAITool.WEB_SEARCH_TOOL],
  });

  const run = await agent.run('Hello, how are you?', thread);
  const stream = await run.getStream();
  
  for await (const chunk of stream) {
    process.stdout.write(chunk);
  }
}

main();
```


## 🔑 Getting Your API Key

Get your API key from https://a2abase.ai/settings/api-keys

Set it as an environment variable:

```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
```

## 📚 Examples

Both SDKs include comprehensive examples:

- **[Python Examples](./python/example/)** - Tool-specific examples and common use cases
- **[TypeScript Examples](./typescript/example/)** - Tool-specific examples and common use cases

### Running Examples

**Python:**
- Run scripts: `cd python && PYTHONPATH=. python3 example/<name>.py`
- Run in Google Colab: See [Python README](./python/README.md#running-examples-in-google-colab) for instructions

**TypeScript:**
- Run compiled: `npm run build && node dist/example/<name>.js`

### Available Tools

Both SDKs provide access to the same set of tools through the `BaseAITool` enum:

- **File Management**: `FILES_TOOL`, `UPLOAD_FILE_TOOL`
- **Development**: `SHELL_TOOL`, `WEB_DEV_TOOL`, `DEPLOY_TOOL`, `EXPOSE_TOOL`
- **Image Tools**: `VISION_TOOL`, `IMAGE_SEARCH_TOOL`, `IMAGE_EDIT_TOOL`
- **Content Creation**: `DOCS_TOOL`, `SHEETS_TOOL`, `PRESENTATION_TOOL`, `PRESENTATION_OUTLINE_TOOL`, `DESIGN_TOOL`
- **Knowledge & Data**: `KB_TOOL`, `DATA_PROVIDERS_TOOL`
- **Search & Browser**: `WEB_SEARCH_TOOL`, `BROWSER_TOOL`

## 📚 Documentation

Each SDK has its own documentation:

- [Python SDK Documentation](./python/README.md)
- [TypeScript SDK Documentation](./typescript/README.md)

## 💬 Support

Need help? Join our Discord community for support and discussions:

- **Discord**: [https://discord.gg/qAncfHmYUm](https://discord.gg/qAncfHmYUm)

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines for each SDK.

## 📄 License

MIT License - see LICENSE file for details.

