"""Project generator - scaffold new projects."""
import shutil
from pathlib import Path

from a2abase_cli.generators.shared import safe_write, slugify, validate_package_name


class ProjectGenerator:
    """Generate a new A2ABase project."""

    def __init__(
        self,
        project_name: str,
        package_name: str,
        template: str,
        package_manager: str,
        project_path: Path,
        force: bool = False,
    ):
        self.project_name = slugify(project_name)
        self.package_name = validate_package_name(package_name)
        self.template = template
        self.package_manager = package_manager
        self.project_path = project_path
        self.force = force

    def generate(self) -> None:
        """Generate the project structure."""
        # Create directory structure
        self._create_directories()
        # Generate files
        self._generate_pyproject_toml()
        self._generate_readme()
        self._generate_gitignore()
        self._generate_env_example()
        self._generate_config()
        
        # Generate based on template mode
        if self.template == "basic":
            self._generate_basic_mode()
        elif self.template == "advanced":
            self._generate_advanced_mode()
        elif self.template == "complex":
            self._generate_complex_mode()
        else:
            # Default to basic for unknown templates
            self._generate_basic_mode()
        
        self._generate_stub_sdk()
        self._generate_tests()

    def _create_directories(self) -> None:
        """Create the directory structure."""
        # Base directories (always created)
        base_dirs = [
            self.project_path / "src" / self.package_name,
            self.project_path / "src" / self.package_name / "agents",
            self.project_path / "src" / self.package_name / "registry",
            self.project_path / "vendor" / "a2abase_sdk_stub",
            self.project_path / "tests",
        ]
        
        # Mode-specific directories
        if self.template in ["advanced", "complex"]:
            base_dirs.append(self.project_path / "src" / self.package_name / "tools")
        
        if self.template == "complex":
            base_dirs.append(self.project_path / "src" / self.package_name / "orchestrator")
        
        for dir_path in base_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _generate_pyproject_toml(self) -> None:
        """Generate pyproject.toml."""
        content = f"""[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.project_name}"
version = "0.1.0"
description = "A2ABase Agent SDK project"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    {{name = "Your Name"}}
]
license = {{text = "MIT"}}
dependencies = [
    "a2abase>=0.1.0",
    "httpx>=0.28.1",
    "fastmcp>=0.1.0",
    "uvicorn>=0.30.0",
    "pyngrok>=7.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[tool.setuptools]
package-dir = {{"" = "src"}}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"
"""
        safe_write(self.project_path / "pyproject.toml", content, self.force)

    def _generate_readme(self) -> None:
        """Generate README.md based on template mode."""
        if self.template == "basic":
            content = self._generate_basic_readme()
        elif self.template == "advanced":
            content = self._generate_advanced_readme()
        elif self.template == "complex":
            content = self._generate_complex_readme()
        else:
            content = self._generate_basic_readme()
        
        safe_write(self.project_path / "README.md", content, self.force)
    
    def _generate_basic_readme(self) -> str:
        """Generate README for basic mode."""
        return f"""# {self.project_name}

A2ABase Agent SDK project - Basic mode (native tools only).

## Features

- **Native A2ABase Tools** - Uses built-in tools (web search, browser, etc.)
- **No MCP Server Required** - Simple setup, no ngrok needed
- **Quick Start** - Get up and running in minutes
- **Development Mode** - Auto-reload on file changes

## Quick Start

1. **Create virtual environment**:
   ```bash
   {'uv venv' if self.package_manager == 'uv' else 'python -m venv venv'}
   ```

2. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   {'source .venv/bin/activate' if self.package_manager == 'uv' else 'source venv/bin/activate'}
   
   # Windows
   {'source .venv\\\\Scripts\\\\activate' if self.package_manager == 'uv' else 'source venv\\\\Scripts\\\\activate'}
   ```

3. **Install dependencies**:
   ```bash
   {'uv pip install -e .' if self.package_manager == 'uv' else 'pip install -e .'}
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your BASEAI_API_KEY
   ```

5. **Run in development mode**:
   ```bash
   a2abase dev
   ```

## Usage

### Development Mode

```bash
a2abase dev
```

Runs your agent with auto-reload on file changes. No MCP server or ngrok needed!

### Run Once

```bash
a2abase run --input "Search the web for latest AI news"
```

### Run Tests

```bash
a2abase test
```

## Project Structure

```
{self.project_name}/
├── src/
│   └── {self.package_name}/
│       ├── agents/
│       │   └── basic_agent.py    # Basic agent using native tools
│       ├── registry/
│       │   └── card.py           # Agent card metadata
│       ├── main.py               # Main entrypoint
│       └── sdk_adapter.py        # SDK adapter (real/stub)
├── tests/                        # Test files
├── vendor/                       # Stub SDK (fallback)
├── .env.example                  # Environment template
├── a2abase.yaml                  # Project config
└── pyproject.toml                # Python project config
```

## Native A2ABase Tools

This project uses built-in A2ABase tools:
- `WEB_SEARCH_TOOL` - Search the web
- `BROWSER_TOOL` - Browse and interact with websites
- And more...

See the agent code in `src/{self.package_name}/agents/basic_agent.py` for examples.

## Environment Variables

- `BASEAI_API_KEY` - Your A2ABase API key (required)
- `BASEAI_API_URL` - A2ABase API URL (default: https://a2abase.ai/api)

## Next Steps

- Add more agents: `a2abase add agent <name>`
- Upgrade to advanced mode for custom tools: Create a new project with `--template advanced`
- Upgrade to complex mode for multi-agent systems: Create a new project with `--template complex`
"""
    
    def _generate_advanced_readme(self) -> str:
        """Generate README for advanced mode."""
        return f"""# {self.project_name}

A2ABase Agent SDK project - Advanced mode (custom tools with MCP server).

## Features

- **Weather Tool** - Real weather data using Open-Meteo API (free, no API key required)
- **MCP Server** - Serve custom tools to A2ABase agents
- **Weather Agent** - Example agent using custom weather tool
- **Development Mode** - Auto-reload with MCP server integration
- **Ngrok Integration** - Required for remote agents (enabled by default)

## Quick Start

1. **Create virtual environment**:
   ```bash
   {'uv venv' if self.package_manager == 'uv' else 'python -m venv venv'}
   ```

2. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   {'source .venv/bin/activate' if self.package_manager == 'uv' else 'source venv/bin/activate'}
   
   # Windows
   {'source .venv\\\\Scripts\\\\activate' if self.package_manager == 'uv' else 'source venv\\\\Scripts\\\\activate'}
   ```

3. **Install dependencies**:
   ```bash
   {'uv pip install -e .' if self.package_manager == 'uv' else 'pip install -e .'}
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your BASEAI_API_KEY
   ```

5. **Run in development mode** (starts MCP server with ngrok automatically):
   ```bash
   # Install ngrok support (required for remote agents)
   pip install pyngrok
   
   # Set ngrok auth token (get free token from https://dashboard.ngrok.com/get-started/your-authtoken)
   export NGROK_AUTH_TOKEN=your_token_here
   
   # Start dev server (ngrok enabled by default)
   a2abase dev
   ```
   
   **Important**: Ngrok is enabled by default because A2ABase agents run on remote servers
   and need public access to your local MCP server. Use `--no-ngrok` only for local testing.

## Usage

### Development Mode

The `a2abase dev` command automatically:
- Starts the MCP server on `http://localhost:8000/mcp`
- Creates ngrok tunnel (required for remote agents)
- Runs your agent with auto-reload on file changes
- Watches for changes in `src/` directory

```bash
a2abase dev
```

#### Ngrok Configuration (Required for Remote Agents)

**IMPORTANT**: Ngrok is enabled by default because A2ABase agents run on remote servers
and require public access to your local MCP server. Your custom tools won't work with
remote agents without ngrok!

**Setup:**
1. **Install pyngrok**:
   ```bash
   pip install pyngrok
   ```

2. **Get ngrok auth token** (free):
   - Sign up at [ngrok.com](https://ngrok.com)
   - Get your auth token from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)

3. **Set environment variable**:
   ```bash
   export NGROK_AUTH_TOKEN=your_token_here
   ```

4. **Run dev command** (ngrok enabled by default):
   ```bash
   a2abase dev
   ```

**Disable ngrok** (only for local testing without remote agents):
```bash
a2abase dev --no-ngrok
```

When ngrok is enabled, you'll see both local and public URLs:
- **Local**: `http://localhost:8000/mcp` (for local testing)
- **Public**: `https://xxxx-xx-xx-xx-xx.ngrok-free.app/mcp` (required for remote agents)

**Use the public URL** in your agent's MCPTools configuration for remote agent access.

### Run Once

Run the agent with a specific prompt:

```bash
a2abase run --input "What's the weather in San Francisco?"
```

### Run Tests

```bash
a2abase test
```

## Project Structure

```
{self.project_name}/
├── src/
│   └── {self.package_name}/
│       ├── agents/
│       │   └── weather_agent.py    # Weather agent example
│       ├── tools/
│       │   ├── weather.py          # Weather tool (Open-Meteo API)
│       │   ├── mcp_server.py       # MCP server for custom tools
│       │   └── README.md           # Tools documentation
│       ├── registry/
│       │   ├── tools.py            # Tool registry
│       │   └── card.py             # Agent card metadata
│       ├── main.py                 # Main entrypoint
│       └── sdk_adapter.py          # SDK adapter (real/stub)
├── tests/                          # Test files
├── vendor/                         # Stub SDK (fallback)
├── .env.example                    # Environment template
├── a2abase.yaml                    # Project config
└── pyproject.toml                  # Python project config
```

## Weather Tool

The project includes a real weather tool that uses the [Open-Meteo API](https://api.open-meteo.com/v1/forecast):

- **Free** - No API key required
- **Current weather** - Temperature, humidity, wind, conditions
- **Forecast** - Up to 16 days of weather forecast
- **Geocoding** - Automatic coordinate lookup for city names

### Usage Example

The weather tool is available via the MCP server and can be used in agents:

```python
from a2abase.tools import MCPTools

# Initialize MCP tools (server must be running)
custom_tools = MCPTools(
    endpoint="http://localhost:8000/mcp",
    name="custom_tools",
    allowed_tools=["get_weather_tool"]
)
await custom_tools.initialize()

# Create agent with weather tool
agent = await client.Agent.create(
    name="Weather Agent",
    system_prompt="You are a helpful weather assistant.",
    a2abase_tools=[custom_tools],
)
```

## Adding Custom Tools

See `src/{self.package_name}/tools/README.md` for detailed instructions on:
- Creating new tools
- Adding tools to the MCP server
- Using tools in agents

## Environment Variables

- `BASEAI_API_KEY` - Your A2ABase API key (required)
- `BASEAI_API_URL` - A2ABase API URL (default: https://a2abase.ai/api)
- `NGROK_AUTH_TOKEN` - Ngrok auth token (required for remote agents)

The weather tool uses Open-Meteo API which doesn't require any API keys.

## Troubleshooting

### MCP Server Not Starting

- Make sure `fastmcp` and `uvicorn` are installed: `pip install fastmcp uvicorn`
- Check if port 8000 is already in use
- Review server logs for errors

### Agent Can't Connect to MCP Server

- Ensure the MCP server is running: `python -m {self.package_name}.tools.mcp_server`
- Verify ngrok tunnel is active (check CLI output)
- Use the public ngrok URL in your agent configuration

### Weather Tool Errors

- Verify city name or coordinates are valid
- Check network connectivity
- Open-Meteo API is free and doesn't require authentication

### Ngrok Issues

- **"pyngrok not installed"**: Install with `pip install pyngrok`
- **"No auth token"**: Get free token from [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
- **Tunnel fails**: Check internet connection and ngrok service status
- **URL not accessible**: Verify ngrok tunnel is active (check CLI output)
"""
    
    def _generate_complex_readme(self) -> str:
        """Generate README for complex mode."""
        return f"""# {self.project_name}

A2ABase Agent SDK project - Complex mode (multi-agent system with orchestrator).

## Features

- **Multi-Agent System** - Coordinate multiple specialized agents
- **Agent Orchestrator** - Intelligent routing and coordination
- **Weather Agent** - Example specialized agent
- **MCP Server** - Serve custom tools to all agents
- **Development Mode** - Auto-reload with MCP server integration
- **Ngrok Integration** - Required for remote agents (enabled by default)

## Quick Start

1. **Create virtual environment**:
   ```bash
   {'uv venv' if self.package_manager == 'uv' else 'python -m venv venv'}
   ```

2. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   {'source .venv/bin/activate' if self.package_manager == 'uv' else 'source venv/bin/activate'}
   
   # Windows
   {'source .venv\\\\Scripts\\\\activate' if self.package_manager == 'uv' else 'source venv\\\\Scripts\\\\activate'}
   ```

3. **Install dependencies**:
   ```bash
   {'uv pip install -e .' if self.package_manager == 'uv' else 'pip install -e .'}
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your BASEAI_API_KEY
   ```

5. **Run in development mode** (starts MCP server with ngrok automatically):
   ```bash
   # Install ngrok support (required for remote agents)
   pip install pyngrok
   
   # Set ngrok auth token (get free token from https://dashboard.ngrok.com/get-started/your-authtoken)
   export NGROK_AUTH_TOKEN=your_token_here
   
   # Start dev server (ngrok enabled by default)
   a2abase dev
   ```

## Usage

### Development Mode

The `a2abase dev` command automatically:
- Starts the MCP server on `http://localhost:8000/mcp`
- Creates ngrok tunnel (required for remote agents)
- Runs the orchestrator with auto-reload
- Watches for changes in `src/` directory

```bash
a2abase dev
```

### Run Once

```bash
a2abase run --input "What's the weather in San Francisco?"
```

The orchestrator will route your request to the appropriate agent.

## Project Structure

```
{self.project_name}/
├── src/
│   └── {self.package_name}/
│       ├── agents/
│       │   └── weather_agent.py    # Weather agent example
│       ├── tools/
│       │   ├── weather.py          # Weather tool (Open-Meteo API)
│       │   ├── mcp_server.py       # MCP server for custom tools
│       │   └── README.md           # Tools documentation
│       ├── orchestrator/
│       │   └── orchestrator.py     # Agent orchestrator
│       ├── registry/
│       │   ├── tools.py            # Tool registry
│       │   └── card.py             # Agent card metadata
│       ├── main.py                 # Main entrypoint (uses orchestrator)
│       └── sdk_adapter.py          # SDK adapter (real/stub)
├── tests/                          # Test files
├── vendor/                         # Stub SDK (fallback)
├── .env.example                    # Environment template
├── a2abase.yaml                    # Project config
└── pyproject.toml                  # Python project config
```

## Agent Orchestrator

The orchestrator coordinates multiple agents and routes requests intelligently:

```python
from {self.package_name}.orchestrator.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(client)
await orchestrator.initialize_agents()

# Route request to appropriate agent
result = await orchestrator.route_request("What's the weather?", thread)
```

### Adding More Agents

1. Create a new agent: `a2abase add agent <name>`
2. Add agent initialization in `orchestrator.py`:
   ```python
   new_agent = await create_new_agent(self.client)
   self.agents["new_agent"] = new_agent
   ```
3. Update routing logic in `route_request()` method

## Environment Variables

- `BASEAI_API_KEY` - Your A2ABase API key (required)
- `BASEAI_API_URL` - A2ABase API URL (default: https://a2abase.ai/api)
- `NGROK_AUTH_TOKEN` - Ngrok auth token (required for remote agents)

## Learn More

- [A2ABase SDK Documentation](https://github.com/A2ABaseAI/sdks)
- [Open-Meteo API](https://api.open-meteo.com/v1/forecast)
- [MCP Protocol](https://modelcontextprotocol.io/)
"""

    def _generate_gitignore(self) -> None:
        """Generate .gitignore."""
        content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db
