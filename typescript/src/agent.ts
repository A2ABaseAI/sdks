/**
 * Agent management for A2ABase SDK
 */

import { AgentsClient, AgentCreateRequest, AgentUpdateRequest, AgentResponse } from './api/agents';
import { ThreadsClient, AgentStartRequest } from './api/threads';
import { A2ABaseTool, MCPTools, A2ABaseTools, getAgentPressToolDescription } from './tools';
import { Thread, AgentRun } from './thread';

export interface AgentCreateOptions {
  name: string;
  systemPrompt: string;
  a2abaseTools?: A2ABaseTools[];
  allowedTools?: string[];
}

export interface AgentUpdateOptions {
  name?: string;
  systemPrompt?: string;
  a2abaseTools?: A2ABaseTools[];
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

    if (options.a2abaseTools) {
      agentpressTools = {};
      customMcps = [];
      
      for (const tool of options.a2abaseTools) {
        if (tool instanceof MCPTools) {
          const isEnabled = options.allowedTools ? options.allowedTools.includes(tool.name) : true;
          customMcps.push({
            name: tool.name,
            type: tool.type,
            config: { url: tool.url },
            enabled_tools: isEnabled ? tool.enabledTools : [],
          });
        } else if (typeof tool === 'string' || Object.values(A2ABaseTool).includes(tool as any)) {
          const toolEnum = typeof tool === 'string' ? (tool as A2ABaseTool) : (tool as A2ABaseTool);
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

export class A2ABaseAgent {
  private client: AgentsClient;

  constructor(client: AgentsClient) {
    this.client = client;
  }

  async create(options: AgentCreateOptions): Promise<Agent> {
    const agentpressTools: Record<string, { enabled: boolean; description: string }> = {};
    const customMcps: any[] = [];

    for (const tool of options.a2abaseTools || []) {
      if (tool instanceof MCPTools) {
        const isEnabled = options.allowedTools ? options.allowedTools.includes(tool.name) : true;
        customMcps.push({
          name: tool.name,
          type: tool.type,
          config: { url: tool.url },
          enabled_tools: isEnabled ? tool.enabledTools : [],
        });
      } else if (typeof tool === 'string' || Object.values(A2ABaseTool).includes(tool as any)) {
        const toolEnum = typeof tool === 'string' ? (tool as A2ABaseTool) : (tool as A2ABaseTool);
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
      let resp = await this.client.getAgents({ page: 1, limit: 100, search: name });
      // First try exact match from search results
      for (const a of resp.agents) {
        if (a.name === name) {
          return new Agent(this.client, a.agent_id);
        }
      }
      // If not found and we have more pages, check them
      if (resp.pagination && resp.pagination.pages > 1) {
        for (let page = 2; page <= Math.min(resp.pagination.pages, 10); page++) {
          resp = await this.client.getAgents({ page, limit: 100, search: name });
          for (const a of resp.agents) {
            if (a.name === name) {
              return new Agent(this.client, a.agent_id);
            }
          }
        }
      }
      return null;
    } catch {
      return null;
    }
  }
}

