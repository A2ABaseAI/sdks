/**
 * Unit tests for agent.ts
 */

import { Agent, A2ABaseAgent, AgentCreateOptions, AgentUpdateOptions } from '../src/agent';
import { AgentsClient, AgentResponse, AgentsResponse } from '../src/api/agents';
import { ThreadsClient, AgentStartResponse } from '../src/api/threads';
import { A2ABaseTool, MCPTools } from '../src/tools';
import { Thread, AgentRun } from '../src/thread';

describe('Agent', () => {
  let agent: Agent;
  let mockAgentsClient: jest.Mocked<AgentsClient>;
  let mockThreadsClient: jest.Mocked<ThreadsClient>;

  beforeEach(() => {
    mockAgentsClient = {
      getAgent: jest.fn(),
      updateAgent: jest.fn(),
      deleteAgent: jest.fn(),
    } as any;
    mockThreadsClient = {
      startAgent: jest.fn(),
    } as any;
    agent = new Agent(mockAgentsClient, 'agent-123');
  });

  describe('constructor', () => {
    it('should create Agent with default model', () => {
      expect(agent).toBeDefined();
    });

    it('should create Agent with custom model', () => {
      const customAgent = new Agent(mockAgentsClient, 'agent-123', 'gpt-4');
      expect(customAgent).toBeDefined();
    });
  });

  describe('details', () => {
    it('should get agent details', async () => {
      const mockDetails: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test Agent',
        system_prompt: 'Test prompt',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockDetails);

      const result = await agent.details();

      expect(mockAgentsClient.getAgent).toHaveBeenCalledWith('agent-123');
      expect(result).toEqual(mockDetails);
    });
  });

  describe('update', () => {
    it('should update agent with A2ABaseTool', async () => {
      const mockDetails: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Old',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockDetails);
      mockAgentsClient.updateAgent.mockResolvedValue(mockDetails);

      await agent.update({
        systemPrompt: 'New prompt',
        a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL],
      });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalledWith(
        'agent-123',
        expect.objectContaining({
          system_prompt: 'New prompt',
          agentpress_tools: expect.objectContaining({
            [A2ABaseTool.WEB_SEARCH_TOOL]: expect.objectContaining({
              enabled: true,
            }),
          }),
        })
      );
    });

    it('should update agent with MCPTools', async () => {
      const mcp = new MCPTools({
        endpoint: 'http://example.com',
        name: 'test-mcp',
        allowedTools: ['tool1'],
      });
      await mcp.initialize();

      await agent.update({
        a2abaseTools: [mcp],
      });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalledWith(
        'agent-123',
        expect.objectContaining({
          custom_mcps: expect.arrayContaining([
            expect.objectContaining({
              name: 'test-mcp',
              type: 'http',
            }),
          ]),
        })
      );
    });

    it('should update agent with MCPTools and allowedTools filtering', async () => {
      const mcp = new MCPTools({
        endpoint: 'http://example.com',
        name: 'test-mcp',
        allowedTools: ['tool1', 'tool2'],
      });
      await mcp.initialize();

      await agent.update({
        a2abaseTools: [mcp],
        allowedTools: ['tool1'], // Only tool1 is allowed
      });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalledWith(
        'agent-123',
        expect.objectContaining({
          custom_mcps: expect.arrayContaining([
            expect.objectContaining({
              enabled_tools: [], // Should be empty since tool1 is not in mcp.enabledTools
            }),
          ]),
        })
      );
    });

    it('should update agent with string tool', async () => {
      const mockDetails: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Old',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockDetails);
      mockAgentsClient.updateAgent.mockResolvedValue(mockDetails);

      // Pass tool as string
      await agent.update({
        a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL as any],
      });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalled();
    });

    it('should update agent with allowedTools filtering', async () => {
      const mockDetails: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {
          [A2ABaseTool.WEB_SEARCH_TOOL]: { enabled: true, description: 'Search' },
          [A2ABaseTool.BROWSER_TOOL]: { enabled: true, description: 'Browser' },
        },
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockDetails);

      await agent.update({
        allowedTools: [A2ABaseTool.WEB_SEARCH_TOOL],
      });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalledWith(
        'agent-123',
        expect.objectContaining({
          agentpress_tools: expect.objectContaining({
            [A2ABaseTool.WEB_SEARCH_TOOL]: expect.objectContaining({ enabled: true }),
            [A2ABaseTool.BROWSER_TOOL]: expect.objectContaining({ enabled: false }),
          }),
        })
      );
    });

    it('should update agent with allowedTools filtering customMcps', async () => {
      const mockDetails: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [
          {
            name: 'test-mcp',
            type: 'http',
            config: { url: 'http://example.com' },
            enabled_tools: ['tool1', 'tool2'],
          },
        ],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockDetails);

      await agent.update({
        allowedTools: ['tool1'],
      });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalledWith(
        'agent-123',
        expect.objectContaining({
          custom_mcps: expect.arrayContaining([
            expect.objectContaining({
              enabled_tools: ['tool1'],
            }),
          ]),
        })
      );
    });

    it('should update agent name only', async () => {
      const mockDetails: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Old',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockDetails);

      await agent.update({ name: 'New Name' });

      expect(mockAgentsClient.updateAgent).toHaveBeenCalledWith(
        'agent-123',
        expect.objectContaining({ name: 'New Name' })
      );
    });
  });

  describe('run', () => {
    it('should run agent', async () => {
      const mockThread = {
        threadId: 'thread-123',
        addMessage: jest.fn().mockResolvedValue('msg-1'),
        client: mockThreadsClient,
      } as any;

      const mockResponse: AgentStartResponse = {
        agent_run_id: 'run-123',
        status: 'started',
      };
      mockThreadsClient.startAgent.mockResolvedValue(mockResponse);

      const result = await agent.run('Test prompt', mockThread);

      expect(mockThread.addMessage).toHaveBeenCalledWith('Test prompt');
      expect(mockThreadsClient.startAgent).toHaveBeenCalledWith(
        'thread-123',
        expect.objectContaining({
          agent_id: 'agent-123',
          model_name: 'gemini/gemini-2.5-pro',
        })
      );
      expect(result).toBeInstanceOf(AgentRun);
    });

    it('should run agent with custom model', async () => {
      const mockThread = {
        threadId: 'thread-123',
        addMessage: jest.fn().mockResolvedValue('msg-1'),
        client: mockThreadsClient,
      } as any;

      const mockResponse: AgentStartResponse = {
        agent_run_id: 'run-123',
        status: 'started',
      };
      mockThreadsClient.startAgent.mockResolvedValue(mockResponse);

      await agent.run('Test prompt', mockThread, 'gpt-4');

      expect(mockThreadsClient.startAgent).toHaveBeenCalledWith(
        'thread-123',
        expect.objectContaining({
          model_name: 'gpt-4',
        })
      );
    });
  });

  describe('delete', () => {
    it('should delete agent', async () => {
      mockAgentsClient.deleteAgent.mockResolvedValue({ message: 'Deleted' });

      await agent.delete();

      expect(mockAgentsClient.deleteAgent).toHaveBeenCalledWith('agent-123');
    });
  });
});

