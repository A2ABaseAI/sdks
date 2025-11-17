/**
 * Agents API client
 */

import { APIClient } from './client';
import { A2ABaseTool } from '../tools';

export interface MCPConfig {
  url: string;
}

export interface CustomMCP {
  name: string;
  type: string;
  config: MCPConfig;
  enabled_tools: string[];
}

export interface A2ABaseToolConfig {
  enabled: boolean;
  description: string;
}

export interface AgentCreateRequest {
  name: string;
  system_prompt: string;
  description?: string;
  custom_mcps?: CustomMCP[];
  agentpress_tools?: Record<string, A2ABaseToolConfig>;
  is_default?: boolean;
  avatar?: string;
  avatar_color?: string;
  profile_image_url?: string;
  icon_name?: string;
  icon_color?: string;
  icon_background?: string;
}

export interface AgentUpdateRequest {
  name?: string;
  description?: string;
  system_prompt?: string;
  custom_mcps?: CustomMCP[];
  agentpress_tools?: Record<string, A2ABaseToolConfig>;
  is_default?: boolean;
  avatar?: string;
  avatar_color?: string;
  profile_image_url?: string;
  icon_name?: string;
  icon_color?: string;
  icon_background?: string;
}

export interface AgentVersionResponse {
  version_id: string;
  agent_id: string;
  version_number: number;
  version_name: string;
  system_prompt: string;
  custom_mcps: CustomMCP[];
  agentpress_tools: Record<string, A2ABaseToolConfig>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface AgentResponse {
  agent_id: string;
  name: string;
  system_prompt: string;
  custom_mcps: CustomMCP[];
  agentpress_tools: Record<string, A2ABaseToolConfig>;
  is_default: boolean;
  created_at: string;
  account_id?: string;
  description?: string;
  avatar?: string;
  avatar_color?: string;
  updated_at?: string;
  is_public?: boolean;
  marketplace_published_at?: string;
  download_count?: number;
  tags?: string[];
  current_version_id?: string;
  version_count?: number;
  current_version?: AgentVersionResponse;
  metadata?: Record<string, any>;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface AgentsResponse {
  agents: AgentResponse[];
  pagination: PaginationInfo;
}

export interface DeleteAgentResponse {
  message: string;
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

export class AgentsClient {
  private client: APIClient;

  constructor(client: APIClient) {
    this.client = client;
  }

  async getAgents(params?: {
    page?: number;
    limit?: number;
    search?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<AgentsResponse> {
    const response = await this.client.get<AgentsResponse>('/agents', params);
    // Normalize pagination info to ensure all required fields are present
    return {
      ...response,
      pagination: normalizePaginationInfo(response.pagination),
    };
  }

  async getAgent(agentId: string): Promise<AgentResponse> {
    return this.client.get<AgentResponse>(`/agents/${agentId}`);
  }

  async createAgent(request: AgentCreateRequest): Promise<AgentResponse> {
    return this.client.post<AgentResponse>('/agents', request);
  }

  async updateAgent(agentId: string, request: AgentUpdateRequest): Promise<AgentResponse> {
    return this.client.put<AgentResponse>(`/agents/${agentId}`, request);
  }

  async deleteAgent(agentId: string): Promise<DeleteAgentResponse> {
    return this.client.delete<DeleteAgentResponse>(`/agents/${agentId}`);
  }
}

