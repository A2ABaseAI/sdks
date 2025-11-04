from .api.threads import AgentStartRequest
from .thread import Thread, AgentRun
from .tools import BaseAITool, MCPTools, BaseAITools
from .api.agents import (
    AgentCreateRequest,
    BaseAIToolConfig,
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
        mcp_tools: list[BaseAITools] | None = None,
        allowed_tools: list[str] | None = None,
    ):
        if mcp_tools:
            agentpress_tools = {} if mcp_tools else None
            custom_mcps: list[CustomMCP] = [] if mcp_tools else None
            for tool in mcp_tools:
                if isinstance(tool, BaseAITool):
                    is_enabled = tool.value in allowed_tools if allowed_tools else True
                    agentpress_tools[tool] = BaseAIToolConfig(
                        enabled=is_enabled, description=tool.get_description()
                    )
                elif isinstance(tool, MCPTools):
                    mcp = tool
                    is_enabled = tool.name in allowed_tools if allowed_tools else True
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


class BaseAIAgent:
    def __init__(self, client: AgentsClient):
        self._client = client

    async def create(
        self,
        name: str,
        system_prompt: str,
        mcp_tools: list[BaseAITools] = [],
        allowed_tools: list[str] | None = None,
    ) -> Agent:
        agentpress_tools = {}
        custom_mcps: list[CustomMCP] = []
        for tool in mcp_tools:
            if isinstance(tool, BaseAITool):
                is_enabled = tool.value in allowed_tools if allowed_tools else True
                agentpress_tools[tool] = BaseAIToolConfig(
                    enabled=is_enabled, description=tool.get_description()
                )
            elif isinstance(tool, MCPTools):
                mcp = tool
                is_enabled = tool.name in allowed_tools if allowed_tools else True
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
            # naive scan of first page; adjust if backend supports search param
            resp = await self._client.get_agents(page=1, limit=100)
            for a in resp.agents:
                if a.name == name:
                    return Agent(self._client, a.agent_id)
            return None
        except Exception:
            return None
