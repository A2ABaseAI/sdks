"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Example: Web Development Agent
 * Demonstrates WEB_DEV_TOOL for creating modern web applications.
 */
const a2abase_1 = require("../src/a2abase");
const tools_1 = require("../src/tools");
async function main() {
    const apiKey = process.env.BASEAI_API_KEY;
    if (!apiKey || apiKey === 'YOUR_API_KEY') {
        throw new Error('Please set BASEAI_API_KEY environment variable');
    }
    const client = new a2abase_1.A2ABase({
        apiKey,
        apiUrl: 'https://a2abase.ai/api',
    });
    const thread = await client.Thread.create();
    const desiredName = 'Web Development Agent';
    let agent = await client.Agent.findByName(desiredName);
    let created = false;
    if (!agent) {
        agent = await client.Agent.create({
            name: desiredName,
            systemPrompt: 'You are a web development assistant. You can create modern web applications using Next.js and shadcn/ui. Help users build responsive, accessible, and performant web applications.',
            a2abaseTools: [tools_1.A2ABaseTool.WEB_DEV_TOOL],
        });
        created = true;
    }
    const run = await agent.run('Create a simple todo list application with Next.js and shadcn/ui components.', thread);
    const stream = await run.getStream();
    for await (const chunk of stream) {
        process.stdout.write(chunk);
    }
    if (created) {
        await agent.delete();
    }
}
main().catch(console.error);
