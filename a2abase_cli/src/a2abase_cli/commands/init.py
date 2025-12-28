"""Init command - scaffold new projects."""
import os
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from a2abase_cli.generators.project import ProjectGenerator
from a2abase_cli.generators.shared import slugify, validate_package_name

console = Console()


def init_command(
    project_name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    package_name: Optional[str] = typer.Option(None, "--package", "-p", help="Package name"),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template: basic (native tools only), advanced (custom tools/MCP), or complex (multi-agent)"
    ),
    package_manager: Optional[str] = typer.Option(
        None, "--pm", help="Package manager: uv or pip"
    ),
    install: bool = typer.Option(False, "--install", help="Install dependencies after creation"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory"),
) -> None:
    """Initialize a new A2ABase Agent SDK project."""
    console.print(Panel.fit("[bold blue]A2ABase Project Scaffolder[/bold blue]", border_style="blue"))

    # Determine working directory
    base_dir = Path(cwd) if cwd else Path.cwd()
    base_dir = base_dir.resolve()

    # Interactive prompts if not provided
    if not project_name:
        project_name = Prompt.ask(
            "[bold cyan]Project name[/bold cyan]",
            default="my-agent-project",
        )
    project_name = slugify(project_name)

    if not package_name:
        package_name = Prompt.ask(
            "[bold cyan]Package name[/bold cyan]",
            default=project_name.replace("-", "_"),
        )
    package_name = validate_package_name(package_name)

    if not template:
        template_table = Table(title="Available Templates", show_header=True, header_style="bold")
        template_table.add_column("Template", style="cyan", no_wrap=True)
        template_table.add_column("Description", style="white")
        template_table.add_row("basic", "Simple agent with native A2ABase tools only (no MCP server)")
        template_table.add_row("advanced", "Agent with custom tools via MCP server (requires ngrok)")
        template_table.add_row("complex", "Multi-agent system with multiple agents and coordination")
        console.print(template_table)
        template = Prompt.ask(
            "[bold cyan]Template[/bold cyan]",
            choices=["basic", "advanced", "complex"],
            default="basic",
        )

    if not package_manager:
        # Check if uv is available
        uv_available = shutil.which("uv") is not None
        if uv_available:
            package_manager = Prompt.ask(
                "[bold cyan]Package manager[/bold cyan]",
                choices=["uv", "pip"],
                default="uv",
            )
        else:
            package_manager = "pip"
            console.print("[yellow]Note:[/yellow] 'uv' not found, using 'pip'")

    project_path = base_dir / project_name

    # Check if directory exists
    if project_path.exists() and not force:
        if not Confirm.ask(
            f"[yellow]Directory '{project_name}' already exists. Overwrite?[/yellow]",
            default=False,
        ):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(1)
        force = True

    # Generate project
    try:
        generator = ProjectGenerator(
            project_name=project_name,
            package_name=package_name,
            template=template,
            package_manager=package_manager,
            project_path=project_path,
            force=force,
        )
        generator.generate()

        console.print(f"\n[green]✓[/green] Project '{project_name}' created successfully!")

        # Next steps
        next_steps = Panel(
            f"""[bold]Next steps:[/bold]

[cyan]1.[/cyan] cd {project_name}
[cyan]2.[/cyan] Create virtual environment:
   {'[dim]uv venv[/dim]' if package_manager == 'uv' else '[dim]python -m venv venv[/dim]'}
[cyan]3.[/cyan] Activate virtual environment:
   {'[dim]source venv/bin/activate  # macOS/Linux[/dim]' if package_manager == 'pip' else '[dim]source .venv/bin/activate  # macOS/Linux[/dim]'}
   {'[dim].\\\\venv\\\\Scripts\\\\activate  # Windows[/dim]' if package_manager == 'pip' else '[dim].\\\\venv\\\\Scripts\\\\activate  # Windows[/dim]'}
[cyan]4.[/cyan] Install dependencies:
   {'[dim]uv pip install -e .[/dim]' if package_manager == 'uv' else '[dim]pip install -e .[/dim]'}
[cyan]5.[/cyan] Set up environment:
   [dim]cp .env.example .env[/dim]
   [dim]# Edit .env and add your BASEAI_API_KEY[/dim]
[cyan]6.[/cyan] Run in dev mode:
   [dim]a2abase dev[/dim]

[bold yellow]Happy coding![/bold yellow]""",
            title="🚀",
            border_style="green",
        )
        console.print(next_steps)

        # Install dependencies if requested
        if install:
            console.print("\n[cyan]Installing dependencies...[/cyan]")
            import subprocess
            import sys

            os.chdir(project_path)
            if package_manager == "uv":
                subprocess.run(["uv", "venv"], check=True)
                subprocess.run(["uv", "pip", "install", "-e", "."], check=True)
            else:
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
                venv_python = project_path / "venv" / "bin" / "python"
                if os.name == "nt":  # Windows
                    venv_python = project_path / "venv" / "Scripts" / "python.exe"
                subprocess.run([str(venv_python), "-m", "pip", "install", "-e", "."], check=True)
            console.print("[green]✓[/green] Dependencies installed!")

    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {e}", err=True)
        raise typer.Exit(1)

