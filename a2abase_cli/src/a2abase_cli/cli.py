"""Main CLI entrypoint using Typer."""
import sys
from typing import Optional

import typer
from rich.console import Console

from a2abase_cli import __version__
from a2abase_cli.commands import (
    add,
    dev,
    doctor,
    init,
    run,
    test,
    version,
)

app = typer.Typer(
    name="a2abase",
    help="[bold blue]A2ABase CLI[/bold blue] - Scaffold and manage Agent SDK projects",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """A2ABase CLI - Production-ready tool for scaffolding Agent SDK projects."""
    if ctx.invoked_subcommand is None:
        from rich.panel import Panel
        from rich.table import Table

        console.print(
            Panel.fit(
                "[bold blue]A2ABase CLI[/bold blue]\n"
                "Production-ready tool for scaffolding and managing Agent SDK projects",
                border_style="blue",
            )
        )

        table = Table(title="Available Commands", show_header=True, header_style="bold cyan")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        table.add_row("init", "Create a new A2ABase project")
        table.add_row("add agent <name>", "Add a new agent module")
        table.add_row("add tool <name>", "Add a new tool module")
        table.add_row("dev", "Run project in development mode (auto-reload)")
        table.add_row("run", "Run the project once")
        table.add_row("test", "Run tests")
        table.add_row("doctor", "Validate environment and configuration")
        table.add_row("version", "Show CLI and SDK versions")

        console.print("\n")
        console.print(table)
        console.print("\n[yellow]Tip:[/yellow] Run [cyan]a2abase <command> --help[/cyan] for detailed help")
        console.print("[dim]Example:[/dim] [cyan]a2abase init --help[/cyan]\n")


# Register commands
app.command(name="init")(init.init_command)
app.add_typer(add.add_app, name="add")
app.command(name="dev")(dev.dev_command)
app.command(name="run")(run.run_command)
app.command(name="test")(test.test_command)
app.command(name="doctor")(doctor.doctor_command)
app.command(name="version")(version.version_command)


def main() -> None:
    """Entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

