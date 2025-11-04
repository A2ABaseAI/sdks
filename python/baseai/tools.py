from typing import Union
from enum import Enum
from fastmcp import Client as FastMCPClient


class MCPTools:
    def __init__(
        self, endpoint: str, name: str, allowed_tools: list[str] | None = None
    ):
        self._mcp_client = FastMCPClient(endpoint)
        self.url = endpoint
        self.name = name
        self.type = "http"
        self._initialized = False
        self._allowed_tools = allowed_tools
        self.enabled_tools: list[str] = []

    async def initialize(self):
        async with self._mcp_client:
            tools = await self._mcp_client.list_tools()

        if self._allowed_tools:
            for tool in tools:
                if tool.name in self._allowed_tools:
                    self.enabled_tools.append(tool.name)
        else:
            self.enabled_tools = [tool.name for tool in tools]
        self._initialized = True
        return self


_BaseAITool_descriptions = {
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
}


class BaseAITool(str, Enum):
    FILES_TOOL = "sb_files_tool"
    SHELL_TOOL = "sb_shell_tool"
    WEB_DEV_TOOL = "sb_web_dev_tool"
    DEPLOY_TOOL = "sb_deploy_tool"
    EXPOSE_TOOL = "sb_expose_tool"
    VISION_TOOL = "sb_vision_tool"
    BROWSER_TOOL = "browser_tool"
    WEB_SEARCH_TOOL = "web_search_tool"
    IMAGE_SEARCH_TOOL = "image_search_tool"
    IMAGE_EDIT_TOOL = "sb_image_edit_tool"
    KB_TOOL = "sb_kb_tool"
    DESIGN_TOOL = "sb_design_tool"
    PRESENTATION_OUTLINE_TOOL = "sb_presentation_outline_tool"
    PRESENTATION_TOOL = "sb_presentation_tool"
    SHEETS_TOOL = "sb_sheets_tool"
    UPLOAD_FILE_TOOL = "sb_upload_file_tool"
    DOCS_TOOL = "sb_docs_tool"
    DATA_PROVIDERS_TOOL = "data_providers_tool"

    def get_description(self) -> str:
        global _BaseAITool_descriptions
        desc = _BaseAITool_descriptions.get(self.value)
        if not desc:
            raise ValueError(f"No description found for {self.value}")
        return desc


BaseAITools = Union[BaseAITool, MCPTools]
