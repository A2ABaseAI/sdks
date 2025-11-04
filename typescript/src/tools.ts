/**
 * Tools for the BaseAI SDK
 */

export enum BaseAITool {
  FILES_TOOL = "sb_files_tool",
  SHELL_TOOL = "sb_shell_tool",
  WEB_DEV_TOOL = "sb_web_dev_tool",
  DEPLOY_TOOL = "sb_deploy_tool",
  EXPOSE_TOOL = "sb_expose_tool",
  VISION_TOOL = "sb_vision_tool",
  BROWSER_TOOL = "browser_tool",
  WEB_SEARCH_TOOL = "web_search_tool",
  IMAGE_SEARCH_TOOL = "image_search_tool",
  IMAGE_EDIT_TOOL = "sb_image_edit_tool",
  KB_TOOL = "sb_kb_tool",
  DESIGN_TOOL = "sb_design_tool",
  PRESENTATION_OUTLINE_TOOL = "sb_presentation_outline_tool",
  PRESENTATION_TOOL = "sb_presentation_tool",
  SHEETS_TOOL = "sb_sheets_tool",
  UPLOAD_FILE_TOOL = "sb_upload_file_tool",
  DOCS_TOOL = "sb_docs_tool",
  DATA_PROVIDERS_TOOL = "data_providers_tool",
}

const BaseAIToolDescriptions: Record<string, string> = {
  "sb_files_tool": "Read, write, and edit files",
  "sb_shell_tool": "Execute shell commands",
  "sb_web_dev_tool": "Create and manage modern web applications with Next.js and shadcn/ui",
  "sb_deploy_tool": "Deploy web applications",
  "sb_expose_tool": "Expose local services to the internet",
  "sb_vision_tool": "Analyze and understand images",
  "browser_tool": "Browse websites and interact with web pages",
  "web_search_tool": "Search the web for information",
  "image_search_tool": "Search for images on the web",
  "sb_image_edit_tool": "Edit and manipulate images",
  "sb_kb_tool": "Access and manage knowledge base",
  "sb_design_tool": "Design and create visual content",
  "sb_presentation_outline_tool": "Create presentation outlines",
  "sb_presentation_tool": "Create and manage presentations",
  "sb_sheets_tool": "Create and manage spreadsheets",
  "sb_upload_file_tool": "Upload files to the sandbox",
  "sb_docs_tool": "Create and manage documents",
  "data_providers_tool": "Access structured data from various providers",
};

export function getAgentPressToolDescription(tool: BaseAITool): string {
  const desc = BaseAIToolDescriptions[tool];
  if (!desc) {
    throw new Error(`No description found for ${tool}`);
  }
  return desc;
}

export interface MCPToolsConfig {
  endpoint: string;
  name: string;
  allowedTools?: string[];
}

export class MCPTools {
  public url: string;
  public name: string;
  public type: string;
  public enabledTools: string[];

  constructor(config: MCPToolsConfig) {
    this.url = config.endpoint;
    this.name = config.name;
    this.type = "http";
    this.enabledTools = config.allowedTools || [];
  }

  async initialize(): Promise<MCPTools> {
    // MCP initialization would go here
    // For now, just return self
    return this;
  }
}

export type BaseAITools = BaseAITool | MCPTools;