"""
        safe_write(self.project_path / ".gitignore", content, self.force)

    def _generate_env_example(self) -> None:
        """Generate .env.example."""
        content = """# A2ABase API Configuration
BASEAI_API_KEY=your_api_key_here
BASEAI_API_URL=https://a2abase.ai/api

# Weather Tool uses Open-Meteo API (free, no API key required)
# See: https://api.open-meteo.com/v1/forecast

# Ngrok Configuration (optional - for exposing MCP server publicly)
# Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN=your_ngrok_auth_token_here
"""
        safe_write(self.project_path / ".env.example", content, self.force)

    def _generate_config(self) -> None:
        """Generate a2abase.yaml."""
        content = f"""package_name: {self.package_name}
template: {self.template}
package_manager: {self.package_manager}
"""
        safe_write(self.project_path / "a2abase.yaml", content, self.force)

    def _generate_basic_mode(self) -> None:
        """Generate basic mode - native tools only, no MCP server."""
        # __init__.py files (no tools directory)
        for init_path in [
            self.project_path / "src" / self.package_name / "__init__.py",
            self.project_path / "src" / self.package_name / "agents" / "__init__.py",
            self.project_path / "src" / self.package_name / "registry" / "__init__.py",
        ]:
            safe_write(init_path, "", self.force)
        
        # Basic agent using only native A2ABase tools
        self._generate_basic_agent()
        self._generate_basic_main()
        self._generate_basic_card()
    
    def _generate_advanced_mode(self) -> None:
        """Generate advanced mode - custom tools with MCP server (current implementation)."""
        # This is the existing _generate_source_files implementation
        self._generate_advanced_source_files()
    
    def _generate_complex_mode(self) -> None:
        """Generate complex mode - multi-agent system."""
        # __init__.py files including orchestrator
        for init_path in [
            self.project_path / "src" / self.package_name / "__init__.py",
            self.project_path / "src" / self.package_name / "agents" / "__init__.py",
            self.project_path / "src" / self.package_name / "tools" / "__init__.py",
            self.project_path / "src" / self.package_name / "registry" / "__init__.py",
            self.project_path / "src" / self.package_name / "orchestrator" / "__init__.py",
        ]:
            safe_write(init_path, "", self.force)
        
        # Complex multi-agent setup
        self._generate_complex_source_files()
    
    def _generate_source_files(self) -> None:
        """Generate source files - legacy method, redirects to mode-specific."""
        # This method is kept for backward compatibility but redirects to mode-specific methods
        if self.template == "basic":
            self._generate_basic_mode()
        elif self.template == "advanced":
            self._generate_advanced_mode()
        elif self.template == "complex":
            self._generate_complex_mode()
        else:
            self._generate_basic_mode()
    
    def _generate_advanced_source_files(self) -> None:
        """Generate advanced mode source files - custom tools with MCP server."""
        # __init__.py files
        for init_path in [
            self.project_path / "src" / self.package_name / "__init__.py",
            self.project_path / "src" / self.package_name / "agents" / "__init__.py",
            self.project_path / "src" / self.package_name / "tools" / "__init__.py",
            self.project_path / "src" / self.package_name / "registry" / "__init__.py",
        ]:
            safe_write(init_path, "", self.force)

        # main.py
        main_content = f'''"""Main entrypoint for the {self.project_name} project."""
import asyncio
import os
import sys
from pathlib import Path

# Add vendor stub to path if SDK not available
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools
except ImportError:
    # Fallback to stub SDK
    vendor_path = Path(__file__).parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools  # type: ignore

from {self.package_name}.agents.weather_agent import create_weather_agent
from {self.package_name}.registry.card import generate_card


async def main(input_text: str | None = None) -> dict:
    """Run the agent.
    
    Note: Make sure the MCP server is running before running this:
        python -m {self.package_name}.tools.mcp_server
    """
    api_key = os.getenv("BASEAI_API_KEY")
    if not api_key:
        raise ValueError("Please set BASEAI_API_KEY environment variable")

    api_url = os.getenv("BASEAI_API_URL", "https://a2abase.ai/api")
    client = A2ABaseClient(api_key=api_key, api_url=api_url)

    # Create thread
    thread = await client.Thread.create()

    # Create agent (requires MCP server to be running for custom tools)
    # Add a small delay to ensure MCP server is fully ready
    import asyncio
    await asyncio.sleep(2)  # Give MCP server extra time to be ready
    agent = await create_weather_agent(client)

    # Run agent
    prompt = input_text or "What's the weather in San Francisco?"
    run = await agent.run(prompt, thread)

    # Stream output
    output = []
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="", flush=True)
        output.append(chunk)

    return {{"output": "".join(output)}}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", help="Input text for the agent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = asyncio.run(main(args.input))
    if args.json:
        import json

        print(json.dumps(result, indent=2))
'''
        safe_write(
            self.project_path / "src" / self.package_name / "main.py", main_content, self.force
        )

        # Weather agent
        weather_agent_content = f'''"""Weather agent example with custom tools via MCP server."""
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools, MCPTools
except ImportError:
    import sys
    from pathlib import Path
    vendor_path = Path(__file__).parent.parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools, MCPTools  # type: ignore


async def create_weather_agent(client: A2ABaseClient):
    """
    Create a weather agent with custom weather tool via MCP server.
    
    Make sure the MCP server is running before creating this agent:
        python -m {self.package_name}.tools.mcp_server
    
    Or use uvicorn:
        uvicorn {self.package_name}.tools.mcp_server:app --port 8000
    """
    # Option 1: Use built-in A2ABase tools (simplest, no MCP server needed)
    # agent = await client.Agent.create(
    #     name="Weather Agent",
    #     system_prompt=(
    #         "You are a helpful weather assistant. "
    #         "You can search the web for current weather information and provide "
    #         "detailed forecasts for any location."
    #     ),
    #     a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL],
    # )
    
    # Option 2: Use custom weather tool via MCP server (recommended)
    # Start the MCP server first: python -m {self.package_name}.tools.mcp_server
    import os
    
    # Get MCP endpoint from environment
    # Prefer ngrok URL if available (set by dev command), otherwise use localhost
    mcp_endpoint = os.getenv("MCP_ENDPOINT", "http://localhost:8000/mcp")
    if mcp_endpoint.startswith("https://"):
        print(f"[cyan]Using ngrok endpoint: {{mcp_endpoint}}[/cyan]")
    else:
        print(f"[dim]Using local endpoint: {{mcp_endpoint}}[/dim]")
    
    # Retry logic for MCP connection
    max_retries = 10
    retry_delay = 3  # Increased delay between retries
    
    # Define the tools to use
    allowed_tools = ["get_weather_tool"]  # Tool names from mcp_server.py
    
    # Generate dynamic name based on tools
    if len(allowed_tools) == 1:
        # For single tool, use a simpler name
        tools_name = allowed_tools[0].replace("_tool", "") + "_tools"
    else:
        # For multiple tools, use a combined name
        tools_name = "custom_tools"
    
    for attempt in range(max_retries):
        try:
            custom_tools = MCPTools(
                endpoint=mcp_endpoint,  # MCP server endpoint
                name=tools_name,
                allowed_tools=allowed_tools
            )
            await custom_tools.initialize()
            
            # Debug: Print discovered tools
            print(f"\\n[cyan]MCP Tools Discovery:[/cyan]")
            print(f"  Endpoint: {{mcp_endpoint}}")
            print(f"  Requested tools: {{allowed_tools}}")
            print(f"  Discovered tools: {{custom_tools.enabled_tools}}")
            
            if not custom_tools.enabled_tools:
                print(f"\\n[yellow]⚠ Warning:[/yellow] No tools discovered from MCP server!")
                print(f"[dim]Make sure the MCP server is running at {{mcp_endpoint}}[/dim]")
                print(f"[dim]Expected tool name: 'get_weather_tool'[/dim]")
            elif "get_weather_tool" not in custom_tools.enabled_tools:
                print(f"\\n[yellow]⚠ Warning:[/yellow] Requested tool 'get_weather_tool' not found!")
                print(f"[dim]Available tools: {{custom_tools.enabled_tools}}[/dim]")
                print(f"[dim]Check that the tool name matches exactly (case-sensitive)[/dim]")
            else:
                print(f"[green]✓[/green] Successfully discovered 'get_weather_tool'")
            
            # Ensure tools were discovered before proceeding
            if not custom_tools.enabled_tools:
                raise ValueError(
                    f"No tools discovered from MCP server at {{mcp_endpoint}}. "
                    f"Make sure the MCP server is running and has tools registered."
                )
            
            break  # Success, exit retry loop
        except Exception as e:
            if attempt < max_retries - 1:
                import asyncio
                print(f"MCP connection attempt {{attempt + 1}} failed: {{e}}")
                print(f"Retrying in {{retry_delay}} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                # Last attempt failed, re-raise the exception
                raise
    
    # Verify custom_tools is initialized and has tools before creating agent
    if not custom_tools._initialized:
        raise ValueError("MCPTools must be initialized before creating agent")
    if not custom_tools.enabled_tools:
        raise ValueError(
            f"No tools available in MCPTools. Discovered tools: {{custom_tools.enabled_tools}}. "
            f"Make sure the MCP server is running and tools are properly registered."
        )
    
    agent = await client.Agent.create(
        name="Weather Agent",
        system_prompt=(
            "You are a helpful weather assistant. "
            "You can get current weather information for any city using the get_weather_tool. "
            "Provide detailed weather reports including temperature, conditions, humidity, and wind."
        ),
        a2abase_tools=[custom_tools],
    )
    
    return agent
'''
        safe_write(
            self.project_path / "src" / self.package_name / "agents" / "weather_agent.py",
            weather_agent_content,
            self.force,
        )

        # Weather tool - real example
        weather_content = f'''"""Weather tool - real example using Open-Meteo API (free, no API key required)."""
from typing import Dict, Any, Optional
import httpx


# OpenAI function calling schema
WEATHER_SCHEMA = {{
    "type": "function",
    "function": {{
        "name": "get_weather",
        "description": "Get current weather information and forecast for a location",
        "parameters": {{
            "type": "object",
            "properties": {{
                "latitude": {{
                    "type": "number",
                    "description": "Latitude of the location (e.g., 37.7749 for San Francisco)"
                }},
                "longitude": {{
                    "type": "number",
                    "description": "Longitude of the location (e.g., -122.4194 for San Francisco)"
                }},
                "city": {{
                    "type": "string",
                    "description": "City name (e.g., 'San Francisco', 'New York'). Used to look up coordinates if lat/lon not provided."
                }},
                "temperature_unit": {{
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit (default: celsius)",
                    "default": "celsius"
                }},
                "forecast_days": {{
                    "type": "integer",
                    "description": "Number of forecast days (1-16, default: 1)",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 16
                }}
            }},
            "required": []
        }}
    }}
}}


async def _get_coordinates(city: str) -> Optional[tuple[float, float]]:
    """Get latitude and longitude for a city name using Open-Meteo geocoding."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={{"name": city, "count": 1, "language": "en", "format": "json"}}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                return (result["latitude"], result["longitude"])
    except Exception:
        pass
    return None


