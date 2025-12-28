# Quick Start Guide

## Installation

### Install the CLI locally

```bash
cd a2abase_cli
pip install -e .
```

Or with `uv`:

```bash
cd a2abase_cli
uv pip install -e .
```

### Verify Installation

```bash
a2abase version
```

## Create Your First Project

### 1. Initialize a project

```bash
a2abase init
```

Follow the interactive prompts, or use flags:

```bash
a2abase init --name my-agent --package my_agent --template basic --pm pip
```

### 2. Set up the project

```bash
cd my-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your BASEAI_API_KEY
```

### 4. Run the project

```bash
# Development mode with auto-reload
a2abase dev

# Or run once
a2abase run --input "What's the weather in San Francisco?"
```

## Adding Agents and Tools

### Add a new agent

```bash
a2abase add agent research
```

This creates `src/<package>/agents/research_agent.py`.

### Add a new tool

```bash
a2abase add tool database_query
```

This creates `src/<package>/tools/database_query.py`.

## Testing

```bash
# Run tests
a2abase test

# With coverage
a2abase test --coverage
```

## Validation

Check your environment:

```bash
a2abase doctor
```

This validates:
- Python version
- Virtual environment
- Dependencies
- Project configuration
- Write permissions

## Project Structure

After `a2abase init`, you'll have:

```
my-agent/
├── src/
│   └── my_agent/
│       ├── main.py              # Entrypoint
│       ├── agents/              # Your agents
│       ├── tools/               # Your tools
│       └── registry/            # Agent cards
├── vendor/
│   └── a2abase_sdk_stub/        # Fallback SDK
├── tests/                       # Your tests
└── a2abase.yaml                 # Project config
```

## Example: Weather Agent

The scaffolded project includes a working weather agent example:

```python
# src/my_agent/agents/weather_agent.py
from a2abase import A2ABaseClient
from a2abase.tools import A2ABaseTools

async def create_weather_agent(client: A2ABaseClient):
    agent = await client.Agent.create(
        name="Weather Agent",
        system_prompt="You are a helpful weather assistant...",
        a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL],
    )
    return agent
```

## Next Steps

1. **Customize agents**: Edit files in `src/<package>/agents/`
2. **Add tools**: Create new tools in `src/<package>/tools/`
3. **Update main.py**: Modify the entrypoint to use your agents
4. **Write tests**: Add tests in `tests/`
5. **Deploy**: Package and deploy your agent project

## Troubleshooting

### SDK not found

The project includes a stub SDK in `vendor/a2abase_sdk_stub/` that allows the code to run even without the real SDK installed. Install the real SDK:

```bash
pip install a2abase
```

### Import errors

Make sure you're in the project directory and have activated the virtual environment:

```bash
cd my-agent
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

### Permission errors

Run `a2abase doctor` to check for permission issues and get fix commands.

## Getting Help

- Run `a2abase --help` for command help
- Run `a2abase <command> --help` for specific command help
- Check the main README.md for detailed documentation

