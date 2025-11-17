/**
 * Unit tests for api/threads.ts
 */

import { ThreadsClient } from '../src/api/threads';
import { APIClient } from '../src/api/client';

describe('ThreadsClient', () => {
  let client: ThreadsClient;
  let mockApiClient: jest.Mocked<APIClient>;

  beforeEach(() => {
    mockApiClient = {
      get: jest.fn(),
      post: jest.fn(),
      delete: jest.fn(),
      baseUrl: 'https://api.example.com',
      headers: { 'X-API-Key': 'test-key' },
    } as any;
    client = new ThreadsClient(mockApiClient);
  });

  describe('getThreads', () => {
    it('should get threads with params', async () => {
      const mockResponse = {
        threads: [{ thread_id: '1' }],
        pagination: { page: 1, limit: 10, total: 1, pages: 1 },
      };
      mockApiClient.get.mockResolvedValue(mockResponse);

      const result = await client.getThreads({ page: 1, limit: 10 });

      expect(mockApiClient.get).toHaveBeenCalledWith('/threads', { page: 1, limit: 10 });
      expect(result.threads).toEqual(mockResponse.threads);
    });

    it('should normalize pagination info', async () => {
      const mockResponse = {
        threads: [],
        pagination: {},
      };
      mockApiClient.get.mockResolvedValue(mockResponse);

      const result = await client.getThreads();

      expect(result.pagination.page).toBe(0);
      expect(result.pagination.limit).toBe(0);
    });

    it('should normalize pagination info with some undefined fields', async () => {
      const mockResponse = {
        threads: [],
        pagination: {
          page: 1,
          limit: 10,
          // total and pages are undefined
        },
      };
      mockApiClient.get.mockResolvedValue(mockResponse);

      const result = await client.getThreads();

      expect(result.pagination.page).toBe(1);
      expect(result.pagination.limit).toBe(10);
      expect(result.pagination.total).toBe(0);
      expect(result.pagination.pages).toBe(0);
    });

    it('should normalize pagination info with explicitly undefined field', async () => {
      const mockResponse = {
        threads: [],
        pagination: {
          page: 1,
          limit: 10,
          total: undefined,
          pages: undefined,
        },
      };
      mockApiClient.get.mockResolvedValue(mockResponse);

      const result = await client.getThreads();

      expect(result.pagination.page).toBe(1);
      expect(result.pagination.limit).toBe(10);
      expect(result.pagination.total).toBe(0);
      expect(result.pagination.pages).toBe(0);
    });
  });

  describe('getThread', () => {
    it('should get thread by ID', async () => {
      const mockThread = { thread_id: '123' };
      mockApiClient.get.mockResolvedValue(mockThread);

      const result = await client.getThread('123');

      expect(mockApiClient.get).toHaveBeenCalledWith('/threads/123');
      expect(result).toEqual(mockThread);
    });
  });

  describe('getThreadMessages', () => {
    it('should get thread messages', async () => {
      const mockResponse = { messages: [] };
      mockApiClient.get.mockResolvedValue(mockResponse);

      const result = await client.getThreadMessages('123', 'asc');

      expect(mockApiClient.get).toHaveBeenCalledWith('/threads/123/messages', { order: 'asc' });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('addMessageToThread', () => {
    it('should add message to thread', async () => {
      const mockMessage = { message_id: 'msg-1', content: 'Hello' };
      mockApiClient.post.mockResolvedValue(mockMessage);

      const result = await client.addMessageToThread('123', 'Hello');

      expect(mockApiClient.post).toHaveBeenCalledWith('/threads/123/messages/add', undefined, { message: 'Hello' });
      expect(result).toEqual(mockMessage);
    });
  });

  describe('deleteMessageFromThread', () => {
    it('should delete message from thread', async () => {
      mockApiClient.delete.mockResolvedValue(undefined);

      await client.deleteMessageFromThread('123', 'msg-1');

      expect(mockApiClient.delete).toHaveBeenCalledWith('/threads/123/messages/msg-1');
    });
  });

  describe('createMessage', () => {
    it('should create message', async () => {
      const request = { content: 'Hello', type: 'user' };
      const mockMessage = { message_id: 'msg-1' };
      mockApiClient.post.mockResolvedValue(mockMessage);

      const result = await client.createMessage('123', request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/threads/123/messages', request);
      expect(result).toEqual(mockMessage);
    });
  });

  describe('createThread', () => {
    it('should create thread with name', async () => {
      const mockResponse = { thread_id: '123', project_id: 'proj-1' };
      mockApiClient.post.mockResolvedValue(mockResponse);

      const result = await client.createThread('Test Thread');

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/threads',
        'name=Test+Thread',
        undefined
      );
      expect(result).toEqual(mockResponse);
    });

    it('should create thread without name', async () => {
      const mockResponse = { thread_id: '123', project_id: 'proj-1' };
      mockApiClient.post.mockResolvedValue(mockResponse);

      const result = await client.createThread();

      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteThread', () => {
    it('should throw error (not implemented)', async () => {
      await expect(client.deleteThread('123')).rejects.toThrow('Not implemented');
    });
  });

  describe('getAgentRunStreamUrl', () => {
    it('should return stream URL', () => {
      const url = client.getAgentRunStreamUrl('run-123');
      expect(url).toBe('https://api.example.com/agent-run/run-123/stream');
    });
  });

  describe('startAgent', () => {
    it('should start agent', async () => {
      const request = { agent_id: 'agent-1', model_name: 'gpt-4' };
      const mockResponse = { agent_run_id: 'run-1', status: 'started' };
      mockApiClient.post.mockResolvedValue(mockResponse);

      const result = await client.startAgent('thread-1', request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/thread/thread-1/agent/start', request);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getters', () => {
    it('should get baseUrl', () => {
      expect(client.baseUrl).toBe('https://api.example.com');
    });

    it('should get headers', () => {
      expect(client.headers).toEqual({ 'X-API-Key': 'test-key' });
    });
  });
});

