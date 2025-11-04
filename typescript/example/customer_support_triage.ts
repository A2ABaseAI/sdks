/**
 * Example: Customer Support Triage Agent
 * Demonstrates web search tools for monitoring and triaging support tickets.
 */
import { BaseAI } from '../src/baseai';
import { BaseAITool } from '../src/tools';

async function main() {
  const apiKey = process.env.BASEAI_API_KEY;
  if (!apiKey || apiKey === 'YOUR_API_KEY') {
    throw new Error('Please set BASEAI_API_KEY environment variable');
  }

  const client = new BaseAI({
    apiKey,
    apiUrl: 'https://a2abase.ai/api',
  });

  const thread = await client.Thread.create();
  const desiredName = 'Customer Support Triage';
  let agent = await client.Agent.findByName(desiredName);
  let created = false;

  if (!agent) {
    agent = await client.Agent.create({
      name: desiredName,
      systemPrompt: 'Monitor support inbox, label priority, suggest responses, and escalate critical issues.',
      mcpTools: [BaseAITool.WEB_SEARCH_TOOL],
    });
    created = true;
  }

  const run = await agent.run("Triage today's new tickets and propose responses.", thread);
  const stream = await run.getStream();

  for await (const chunk of stream) {
    process.stdout.write(chunk);
  }

  if (created) {
    await agent.delete();
  }
}

main().catch(console.error);

