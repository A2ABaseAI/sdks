# BaseAI TypeScript/JavaScript SDK

TypeScript/JavaScript SDK for the BaseAI platform.

## Installation

```bash
npm install @belarabyai/baseai
```

Or with yarn:

```bash
yarn add @belarabyai/baseai
```

## Quick Start

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

## Building

```bash
npm run build
```

## Examples

Comprehensive examples are available in the [`example/`](./example/) directory, demonstrating:

- **Tool-Specific Examples**: Each tool from `BaseAITool` enum with practical use cases
- **Common Use Cases**: Real-world scenarios like research, content creation, automation, and more

See the [examples README](./example/README.md) for a complete list of available examples.

To run an example:

```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
npm run build
node dist/example/customer_support_triage.js
```

## Available Tools

The SDK provides access to various tools through the `BaseAITool` enum:

- **File Management**: `FILES_TOOL`, `UPLOAD_FILE_TOOL`
- **Development**: `SHELL_TOOL`, `WEB_DEV_TOOL`, `DEPLOY_TOOL`, `EXPOSE_TOOL`
- **Image Tools**: `VISION_TOOL`, `IMAGE_SEARCH_TOOL`, `IMAGE_EDIT_TOOL`
- **Content Creation**: `DOCS_TOOL`, `SHEETS_TOOL`, `PRESENTATION_TOOL`, `PRESENTATION_OUTLINE_TOOL`, `DESIGN_TOOL`
- **Knowledge & Data**: `KB_TOOL`, `DATA_PROVIDERS_TOOL`
- **Search & Browser**: `WEB_SEARCH_TOOL`, `BROWSER_TOOL`

## Documentation

See the [full documentation](https://github.com/A2ABaseAI/sdks) for more examples and API reference.

