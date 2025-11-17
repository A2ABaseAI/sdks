/**
 * Example: Research Agent
 * Demonstrates web search and browser tools for research tasks.
 */
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
  const desiredName = 'Research Agent';
  let agent = await client.Agent.findByName(desiredName);
  let created = false;

  if (!agent) {
    agent = await client.Agent.create({
      name: desiredName,
      systemPrompt: 'You are a research assistant. You can search the web, browse websites, analyze information from multiple sources, and compile comprehensive reports.',
      a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL, A2ABaseTool.BROWSER_TOOL],
    });
    created = true;
  }

  const run = await agent.run(
    'Research the latest developments in AI safety and create a comprehensive report with citations.',
    thread
  );
  const stream = await run.getStream();

  for await (const chunk of stream) {
    process.stdout.write(chunk);
  }

  if (created) {
    await agent.delete();
  }
}

main().catch(console.error);

