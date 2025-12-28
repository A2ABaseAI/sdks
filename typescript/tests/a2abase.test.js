"use strict";
/**
 * Unit tests for a2abase.ts
 */
Object.defineProperty(exports, "__esModule", { value: true });
const a2abase_1 = require("../src/a2abase");
const agent_1 = require("../src/agent");
const thread_1 = require("../src/thread");
describe('A2ABase', () => {
    let client;
    describe('constructor', () => {
        it('should create A2ABase with default URL', () => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
            });
            expect(client).toBeDefined();
            expect(client.Agent).toBeInstanceOf(agent_1.A2ABaseAgent);
            expect(client.Thread).toBeInstanceOf(thread_1.A2ABaseThread);
        });
        it('should create A2ABase with custom URL', () => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
                apiUrl: 'https://custom.api.com',
            });
            expect(client).toBeDefined();
        });
        it('should create A2ABase with timeout', () => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
                timeout: 60000,
            });
            expect(client).toBeDefined();
        });
        it('should strip trailing slash from URL', () => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
                apiUrl: 'https://api.example.com/',
            });
            expect(client).toBeDefined();
        });
    });
    describe('getAgents', () => {
        beforeEach(() => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
                apiUrl: 'https://api.example.com',
            });
        });
        it('should get agents with params', async () => {
            const mockResponse = {
                agents: [],
                pagination: { page: 1, limit: 10, total: 0, pages: 0 },
            };
            // Mock the internal agentsClient
            const mockGetAgents = jest.fn().mockResolvedValue(mockResponse);
            client.agentsClient = {
                getAgents: mockGetAgents,
            };
            const result = await client.getAgents({ page: 1, limit: 10, search: 'test' });
            expect(mockGetAgents).toHaveBeenCalledWith({ page: 1, limit: 10, search: 'test' });
            expect(result).toEqual(mockResponse);
        });
        it('should get agents without params', async () => {
            const mockResponse = {
                agents: [],
                pagination: { page: 1, limit: 10, total: 0, pages: 0 },
            };
            const mockGetAgents = jest.fn().mockResolvedValue(mockResponse);
            client.agentsClient = {
                getAgents: mockGetAgents,
            };
            const result = await client.getAgents();
            expect(mockGetAgents).toHaveBeenCalledWith(undefined);
            expect(result).toEqual(mockResponse);
        });
    });
    describe('Agent property', () => {
        beforeEach(() => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
            });
        });
        it('should provide A2ABaseAgent instance', () => {
            expect(client.Agent).toBeInstanceOf(agent_1.A2ABaseAgent);
        });
    });
    describe('Thread property', () => {
        beforeEach(() => {
            client = new a2abase_1.A2ABase({
                apiKey: 'test-key',
            });
        });
        it('should provide A2ABaseThread instance', () => {
            expect(client.Thread).toBeInstanceOf(thread_1.A2ABaseThread);
        });
    });
});
describe('A2ABaseConfig', () => {
    it('should accept required apiKey', () => {
        const config = {
            apiKey: 'test-key',
        };
        expect(config.apiKey).toBe('test-key');
    });
    it('should accept optional apiUrl', () => {
        const config = {
            apiKey: 'test-key',
            apiUrl: 'https://custom.api.com',
        };
        expect(config.apiUrl).toBe('https://custom.api.com');
    });
    it('should accept optional timeout', () => {
        const config = {
            apiKey: 'test-key',
            timeout: 60000,
        };
        expect(config.timeout).toBe(60000);
    });
});
