"use strict";
/**
 * Unit tests for models.ts
 */
Object.defineProperty(exports, "__esModule", { value: true });
const models_1 = require("../src/models");
describe('Role enum', () => {
    it('should have correct values', () => {
        expect(models_1.Role.USER).toBe('user');
        expect(models_1.Role.ASSISTANT).toBe('assistant');
        expect(models_1.Role.SYSTEM).toBe('system');
    });
});
describe('MessageType enum', () => {
    it('should have correct values', () => {
        expect(models_1.MessageType.USER).toBe('user');
        expect(models_1.MessageType.ASSISTANT).toBe('assistant');
        expect(models_1.MessageType.TOOL).toBe('tool');
        expect(models_1.MessageType.STATUS).toBe('status');
        expect(models_1.MessageType.ASSISTANT_RESPONSE_END).toBe('assistant_response_end');
    });
});
describe('ContentObject', () => {
    it('should create ContentObject with required fields', () => {
        const content = {
            role: models_1.Role.USER,
            content: 'Hello',
        };
        expect(content.role).toBe(models_1.Role.USER);
        expect(content.content).toBe('Hello');
    });
    it('should create ContentObject with tool_calls', () => {
        const content = {
            role: models_1.Role.ASSISTANT,
            content: 'Response',
            tool_calls: [{ name: 'test', arguments: {} }],
        };
        expect(content.tool_calls).toBeDefined();
    });
});
describe('Message interfaces', () => {
    const baseMessage = {
        message_id: 'msg-1',
        thread_id: 'thread-1',
        type: models_1.MessageType.USER,
        is_llm_message: true,
        metadata: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
    };
    it('should create UserMessage', () => {
        const message = {
            ...baseMessage,
            type: models_1.MessageType.USER,
            content: 'Hello',
        };
        expect(message.type).toBe(models_1.MessageType.USER);
        expect(message.content).toBe('Hello');
    });
    it('should create AssistantMessage', () => {
        const message = {
            ...baseMessage,
            type: models_1.MessageType.ASSISTANT,
            content: {
                role: models_1.Role.ASSISTANT,
                content: 'Response',
            },
        };
        expect(message.type).toBe(models_1.MessageType.ASSISTANT);
        expect(message.content.role).toBe(models_1.Role.ASSISTANT);
    });
    it('should create ToolResultMessage', () => {
        const message = {
            ...baseMessage,
            type: models_1.MessageType.TOOL,
            content: {
                result: 'success',
            },
        };
        expect(message.type).toBe(models_1.MessageType.TOOL);
        expect(message.content.result).toBe('success');
    });
    it('should create StatusMessage', () => {
        const message = {
            ...baseMessage,
            type: models_1.MessageType.STATUS,
            content: {
                status: 'running',
            },
        };
        expect(message.type).toBe(models_1.MessageType.STATUS);
        expect(message.content.status).toBe('running');
    });
    it('should create AssistantResponseEndMessage', () => {
        const message = {
            ...baseMessage,
            type: models_1.MessageType.ASSISTANT_RESPONSE_END,
            content: {
                finished: true,
            },
        };
        expect(message.type).toBe(models_1.MessageType.ASSISTANT_RESPONSE_END);
        expect(message.content.finished).toBe(true);
    });
});
describe('ChatMessage type', () => {
    it('should accept UserMessage', () => {
        const message = {
            message_id: 'msg-1',
            thread_id: 'thread-1',
            type: models_1.MessageType.USER,
            is_llm_message: true,
            metadata: {},
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            content: 'Hello',
        };
        expect(message.type).toBe(models_1.MessageType.USER);
    });
});
describe('AgentRun interface', () => {
    it('should create AgentRun with required fields', () => {
        const run = {
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
        const run = {
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
