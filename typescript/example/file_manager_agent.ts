/**
 * Example: File Manager Agent
 * Demonstrates FILES_TOOL for reading, writing, and managing files.
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
  const desiredName = 'File Manager Agent';
  let agent = await client.Agent.findByName(desiredName);
  let created = false;

  if (!agent) {
    agent = await client.Agent.create({
      name: desiredName,
      systemPrompt: 'You are a file management assistant. You can read, write, edit, and organize files. Help users manage their file system, create documentation, organize files into directories, and perform file operations safely.',
      a2abaseTools: [A2ABaseTool.FILES_TOOL],
    });
    created = true;
  }

  const run = await agent.run(
    "Create a README.md file for this project describing the file structure, then organize any loose files into appropriate directories.",
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

