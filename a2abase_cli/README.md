# A2ABase CLI

Production-ready CLI tool for scaffolding and managing A2ABase Agent SDK projects.

## Installation

```bash
pip install -e .
```

Or with `uv`:

```bash
uv pip install -e .
```

## Usage

### Initialize a new project

```bash
a2abase init
```

This will interactively prompt you for:
- Project name
- Package name
- Template (basic, api, agentic)
- Package manager (uv or pip)

Options:
- `--name, -n`: Project name (non-interactive)
- `--package, -p`: Package name (non-interactive)
- `--template, -t`: Template type (non-interactive)
- `--pm`: Package manager (non-interactive)
- `--install`: Install dependencies after creation
- `--force`: Overwrite existing files
- `--cwd`: Working directory

### Add an agent

```bash
a2abase add agent <name>
```

Example:
```bash
a2abase add agent weather
```

This creates `src/<package>/agents/weather_agent.py` with a basic agent implementation.

### Add a tool

```bash
a2abase add tool <name>
```

Example:
```bash
a2abase add tool web_search
```

This creates `src/<package>/tools/web_search.py` with a basic tool implementation.

Options:
- `--from-api`: Select from available A2ABase API tools
- `--agent, -a`: Associate tool with specific agent
- `--force`: Overwrite existing tool file

**Select from A2ABase API tools:**
```bash
a2abase add tool --from-api
```

This will show an interactive list of available A2ABase built-in tools.

### Run in development mode

```bash
a2abase dev
```

**IMPORTANT**: Ngrok is enabled by default because A2ABase agents run on remote servers
and require public access to your local MCP server. Your custom tools won't work without ngrok!

Runs the project with auto-reload on file changes. Automatically starts the MCP server with ngrok tunnel.

**Setup (required):**
```bash
# 1. Install ngrok support
pip install pyngrok

# 2. Get free ngrok auth token from https://dashboard.ngrok.com/get-started/your-authtoken
export NGROK_AUTH_TOKEN=your_token_here

# 3. Run dev command (ngrok enabled by default)
a2abase dev
```

Options:
- `--watch/--no-watch`: Enable/disable auto-reload (default: enabled)
- `--mcp-port`: MCP server port (default: 8000)
- `--no-mcp`: Don't start MCP server
- `--ngrok/--no-ngrok`: Enable/disable ngrok tunnel (default: enabled, required for remote agents)
- `--ngrok-token`: Ngrok auth token (or set NGROK_AUTH_TOKEN env var)

The dev command will:
- Start MCP server on `http://localhost:8000/mcp` (or custom port)
- Create ngrok tunnel (enabled by default, required for remote agents)
- Display both local and public URLs in a formatted table
- Run your agent with auto-reload on file changes

**Disable ngrok** (only for local testing without remote agents):
```bash
a2abase dev --no-ngrok
```

### Run once

```bash
a2abase run --input "your prompt here"
```

Options:
- `--input, -i`: Input text for the agent
- `--json`: Output as JSON

### Run tests

```bash
a2abase test
```

Options:
- `--verbose, -v`: Verbose output
- `--coverage`: Run with coverage

### Doctor (validate environment)

```bash
a2abase doctor
```

Checks:
- Python version (3.11+)
- Virtual environment
- Required dependencies
- Project configuration
- Write permissions
- Package manager availability

### Show version

```bash
a2abase version
```

Shows CLI version, SDK version, and Python version.

## Project Structure

When you run `a2abase init`, it creates:

```
<project_name>/
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
├── .gitignore             # Git ignore rules
├── .env.example           # Environment variables template
├── a2abase.yaml           # A2ABase project config
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── main.py        # Entrypoint
│       ├── sdk_adapter.py # SDK adapter (real or stub)
│       ├── agents/
│       │   ├── __init__.py
│       │   └── weather_agent.py  # Example weather agent
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── weather.py         # Real weather tool (Open-Meteo API)
│       │   ├── mcp_server.py     # MCP server for custom tools
│       │   └── README.md         # Tools documentation
│       └── registry/
│           ├── __init__.py
│           ├── tools.py          # Tool registry
│           └── card.py           # Agent card generator
├── vendor/
│   └── a2abase_sdk_stub/  # Fallback stub SDK
│       ├── __init__.py
│       ├── agent.py
│       ├── tools.py
│       └── runner.py
└── tests/
    ├── __init__.py
    └── test_smoke.py
```

