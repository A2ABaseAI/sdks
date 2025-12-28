"""Agent generator - create new agent modules."""
from pathlib import Path

from a2abase_cli.generators.shared import safe_write, slugify


class AgentGenerator:
    """Generate a new agent module."""

    def __init__(
        self,
        agent_name: str,
        package_name: str,
        project_root: Path,
        force: bool = False,
    ):
        self.agent_name = slugify(agent_name)
        self.package_name = package_name
        self.project_root = project_root
        self.force = force

    def generate(self) -> None:
        """Generate the agent module."""
        agents_dir = self.project_root / "src" / self.package_name / "agents"
        agent_file = agents_dir / f"{self.agent_name}_agent.py"

        content = f'''"""{self.agent_name.replace("_", " ").title()} agent with custom tools."""
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools, MCPTools
except ImportError:
    import sys
    from pathlib import Path
    vendor_path = Path(__file__).parent.parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools, MCPTools  # type: ignore

# Import your custom tool schemas here
# from {self.package_name}.tools.your_tool import YOUR_TOOL_SCHEMA


async def create_{self.agent_name}_agent(client: A2ABaseClient):
    """
    Create a {self.agent_name.replace("_", " ")} agent.

    Args:
        client: A2ABase client instance

    Returns:
        Agent instance
    
    Note: To use custom tools with OpenAI schema, register them via MCP:
    1. Set up an MCP server that serves your tools
    2. Use MCPTools to connect to your MCP server
    3. Pass the MCPTools instance in a2abase_tools
    """
    # Option 1: Use built-in A2ABase tools
    agent = await client.Agent.create(
        name="{self.agent_name.replace("_", " ").title()} Agent",
        system_prompt=(
            "You are a helpful {self.agent_name.replace("_", " ")} assistant. "
            "Provide accurate and useful information."
        ),
        a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL],
    )
    
    # Option 2: Add custom tools via MCP (uncomment when MCP server is ready)
    # custom_tools = MCPTools(
    #     endpoint="http://localhost:8000/mcp",
    #     name="custom_tools",
    #     allowed_tools=["your_tool_name"]
    # )
    # await custom_tools.initialize()
    # agent = await client.Agent.create(
    #     name="{self.agent_name.replace("_", " ").title()} Agent",
    #     system_prompt="...",
    #     a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL, custom_tools],
    # )
    
    return agent
'''
        safe_write(agent_file, content, self.force)

