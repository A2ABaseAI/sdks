/**
 * Unit tests for thread.ts
 */

// Mock undici before importing
jest.mock('undici', () => ({
  request: jest.fn(),
}));

import { Thread, AgentRun, A2ABaseThread } from '../src/thread';
import { ThreadsClient, Thread as APIThread, Message } from '../src/api/threads';
import { request } from 'undici';

describe('Thread', () => {
  let thread: Thread;
  let mockThreadsClient: jest.Mocked<ThreadsClient>;

  beforeEach(() => {
    mockThreadsClient = {
      addMessageToThread: jest.fn(),
      deleteMessageFromThread: jest.fn(),
      getThreadMessages: jest.fn(),
      getThread: jest.fn(),
      startAgent: jest.fn(),
      getAgentRunStreamUrl: jest.fn(),
      headers: { 'X-API-Key': 'test-key' },
    } as any;
    thread = new Thread(mockThreadsClient, 'thread-123');
  });

  describe('constructor', () => {
    it('should create Thread with client and threadId', () => {
      expect(thread.client).toBe(mockThreadsClient);
      expect(thread.threadId).toBe('thread-123');
    });
  });

  describe('addMessage', () => {
    it('should add message to thread', async () => {
      const mockMessage: Message = {
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
      const mockMessages: Message[] = [
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
      const mockThreadData: APIThread = {
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
        expect(result[0]).toBeInstanceOf(AgentRun);
      }
    });

    it('should return null when no runs', async () => {
      const mockThreadData: APIThread = {
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
      const mockThreadData: APIThread = {
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
      const mockThreadData: APIThread = {
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
  let agentRun: AgentRun;
  let mockThread: jest.Mocked<Thread>;

  beforeEach(() => {
    mockThread = {
      threadId: 'thread-123',
      client: {
        getAgentRunStreamUrl: jest.fn().mockReturnValue('https://api.example.com/stream/run-1'),
        headers: { 'X-API-Key': 'test-key' },
      } as any,
    } as any;
    agentRun = new AgentRun(mockThread, 'run-1');
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
      (request as jest.MockedFunction<typeof request>).mockResolvedValue({
        body: mockBody,
      } as any);

      const stream = await agentRun.getStream();
      const chunks: string[] = [];
      
      for await (const chunk of stream) {
        chunks.push(chunk);
        if (chunks.length >= 2) break;
      }

      expect(request).toHaveBeenCalledWith(
        'https://api.example.com/stream/run-1',
        expect.objectContaining({
          method: 'GET',
          headers: { 'X-API-Key': 'test-key' },
        })
      );
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
      (request as jest.MockedFunction<typeof request>).mockResolvedValue({
        body: mockBody,
      } as any);

      const stream = await agentRun.getStream();
      const chunks: string[] = [];
      
      for await (const chunk of stream) {
        chunks.push(chunk);
        if (chunks.length >= 2) break;
      }

      // Should only have non-empty chunks
      expect(chunks.every(chunk => chunk.trim().length > 0)).toBe(true);
    });
  });
});

describe('A2ABaseThread', () => {
  let threadManager: A2ABaseThread;
  let mockThreadsClient: jest.Mocked<ThreadsClient>;

  beforeEach(() => {
    mockThreadsClient = {
      createThread: jest.fn(),
      deleteThread: jest.fn(),
    } as any;
    threadManager = new A2ABaseThread(mockThreadsClient);
  });

  describe('create', () => {
    it('should create thread without name', async () => {
      const mockResponse = { thread_id: 'thread-123', project_id: 'proj-1' };
      mockThreadsClient.createThread.mockResolvedValue(mockResponse);

      const result = await threadManager.create();

      expect(mockThreadsClient.createThread).toHaveBeenCalledWith(undefined);
      expect(result).toBeInstanceOf(Thread);
      expect(result.threadId).toBe('thread-123');
    });

    it('should create thread with name', async () => {
      const mockResponse = { thread_id: 'thread-123', project_id: 'proj-1' };
      mockThreadsClient.createThread.mockResolvedValue(mockResponse);

      const result = await threadManager.create('Test Thread');

      expect(mockThreadsClient.createThread).toHaveBeenCalledWith('Test Thread');
      expect(result).toBeInstanceOf(Thread);
    });
  });

  describe('get', () => {
    it('should get thread by ID', async () => {
      const result = await threadManager.get('thread-123');

      expect(result).toBeInstanceOf(Thread);
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

