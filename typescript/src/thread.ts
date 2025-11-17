/**
 * Thread management for A2ABase SDK
 */

import { ThreadsClient, Message, AgentStartRequest, AgentStartResponse } from './api/threads';
import { request } from 'undici';

export class Thread {
  public readonly client: ThreadsClient;
  public readonly threadId: string;

  constructor(client: ThreadsClient, threadId: string) {
    this.client = client;
    this.threadId = threadId;
  }

  async addMessage(message: string): Promise<string> {
    const response = await this.client.addMessageToThread(this.threadId, message);
    return response.message_id;
  }

  async deleteMessage(messageId: string): Promise<void> {
    await this.client.deleteMessageFromThread(this.threadId, messageId);
  }

  async getMessages(): Promise<Message[]> {
    const response = await this.client.getThreadMessages(this.threadId);
    return response.messages;
  }

  async getAgentRuns(): Promise<AgentRun[] | null> {
    try {
      const threadData = await this.client.getThread(this.threadId);
      const recentRuns = threadData.recent_agent_runs;
      if (!recentRuns || recentRuns.length === 0) {
        return null;
      }
      return recentRuns
        .map((run: { id?: string; agent_run_id?: string }) => run.id || run.agent_run_id)
        .filter((id): id is string => !!id)
        .map((id: string) => new AgentRun(this, id));
    } catch {
      return null;
    }
  }
}

export class AgentRun {
  private thread: Thread;
  private agentRunId: string;

  constructor(thread: Thread, agentRunId: string) {
    this.thread = thread;
    this.agentRunId = agentRunId;
  }

  async getStream(): Promise<AsyncGenerator<string, void, unknown>> {
    const client = this.thread['client'] as ThreadsClient;
    const streamUrl = client.getAgentRunStreamUrl(this.agentRunId);
    const headers = client.headers;
    
    return this.streamFromUrl(streamUrl, headers);
  }

  private async *streamFromUrl(
    url: string,
    headers: Record<string, string>
  ): AsyncGenerator<string, void, unknown> {
    const { body } = await request(url, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(300000), // 5 minute timeout
    });

    for await (const chunk of body) {
      const lines = chunk.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          yield line.trim();
        }
      }
    }
  }
}

export class A2ABaseThread {
  private client: ThreadsClient;

  constructor(client: ThreadsClient) {
    this.client = client;
  }

  async create(name?: string): Promise<Thread> {
    const response = await this.client.createThread(name);
    return new Thread(this.client, response.thread_id);
  }

  async get(threadId: string): Promise<Thread> {
    return new Thread(this.client, threadId);
  }

  async delete(threadId: string): Promise<void> {
    await this.client.deleteThread(threadId);
  }
}

