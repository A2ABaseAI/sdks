/**
 * Main A2ABase client
 */

import { APIClient } from './api/client';
import { AgentsClient, AgentsResponse } from './api/agents';
import { ThreadsClient } from './api/threads';
import { A2ABaseAgent } from './agent';
import { A2ABaseThread } from './thread';

export interface A2ABaseConfig {
  apiKey: string;
  apiUrl?: string;
  timeout?: number;
}

export class A2ABase {
  public readonly Agent: A2ABaseAgent;
  public readonly Thread: A2ABaseThread;

  private agentsClient: AgentsClient;
  private threadsClient: ThreadsClient;

  constructor(config: A2ABaseConfig) {
    const apiUrl = config.apiUrl || "https://a2abase.ai";
    const apiClient = new APIClient({
      baseUrl: apiUrl,
      apiKey: config.apiKey,
      timeout: config.timeout,
    });

    this.agentsClient = new AgentsClient(apiClient);
    this.threadsClient = new ThreadsClient(apiClient);

    this.Agent = new A2ABaseAgent(this.agentsClient);
    this.Thread = new A2ABaseThread(this.threadsClient);
  }

  /**
   * Get agents with pagination
   * This matches the Python SDK's get_agents method
   */
  async getAgents(params?: {
    page?: number;
    limit?: number;
    search?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<AgentsResponse> {
    return this.agentsClient.getAgents(params);
  }
}

