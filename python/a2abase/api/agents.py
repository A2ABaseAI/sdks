# Re-implemented via local a2astudio tools/types
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import httpx
import json

from ..tools import A2ABaseTools


@dataclass
class MCPConfig:
    url: str


@dataclass
class CustomMCP:
    name: str
    type: str
    config: MCPConfig
    enabled_tools: List[str]


@dataclass
class AgentPress_ToolConfig:
    enabled: bool
    description: str


@dataclass
class AgentCreateRequest:
    name: str
    system_prompt: str
    description: Optional[str] = None
    custom_mcps: Optional[List[CustomMCP]] = None
    agentpress_tools: Optional[Dict[A2ABaseTools, AgentPress_ToolConfig]] = None
    is_default: bool = False
    avatar: Optional[str] = None
    avatar_color: Optional[str] = None
    profile_image_url: Optional[str] = None
    icon_name: Optional[str] = None
    icon_color: Optional[str] = None
    icon_background: Optional[str] = None


@dataclass
class AgentUpdateRequest:
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    custom_mcps: Optional[List[CustomMCP]] = None
    agentpress_tools: Optional[Dict[A2ABaseTools, AgentPress_ToolConfig]] = None
    is_default: Optional[bool] = None
    avatar: Optional[str] = None
    avatar_color: Optional[str] = None
    profile_image_url: Optional[str] = None
    icon_name: Optional[str] = None
    icon_color: Optional[str] = None
    icon_background: Optional[str] = None


@dataclass
class AgentVersionResponse:
    version_id: str
    agent_id: str
    version_number: int
    version_name: str
    system_prompt: str
    custom_mcps: List[CustomMCP]
    agentpress_tools: Dict[A2ABaseTools, AgentPress_ToolConfig]
    is_active: bool
    created_at: str
    updated_at: str
    created_by: Optional[str] = None


@dataclass
class AgentResponse:
    agent_id: str
    name: str
    system_prompt: str
    custom_mcps: List[CustomMCP]
    agentpress_tools: Dict[A2ABaseTools, AgentPress_ToolConfig]
    is_default: bool
    created_at: str
    # Optional fields must follow required ones
    account_id: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    avatar_color: Optional[str] = None
    updated_at: Optional[str] = None
    is_public: Optional[bool] = False
    marketplace_published_at: Optional[str] = None
    download_count: Optional[int] = 0
    tags: Optional[List[str]] = None
    current_version_id: Optional[str] = None
    version_count: Optional[int] = 1
    current_version: Optional[AgentVersionResponse] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaginationInfo:
    page: int
    limit: int
    total: int
    pages: int


@dataclass
class AgentsResponse:
    agents: List[AgentResponse]
    pagination: PaginationInfo


@dataclass
class AgentTool:
    name: str
    enabled: bool
    server: Optional[str] = None
    description: Optional[str] = None


@dataclass
class AgentToolsResponse:
    agentpress_tools: List[AgentTool]
    mcp_tools: List[AgentTool]


@dataclass
class DeleteAgentResponse:
    message: str


def to_dict(obj) -> Dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: v for k, v in asdict(obj).items() if v is not None}
    return obj


