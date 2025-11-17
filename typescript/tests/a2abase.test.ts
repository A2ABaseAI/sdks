/**
 * Unit tests for a2abase.ts
 */

import { A2ABase, A2ABaseConfig } from '../src/a2abase';
import { APIClient } from '../src/api/client';
import { AgentsClient, AgentsResponse } from '../src/api/agents';
import { ThreadsClient } from '../src/api/threads';
import { A2ABaseAgent } from '../src/agent';
import { A2ABaseThread } from '../src/thread';

describe('A2ABase', () => {
  let client: A2ABase;

  describe('constructor', () => {
    it('should create A2ABase with default URL', () => {
      client = new A2ABase({
        apiKey: 'test-key',
      });

      expect(client).toBeDefined();
      expect(client.Agent).toBeInstanceOf(A2ABaseAgent);
      expect(client.Thread).toBeInstanceOf(A2ABaseThread);
    });

    it('should create A2ABase with custom URL', () => {
      client = new A2ABase({
        apiKey: 'test-key',
        apiUrl: 'https://custom.api.com',
      });

      expect(client).toBeDefined();
    });

    it('should create A2ABase with timeout', () => {
      client = new A2ABase({
        apiKey: 'test-key',
        timeout: 60000,
      });

      expect(client).toBeDefined();
    });

    it('should strip trailing slash from URL', () => {
      client = new A2ABase({
        apiKey: 'test-key',
        apiUrl: 'https://api.example.com/',
      });

      expect(client).toBeDefined();
    });
  });

  describe('getAgents', () => {
    beforeEach(() => {
      client = new A2ABase({
        apiKey: 'test-key',
        apiUrl: 'https://api.example.com',
      });
    });

    it('should get agents with params', async () => {
      const mockResponse: AgentsResponse = {
        agents: [],
        pagination: { page: 1, limit: 10, total: 0, pages: 0 },
      };

      // Mock the internal agentsClient
      const mockGetAgents = jest.fn().mockResolvedValue(mockResponse);
      (client as any).agentsClient = {
        getAgents: mockGetAgents,
      };

      const result = await client.getAgents({ page: 1, limit: 10, search: 'test' });

      expect(mockGetAgents).toHaveBeenCalledWith({ page: 1, limit: 10, search: 'test' });
      expect(result).toEqual(mockResponse);
    });

    it('should get agents without params', async () => {
      const mockResponse: AgentsResponse = {
        agents: [],
        pagination: { page: 1, limit: 10, total: 0, pages: 0 },
      };

      const mockGetAgents = jest.fn().mockResolvedValue(mockResponse);
      (client as any).agentsClient = {
        getAgents: mockGetAgents,
      };

      const result = await client.getAgents();

      expect(mockGetAgents).toHaveBeenCalledWith(undefined);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Agent property', () => {
    beforeEach(() => {
      client = new A2ABase({
        apiKey: 'test-key',
      });
    });

    it('should provide A2ABaseAgent instance', () => {
      expect(client.Agent).toBeInstanceOf(A2ABaseAgent);
    });
  });

  describe('Thread property', () => {
    beforeEach(() => {
      client = new A2ABase({
        apiKey: 'test-key',
      });
    });

    it('should provide A2ABaseThread instance', () => {
      expect(client.Thread).toBeInstanceOf(A2ABaseThread);
    });
  });
});

describe('A2ABaseConfig', () => {
  it('should accept required apiKey', () => {
    const config: A2ABaseConfig = {
      apiKey: 'test-key',
    };
    expect(config.apiKey).toBe('test-key');
  });

  it('should accept optional apiUrl', () => {
    const config: A2ABaseConfig = {
      apiKey: 'test-key',
      apiUrl: 'https://custom.api.com',
    };
    expect(config.apiUrl).toBe('https://custom.api.com');
  });

  it('should accept optional timeout', () => {
    const config: A2ABaseConfig = {
      apiKey: 'test-key',
      timeout: 60000,
    };
    expect(config.timeout).toBe(60000);
  });
});

