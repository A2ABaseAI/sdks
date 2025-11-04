/**
 * Agent management for BaseAI SDK
 */

import { AgentsClient, AgentCreateRequest, AgentUpdateRequest, AgentResponse } from './api/agents';
import { ThreadsClient, AgentStartRequest } from './api/threads';
import { BaseAITool, MCPTools, BaseAITools, getAgentPressToolDescription } from './tools';
import { Thread, AgentRun } from './thread';

export interface AgentCreateOptions {
  name: string;
  systemPrompt: string;
  mcpTools?: BaseAITools[];
  allowedTools?: string[];
}

export interface AgentUpdateOptions {
  name?: string;
  systemPrompt?: string;
  mcpTools?: BaseAITools[];
  allowedTools?: string[];
}

export class Agent {
  private client: AgentsClient;
  private agentId: string;
  private model: string;

  constructor(client: AgentsClient, agentId: string, model: string = "gemini/gemini-2.5-pro") {
    this.client = client;
    this.agentId = agentId;
    this.model = model;
  }

  async update(options: AgentUpdateOptions): Promise<void> {
    let agentpressTools: Record<string, { enabled: boolean; description: string }> | undefined;
    let customMcps: any[] | undefined;

    if (options.mcpTools) {
      agentpressTools = {};
      customMcps = [];
      
      for (const tool of options.mcpTools) {
        if (tool instanceof MCPTools) {
          const isEnabled = options.allowedTools ? options.allowedTools.includes(tool.name) : true;
          customMcps.push({
            name: tool.name,
            type: tool.type,
            config: { url: tool.url },
            enabled_tools: isEnabled ? tool.enabledTools : [],
          });
        } else if (typeof tool === 'string' || Object.values(BaseAITool).includes(tool as any)) {
          const toolEnum = typeof tool === 'string' ? (tool as BaseAITool) : (tool as BaseAITool);
          const isEnabled = options.allowedTools ? options.allowedTools.includes(toolEnum) : true;
          agentpressTools[toolEnum] = {
            enabled: isEnabled,
            description: getAgentPressToolDescription(toolEnum),
          };
        }
      }
    } else {
      const agentDetails = await this.details();
      agentpressTools = agentDetails.agentpress_tools;
      customMcps = agentDetails.custom_mcps;
      
      if (options.allowedTools) {
        if (agentpressTools) {
          for (const toolName in agentpressTools) {
            if (!options.allowedTools.includes(toolName)) {
              agentpressTools[toolName].enabled = false;
            }
          }
        }
        if (customMcps) {
          for (const mcp of customMcps) {
            mcp.enabled_tools = options.allowedTools;
          }
        }
      }
    }

    const updateRequest: AgentUpdateRequest = {
      name: options.name,
      system_prompt: options.systemPrompt,
      custom_mcps: customMcps,
      agentpress_tools: agentpressTools,
    };

    await this.client.updateAgent(this.agentId, updateRequest);
  }

  async details(): Promise<AgentResponse> {
    return this.client.getAgent(this.agentId);
  }

  async run(prompt: string, thread: Thread, model?: string): Promise<AgentRun> {
    await thread.addMessage(prompt);
    const response = await thread.client.startAgent(
      thread.threadId,
      {
        agent_id: this.agentId,
        model_name: model || this.model,
      } as AgentStartRequest
    );
    return new AgentRun(thread, response.agent_run_id);
  }

  async delete(): Promise<void> {
    await this.client.deleteAgent(this.agentId);
  }
}

export class BaseAIAgent {
  private client: AgentsClient;

  constructor(client: AgentsClient) {
    this.client = client;
  }

  async create(options: AgentCreateOptions): Promise<Agent> {
    const agentpressTools: Record<string, { enabled: boolean; description: string }> = {};
    const customMcps: any[] = [];

    for (const tool of options.mcpTools || []) {
      if (tool instanceof MCPTools) {
        const isEnabled = options.allowedTools ? options.allowedTools.includes(tool.name) : true;
        customMcps.push({
          name: tool.name,
          type: tool.type,
          config: { url: tool.url },
          enabled_tools: isEnabled ? tool.enabledTools : [],
        });
      } else if (typeof tool === 'string' || Object.values(BaseAITool).includes(tool as any)) {
        const toolEnum = typeof tool === 'string' ? (tool as BaseAITool) : (tool as BaseAITool);
        const isEnabled = options.allowedTools ? options.allowedTools.includes(toolEnum) : true;
        agentpressTools[toolEnum] = {
          enabled: isEnabled,
          description: getAgentPressToolDescription(toolEnum),
        };
      } else {
        throw new Error(`Unknown tool type: ${typeof tool}`);
      }
    }

    const createRequest: AgentCreateRequest = {
      name: options.name,
      system_prompt: options.systemPrompt,
      custom_mcps: customMcps.length > 0 ? customMcps : undefined,
      agentpress_tools: Object.keys(agentpressTools).length > 0 ? agentpressTools : undefined,
    };

    const agent = await this.client.createAgent(createRequest);
    return new Agent(this.client, agent.agent_id);
  }

  async get(agentId: string): Promise<Agent> {
    const agent = await this.client.getAgent(agentId);
    return new Agent(this.client, agent.agent_id);
  }

  async findByName(name: string): Promise<Agent | null> {
    try {
      const response = await this.client.getAgents({ page: 1, limit: 100 });
      for (const agent of response.agents) {
        if (agent.name === name) {
          return new Agent(this.client, agent.agent_id);
        }
      }
      return null;
    } catch {
      return null;
    }
  }
}

