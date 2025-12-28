# A2ABase TypeScript/JavaScript Examples

This directory contains comprehensive examples demonstrating how to use the A2ABase TypeScript/JavaScript SDK.

## Prerequisites

1. Install dependencies:
```bash
npm install
```

2. Set your API key:
```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
```

## Running Examples

### Compile TypeScript

```bash
npm run build
```

### Run Examples

```bash
# Customer Support Triage Agent
node dist/example/customer_support_triage.js

# File Manager Agent
node dist/example/file_manager_agent.js

# Research Agent
node dist/example/research_agent.js

# Web Development Agent
node dist/example/web_development_agent.js
```

## Running in Notebooks

Google Colab primarily supports Python. For TypeScript/JavaScript, use:

**Option 1: Observable Notebooks**
1. Go to [Observable](https://observablehq.com/)
2. Create a new notebook
3. Install: `npm install a2abase`
4. Copy example code from files in this directory

**Option 2: Jupyter with JavaScript kernel**
1. Install: `npm install -g ijavascript`
2. Install kernel: `jupyter kernelspec install --name javascript --user`
3. Start Jupyter: `jupyter notebook`
4. Create a new JavaScript notebook
5. Copy example code from files in this directory

## Available Examples

### Search and Browser
- **`customer_support_triage.ts`** - Demonstrates `WEB_SEARCH_TOOL` for monitoring and triaging support tickets

### File Management
- **`file_manager_agent.ts`** - Demonstrates `FILES_TOOL` for reading, writing, and managing files

### Development Tools
- **`web_development_agent.ts`** - Demonstrates `WEB_DEV_TOOL` for creating modern web applications with Next.js and shadcn/ui

### Research and Analysis
- **`research_agent.ts`** - Demonstrates `WEB_SEARCH_TOOL` and `BROWSER_TOOL` for comprehensive research tasks

## Example Structure

All examples follow this pattern:

1. **Get API key from environment variable** - Check for `BASEAI_API_KEY` and fail fast with helpful error
2. **Create an A2ABase client** - Initialize with API key and URL
3. **Create or find an agent** - Use `findByName` to reuse existing agents or create new ones
4. **Run the agent with a prompt** - Execute the agent with a specific task
5. **Stream and print the response** - Process the streaming response in real-time
6. **Clean up** - Delete the agent if it was created for this example

## Example Code Pattern

```typescript
import { A2ABase } from '../src/a2abase';
import { A2ABaseTool } from '../src/tools';

async function main() {
  const apiKey = process.env.BASEAI_API_KEY;
  if (!apiKey || apiKey === 'YOUR_API_KEY') {
    throw new Error('Please set BASEAI_API_KEY environment variable');
  }

  const client = new A2ABase({
    apiKey,
    apiUrl: 'https://a2abase.ai/api',
  });

  const thread = await client.Thread.create();
  const desiredName = 'My Agent';
  let agent = await client.Agent.findByName(desiredName);
  let created = false;

  if (!agent) {
    agent = await client.Agent.create({
      name: desiredName,
      systemPrompt: 'You are a helpful assistant.',
      a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL],
    });
    created = true;
  }

  const run = await agent.run('Your task here', thread);
  const stream = await run.getStream();

  for await (const chunk of stream) {
    process.stdout.write(chunk);
  }

  if (created) {
    await agent.delete();
  }
}

main().catch(console.error);
```

## Available Tools

The SDK provides access to various tools through the `A2ABaseTool` enum:

- **File Management**: `FILES_TOOL`, `UPLOAD_FILE_TOOL`
- **Development**: `SHELL_TOOL`, `WEB_DEV_TOOL`, `DEPLOY_TOOL`, `EXPOSE_TOOL`
- **Image Tools**: `VISION_TOOL`, `IMAGE_SEARCH_TOOL`, `IMAGE_EDIT_TOOL`
- **Content Creation**: `DOCS_TOOL`, `SHEETS_TOOL`, `PRESENTATION_TOOL`, `PRESENTATION_OUTLINE_TOOL`, `DESIGN_TOOL`
- **Knowledge & Data**: `KB_TOOL`, `DATA_PROVIDERS_TOOL`
- **Search & Browser**: `WEB_SEARCH_TOOL`, `BROWSER_TOOL`

## For More Examples

See the [Python examples](../python/example/) for additional use cases and tool demonstrations, including:
- Tool-specific examples for each available tool
- Common use case examples (research, automation, content creation, etc.)
- Multi-agent workflows

