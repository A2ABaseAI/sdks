/**
 * Data models for the BaseAI SDK
 */

export enum Role {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system",
}

export enum MessageType {
  USER = "user",
  ASSISTANT = "assistant",
  TOOL = "tool",
  STATUS = "status",
  ASSISTANT_RESPONSE_END = "assistant_response_end",
}

export interface ContentObject {
  role: Role;
  content: string | null;
  tool_calls?: any;
}

export interface BaseMessage {
  message_id: string;
  thread_id: string;
  type: MessageType;
  is_llm_message: boolean;
  metadata: any;
  created_at: string;
  updated_at: string;
}

export interface UserMessage extends BaseMessage {
  type: MessageType.USER;
  content: string;
}

export interface AssistantMessage extends BaseMessage {
  type: MessageType.ASSISTANT;
  content: ContentObject;
}

export interface ToolResultMessage extends BaseMessage {
  type: MessageType.TOOL;
  content: Record<string, string | any>;
}

export interface StatusMessage extends BaseMessage {
  type: MessageType.STATUS;
  content: Record<string, any>;
}

export interface AssistantResponseEndMessage extends BaseMessage {
  type: MessageType.ASSISTANT_RESPONSE_END;
  content: Record<string, any>;
}

export type ChatMessage =
  | UserMessage
  | AssistantMessage
  | ToolResultMessage
  | StatusMessage
  | AssistantResponseEndMessage;

export interface AgentRun {
  id: string;
  thread_id: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  error?: any;
  created_at: string;
  updated_at: string;
}