async def get_weather(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    city: Optional[str] = None,
    temperature_unit: str = "celsius",
    forecast_days: int = 1,
) -> Dict[str, Any]:
    """
    Get current weather information and forecast for a location.
    
    Uses Open-Meteo API (https://api.open-meteo.com/v1/forecast) - free, no API key required!
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        city: City name (will look up coordinates if lat/lon not provided)
        temperature_unit: Temperature unit (celsius or fahrenheit)
        forecast_days: Number of forecast days (1-16)
    
    Returns:
        Dictionary with weather information
    """
    # Get coordinates if not provided
    if latitude is None or longitude is None:
        if city:
            coords = await _get_coordinates(city)
            if coords:
                latitude, longitude = coords
            else:
                return {{
                    "error": "Could not find coordinates for city",
                    "message": f"Could not geocode city: {{city}}. Please provide latitude and longitude.",
                }}
        else:
            return {{
                "error": "Missing location",
                "message": "Please provide either (latitude, longitude) or city name.",
            }}
    
    try:
        # Open-Meteo API endpoint
        base_url = "https://api.open-meteo.com/v1/forecast"
        params = {{
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m",
            "hourly": "temperature_2m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "temperature_unit": temperature_unit,
            "forecast_days": min(max(forecast_days, 1), 16),
            "timezone": "auto",
        }}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {{}})
            daily = data.get("daily", {{}})
            
            # Weather code descriptions (simplified)
            weather_codes = {{
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Foggy", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                56: "Light freezing drizzle", 57: "Dense freezing drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                66: "Light freezing rain", 67: "Heavy freezing rain",
                71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
                82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
            }}
            
            weather_code = current.get("weather_code", 0)
            condition = weather_codes.get(weather_code, "Unknown")
            
            result = {{
                "location": {{
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": city or "Unknown",
                }},
                "current": {{
                    "temperature": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "condition": condition,
                    "weather_code": weather_code,
                    "wind_speed": current.get("wind_speed_10m"),
                    "wind_direction": current.get("wind_direction_10m"),
                }},
                "temperature_unit": temperature_unit,
                "forecast_days": forecast_days,
            }}
            
            # Add daily forecast if available
            if daily.get("time"):
                daily_forecast = []
                for i in range(min(len(daily["time"]), forecast_days)):
                    daily_forecast.append({{
                        "date": daily["time"][i],
                        "max_temperature": daily.get("temperature_2m_max", [None])[i] if daily.get("temperature_2m_max") else None,
                        "min_temperature": daily.get("temperature_2m_min", [None])[i] if daily.get("temperature_2m_min") else None,
                        "weather_code": daily.get("weather_code", [None])[i] if daily.get("weather_code") else None,
                        "condition": weather_codes.get(daily.get("weather_code", [0])[i] if daily.get("weather_code") else 0, "Unknown"),
                    }})
                result["daily_forecast"] = daily_forecast
            
            return result
            
    except httpx.HTTPStatusError as e:
        return {{
            "error": f"HTTP error: {{e.response.status_code}}",
            "message": "Could not fetch weather data from Open-Meteo API.",
        }}
    except Exception as e:
        return {{
            "error": str(e),
            "message": "An error occurred while fetching weather data.",
        }}