describe('A2ABaseAgent', () => {
  let agentManager: A2ABaseAgent;
  let mockAgentsClient: jest.Mocked<AgentsClient>;

  beforeEach(() => {
    mockAgentsClient = {
      createAgent: jest.fn(),
      getAgent: jest.fn(),
      getAgents: jest.fn(),
    } as any;
    agentManager = new A2ABaseAgent(mockAgentsClient);
  });

  describe('create', () => {
    it('should create agent without tools', async () => {
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      const result = await agentManager.create({
        name: 'Test',
        systemPrompt: 'Test',
      });

      expect(mockAgentsClient.createAgent).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test',
          system_prompt: 'Test',
        })
      );
      expect(result).toBeInstanceOf(Agent);
    });

    it('should create agent with A2ABaseTool', async () => {
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      await agentManager.create({
        name: 'Test',
        systemPrompt: 'Test',
        a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL],
      });

      expect(mockAgentsClient.createAgent).toHaveBeenCalledWith(
        expect.objectContaining({
          agentpress_tools: expect.objectContaining({
            [A2ABaseTool.WEB_SEARCH_TOOL]: expect.objectContaining({
              enabled: true,
            }),
          }),
        })
      );
    });

    it('should create agent with MCPTools', async () => {
      const mcp = new MCPTools({
        endpoint: 'http://example.com',
        name: 'test-mcp',
      });
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      await agentManager.create({
        name: 'Test',
        systemPrompt: 'Test',
        a2abaseTools: [mcp],
      });

      expect(mockAgentsClient.createAgent).toHaveBeenCalledWith(
        expect.objectContaining({
          custom_mcps: expect.arrayContaining([
            expect.objectContaining({ name: 'test-mcp' }),
          ]),
        })
      );
    });

    it('should create agent with MCPTools and allowedTools filtering', async () => {
      const mcp = new MCPTools({
        endpoint: 'http://example.com',
        name: 'test-mcp',
        allowedTools: ['tool1', 'tool2'],
      });
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      await agentManager.create({
        name: 'Test',
        systemPrompt: 'Test',
        a2abaseTools: [mcp],
        allowedTools: ['tool1'], // Only tool1 is allowed
      });

      expect(mockAgentsClient.createAgent).toHaveBeenCalledWith(
        expect.objectContaining({
          custom_mcps: expect.arrayContaining([
            expect.objectContaining({
              enabled_tools: [], // Should be empty since tool1 is not in mcp.enabledTools
            }),
          ]),
        })
      );
    });

    it('should create agent with string tool', async () => {
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      // Pass tool as string
      await agentManager.create({
        name: 'Test',
        systemPrompt: 'Test',
        a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL as any],
      });

      expect(mockAgentsClient.createAgent).toHaveBeenCalled();
    });

    it('should create agent with allowedTools', async () => {
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      await agentManager.create({
        name: 'Test',
        systemPrompt: 'Test',
        a2abaseTools: [A2ABaseTool.WEB_SEARCH_TOOL, A2ABaseTool.BROWSER_TOOL],
        allowedTools: [A2ABaseTool.WEB_SEARCH_TOOL],
      });

      expect(mockAgentsClient.createAgent).toHaveBeenCalledWith(
        expect.objectContaining({
          agentpress_tools: expect.objectContaining({
            [A2ABaseTool.WEB_SEARCH_TOOL]: expect.objectContaining({ enabled: true }),
            [A2ABaseTool.BROWSER_TOOL]: expect.objectContaining({ enabled: false }),
          }),
        })
      );
    });

    it('should throw error for unknown tool type', async () => {
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.createAgent.mockResolvedValue(mockAgent);

      await expect(
        agentManager.create({
          name: 'Test',
          systemPrompt: 'Test',
          a2abaseTools: [{} as any],
        })
      ).rejects.toThrow();
    });
  });

  describe('get', () => {
    it('should get agent by ID', async () => {
      const mockAgent: AgentResponse = {
        agent_id: 'agent-123',
        name: 'Test',
        system_prompt: 'Test',
        custom_mcps: [],
        agentpress_tools: {},
        is_default: false,
        created_at: '2024-01-01',
      };
      mockAgentsClient.getAgent.mockResolvedValue(mockAgent);

      const result = await agentManager.get('agent-123');

      expect(mockAgentsClient.getAgent).toHaveBeenCalledWith('agent-123');
      expect(result).toBeInstanceOf(Agent);
    });
  });

  describe('findByName', () => {
    it('should find agent by name on first page', async () => {
      const mockResponse: AgentsResponse = {
        agents: [
          { 
            agent_id: 'agent-1', 
            name: 'Agent 1',
            system_prompt: 'Test',
            custom_mcps: [],
            agentpress_tools: {},
            is_default: false,
            created_at: '2024-01-01',
          },
          { 
            agent_id: 'agent-2', 
            name: 'Target Agent',
            system_prompt: 'Test',
            custom_mcps: [],
            agentpress_tools: {},
            is_default: false,
            created_at: '2024-01-01',
          },
        ],
        pagination: { page: 1, limit: 100, total: 2, pages: 1 },
      };
      mockAgentsClient.getAgents.mockResolvedValue(mockResponse);

      const result = await agentManager.findByName('Target Agent');

      expect(mockAgentsClient.getAgents).toHaveBeenCalledWith({
        page: 1,
        limit: 100,
        search: 'Target Agent',
      });
      expect(result).toBeInstanceOf(Agent);
    });

    it('should find agent by name on second page', async () => {
      const mockResponse1: AgentsResponse = {
        agents: [{ 
          agent_id: 'agent-1', 
          name: 'Agent 1',
          system_prompt: 'Test',
          custom_mcps: [],
          agentpress_tools: {},
          is_default: false,
          created_at: '2024-01-01',
        }],
        pagination: { page: 1, limit: 100, total: 101, pages: 2 },
      };
      const mockResponse2: AgentsResponse = {
        agents: [{ 
          agent_id: 'agent-2', 
          name: 'Target Agent',
          system_prompt: 'Test',
          custom_mcps: [],
          agentpress_tools: {},
          is_default: false,
          created_at: '2024-01-01',
        }],
        pagination: { page: 2, limit: 100, total: 101, pages: 2 },
      };
      mockAgentsClient.getAgents
        .mockResolvedValueOnce(mockResponse1)
        .mockResolvedValueOnce(mockResponse2);

      const result = await agentManager.findByName('Target Agent');

      expect(mockAgentsClient.getAgents).toHaveBeenCalledTimes(2);
      expect(result).toBeInstanceOf(Agent);
    });

    it('should return null if agent not found', async () => {
      const mockResponse: AgentsResponse = {
        agents: [{ 
          agent_id: 'agent-1', 
          name: 'Agent 1',
          system_prompt: 'Test',
          custom_mcps: [],
          agentpress_tools: {},
          is_default: false,
          created_at: '2024-01-01',
        }],
        pagination: { page: 1, limit: 100, total: 1, pages: 1 },
      };
      mockAgentsClient.getAgents.mockResolvedValue(mockResponse);

      const result = await agentManager.findByName('Non-existent');

      expect(result).toBeNull();
    });

    it('should return null on error', async () => {
      mockAgentsClient.getAgents.mockRejectedValue(new Error('API Error'));

      const result = await agentManager.findByName('Test');

      expect(result).toBeNull();
    });

    it('should limit to 10 pages', async () => {
      const mockResponse = {
        agents: [],
        pagination: { page: 1, limit: 100, total: 1000, pages: 20 },
      };
      mockAgentsClient.getAgents.mockResolvedValue(mockResponse);

      await agentManager.findByName('Test');

      // Should only call up to page 10
      expect(mockAgentsClient.getAgents).toHaveBeenCalledTimes(10);
    });
  });
});

