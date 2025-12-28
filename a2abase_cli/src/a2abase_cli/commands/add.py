"""Add command - add agents and tools to existing projects."""
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from a2abase_cli.generators.agent import AgentGenerator
from a2abase_cli.generators.shared import (
    find_agent_files,
    find_project_root,
    get_available_a2abase_tools,
    slugify,
    update_agent_with_tool,
)
from a2abase_cli.generators.tool import ToolGenerator

console = Console()

add_app = typer.Typer(name="add", help="Add agents or tools to your project")


@add_app.command(name="agent")
def add_agent_command(
    name: str = typer.Argument(..., help="Agent name"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
) -> None:
    """Add a new agent module to your project."""
    console.print(Panel.fit(f"[bold blue]Adding Agent: {name}[/bold blue]", border_style="blue"))

    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an A2ABase project. Run 'a2abase init' first.")
        raise typer.Exit(1)

    # Load project config
    config_path = project_root / "a2abase.yaml"
    if not config_path.exists():
        console.print("[red]Error:[/red] a2abase.yaml not found.")
        raise typer.Exit(1)

    try:
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error reading config:[/red] {e}")
        raise typer.Exit(1)

    package_name = config.get("package_name", "src")
    agents_dir = project_root / "src" / package_name / "agents"

    agent_name = slugify(name)
    agent_file = agents_dir / f"{agent_name}_agent.py"

    if agent_file.exists() and not force:
        if not Confirm.ask(f"[yellow]Agent '{agent_name}' already exists. Overwrite?[/yellow]"):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(1)

    try:
        generator = AgentGenerator(
            agent_name=agent_name,
            package_name=package_name,
            project_root=project_root,
            force=force,
        )
        generator.generate()

        console.print(f"[green]✓[/green] Agent '{agent_name}' created at {agent_file.relative_to(project_root)}")
        console.print(f"[cyan]Next:[/cyan] Import and register it in your main.py or registry")

    except Exception as e:
        console.print(f"[red]Error creating agent:[/red] {e}")
        raise typer.Exit(1)


@add_app.command(name="tool")
def add_tool_command(
    name: Optional[str] = typer.Argument(None, help="Tool name (or select from available tools)"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent name to associate with (skip prompt)"),
    from_api: bool = typer.Option(False, "--from-api", help="Select from A2ABase API tools"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
) -> None:
    """Add a new tool module to your project."""
    console.print(Panel.fit("[bold blue]Adding Tool[/bold blue]", border_style="blue"))

    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an A2ABase project. Run 'a2abase init' first.")
        raise typer.Exit(1)

    # Load project config
    config_path = project_root / "a2abase.yaml"
    if not config_path.exists():
        console.print("[red]Error:[/red] a2abase.yaml not found.")
        raise typer.Exit(1)

    try:
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error reading config:[/red] {e}")
        raise typer.Exit(1)

    package_name = config.get("package_name", "src")
    tools_dir = project_root / "src" / package_name / "tools"
    agents_dir = project_root / "src" / package_name / "agents"

    # Show available A2ABase API tools and let user choose
    tool_name = None
    is_api_tool = False
    api_tool_value = None

    if from_api or name is None:
        # Show available API tools
        api_tools = get_available_a2abase_tools()

        if api_tools:
            table = Table(title="Available A2ABase API Tools", show_header=True, header_style="bold")
            table.add_column("#", style="cyan", no_wrap=True)
            table.add_column("Tool Name", style="white")
            table.add_column("Description", style="dim")

            for idx, (tool_value, description) in enumerate(api_tools, 1):
                table.add_row(str(idx), tool_value, description)

            console.print("\n")
            console.print(table)

            tool_choice = Prompt.ask(
                "\n[bold cyan]Select a tool to add (or enter custom name for new tool)[/bold cyan]",
                default="",
            )

            if tool_choice.isdigit():
                # User selected by number
                tool_idx = int(tool_choice) - 1
                if 0 <= tool_idx < len(api_tools):
                    api_tool_value, description = api_tools[tool_idx]
                    tool_name = api_tool_value.replace("_tool", "").replace("sb_", "")
                    is_api_tool = True
                else:
                    console.print("[red]Invalid selection[/red]")
                    raise typer.Exit(1)
            elif tool_choice:
                # User entered custom name
                tool_name = slugify(tool_choice)
            else:
                console.print("[yellow]No tool selected[/yellow]")
                raise typer.Exit(1)
        else:
            # No API tools available, ask for custom name
            if name is None:
                name = Prompt.ask("[bold cyan]Enter tool name[/bold cyan]")
            tool_name = slugify(name)

    if tool_name is None:
        tool_name = slugify(name) if name else "custom_tool"

    tool_file = tools_dir / f"{tool_name}.py"
    tool_schema_name = f"{tool_name.upper()}_SCHEMA"

    if tool_file.exists() and not force:
        if not Confirm.ask(f"[yellow]Tool '{tool_name}' already exists. Overwrite?[/yellow]"):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(1)

    # Find available agents
    available_agents = find_agent_files(agents_dir)

    # Ask which agent(s) to associate with
    selected_agents = []
    if agent:
        # Use provided agent name
        agent_name = slugify(agent)
        agent_file = agents_dir / f"{agent_name}_agent.py"
        if agent_file.exists():
            selected_agents.append((agent_name, agent_file))
        else:
            console.print(f"[yellow]Warning:[/yellow] Agent '{agent_name}' not found. Tool will be created but not associated.")
    elif available_agents:
        # Show available agents
        table = Table(title="Available Agents", show_header=True, header_style="bold")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Agent Name", style="white")

        for idx, (agent_name, _) in enumerate(available_agents, 1):
            table.add_row(str(idx), agent_name)

        console.print("\n")
        console.print(table)

        agent_choice = Prompt.ask(
            "\n[bold cyan]Which agent(s) should this tool be associated with?[/bold cyan]",
            default="all",
            help="Enter agent number(s) separated by commas, 'all' for all agents, or 'none' to skip",
        )

        if agent_choice.lower() == "all":
            selected_agents = available_agents
        elif agent_choice.lower() == "none":
            selected_agents = []
        else:
            # Parse comma-separated numbers
            try:
                indices = [int(x.strip()) for x in agent_choice.split(",")]
                selected_agents = [
                    available_agents[i - 1]
                    for i in indices
                    if 1 <= i <= len(available_agents)
                ]
            except (ValueError, IndexError):
                console.print("[yellow]Invalid selection. Tool will be created but not associated.[/yellow]")
                selected_agents = []
    else:
        console.print("[yellow]No agents found. Tool will be created but not associated with any agent.[/yellow]")

    try:
        # Generate the tool
        generator = ToolGenerator(
            tool_name=tool_name,
            package_name=package_name,
            project_root=project_root,
            force=force,
            is_api_tool=is_api_tool,
            api_tool_value=api_tool_value if is_api_tool else None,
        )
        generator.generate()

        tool_type = "A2ABase API tool wrapper" if is_api_tool else "custom tool"
        console.print(f"[green]✓[/green] {tool_type} '{tool_name}' created at {tool_file.relative_to(project_root)}")

        # Update agent files
        if selected_agents:
            console.print(f"\n[cyan]Associating tool with {len(selected_agents)} agent(s)...[/cyan]")
            for agent_name, agent_file in selected_agents:
                try:
                    updated = update_agent_with_tool(
                        agent_file, tool_name, tool_schema_name, package_name
                    )
                    if updated:
                        console.print(f"  [green]✓[/green] Updated {agent_name}_agent.py")
                    else:
                        console.print(f"  [dim]ℹ[/dim] {agent_name}_agent.py already has this tool")
                except Exception as e:
                    console.print(f"  [yellow]⚠[/yellow] Could not update {agent_name}_agent.py: {e}")
        else:
            console.print(f"\n[yellow]Note:[/yellow] Tool created but not associated with any agent.")
            console.print(f"[cyan]Next:[/cyan] Import {tool_schema_name} from {package_name}.tools.{tool_name} in your agent files")

    except Exception as e:
        console.print(f"[red]Error creating tool:[/red] {e}")
        raise typer.Exit(1)


# Export add_app for use in main CLI
__all__ = ["add_app"]

