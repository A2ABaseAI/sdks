from .api.threads import AgentStartRequest
from .thread import Thread, AgentRun
from .tools import A2ABaseTools, MCPTools, A2ABaseTool
from .api.agents import (
    AgentCreateRequest,
    AgentPress_ToolConfig,
    AgentUpdateRequest,
    AgentsClient,
    CustomMCP,
    MCPConfig,
)


class Agent:
    def __init__(
        self,
        client: AgentsClient,
        agent_id: str,
        model: str = "gemini/gemini-2.5-pro",
    ):
        self._client = client
        self._agent_id = agent_id
        self._model = model

    async def update(
        self,
        name: str | None = None,
        system_prompt: str | None = None,
        a2abase_tools: list[A2ABaseTool] | None = None,
        allowed_tools: list[str] | None = None,
    ):
        if a2abase_tools:
            agentpress_tools = {} if a2abase_tools else None
            custom_mcps: list[CustomMCP] = [] if a2abase_tools else None
            for tool in a2abase_tools:
                if isinstance(tool, A2ABaseTools):
                    is_enabled = tool.value in allowed_tools if allowed_tools else True
                    agentpress_tools[tool] = AgentPress_ToolConfig(
                        enabled=is_enabled, description=tool.get_description()
                    )
                elif isinstance(tool, MCPTools):
                    mcp = tool
                    # For MCPTools, if allowed_tools is None or empty, enable all discovered tools
                    # If allowed_tools is provided, check if MCP name is in the list
                    # Note: MCPTools already filters tools via its own allowed_tools parameter during initialize()
                    if allowed_tools is None or len(allowed_tools) == 0:
                        # No filtering - enable all discovered tools
                        is_enabled = True
                    else:
                        # Check if this MCP server name is in the allowed_tools list
                        is_enabled = tool.name in allowed_tools
                    
                    custom_mcps.append(
                        CustomMCP(
                            name=mcp.name,
                            type=mcp.type,
                            config=MCPConfig(url=mcp.url),
                            enabled_tools=mcp.enabled_tools if is_enabled else [],
                        )
                    )
        else:
            agent_details = await self.details()
            agentpress_tools = agent_details.agentpress_tools
            custom_mcps = agent_details.custom_mcps
            if allowed_tools:
                for tool in agentpress_tools:
                    if tool.value not in allowed_tools:
                        agentpress_tools[tool].enabled = False
                for mcp in custom_mcps:
                    mcp.enabled_tools = allowed_tools

        await self._client.update_agent(
            self._agent_id,
            AgentUpdateRequest(
                name=name,
                system_prompt=system_prompt,
                custom_mcps=custom_mcps,
                agentpress_tools=agentpress_tools,
            ),
        )

    async def details(self):
        response = await self._client.get_agent(self._agent_id)
        return response

    async def run(
        self,
        prompt: str,
        thread: Thread,
        model: str | None = None,
    ):
        await thread.add_message(prompt)
        response = await thread._client.start_agent(
            thread._thread_id,
            AgentStartRequest(
                agent_id=self._agent_id,
                model_name=model or self._model,
            ),
        )
        return AgentRun(thread, response.agent_run_id)

    async def delete(self) -> None:
        await self._client.delete_agent(self._agent_id)


class A2ABaseAgent:
    def __init__(self, client: AgentsClient):
        self._client = client

    async def create(
        self,
        name: str,
        system_prompt: str,
        a2abase_tools: list[A2ABaseTool] = [],
        allowed_tools: list[str] | None = None,
    ) -> Agent:
        agentpress_tools = {}
        custom_mcps: list[CustomMCP] = []
        for tool in a2abase_tools:
            if isinstance(tool, A2ABaseTools):
                is_enabled = tool.value in allowed_tools if allowed_tools else True
                agentpress_tools[tool] = AgentPress_ToolConfig(
                    enabled=is_enabled, description=tool.get_description()
                )
            elif isinstance(tool, MCPTools):
                mcp = tool
                # For MCPTools, if allowed_tools is None or empty, enable all discovered tools
                # If allowed_tools is provided, check if MCP name is in the list
                # Note: MCPTools already filters tools via its own allowed_tools parameter during initialize()
                if allowed_tools is None or len(allowed_tools) == 0:
                    # No filtering - enable all discovered tools
                    is_enabled = True
                else:
                    # Check if this MCP server name is in the allowed_tools list
                    is_enabled = tool.name in allowed_tools
                
                custom_mcps.append(
                    CustomMCP(
                        name=mcp.name,
                        type=mcp.type,
                        config=MCPConfig(url=mcp.url),
                        enabled_tools=mcp.enabled_tools if is_enabled else [],
                    )
                )
            else:
                raise ValueError(f"Unknown tool type: {type(tool)}")

        agent = await self._client.create_agent(
            AgentCreateRequest(
                name=name,
                system_prompt=system_prompt,
                custom_mcps=custom_mcps,
                agentpress_tools=agentpress_tools,
            )
        )

        return Agent(self._client, agent.agent_id)

    async def get(self, agent_id: str) -> Agent:
        agent = await self._client.get_agent(agent_id)
        return Agent(self._client, agent.agent_id)

    async def find_by_name(self, name: str) -> Agent | None:
        try:
            resp = await self._client.get_agents(page=1, limit=100, search=name)
            # First try exact match from search results
            for a in resp.agents:
                if a.name == name:
                    return Agent(self._client, a.agent_id)
            # If not found and we have more pages, check them
            if resp.pagination and resp.pagination.pages > 1:
                for page in range(2, min(resp.pagination.pages + 1, 10)):  # Limit to 10 pages
                    resp = await self._client.get_agents(page=page, limit=100, search=name)
                    for a in resp.agents:
                        if a.name == name:
                            return Agent(self._client, a.agent_id)
            return None
        except Exception:
            return None
