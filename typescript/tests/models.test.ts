/**
 * Unit tests for models.ts
 */

import {
  Role,
  MessageType,
  ContentObject,
  BaseMessage,
  UserMessage,
  AssistantMessage,
  ToolResultMessage,
  StatusMessage,
  AssistantResponseEndMessage,
  ChatMessage,
  AgentRun,
} from '../src/models';

describe('Role enum', () => {
  it('should have correct values', () => {
    expect(Role.USER).toBe('user');
    expect(Role.ASSISTANT).toBe('assistant');
    expect(Role.SYSTEM).toBe('system');
  });
});

describe('MessageType enum', () => {
  it('should have correct values', () => {
    expect(MessageType.USER).toBe('user');
    expect(MessageType.ASSISTANT).toBe('assistant');
    expect(MessageType.TOOL).toBe('tool');
    expect(MessageType.STATUS).toBe('status');
    expect(MessageType.ASSISTANT_RESPONSE_END).toBe('assistant_response_end');
  });
});

describe('ContentObject', () => {
  it('should create ContentObject with required fields', () => {
    const content: ContentObject = {
      role: Role.USER,
      content: 'Hello',
    };
    expect(content.role).toBe(Role.USER);
    expect(content.content).toBe('Hello');
  });

  it('should create ContentObject with tool_calls', () => {
    const content: ContentObject = {
      role: Role.ASSISTANT,
      content: 'Response',
      tool_calls: [{ name: 'test', arguments: {} }],
    };
    expect(content.tool_calls).toBeDefined();
  });
});

describe('Message interfaces', () => {
  const baseMessage: BaseMessage = {
    message_id: 'msg-1',
    thread_id: 'thread-1',
    type: MessageType.USER,
    is_llm_message: true,
    metadata: {},
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  it('should create UserMessage', () => {
    const message: UserMessage = {
      ...baseMessage,
      type: MessageType.USER,
      content: 'Hello',
    };
    expect(message.type).toBe(MessageType.USER);
    expect(message.content).toBe('Hello');
  });

  it('should create AssistantMessage', () => {
    const message: AssistantMessage = {
      ...baseMessage,
      type: MessageType.ASSISTANT,
      content: {
        role: Role.ASSISTANT,
        content: 'Response',
      },
    };
    expect(message.type).toBe(MessageType.ASSISTANT);
    expect(message.content.role).toBe(Role.ASSISTANT);
  });

  it('should create ToolResultMessage', () => {
    const message: ToolResultMessage = {
      ...baseMessage,
      type: MessageType.TOOL,
      content: {
        result: 'success',
      },
    };
    expect(message.type).toBe(MessageType.TOOL);
    expect(message.content.result).toBe('success');
  });

  it('should create StatusMessage', () => {
    const message: StatusMessage = {
      ...baseMessage,
      type: MessageType.STATUS,
      content: {
        status: 'running',
      },
    };
    expect(message.type).toBe(MessageType.STATUS);
    expect(message.content.status).toBe('running');
  });

  it('should create AssistantResponseEndMessage', () => {
    const message: AssistantResponseEndMessage = {
      ...baseMessage,
      type: MessageType.ASSISTANT_RESPONSE_END,
      content: {
        finished: true,
      },
    };
    expect(message.type).toBe(MessageType.ASSISTANT_RESPONSE_END);
    expect(message.content.finished).toBe(true);
  });
});

describe('ChatMessage type', () => {
  it('should accept UserMessage', () => {
    const message: ChatMessage = {
      message_id: 'msg-1',
      thread_id: 'thread-1',
      type: MessageType.USER,
      is_llm_message: true,
      metadata: {},
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      content: 'Hello',
    };
    expect(message.type).toBe(MessageType.USER);
  });
});

describe('AgentRun interface', () => {
  it('should create AgentRun with required fields', () => {
    const run: AgentRun = {
      id: 'run-1',
      thread_id: 'thread-1',
      status: 'completed',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    expect(run.id).toBe('run-1');
    expect(run.status).toBe('completed');
  });

  it('should create AgentRun with optional fields', () => {
    const run: AgentRun = {
      id: 'run-1',
      thread_id: 'thread-1',
      status: 'completed',
      started_at: '2024-01-01T00:00:00Z',
      completed_at: '2024-01-01T00:01:00Z',
      error: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    expect(run.started_at).toBeDefined();
    expect(run.completed_at).toBeDefined();
  });
});

