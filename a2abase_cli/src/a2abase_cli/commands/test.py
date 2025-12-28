"""Test command - run tests."""
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from a2abase_cli.generators.shared import find_project_root

console = Console()


def test_command(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    coverage: bool = typer.Option(False, "--coverage", help="Run with coverage"),
) -> None:
    """Run tests for the project."""
    console.print(Panel.fit("[bold blue]Running Tests[/bold blue]", border_style="blue"))

    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an A2ABase project. Run 'a2abase init' first.")
        raise typer.Exit(1)

    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        console.print("[yellow]Warning:[/yellow] No tests directory found. Creating one...")
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").touch()

    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        console.print("[red]Error:[/red] pytest not installed. Install it with: pip install pytest")
        raise typer.Exit(1)

    # Prepare pytest command
    cmd = [sys.executable, "-m", "pytest"]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov", "src", "--cov-report", "html", "--cov-report", "term"])

    try:
        result = subprocess.run(cmd, cwd=project_root)

        if result.returncode == 0:
            console.print("[green]✓[/green] All tests passed!")
        else:
            console.print("[red]✗[/red] Some tests failed")

        raise typer.Exit(result.returncode)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error running tests:[/red] {e}", err=True)
        raise typer.Exit(1)