def from_dict(cls, data: Dict[str, Any]):
    if not data:
        return None
    if cls == AgentsResponse:
        agents = [from_dict(AgentResponse, a) for a in data.get("agents", [])]
        pagination_data = data.get("pagination", {})
        if pagination_data and isinstance(pagination_data, dict) and len(pagination_data) > 0:
            try:
                pagination = from_dict(PaginationInfo, pagination_data)
            except (TypeError, KeyError):
                # Fallback if pagination parsing fails
                pagination = PaginationInfo(
                    page=pagination_data.get("page", data.get("page", 1)),
                    limit=pagination_data.get("limit", data.get("limit", len(agents))),
                    total=pagination_data.get("total", data.get("total", len(agents))),
                    pages=pagination_data.get("pages", data.get("pages", 1))
                )
        else:
            # Fallback if pagination is missing
            pagination = PaginationInfo(
                page=data.get("page", 1),
                limit=data.get("limit", len(agents)),
                total=data.get("total", len(agents)),
                pages=data.get("pages", 1)
            )
        return cls(agents=agents, pagination=pagination)
    if cls == AgentResponse:
        current_version = None
        if data.get("current_version"):
            current_version = from_dict(AgentVersionResponse, data["current_version"])
        custom_mcps = []
        if data.get("custom_mcps"):
            custom_mcps = [from_dict(CustomMCP, m) for m in data["custom_mcps"]]
        # Handle agentpress_tools - it comes as a dict with string keys
        agentpress_tools = {}
        if data.get("agentpress_tools"):
            from ..tools import A2ABaseTools
            for tool_key, tool_config in data["agentpress_tools"].items():
                try:
                    tool_enum = A2ABaseTools(tool_key)
                    if isinstance(tool_config, dict):
                        config = AgentPress_ToolConfig(
                            enabled=tool_config.get("enabled", False),
                            description=tool_config.get("description", "")
                        )
                    else:
                        config = tool_config
                    agentpress_tools[tool_enum] = config
                except (ValueError, KeyError):
                    # Skip invalid tool keys
                    pass
        agent_data = {k: v for k, v in data.items() if k not in ["current_version", "custom_mcps", "agentpress_tools"]}
        agent_data["current_version"] = current_version
        agent_data["custom_mcps"] = custom_mcps
        agent_data["agentpress_tools"] = agentpress_tools
        agent_data["tags"] = agent_data.get("tags", [])
        return cls(**{k: v for k, v in agent_data.items() if k in cls.__dataclass_fields__})
    if hasattr(cls, "__dataclass_fields__"):
        filtered = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**filtered)
    return data


class AgentsClient:
    def __init__(self, base_url: str, auth_token: Optional[str] = None, custom_headers: Optional[Dict[str, str]] = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        default_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if auth_token:
            default_headers["X-API-Key"] = auth_token
        if custom_headers:
            default_headers.update(custom_headers)
        self.client = httpx.AsyncClient(headers=default_headers, timeout=timeout, base_url=self.base_url)

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", f"HTTP {response.status_code}")
            except:
                detail = f"HTTP {response.status_code}"
            raise httpx.HTTPStatusError(f"API request failed: {detail}", request=response.request, response=response)
        return response.json()

    async def get_agents(self, page: int = 1, limit: int = 20, search: Optional[str] = None, sort_by: str = "created_at", sort_order: str = "desc") -> AgentsResponse:
        params = {"page": page, "limit": limit, "sort_by": sort_by, "sort_order": sort_order}
        if search:
            params["search"] = search
        data = self._handle_response(await self.client.get("/agents", params=params))
        return from_dict(AgentsResponse, data)

    async def get_agent(self, agent_id: str) -> AgentResponse:
        data = self._handle_response(await self.client.get(f"/agents/{agent_id}"))
        return from_dict(AgentResponse, data)

    async def create_agent(self, request: AgentCreateRequest) -> AgentResponse:
        data = self._handle_response(await self.client.post("/agents", json=to_dict(request)))
        return from_dict(AgentResponse, data)

    async def update_agent(self, agent_id: str, request: AgentUpdateRequest) -> AgentResponse:
        data = self._handle_response(await self.client.put(f"/agents/{agent_id}", json=to_dict(request)))
        return from_dict(AgentResponse, data)

    async def delete_agent(self, agent_id: str) -> DeleteAgentResponse:
        data = self._handle_response(await self.client.delete(f"/agents/{agent_id}"))
        return DeleteAgentResponse(message=data.get("message", "ok"))


def create_agents_client(base_url: str, auth_token: Optional[str] = None, custom_headers: Optional[Dict[str, str]] = None, timeout: float = 30.0) -> AgentsClient:
    return AgentsClient(base_url=base_url, auth_token=auth_token, custom_headers=custom_headers, timeout=timeout)