## Generated Project Features

### Weather Tool
- 🌤️ **Real weather data** using [Open-Meteo API](https://api.open-meteo.com/v1/forecast)
- ✅ **Free** - No API key required
- ✅ **Current weather** - Temperature, humidity, wind, conditions
- ✅ **Forecast** - Up to 16 days of weather forecast
- ✅ **Geocoding** - Automatic coordinate lookup for city names

### MCP Server
- 🔧 **Custom tools** - Serve your tools via MCP (Model Context Protocol)
- 🚀 **Auto-start** - Automatically started by `a2abase dev`
- 🌐 **Ngrok support** - Expose server publicly with `--ngrok` flag
- 📝 **Well-documented** - Complete guide in `tools/README.md`

### Example Agent
- 🤖 **Weather Agent** - Ready-to-use example with custom weather tool
- 📋 **Agent cards** - Metadata generation for agent registry
- 🔄 **Auto-reload** - Development mode with file watching

## Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Quality

The project uses `ruff` for linting and formatting:

```bash
ruff check .
ruff format .
```

## Features

- ✅ **Interactive project scaffolding** - Create projects with guided prompts
- ✅ **Agent and tool generators** - Quickly add new agents and tools
- ✅ **MCP server integration** - Serve custom tools to A2ABase agents
- ✅ **Ngrok support** - Expose MCP server publicly for remote access
- ✅ **Weather tool example** - Real weather API integration (Open-Meteo)
- ✅ **Auto-reload development server** - Watch for changes and auto-restart
- ✅ **Environment validation** - Doctor command checks your setup
- ✅ **Fallback stub SDK** - Projects work without SDK installed
- ✅ **Idempotent operations** - Won't overwrite without `--force`
- ✅ **Rich terminal UI** - Beautiful colors, tables, and formatting
- ✅ **Cross-platform** - Works on macOS, Linux, Windows
- ✅ **Python 3.11+ support** - Modern Python features

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Commands Reference](docs/COMMANDS.md)** - Complete command documentation
- **[Architecture](docs/ARCHITECTURE.md)** - Technical details and design
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Quick Example

```bash
# 1. Create a new project
a2abase init --name my-weather-agent

# 2. Navigate to project
cd my-weather-agent

# 3. Set up environment
cp .env.example .env
# Edit .env and add BASEAI_API_KEY

# 4. Install dependencies
pip install -e .

# 5. Install ngrok support (required for remote agents)
pip install pyngrok

# 6. Set ngrok auth token (get free token from https://dashboard.ngrok.com/get-started/your-authtoken)
export NGROK_AUTH_TOKEN=your_token_here

# 7. Run in development mode (ngrok enabled by default)
a2abase dev
```

## Ngrok Integration (Required)

**Ngrok is enabled by default** because A2ABase agents run on remote servers and need
public access to your local MCP server. Without ngrok, remote agents cannot access
your custom tools.

### Why Ngrok is Required

- A2ABase agents execute on remote servers (not locally)
- Your MCP server runs locally on your machine
- Remote agents need a public URL to access your local MCP server
- Ngrok creates a secure tunnel from the internet to your local server

### Setup

1. **Get free ngrok auth token**:
   - Sign up at [ngrok.com](https://ngrok.com)
   - Get token from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)

2. **Install pyngrok**:
   ```bash
   pip install pyngrok
   ```

3. **Set environment variable**:
   ```bash
   export NGROK_AUTH_TOKEN=your_token_here
   ```

4. **Run dev command** (ngrok enabled by default):
   ```bash
   a2abase dev
   ```

The CLI will display both local and public URLs. **Use the public URL** in your agent's
MCPTools configuration for remote agent access.

⚠️ **Security Note**: Ngrok exposes your MCP server publicly. Use only for development/testing.
For production, deploy your MCP server to a proper hosting service with HTTPS and authentication.

## Getting Help

- Run `a2abase` to see available commands
- Run `a2abase --help` for command overview
- Run `a2abase <command> --help` for specific command help
- Run `a2abase doctor` to validate your environment
- Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for common issues

## License

MIT

