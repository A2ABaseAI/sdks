/**
 * Base HTTP client for API requests
 */

import { request, Dispatcher } from 'undici';

export interface ClientConfig {
  baseUrl: string;
  apiKey: string;
  timeout?: number;
}

export class APIClient {
  public readonly baseUrl: string;
  public readonly headers: Record<string, string>;
  private timeout: number;

  constructor(config: ClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    this.timeout = config.timeout || 30000;
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-API-Key': config.apiKey,
    };
  }

  private async request<T>(
    method: string,
    path: string,
    options: {
      body?: any;
      params?: Record<string, string | number>;
      headers?: Record<string, string>;
    } = {}
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const headers: Record<string, string> = { ...this.headers };
    if (options.headers) {
      Object.assign(headers, options.headers);
    }
    
    const body = options.body ? JSON.stringify(options.body) : undefined;

    const response = await request(url.toString(), {
      method: method as Dispatcher.HttpMethod,
      headers,
      body,
      signal: AbortSignal.timeout(this.timeout),
    });

    if (response.statusCode >= 400) {
      let errorMessage = `HTTP ${response.statusCode}`;
      try {
        const errorData = await response.body.json() as any;
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // Use default error message
      }
      throw new Error(`API request failed: ${errorMessage}`);
    }

    return (await response.body.json()) as Promise<T>;
  }

  async get<T>(path: string, params?: Record<string, string | number>): Promise<T> {
    return this.request<T>('GET', path, { params });
  }

  async post<T>(path: string, body?: any, params?: Record<string, string | number>): Promise<T> {
    return this.request<T>('POST', path, { body, params });
  }

  async put<T>(path: string, body?: any): Promise<T> {
    return this.request<T>('PUT', path, { body });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }
}

