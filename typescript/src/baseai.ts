/**
 * Main BaseAI client
 */

import { APIClient } from './api/client';
import { AgentsClient } from './api/agents';
import { ThreadsClient } from './api/threads';
import { BaseAIAgent } from './agent';
import { BaseAIThread } from './thread';

export interface BaseAIConfig {
  apiKey: string;
  apiUrl?: string;
  timeout?: number;
}

export class BaseAI {
  public readonly Agent: BaseAIAgent;
  public readonly Thread: BaseAIThread;

  private agentsClient: AgentsClient;
  private threadsClient: ThreadsClient;

  constructor(config: BaseAIConfig) {
    const apiUrl = config.apiUrl || "https://a2abase.ai";
    const apiClient = new APIClient({
      baseUrl: apiUrl,
      apiKey: config.apiKey,
      timeout: config.timeout,
    });

    this.agentsClient = new AgentsClient(apiClient);
    this.threadsClient = new ThreadsClient(apiClient);

    this.Agent = new BaseAIAgent(this.agentsClient);
    this.Thread = new BaseAIThread(this.threadsClient);
  }
}

