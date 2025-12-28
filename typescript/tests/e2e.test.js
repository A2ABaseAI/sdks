"use strict";
/**
 * Comprehensive E2E test with real API
 * Tests the full flow: client creation, agent management, thread management, and agent execution
 */
Object.defineProperty(exports, "__esModule", { value: true });
const a2abase_1 = require("../src/a2abase");
const tools_1 = require("../src/tools");
describe('E2E Tests with Real API', () => {
    const apiKey = process.env.BASEAI_API_KEY;
    const apiUrl = process.env.BASEAI_API_URL || 'https://a2abase.ai/api';
    if (!apiKey || apiKey === 'YOUR_API_KEY') {
        console.warn('Skipping E2E tests: BASEAI_API_KEY not set');
        return;
    }
    let client;
    let testAgentId = null;
    let testThreadId = null;
    beforeAll(() => {
        client = new a2abase_1.A2ABase({
            apiKey,
            apiUrl,
        });
    });
    afterAll(async () => {
        // Cleanup: delete test agent and thread if they were created
        if (testAgentId) {
            try {
                const agent = await client.Agent.get(testAgentId);
                await agent.delete();
            }
            catch (error) {
                // Ignore cleanup errors
            }
        }
        if (testThreadId) {
            try {
                await client.Thread.delete(testThreadId);
            }
            catch (error) {
                // Ignore cleanup errors
            }
        }
    });
    describe('Client Initialization', () => {
        it('should create A2ABase client with default URL', () => {
            const defaultClient = new a2abase_1.A2ABase({
                apiKey: 'test-key',
            });
            expect(defaultClient).toBeDefined();
            expect(defaultClient.Agent).toBeDefined();
            expect(defaultClient.Thread).toBeDefined();
        });
        it('should create A2ABase client with custom URL', () => {
            const customClient = new a2abase_1.A2ABase({
                apiKey: 'test-key',
                apiUrl: 'https://custom.api.com',
            });
            expect(customClient).toBeDefined();
        });
        it('should create A2ABase client with timeout', () => {
            const timeoutClient = new a2abase_1.A2ABase({
                apiKey: 'test-key',
                timeout: 60000,
            });
            expect(timeoutClient).toBeDefined();
        });
    });
    describe('Agent Management', () => {
        const testAgentName = `E2E Test Agent ${Date.now()}`;
        it('should create an agent with tools', async () => {
            const agent = await client.Agent.create({
                name: testAgentName,
                systemPrompt: 'You are a helpful test assistant for E2E testing.',
                a2abaseTools: [tools_1.A2ABaseTool.WEB_SEARCH_TOOL],
            });
            expect(agent).toBeDefined();
            testAgentId = (await agent.details()).agent_id;
            expect(testAgentId).toBeDefined();
        }, 30000);
        it('should get agent details', async () => {
            if (!testAgentId) {
                throw new Error('Test agent not created');
            }
            const agent = await client.Agent.get(testAgentId);
            const details = await agent.details();
            expect(details).toBeDefined();
            expect(details.agent_id).toBe(testAgentId);
            expect(details.name).toBe(testAgentName);
            expect(details.system_prompt).toContain('E2E testing');
        }, 30000);
        it('should find agent by name', async () => {
            const foundAgent = await client.Agent.findByName(testAgentName);
            expect(foundAgent).not.toBeNull();
            if (foundAgent) {
                const details = await foundAgent.details();
                expect(details.name).toBe(testAgentName);
            }
        }, 30000);
        it('should update agent', async () => {
            if (!testAgentId) {
                throw new Error('Test agent not created');
            }
            const agent = await client.Agent.get(testAgentId);
            const newPrompt = 'Updated system prompt for E2E testing';
            await agent.update({
                systemPrompt: newPrompt,
            });
            const details = await agent.details();
            expect(details.system_prompt).toBe(newPrompt);
        }, 30000);
        it('should get agents list', async () => {
            const response = await client.getAgents({
                page: 1,
                limit: 10,
            });
            expect(response).toBeDefined();
            expect(response.agents).toBeInstanceOf(Array);
            expect(response.pagination).toBeDefined();
            expect(response.pagination.page).toBeGreaterThanOrEqual(1);
        }, 30000);
    });
    describe('Thread Management', () => {
        it('should create a thread', async () => {
            const thread = await client.Thread.create();
            expect(thread).toBeDefined();
            expect(thread.threadId).toBeDefined();
            testThreadId = thread.threadId;
        }, 30000);
        it('should create a thread with name', async () => {
            const threadName = `E2E Test Thread ${Date.now()}`;
            const thread = await client.Thread.create(threadName);
            expect(thread).toBeDefined();
            expect(thread.threadId).toBeDefined();
            // Cleanup
            await client.Thread.delete(thread.threadId);
        }, 30000);
        it('should get thread by ID', async () => {
            if (!testThreadId) {
                throw new Error('Test thread not created');
            }
            const thread = await client.Thread.get(testThreadId);
            expect(thread).toBeDefined();
            expect(thread.threadId).toBe(testThreadId);
        }, 30000);
        it('should add message to thread', async () => {
            if (!testThreadId) {
                throw new Error('Test thread not created');
            }
            const thread = await client.Thread.get(testThreadId);
            const messageId = await thread.addMessage('Hello from E2E test');
            expect(messageId).toBeDefined();
            expect(typeof messageId).toBe('string');
        }, 30000);
        it('should get messages from thread', async () => {
            if (!testThreadId) {
                throw new Error('Test thread not created');
            }
            const thread = await client.Thread.get(testThreadId);
            const messages = await thread.getMessages();
            expect(messages).toBeInstanceOf(Array);
            expect(messages.length).toBeGreaterThan(0);
        }, 30000);
        it('should get agent runs from thread', async () => {
            if (!testThreadId) {
                throw new Error('Test thread not created');
            }
            const thread = await client.Thread.get(testThreadId);
            const runs = await thread.getAgentRuns();
            // Can be null or array
            expect(runs === null || Array.isArray(runs)).toBe(true);
        }, 30000);
    });
    describe('Agent Execution', () => {
        it('should run agent and stream response', async () => {
            if (!testAgentId || !testThreadId) {
                throw new Error('Test agent or thread not created');
            }
            const agent = await client.Agent.get(testAgentId);
            const thread = await client.Thread.get(testThreadId);
            const run = await agent.run('Say hello and introduce yourself briefly.', thread);
            expect(run).toBeDefined();
            // Stream the response
            const stream = await run.getStream();
            let hasContent = false;
            for await (const chunk of stream) {
                expect(chunk).toBeDefined();
                expect(typeof chunk).toBe('string');
                hasContent = true;
                // Limit to first few chunks to avoid long test
                if (hasContent)
                    break;
            }
            expect(hasContent).toBe(true);
        }, 60000);
        it('should run agent with custom model', async () => {
            if (!testAgentId || !testThreadId) {
                throw new Error('Test agent or thread not created');
            }
            const agent = await client.Agent.get(testAgentId);
            const thread = await client.Thread.get(testThreadId);
            const run = await agent.run('Say "test"', thread, 'gemini/gemini-2.5-pro');
            expect(run).toBeDefined();
            const stream = await run.getStream();
            let chunkCount = 0;
            for await (const chunk of stream) {
                chunkCount++;
                if (chunkCount >= 3)
                    break; // Limit chunks
            }
            expect(chunkCount).toBeGreaterThan(0);
        }, 60000);
    });
    describe('Full Workflow', () => {
        it('should complete full workflow: create agent, create thread, run agent, cleanup', async () => {
            // Create agent
            const workflowAgentName = `Workflow Test Agent ${Date.now()}`;
            const agent = await client.Agent.create({
                name: workflowAgentName,
                systemPrompt: 'You are a workflow test assistant.',
                a2abaseTools: [tools_1.A2ABaseTool.WEB_SEARCH_TOOL],
            });
            const agentDetails = await agent.details();
            expect(agentDetails.agent_id).toBeDefined();
            // Create thread
            const thread = await client.Thread.create('Workflow Test Thread');
            expect(thread.threadId).toBeDefined();
            // Add message
            const messageId = await thread.addMessage('What is 2+2?');
            expect(messageId).toBeDefined();
            // Run agent
            const run = await agent.run('Answer the question in the thread.', thread);
            expect(run).toBeDefined();
            // Stream response
            const stream = await run.getStream();
            let receivedChunks = 0;
            for await (const chunk of stream) {
                receivedChunks++;
                if (receivedChunks >= 5)
                    break; // Limit chunks
            }
            expect(receivedChunks).toBeGreaterThan(0);
            // Get messages
            const messages = await thread.getMessages();
            expect(messages.length).toBeGreaterThan(0);
            // Cleanup
            await agent.delete();
            await client.Thread.delete(thread.threadId);
        }, 120000);
    });
});
