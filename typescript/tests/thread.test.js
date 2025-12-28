"use strict";
/**
 * Unit tests for thread.ts
 */
Object.defineProperty(exports, "__esModule", { value: true });
// Mock undici before importing
jest.mock('undici', () => ({
    request: jest.fn(),
}));
const thread_1 = require("../src/thread");
const undici_1 = require("undici");
describe('Thread', () => {
    let thread;
    let mockThreadsClient;
    beforeEach(() => {
        mockThreadsClient = {
            addMessageToThread: jest.fn(),
            deleteMessageFromThread: jest.fn(),
            getThreadMessages: jest.fn(),
            getThread: jest.fn(),
            startAgent: jest.fn(),
            getAgentRunStreamUrl: jest.fn(),
            headers: { 'X-API-Key': 'test-key' },
        };
        thread = new thread_1.Thread(mockThreadsClient, 'thread-123');
    });
    describe('constructor', () => {
        it('should create Thread with client and threadId', () => {
            expect(thread.client).toBe(mockThreadsClient);
            expect(thread.threadId).toBe('thread-123');
        });
    });
    describe('addMessage', () => {
        it('should add message to thread', async () => {
            const mockMessage = {
                message_id: 'msg-1',
                thread_id: 'thread-123',
                content: 'Hello',
                type: 'user',
                is_llm_message: true,
                created_at: '2024-01-01',
                updated_at: '2024-01-01',
                agent_id: '',
                agent_version_id: '',
                metadata: {},
            };
            mockThreadsClient.addMessageToThread.mockResolvedValue(mockMessage);
            const result = await thread.addMessage('Hello');
            expect(mockThreadsClient.addMessageToThread).toHaveBeenCalledWith('thread-123', 'Hello');
            expect(result).toBe('msg-1');
        });
    });
    describe('deleteMessage', () => {
        it('should delete message from thread', async () => {
            mockThreadsClient.deleteMessageFromThread.mockResolvedValue(undefined);
            await thread.deleteMessage('msg-1');
            expect(mockThreadsClient.deleteMessageFromThread).toHaveBeenCalledWith('thread-123', 'msg-1');
        });
    });
    describe('getMessages', () => {
        it('should get messages from thread', async () => {
            const mockMessages = [
                {
                    message_id: 'msg-1',
                    thread_id: 'thread-123',
                    content: 'Hello',
                    type: 'user',
                    is_llm_message: true,
                    created_at: '2024-01-01',
                    updated_at: '2024-01-01',
                    agent_id: '',
                    agent_version_id: '',
                    metadata: {},
                },
            ];
            mockThreadsClient.getThreadMessages.mockResolvedValue({ messages: mockMessages });
            const result = await thread.getMessages();
            expect(mockThreadsClient.getThreadMessages).toHaveBeenCalledWith('thread-123');
            expect(result).toEqual(mockMessages);
        });
    });
    describe('getAgentRuns', () => {
        it('should get agent runs when available', async () => {
            const mockThreadData = {
                thread_id: 'thread-123',
                account_id: 'acc-1',
                metadata: {},
                is_public: false,
                created_at: '2024-01-01',
                updated_at: '2024-01-01',
                recent_agent_runs: [
                    { id: 'run-1' },
                    { agent_run_id: 'run-2' },
                ],
            };
            mockThreadsClient.getThread.mockResolvedValue(mockThreadData);
            const result = await thread.getAgentRuns();
            expect(result).not.toBeNull();
            expect(Array.isArray(result)).toBe(true);
            if (result) {
                expect(result.length).toBe(2);
                expect(result[0]).toBeInstanceOf(thread_1.AgentRun);
            }
        });
        it('should return null when no runs', async () => {
            const mockThreadData = {
                thread_id: 'thread-123',
                account_id: 'acc-1',
                metadata: {},
                is_public: false,
                created_at: '2024-01-01',
                updated_at: '2024-01-01',
                recent_agent_runs: [],
            };
            mockThreadsClient.getThread.mockResolvedValue(mockThreadData);
            const result = await thread.getAgentRuns();
            expect(result).toBeNull();
        });
        it('should return null when recent_agent_runs is undefined', async () => {
            const mockThreadData = {
                thread_id: 'thread-123',
                account_id: 'acc-1',
                metadata: {},
                is_public: false,
                created_at: '2024-01-01',
                updated_at: '2024-01-01',
            };
            mockThreadsClient.getThread.mockResolvedValue(mockThreadData);
            const result = await thread.getAgentRuns();
            expect(result).toBeNull();
        });
        it('should return null on error', async () => {
            mockThreadsClient.getThread.mockRejectedValue(new Error('API Error'));
            const result = await thread.getAgentRuns();
            expect(result).toBeNull();
        });
        it('should filter out runs without id or agent_run_id', async () => {
            const mockThreadData = {
                thread_id: 'thread-123',
                account_id: 'acc-1',
                metadata: {},
                is_public: false,
                created_at: '2024-01-01',
                updated_at: '2024-01-01',
                recent_agent_runs: [
                    { id: 'run-1' },
                    {}, // Invalid run
                    { agent_run_id: 'run-2' },
                ],
            };
            mockThreadsClient.getThread.mockResolvedValue(mockThreadData);
            const result = await thread.getAgentRuns();
            expect(result).not.toBeNull();
            if (result) {
                expect(result.length).toBe(2); // Should filter out invalid run
            }
        });
    });
});
describe('AgentRun', () => {
    let agentRun;
    let mockThread;
    beforeEach(() => {
        mockThread = {
            threadId: 'thread-123',
            client: {
                getAgentRunStreamUrl: jest.fn().mockReturnValue('https://api.example.com/stream/run-1'),
                headers: { 'X-API-Key': 'test-key' },
            },
        };
        agentRun = new thread_1.AgentRun(mockThread, 'run-1');
    });
    describe('constructor', () => {
        it('should create AgentRun with thread and agentRunId', () => {
            expect(agentRun).toBeDefined();
        });
    });
    describe('getStream', () => {
        it('should stream response from URL', async () => {
            const mockBody = {
                [Symbol.asyncIterator]: async function* () {
                    yield Buffer.from('data: {"chunk": "1"}\n');
                    yield Buffer.from('data: {"chunk": "2"}\n\n');
                },
            };
            undici_1.request.mockResolvedValue({
                body: mockBody,
            });
            const stream = await agentRun.getStream();
            const chunks = [];
            for await (const chunk of stream) {
                chunks.push(chunk);
                if (chunks.length >= 2)
                    break;
            }
            expect(undici_1.request).toHaveBeenCalledWith('https://api.example.com/stream/run-1', expect.objectContaining({
                method: 'GET',
                headers: { 'X-API-Key': 'test-key' },
            }));
            expect(chunks.length).toBeGreaterThan(0);
        });
        it('should skip empty lines', async () => {
            const mockBody = {
                [Symbol.asyncIterator]: async function* () {
                    yield Buffer.from('data: {"chunk": "1"}\n\n');
                    yield Buffer.from('\n');
                    yield Buffer.from('data: {"chunk": "2"}\n');
                },
            };
            undici_1.request.mockResolvedValue({
                body: mockBody,
            });
            const stream = await agentRun.getStream();
            const chunks = [];
            for await (const chunk of stream) {
                chunks.push(chunk);
                if (chunks.length >= 2)
                    break;
            }
            // Should only have non-empty chunks
            expect(chunks.every(chunk => chunk.trim().length > 0)).toBe(true);
        });
    });
});
describe('A2ABaseThread', () => {
    let threadManager;
    let mockThreadsClient;
    beforeEach(() => {
        mockThreadsClient = {
            createThread: jest.fn(),
            deleteThread: jest.fn(),
        };
        threadManager = new thread_1.A2ABaseThread(mockThreadsClient);
    });
    describe('create', () => {
        it('should create thread without name', async () => {
            const mockResponse = { thread_id: 'thread-123', project_id: 'proj-1' };
            mockThreadsClient.createThread.mockResolvedValue(mockResponse);
            const result = await threadManager.create();
            expect(mockThreadsClient.createThread).toHaveBeenCalledWith(undefined);
            expect(result).toBeInstanceOf(thread_1.Thread);
            expect(result.threadId).toBe('thread-123');
        });
        it('should create thread with name', async () => {
            const mockResponse = { thread_id: 'thread-123', project_id: 'proj-1' };
            mockThreadsClient.createThread.mockResolvedValue(mockResponse);
            const result = await threadManager.create('Test Thread');
            expect(mockThreadsClient.createThread).toHaveBeenCalledWith('Test Thread');
            expect(result).toBeInstanceOf(thread_1.Thread);
        });
    });
    describe('get', () => {
        it('should get thread by ID', async () => {
            const result = await threadManager.get('thread-123');
            expect(result).toBeInstanceOf(thread_1.Thread);
            expect(result.threadId).toBe('thread-123');
        });
    });
    describe('delete', () => {
        it('should delete thread', async () => {
            mockThreadsClient.deleteThread.mockResolvedValue(undefined);
            await threadManager.delete('thread-123');
            expect(mockThreadsClient.deleteThread).toHaveBeenCalledWith('thread-123');
        });
    });
});
