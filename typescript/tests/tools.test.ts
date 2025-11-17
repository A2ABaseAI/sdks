/**
 * Unit tests for tools.ts
 */

import { A2ABaseTool, MCPTools, A2ABaseTools, getAgentPressToolDescription } from '../src/tools';

describe('A2ABaseTool', () => {
  it('should have all expected tool values', () => {
    expect(A2ABaseTool.FILES_TOOL).toBe('sb_files_tool');
    expect(A2ABaseTool.WEB_SEARCH_TOOL).toBe('web_search_tool');
    expect(A2ABaseTool.BROWSER_TOOL).toBe('browser_tool');
  });

  it('should get description for valid tool', () => {
    const desc = getAgentPressToolDescription(A2ABaseTool.WEB_SEARCH_TOOL);
    expect(desc).toBe('Search the web for information');
  });

  it('should get description for all tools', () => {
    const tools = Object.values(A2ABaseTool);
    for (const tool of tools) {
      const desc = getAgentPressToolDescription(tool);
      expect(desc).toBeDefined();
      expect(typeof desc).toBe('string');
      expect(desc.length).toBeGreaterThan(0);
    }
  });

  it('should throw error for invalid tool', () => {
    expect(() => {
      getAgentPressToolDescription('invalid_tool' as A2ABaseTool);
    }).toThrow('No description found for invalid_tool');
  });
});

describe('MCPTools', () => {
  it('should create MCPTools with required config', () => {
    const mcp = new MCPTools({
      endpoint: 'http://example.com/mcp',
      name: 'test-mcp',
    });

    expect(mcp.url).toBe('http://example.com/mcp');
    expect(mcp.name).toBe('test-mcp');
    expect(mcp.type).toBe('http');
    expect(mcp.enabledTools).toEqual([]);
  });

  it('should create MCPTools with allowedTools', () => {
    const mcp = new MCPTools({
      endpoint: 'http://example.com/mcp',
      name: 'test-mcp',
      allowedTools: ['tool1', 'tool2'],
    });

    expect(mcp.enabledTools).toEqual(['tool1', 'tool2']);
  });

  it('should initialize MCPTools', async () => {
    const mcp = new MCPTools({
      endpoint: 'http://example.com/mcp',
      name: 'test-mcp',
    });

    const initialized = await mcp.initialize();
    expect(initialized).toBe(mcp);
  });
});

describe('A2ABaseTools type', () => {
  it('should accept A2ABaseTool enum', () => {
    const tool: A2ABaseTools = A2ABaseTool.WEB_SEARCH_TOOL;
    expect(tool).toBe(A2ABaseTool.WEB_SEARCH_TOOL);
  });

  it('should accept MCPTools instance', () => {
    const mcp = new MCPTools({
      endpoint: 'http://example.com/mcp',
      name: 'test-mcp',
    });
    const tool: A2ABaseTools = mcp;
    expect(tool).toBe(mcp);
  });
});