# Export schema for registration
__all__ = ["WEATHER_SCHEMA", "get_weather"]
'''
        safe_write(
            self.project_path / "src" / self.package_name / "tools" / "weather.py",
            weather_content,
            self.force,
        )

        # MCP Server
        mcp_server_content = f'''"""MCP Server for serving custom tools to A2ABase agents.

This server exposes your custom tools via the MCP (Model Context Protocol) so they can
be used by A2ABase agents. Start this server before creating agents that use custom tools.

Usage:
    # Install dependencies
    pip install fastmcp uvicorn
    
    # Start the server
    python -m {self.package_name}.tools.mcp_server
    
    # Or use uvicorn directly
    uvicorn {self.package_name}.tools.mcp_server:app --port 8000

The server will be available at http://localhost:8000/mcp
"""
from fastmcp import FastMCP
from .weather import get_weather

# Create MCP server instance
mcp = FastMCP(name="{self.project_name}_tools")

# Create ASGI app for uvicorn
app = mcp.http_app()


@mcp.tool()
async def get_weather_tool(
    city: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    temperature_unit: str = "celsius",
    forecast_days: int = 1,
) -> str:
    """
    Get current weather information and forecast for a location.
    
    Uses Open-Meteo API (free, no API key required).
    
    Args:
        city: City name (e.g., 'San Francisco', 'New York'). Used if lat/lon not provided.
        latitude: Latitude of the location (optional if city provided)
        longitude: Longitude of the location (optional if city provided)
        temperature_unit: Temperature unit (celsius or fahrenheit). Default: celsius
        forecast_days: Number of forecast days (1-16). Default: 1
    
    Returns:
        JSON string with weather information
    """
    import json
    result = await get_weather(
        city=city,
        latitude=latitude,
        longitude=longitude,
        temperature_unit=temperature_unit,
        forecast_days=forecast_days,
    )
    return json.dumps(result, indent=2)


