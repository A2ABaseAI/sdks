"use strict";
/**
 * Unit tests for api/agents.ts
 */
Object.defineProperty(exports, "__esModule", { value: true });
const agents_1 = require("../src/api/agents");
describe('AgentsClient', () => {
    let client;
    let mockApiClient;
    beforeEach(() => {
        mockApiClient = {
            get: jest.fn(),
            post: jest.fn(),
            put: jest.fn(),
            delete: jest.fn(),
        };
        client = new agents_1.AgentsClient(mockApiClient);
    });
    describe('getAgents', () => {
        it('should get agents with params', async () => {
            const mockResponse = {
                agents: [{ agent_id: '1', name: 'Agent 1' }],
                pagination: { page: 1, limit: 10, total: 1, pages: 1 },
            };
            mockApiClient.get.mockResolvedValue(mockResponse);
            const result = await client.getAgents({ page: 1, limit: 10, search: 'test' });
            expect(mockApiClient.get).toHaveBeenCalledWith('/agents', { page: 1, limit: 10, search: 'test' });
            expect(result.agents).toEqual(mockResponse.agents);
            expect(result.pagination).toEqual(mockResponse.pagination);
        });
        it('should normalize pagination info with missing fields', async () => {
            const mockResponse = {
                agents: [],
                pagination: { page: 1 },
            };
            mockApiClient.get.mockResolvedValue(mockResponse);
            const result = await client.getAgents();
            expect(result.pagination.page).toBe(1);
            expect(result.pagination.limit).toBe(0);
            expect(result.pagination.total).toBe(0);
            expect(result.pagination.pages).toBe(0);
        });
        it('should normalize pagination info with undefined fields', async () => {
            const mockResponse = {
                agents: [],
                pagination: {},
            };
            mockApiClient.get.mockResolvedValue(mockResponse);
            const result = await client.getAgents();
            expect(result.pagination.page).toBe(0);
            expect(result.pagination.limit).toBe(0);
            expect(result.pagination.total).toBe(0);
            expect(result.pagination.pages).toBe(0);
        });
        it('should normalize pagination info with some undefined fields', async () => {
            const mockResponse = {
                agents: [],
                pagination: {
                    page: 1,
                    limit: 10,
                    // total and pages are undefined
                },
            };
            mockApiClient.get.mockResolvedValue(mockResponse);
            const result = await client.getAgents();
            expect(result.pagination.page).toBe(1);
            expect(result.pagination.limit).toBe(10);
            expect(result.pagination.total).toBe(0);
            expect(result.pagination.pages).toBe(0);
        });
        it('should normalize pagination info with explicitly undefined field', async () => {
            const mockResponse = {
                agents: [],
                pagination: {
                    page: 1,
                    limit: 10,
                    total: undefined,
                    pages: undefined,
                },
            };
            mockApiClient.get.mockResolvedValue(mockResponse);
            const result = await client.getAgents();
            expect(result.pagination.page).toBe(1);
            expect(result.pagination.limit).toBe(10);
            expect(result.pagination.total).toBe(0);
            expect(result.pagination.pages).toBe(0);
        });
    });
    describe('getAgent', () => {
        it('should get agent by ID', async () => {
            const mockAgent = { agent_id: '123', name: 'Test Agent' };
            mockApiClient.get.mockResolvedValue(mockAgent);
            const result = await client.getAgent('123');
            expect(mockApiClient.get).toHaveBeenCalledWith('/agents/123');
            expect(result).toEqual(mockAgent);
        });
    });
    describe('createAgent', () => {
        it('should create agent', async () => {
            const request = { name: 'Test', system_prompt: 'Test prompt' };
            const mockAgent = { agent_id: '123', name: 'Test' };
            mockApiClient.post.mockResolvedValue(mockAgent);
            const result = await client.createAgent(request);
            expect(mockApiClient.post).toHaveBeenCalledWith('/agents', request);
            expect(result).toEqual(mockAgent);
        });
    });
    describe('updateAgent', () => {
        it('should update agent', async () => {
            const request = { name: 'Updated' };
            const mockAgent = { agent_id: '123', name: 'Updated' };
            mockApiClient.put.mockResolvedValue(mockAgent);
            const result = await client.updateAgent('123', request);
            expect(mockApiClient.put).toHaveBeenCalledWith('/agents/123', request);
            expect(result).toEqual(mockAgent);
        });
    });
    describe('deleteAgent', () => {
        it('should delete agent', async () => {
            const mockResponse = { message: 'Deleted' };
            mockApiClient.delete.mockResolvedValue(mockResponse);
            const result = await client.deleteAgent('123');
            expect(mockApiClient.delete).toHaveBeenCalledWith('/agents/123');
            expect(result).toEqual(mockResponse);
        });
    });
});
