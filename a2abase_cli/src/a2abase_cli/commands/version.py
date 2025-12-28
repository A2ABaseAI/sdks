"""Version command - show CLI and SDK versions."""
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from a2abase_cli import __version__

console = Console()


def get_sdk_version() -> str:
    """Try to get the SDK version."""
    try:
        import a2abase  # noqa: F401

        return getattr(a2abase, "__version__", "unknown")
    except ImportError:
        # Try to find it in the project
        project_root = Path.cwd()
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomli

                with open(pyproject, "rb") as f:
                    data = tomli.load(f)
                    return data.get("project", {}).get("version", "unknown")
            except Exception:
                pass
        return "not installed"


def version_command() -> None:
    """Show CLI and SDK versions."""
    cli_version = __version__
    sdk_version = get_sdk_version()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    table = Table(title="Version Information", show_header=True, header_style="bold")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="white")

    table.add_row("A2ABase CLI", cli_version)
    table.add_row("A2ABase SDK", sdk_version)
    table.add_row("Python", python_version)

    console.print(table)

