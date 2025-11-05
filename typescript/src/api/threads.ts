/**
 * Threads API client
 */

import { APIClient } from './client';

export interface MessageCreateRequest {
  content: string;
  type?: string;
  is_llm_message?: boolean;
}

export interface AgentStartRequest {
  model_name?: string;
  enable_thinking?: boolean;
  reasoning_effort?: string;
  stream?: boolean;
  enable_context_manager?: boolean;
  agent_id?: string;
}

export interface Thread {
  thread_id: string;
  account_id: string;
  project_id?: string;
  metadata: Record<string, any>;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  recent_agent_runs?: Array<{ id: string }>;
}

export interface Message {
  message_id: string;
  thread_id: string;
  type: string;
  is_llm_message: boolean;
  content: any;
  created_at: string;
  updated_at: string;
  agent_id: string;
  agent_version_id: string;
  metadata: any;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface ThreadsResponse {
  threads: Thread[];
  pagination: PaginationInfo;
}

export interface MessagesResponse {
  messages: Message[];
}

export interface CreateThreadResponse {
  thread_id: string;
  project_id: string;
}

export interface AgentStartResponse {
  agent_run_id: string;
  status: string;
}

/**
 * Normalizes PaginationInfo to ensure all required fields are present
 * This matches the Python SDK's from_dict behavior
 */
function normalizePaginationInfo(data: any): PaginationInfo {
  const requiredFields = ['page', 'limit', 'total', 'pages'];
  const normalized: PaginationInfo = {
    page: data?.page ?? 0,
    limit: data?.limit ?? 0,
    total: data?.total ?? 0,
    pages: data?.pages ?? 0,
  };
  
  // Ensure all required fields are present
  for (const field of requiredFields) {
    if (normalized[field as keyof PaginationInfo] === undefined) {
      normalized[field as keyof PaginationInfo] = 0;
    }
  }
  
  return normalized;
}

export class ThreadsClient {
  private client: APIClient;

  constructor(client: APIClient) {
    this.client = client;
  }

  async getThreads(params?: { page?: number; limit?: number }): Promise<ThreadsResponse> {
    const response = await this.client.get<ThreadsResponse>('/threads', params);
    // Normalize pagination info to ensure all required fields are present
    return {
      ...response,
      pagination: normalizePaginationInfo(response.pagination),
    };
  }

  async getThread(threadId: string): Promise<Thread> {
    return this.client.get<Thread>(`/threads/${threadId}`);
  }

  async getThreadMessages(threadId: string, order: string = 'desc'): Promise<MessagesResponse> {
    return this.client.get<MessagesResponse>(`/threads/${threadId}/messages`, { order });
  }

  async addMessageToThread(threadId: string, message: string): Promise<Message> {
    return this.client.post<Message>(`/threads/${threadId}/messages/add`, undefined, { message });
  }

  async deleteMessageFromThread(threadId: string, messageId: string): Promise<void> {
    await this.client.delete(`/threads/${threadId}/messages/${messageId}`);
  }

  async createMessage(threadId: string, request: MessageCreateRequest): Promise<Message> {
    return this.client.post<Message>(`/threads/${threadId}/messages`, request);
  }

  async createThread(name?: string): Promise<CreateThreadResponse> {
    // Backend expects form data for name
    const formData = name ? new URLSearchParams({ name }) : undefined;
    const headers: Record<string, string> = { 'Content-Type': 'application/x-www-form-urlencoded' };
    return this.client.post<CreateThreadResponse>('/threads', formData?.toString(), undefined);
  }

  async deleteThread(threadId: string): Promise<void> {
    throw new Error('Not implemented');
  }

  getAgentRunStreamUrl(agentRunId: string): string {
    return `${(this.client as any).baseUrl}/agent-run/${agentRunId}/stream`;
  }
  
  get baseUrl(): string {
    return (this.client as any).baseUrl;
  }

  get headers(): Record<string, string> {
    return (this.client as any).headers;
  }

  async startAgent(threadId: string, request: AgentStartRequest): Promise<AgentStartResponse> {
    return this.client.post<AgentStartResponse>(`/thread/${threadId}/agent/start`, request);
  }
}