# Add more tools here by decorating functions with @mcp.tool()
# Example:
# @mcp.tool()
# async def my_custom_tool(param: str) -> str:
#     \"\"\"Tool description.\"\"\"
#     return "result"


if __name__ == "__main__":
    import uvicorn
    
    print("Starting MCP server at http://localhost:8000/mcp")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        safe_write(
            self.project_path / "src" / self.package_name / "tools" / "mcp_server.py",
            mcp_server_content,
            self.force,
        )

        # Tools README
        tools_readme_content = f'''# Tools Directory

This directory contains custom tools for your A2ABase agents.

## Structure

- `weather.py` - Real weather tool example using OpenWeatherMap API
- `mcp_server.py` - MCP server for serving tools to agents
- `__init__.py` - Package initialization

## Using Custom Tools

### Option 1: Using Built-in A2ABase Tools (Simplest)

The easiest way is to use A2ABase's built-in tools:

```python
from a2abase.tools import A2ABaseTools

agent = await client.Agent.create(
    name="My Agent",
    system_prompt="...",
    a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL, A2ABaseTools.BROWSER_TOOL],
)
```

### Option 2: Using Custom Tools via MCP Server (Recommended for Custom Tools)

1. **Start the MCP server**:
   ```bash
   python -m {self.package_name}.tools.mcp_server
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn {self.package_name}.tools.mcp_server:app --port 8000
   ```

2. **Use the tools in your agent**:
   ```python
   from a2abase.tools import MCPTools
   
   # Initialize MCP tools
   custom_tools = MCPTools(
       endpoint="http://localhost:8000/mcp",
       name="custom_tools",
       allowed_tools=["get_weather_tool"]  # List of tool names from your MCP server
   )
   await custom_tools.initialize()
   
   # Create agent with custom tools
   agent = await client.Agent.create(
       name="Weather Agent",
       system_prompt="You are a weather assistant.",
       a2abase_tools=[custom_tools],
   )
   ```

## Adding New Tools

### Step 1: Create the Tool Function

Create a new file in this directory (e.g., `my_tool.py`):

```python
"""My custom tool."""
from typing import Dict, Any

async def my_tool(param: str) -> Dict[str, Any]:
    \"\"\"Tool description.\"\"\"
    return {{"result": f"Processed: {{param}}"}}
```

### Step 2: Add to MCP Server

Edit `mcp_server.py` and add your tool:

```python
from .my_tool import my_tool

@mcp.tool()
async def my_tool_mcp(param: str) -> str:
    \"\"\"Tool description.\"\"\"
    import json
    result = await my_tool(param)
    return json.dumps(result, indent=2)
```

### Step 3: Restart MCP Server

Restart the server to load the new tool:

```bash
python -m {self.package_name}.tools.mcp_server
```

### Step 4: Use in Agent

Update your agent creation to include the new tool:

```python
custom_tools = MCPTools(
    endpoint="http://localhost:8000/mcp",
    name="custom_tools",
    allowed_tools=["get_weather_tool", "my_tool_mcp"]  # Add your tool name
)
```

## Weather Tool Example

The `weather.py` file contains a real weather tool that uses the [Open-Meteo API](https://api.open-meteo.com/v1/forecast).

### Features

- **Free and open-source** - No API key required!
- **Current weather** - Temperature, humidity, wind speed, conditions
- **Forecast** - Up to 16 days of weather forecast
- **Geocoding** - Automatically looks up coordinates for city names
- **Multiple units** - Celsius or Fahrenheit

### Usage

The tool is automatically available via the MCP server. You can use it with:
- City name: `get_weather_tool(city="San Francisco")`
- Coordinates: `get_weather_tool(latitude=37.7749, longitude=-122.4194)`
- With forecast: `get_weather_tool(city="New York", forecast_days=7)`

## MCP Server Details

The MCP server uses [FastMCP](https://github.com/jlowin/fastmcp) to expose tools via HTTP.

- **Endpoint**: `http://localhost:8000/mcp` (default)
- **Protocol**: MCP (Model Context Protocol)
- **Port**: 8000 (configurable)

To change the port, edit `mcp_server.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

## Ngrok Configuration (Required for Remote Agents)

**IMPORTANT**: Ngrok is **required** because A2ABase agents run on remote servers and need
public access to your local MCP server. Without ngrok, remote agents cannot access your
custom tools!

### Why Ngrok is Required

- A2ABase agents execute on remote servers (not on your local machine)
- Your MCP server runs locally
- Remote agents need a public URL to reach your local MCP server
- Ngrok creates a secure tunnel from the internet to your localhost

### Using CLI (Recommended - Enabled by Default)

```bash
# 1. Install ngrok support
pip install pyngrok

# 2. Get free ngrok auth token from https://dashboard.ngrok.com/get-started/your-authtoken
export NGROK_AUTH_TOKEN=your_token_here

# 3. Run dev mode (ngrok enabled by default)
a2abase dev
```

The CLI will automatically:
- Start the MCP server
- Create an ngrok tunnel (enabled by default)
- Display both local and public URLs in a formatted table

**Disable ngrok** (only for local testing without remote agents):
```bash
a2abase dev --no-ngrok
```

### Manual Setup

If you need to run MCP server and ngrok separately:

1. **Install pyngrok**:
   ```bash
   pip install pyngrok
   ```

2. **Get ngrok auth token**:
   - Sign up at [ngrok.com](https://ngrok.com)
   - Get token from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
   - Set environment variable: `export NGROK_AUTH_TOKEN=your_token`

3. **Start MCP server**:
   ```bash
   python -m {self.package_name}.tools.mcp_server
   ```

4. **Start ngrok tunnel** (in another terminal):
   ```bash
   ngrok http 8000
   ```

5. **Use public URL**:
   - Copy the ngrok URL (e.g., `https://xxxx-xx-xx-xx-xx.ngrok-free.app`)
   - Use it in your agent: `https://xxxx-xx-xx-xx-xx.ngrok-free.app/mcp`

### Security Notes

**Warning**: When using ngrok, your MCP server is publicly accessible!

- Use ngrok only for development/testing
- Consider adding authentication for production use
- Free ngrok tunnels have limitations (session timeouts, etc.)
- For production, deploy your MCP server to proper hosting with HTTPS and authentication

## Troubleshooting

### Server won't start

- Make sure `fastmcp` and `uvicorn` are installed:
  ```bash
  pip install fastmcp uvicorn
  ```

### Tools not available

- Check that the MCP server is running
- Verify the endpoint URL matches your server configuration
- Check that tool names match exactly (case-sensitive)
- Review server logs for errors

### API errors

- For weather tool: Open-Meteo API is free and doesn't require an API key
- Check network connectivity
- Verify city name or coordinates are valid
'''
        safe_write(
            self.project_path / "src" / self.package_name / "tools" / "README.md",
            tools_readme_content,
            self.force,
        )

        # Tool registry helper
        registry_helper_content = f'''"""Tool registry helper for managing custom tools with OpenAI schema."""
from typing import Dict, Any, List
from {self.package_name}.tools.weather import WEATHER_SCHEMA


# Registry of all available tools with their OpenAI schemas
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {{
    "get_weather": WEATHER_SCHEMA,
}}


def get_tool_schema(tool_name: str) -> Dict[str, Any] | None:
    """
    Get OpenAI schema for a tool by name.

    Args:
        tool_name: Name of the tool

    Returns:
        OpenAI function calling schema or None if not found
    """
    return TOOL_REGISTRY.get(tool_name)


def list_tool_schemas() -> List[Dict[str, Any]]:
    """
    List all available tool schemas.

    Returns:
        List of OpenAI function calling schemas
    """
    return list(TOOL_REGISTRY.values())


def register_tool(tool_name: str, schema: Dict[str, Any]) -> None:
    """
    Register a new tool schema.

    Args:
        tool_name: Name of the tool
        schema: OpenAI function calling schema
    """
    TOOL_REGISTRY[tool_name] = schema


# Export for use in agents
__all__ = ["TOOL_REGISTRY", "get_tool_schema", "list_tool_schemas", "register_tool"]
'''
        safe_write(
            self.project_path / "src" / self.package_name / "registry" / "tools.py",
            registry_helper_content,
            self.force,
        )

        # Registry card
        card_content = f'''"""Generate agent card metadata."""
from typing import Dict, Any
from {self.package_name}.agents.weather_agent import create_weather_agent


def generate_card() -> Dict[str, Any]:
    """
    Generate an agent card with metadata.

    Returns:
        Dictionary with agent card information
    """
    return {{
        "id": "weather_agent",
        "name": "Weather Agent",
        "description": "A helpful weather assistant that can search for current weather information",
        "capabilities": [
            "get_weather",
            "weather_forecast",
        ],
        "input_schema": {{
            "type": "object",
            "properties": {{
                "location": {{
                    "type": "string",
                    "description": "Location to get weather for",
                }},
            }},
        }},
        "tools": ["get_weather_tool"],
    }}
'''
        safe_write(
            self.project_path / "src" / self.package_name / "registry" / "card.py",
            card_content,
            self.force,
        )

        # SDK adapter
        adapter_content = f'''"""SDK adapter - wraps real SDK or uses stub."""
import sys
from pathlib import Path

# Try to import real SDK first
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools, MCPTools
    SDK_AVAILABLE = True
except ImportError:
    # Fallback to stub
    vendor_path = Path(__file__).parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    try:
        from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools, MCPTools
        SDK_AVAILABLE = False
    except ImportError:
        raise ImportError(
            "Neither a2abase SDK nor stub found. "
            "Install with: pip install a2abase"
        )

__all__ = ["A2ABaseClient", "A2ABaseTools", "MCPTools", "SDK_AVAILABLE"]
'''
        safe_write(
            self.project_path / "src" / self.package_name / "sdk_adapter.py",
            adapter_content,
            self.force,
        )

    def _generate_basic_mode(self) -> None:
        """Generate basic mode - native tools only, no MCP server."""
        # __init__.py files (no tools directory)
        for init_path in [
            self.project_path / "src" / self.package_name / "__init__.py",
            self.project_path / "src" / self.package_name / "agents" / "__init__.py",
            self.project_path / "src" / self.package_name / "registry" / "__init__.py",
        ]:
            safe_write(init_path, "", self.force)
        
        # Basic agent using only native A2ABase tools
        self._generate_basic_agent()
        self._generate_basic_main()
        self._generate_basic_card()
        self._generate_basic_sdk_adapter()
    
    def _generate_advanced_mode(self) -> None:
        """Generate advanced mode - custom tools with MCP server."""
        self._generate_advanced_source_files()
    
    def _generate_complex_mode(self) -> None:
        """Generate complex mode - multi-agent system."""
        # Create orchestrator directory
        (self.project_path / "src" / self.package_name / "orchestrator").mkdir(parents=True, exist_ok=True)
        
        # __init__.py files including orchestrator
        for init_path in [
            self.project_path / "src" / self.package_name / "__init__.py",
            self.project_path / "src" / self.package_name / "agents" / "__init__.py",
            self.project_path / "src" / self.package_name / "tools" / "__init__.py",
            self.project_path / "src" / self.package_name / "registry" / "__init__.py",
            self.project_path / "src" / self.package_name / "orchestrator" / "__init__.py",
        ]:
            safe_write(init_path, "", self.force)
        
        # Complex multi-agent setup
        self._generate_complex_source_files()
    
    def _generate_basic_agent(self) -> None:
        """Generate basic agent using only native A2ABase tools."""
        agent_content = f'''"""Basic agent example using native A2ABase tools only."""
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools
except ImportError:
    import sys
    from pathlib import Path
    vendor_path = Path(__file__).parent.parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools  # type: ignore


async def create_basic_agent(client: A2ABaseClient):
    """
    Create a basic agent using only native A2ABase tools.
    
    This agent uses built-in A2ABase tools - no MCP server required!
    Perfect for getting started quickly.
    """
    agent = await client.Agent.create(
        name="Basic Agent",
        system_prompt=(
            "You are a helpful assistant. "
            "You can search the web, browse websites, and help users with various tasks "
            "using the built-in A2ABase tools."
        ),
        a2abase_tools=[
            A2ABaseTools.WEB_SEARCH_TOOL,
            A2ABaseTools.BROWSER_TOOL,
        ],
    )
    
    return agent
'''
        safe_write(
            self.project_path / "src" / self.package_name / "agents" / "basic_agent.py",
            agent_content,
            self.force,
        )
    
    def _generate_basic_main(self) -> None:
        """Generate basic main.py."""
        main_content = f'''"""Main entrypoint for the {self.project_name} project."""
import asyncio
import os
import sys
from pathlib import Path

# Add vendor stub to path if SDK not available
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools
except ImportError:
    # Fallback to stub SDK
    vendor_path = Path(__file__).parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools  # type: ignore

from {self.package_name}.agents.basic_agent import create_basic_agent


async def main(input_text: str | None = None) -> dict:
    """Run the agent."""
    api_key = os.getenv("BASEAI_API_KEY")
    if not api_key:
        raise ValueError("Please set BASEAI_API_KEY environment variable")

    api_url = os.getenv("BASEAI_API_URL", "https://a2abase.ai/api")
    client = A2ABaseClient(api_key=api_key, api_url=api_url)

    # Create thread
    thread = await client.Thread.create()

    # Create agent (uses native tools only - no MCP server needed!)
    agent = await create_basic_agent(client)

    # Run agent
    prompt = input_text or "Search the web for the latest news about AI"
    run = await agent.run(prompt, thread)

    # Stream output
    output = []
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="", flush=True)
        output.append(chunk)

    return {{"output": "".join(output)}}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", help="Input text for the agent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = asyncio.run(main(args.input))
    if args.json:
        import json

        print(json.dumps(result, indent=2))
'''
        safe_write(
            self.project_path / "src" / self.package_name / "main.py", main_content, self.force
        )
    
    def _generate_basic_card(self) -> None:
        """Generate basic agent card."""
        card_content = f'''"""Generate agent card metadata."""
from typing import Dict, Any


def generate_card() -> Dict[str, Any]:
    """
    Generate an agent card with metadata.

    Returns:
        Dictionary with agent card information
    """
    return {{
        "id": "basic_agent",
        "name": "Basic Agent",
        "description": "A helpful assistant using native A2ABase tools",
        "capabilities": [
            "web_search",
            "browser_navigation",
        ],
        "input_schema": {{
            "type": "object",
            "properties": {{
                "query": {{
                    "type": "string",
                    "description": "User query or request",
                }},
            }},
        }},
        "tools": ["web_search_tool", "browser_tool"],
    }}
'''
        safe_write(
            self.project_path / "src" / self.package_name / "registry" / "card.py",
            card_content,
            self.force,
        )
    
    def _generate_basic_sdk_adapter(self) -> None:
        """Generate basic SDK adapter."""
        adapter_content = f'''"""SDK adapter - wraps real SDK or uses stub."""
import sys
from pathlib import Path

# Try to import real SDK first
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools
    SDK_AVAILABLE = True
except ImportError:
    # Fallback to stub
    vendor_path = Path(__file__).parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    try:
        from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools
        SDK_AVAILABLE = False
    except ImportError:
        raise ImportError(
            "Neither a2abase SDK nor stub found. "
            "Install with: pip install a2abase"
        )

__all__ = ["A2ABaseClient", "A2ABaseTools", "SDK_AVAILABLE"]
'''
        safe_write(
            self.project_path / "src" / self.package_name / "sdk_adapter.py",
            adapter_content,
            self.force,
        )
    
    def _generate_complex_source_files(self) -> None:
        """Generate complex mode - multi-agent system with orchestrator."""
        # Generate advanced mode files first (includes tools and MCP server)
        self._generate_advanced_source_files()
        
        # Add orchestrator
        orchestrator_content = f'''"""Orchestrator for coordinating multiple agents."""
try:
    from a2abase import A2ABaseClient
    from a2abase.tools import A2ABaseTools, MCPTools
except ImportError:
    import sys
    from pathlib import Path
    vendor_path = Path(__file__).parent.parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient, A2ABaseTools, MCPTools  # type: ignore

from {self.package_name}.agents.weather_agent import create_weather_agent


class AgentOrchestrator:
    """Orchestrator for managing multiple agents."""
    
    def __init__(self, client: A2ABaseClient):
        self.client = client
        self.agents = {{}}
    
    async def initialize_agents(self):
        """Initialize all agents in the system."""
        # Create weather agent
        weather_agent = await create_weather_agent(self.client)
        self.agents["weather"] = weather_agent
        
        # Add more agents here as needed
        # research_agent = await create_research_agent(self.client)
        # self.agents["research"] = research_agent
    
    async def route_request(self, user_input: str, thread) -> str:
        """
        Route user request to appropriate agent(s).
        
        This is a simple router - enhance with LLM-based routing for production.
        """
        user_lower = user_input.lower()
        
        # Simple keyword-based routing
        if any(word in user_lower for word in ["weather", "temperature", "forecast", "rain", "snow"]):
            agent = self.agents.get("weather")
            if agent:
                run = await agent.run(user_input, thread)
                output = []
                stream = await run.get_stream()
                async for chunk in stream:
                    output.append(chunk)
                return "".join(output)
        
        # Default: use first available agent
        if self.agents:
            agent = list(self.agents.values())[0]
            run = await agent.run(user_input, thread)
            output = []
            stream = await run.get_stream()
            async for chunk in stream:
                output.append(chunk)
            return "".join(output)
        
        return "No agents available"
'''
        safe_write(
            self.project_path / "src" / self.package_name / "orchestrator" / "orchestrator.py",
            orchestrator_content,
            self.force,
        )
        
        # Update main.py for complex mode
        complex_main_content = f'''"""Main entrypoint for the {self.project_name} project - Multi-Agent System."""
import asyncio
import os
import sys
from pathlib import Path

# Add vendor stub to path if SDK not available
try:
    from a2abase import A2ABaseClient
except ImportError:
    # Fallback to stub SDK
    vendor_path = Path(__file__).parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseClient  # type: ignore

from {self.package_name}.orchestrator.orchestrator import AgentOrchestrator


async def main(input_text: str | None = None) -> dict:
    """
    Run the multi-agent system.
    
    Note: Make sure the MCP server is running before running this:
        python -m {self.package_name}.tools.mcp_server
    """
    api_key = os.getenv("BASEAI_API_KEY")
    if not api_key:
        raise ValueError("Please set BASEAI_API_KEY environment variable")

    api_url = os.getenv("BASEAI_API_URL", "https://a2abase.ai/api")
    client = A2ABaseClient(api_key=api_key, api_url=api_url)

    # Create thread
    thread = await client.Thread.create()

    # Initialize orchestrator and agents
    orchestrator = AgentOrchestrator(client)
    await orchestrator.initialize_agents()

    # Route request to appropriate agent
    prompt = input_text or "What's the weather in San Francisco?"
    result = await orchestrator.route_request(prompt, thread)
    
    print(result)

    return {{"output": result}}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", help="Input text for the agent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = asyncio.run(main(args.input))
    if args.json:
        import json

        print(json.dumps(result, indent=2))
'''
        safe_write(
            self.project_path / "src" / self.package_name / "main.py", complex_main_content, self.force
        )

    def _generate_stub_sdk(self) -> None:
        """Generate stub SDK for fallback."""
        stub_dir = self.project_path / "vendor" / "a2abase_sdk_stub"

        # __init__.py
        init_content = '''"""Stub SDK for A2ABase when real SDK is not installed."""
from .agent import Agent, A2ABaseAgent
from .tools import A2ABaseTools, MCPTools
from .runner import A2ABaseClient, Thread, AgentRun, A2ABaseThread

__all__ = [
    "Agent",
    "A2ABaseAgent",
    "A2ABaseTools",
    "MCPTools",
    "A2ABaseClient",
    "Thread",
    "AgentRun",
    "A2ABaseThread",
]
'''
        safe_write(stub_dir / "__init__.py", init_content, self.force)

        # agent.py
        agent_content = '''"""Stub Agent implementation."""
from typing import Any


class Agent:
    """Stub Agent class."""

    def __init__(self, client: Any, agent_id: str, model: str = "gemini/gemini-2.5-pro"):
        self._client = client
        self._agent_id = agent_id
        self._model = model

    async def run(self, prompt: str, thread: Any, model: str | None = None):
        """Run the agent."""
        from .runner import AgentRun
        return AgentRun(thread, "stub_run_id")

    async def details(self):
        """Get agent details."""
        # Stub implementation
        class AgentDetails:
            def __init__(self):
                self.agent_id = "stub_agent_id"
                self.name = "Stub Agent"
                self.agentpress_tools = {}
                self.custom_mcps = []

        return AgentDetails()

    async def update(
        self,
        name: str | None = None,
        system_prompt: str | None = None,
        a2abase_tools: list = None,
        allowed_tools: list[str] | None = None,
    ):
        """Update the agent."""
        pass

    async def delete(self) -> None:
        """Delete the agent."""
        pass


class A2ABaseAgent:
    """Stub A2ABaseAgent class."""

    def __init__(self, client: Any):
        self._client = client

    async def create(
        self,
        name: str,
        system_prompt: str,
        a2abase_tools: list = None,
        allowed_tools: list[str] | None = None,
    ) -> Agent:
        """Create an agent."""
        # Stub implementation
        return Agent(self._client, "stub_agent_id")

    async def get(self, agent_id: str) -> Agent:
        """Get an agent."""
        return Agent(self._client, agent_id)

    async def find_by_name(self, name: str) -> Agent | None:
        """Find agent by name."""
        return None
'''
        safe_write(stub_dir / "agent.py", agent_content, self.force)

        # tools.py
        tools_content = '''"""Stub Tools implementation."""
from enum import Enum
from typing import List, Optional


_A2ABaseTools_descriptions = {
    "sb_files_tool": "Read, write, and edit files",
    "sb_shell_tool": "Execute shell commands",
    "sb_deploy_tool": "Deploy web applications",
    "sb_expose_tool": "Expose local services to the internet",
    "sb_vision_tool": "Analyze and understand images",
    "browser_tool": "Browse websites and interact with web pages",
    "web_search_tool": "Search the web for information",
    "sb_image_edit_tool": "Edit and manipulate images",
    "data_providers_tool": "Access structured data from various providers",
}


class A2ABaseTools(str, Enum):
    """Stub A2ABaseTools enum."""

    SB_FILES_TOOL = "sb_files_tool"
    SB_SHELL_TOOL = "sb_shell_tool"
    SB_DEPLOY_TOOL = "sb_deploy_tool"
    SB_EXPOSE_TOOL = "sb_expose_tool"
    SB_VISION_TOOL = "sb_vision_tool"
    SB_IMAGE_EDIT_TOOL = "sb_image_edit_tool"
    BROWSER_TOOL = "browser_tool"
    WEB_SEARCH_TOOL = "web_search_tool"
    DATA_PROVIDERS_TOOL = "data_providers_tool"

    def get_description(self) -> str:
        """Get description for the tool."""
        global _A2ABaseTools_descriptions
        desc = _A2ABaseTools_descriptions.get(self.value)
        if not desc:
            raise ValueError(f"No description found for {self.value}")
        return desc


class MCPTools:
    """Stub MCPTools class for custom tools."""

    def __init__(
        self, endpoint: str, name: str, allowed_tools: Optional[List[str]] = None
    ):
        self.url = endpoint
        self.name = name
        self.type = "http"
        self._allowed_tools = allowed_tools
        self.enabled_tools: List[str] = []

    async def initialize(self):
        """Initialize MCP tools."""
        # Stub implementation
        self.enabled_tools = self._allowed_tools or []
        return self
'''
        safe_write(stub_dir / "tools.py", tools_content, self.force)

        # runner.py (client)
        runner_content = '''"""Stub A2ABaseClient implementation."""
from typing import Any
from .agent import A2ABaseAgent


class Thread:
    """Stub Thread class."""

    def __init__(self, client: Any, thread_id: str):
        self._client = client
        self._thread_id = thread_id

    async def add_message(self, message: str):
        """Add a message to the thread."""
        return "stub_message_id"

    async def get_messages(self):
        """Get messages from the thread."""
        return []


class AgentRun:
    """Stub AgentRun class."""

    def __init__(self, thread: Thread, agent_run_id: str):
        self._thread = thread
        self._agent_run_id = agent_run_id

    async def get_stream(self):
        """Get stream of agent output."""
        async def stream():
            yield "[STUB] Agent run - install a2abase SDK for real functionality\\n"

        return stream()


class A2ABaseThread:
    """Stub A2ABaseThread class."""

    def __init__(self, client: Any):
        self._client = client

    async def create(self, name: str | None = None) -> Thread:
        """Create a thread."""
        return Thread(self._client, "stub_thread_id")

    async def get(self, thread_id: str) -> Thread:
        """Get a thread."""
        return Thread(self._client, thread_id)


class A2ABaseClient:
    """Stub A2ABaseClient class."""

    def __init__(self, api_key: str, api_url: str = "https://a2abase.ai"):
        self.api_key = api_key
        self.api_url = api_url
        # Create stub client objects
        stub_agents_client = None
        stub_threads_client = None
        self.Agent = A2ABaseAgent(stub_agents_client)
        self.Thread = A2ABaseThread(stub_threads_client)
'''
        safe_write(stub_dir / "runner.py", runner_content, self.force)

    def _generate_tests(self) -> None:
        """Generate test files."""
        test_content = f'''"""Smoke tests for {self.project_name}."""
import pytest
from {self.package_name}.agents.weather_agent import create_weather_agent
from {self.package_name}.registry.card import generate_card


@pytest.mark.asyncio
async def test_weather_agent_creation():
    """Test that weather agent can be created."""
    # This is a stub test - replace with real SDK client in actual tests
    # client = A2ABaseClient(api_key="test", api_url="https://test.com")
    # agent = await create_weather_agent(client)
    # assert agent is not None
    pass


def test_card_generation():
    """Test that card can be generated."""
    card = generate_card()
    assert card is not None
    assert "id" in card
    assert "name" in card
'''
        safe_write(self.project_path / "tests" / "test_smoke.py", test_content, self.force)
        safe_write(self.project_path / "tests" / "__init__.py", "", self.force)

