"use strict";
/**
 * Unit tests for api/client.ts
 */
Object.defineProperty(exports, "__esModule", { value: true });
// Mock undici before importing
jest.mock('undici', () => ({
    request: jest.fn(),
}));
const client_1 = require("../src/api/client");
const undici_1 = require("undici");
describe('APIClient', () => {
    let client;
    const mockRequest = undici_1.request;
    beforeEach(() => {
        jest.clearAllMocks();
        client = new client_1.APIClient({
            baseUrl: 'https://api.example.com',
            apiKey: 'test-api-key',
        });
    });
    describe('constructor', () => {
        it('should create APIClient with required config', () => {
            expect(client.baseUrl).toBe('https://api.example.com');
            expect(client.headers['X-API-Key']).toBe('test-api-key');
            expect(client.headers['Content-Type']).toBe('application/json');
            expect(client.headers['Accept']).toBe('application/json');
        });
        it('should strip trailing slash from baseUrl', () => {
            const clientWithSlash = new client_1.APIClient({
                baseUrl: 'https://api.example.com/',
                apiKey: 'test-key',
            });
            expect(clientWithSlash.baseUrl).toBe('https://api.example.com');
        });
        it('should set default timeout', () => {
            expect(client).toBeDefined();
        });
        it('should set custom timeout', () => {
            const customClient = new client_1.APIClient({
                baseUrl: 'https://api.example.com',
                apiKey: 'test-key',
                timeout: 60000,
            });
            expect(customClient).toBeDefined();
        });
    });
    describe('get', () => {
        it('should make GET request', async () => {
            const mockResponse = {
                statusCode: 200,
                body: {
                    json: jest.fn().mockResolvedValue({ data: 'test' }),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            const result = await client.get('/test', { param: 'value' });
            expect(mockRequest).toHaveBeenCalledWith('https://api.example.com/test?param=value', expect.objectContaining({
                method: 'GET',
                headers: expect.objectContaining({
                    'X-API-Key': 'test-api-key',
                }),
            }));
            expect(result).toEqual({ data: 'test' });
        });
        it('should merge custom headers in request', async () => {
            const mockResponse = {
                statusCode: 200,
                body: {
                    json: jest.fn().mockResolvedValue({ data: 'test' }),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            // Access private method via type assertion to test header merging
            const requestMethod = client.request.bind(client);
            await requestMethod('POST', '/test', {
                body: { name: 'test' },
                headers: { 'Custom-Header': 'value' },
            });
            expect(mockRequest).toHaveBeenCalledWith('https://api.example.com/test', expect.objectContaining({
                headers: expect.objectContaining({
                    'X-API-Key': 'test-api-key',
                    'Custom-Header': 'value',
                }),
            }));
        });
    });
    describe('post', () => {
        it('should make POST request with body', async () => {
            const mockResponse = {
                statusCode: 200,
                body: {
                    json: jest.fn().mockResolvedValue({ id: '123' }),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            const result = await client.post('/test', { name: 'test' });
            expect(mockRequest).toHaveBeenCalledWith('https://api.example.com/test', expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ name: 'test' }),
            }));
            expect(result).toEqual({ id: '123' });
        });
    });
    describe('put', () => {
        it('should make PUT request', async () => {
            const mockResponse = {
                statusCode: 200,
                body: {
                    json: jest.fn().mockResolvedValue({ updated: true }),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            const result = await client.put('/test', { name: 'updated' });
            expect(mockRequest).toHaveBeenCalledWith('https://api.example.com/test', expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify({ name: 'updated' }),
            }));
            expect(result).toEqual({ updated: true });
        });
    });
    describe('delete', () => {
        it('should make DELETE request', async () => {
            const mockResponse = {
                statusCode: 200,
                body: {
                    json: jest.fn().mockResolvedValue({ deleted: true }),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            const result = await client.delete('/test');
            expect(mockRequest).toHaveBeenCalledWith('https://api.example.com/test', expect.objectContaining({
                method: 'DELETE',
            }));
            expect(result).toEqual({ deleted: true });
        });
    });
    describe('error handling', () => {
        it('should handle HTTP error with JSON response', async () => {
            const mockResponse = {
                statusCode: 400,
                body: {
                    json: jest.fn().mockResolvedValue({ detail: 'Bad request' }),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            await expect(client.get('/test')).rejects.toThrow('API request failed: Bad request');
        });
        it('should handle HTTP error without JSON response', async () => {
            const mockResponse = {
                statusCode: 500,
                body: {
                    json: jest.fn().mockRejectedValue(new Error('Invalid JSON')),
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            await expect(client.get('/test')).rejects.toThrow('API request failed: HTTP 500');
        });
        it('should handle HTTP error with JSON response without detail', async () => {
            const mockResponse = {
                statusCode: 400,
                body: {
                    json: jest.fn().mockResolvedValue({ message: 'Error' }), // No 'detail' field
                },
            };
            mockRequest.mockResolvedValue(mockResponse);
            await expect(client.get('/test')).rejects.toThrow('API request failed: HTTP 400');
        });
    });
});
