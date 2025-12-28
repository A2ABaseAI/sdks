"""Doctor command - validate environment and configuration."""
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from a2abase_cli.generators.shared import find_project_root

console = Console()


def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro} (requires 3.11+)"


def check_venv() -> Tuple[bool, str]:
    """Check if running in a virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        return True, sys.prefix
    return False, "Not in a virtual environment"


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check if required dependencies are installed."""
    deps = [
        ("typer", "typer"),
        ("rich", "rich"),
        ("jinja2", "jinja2"),
        ("watchfiles", "watchfiles"),
        ("pydantic", "pydantic"),
        ("yaml", "pyyaml"),
        ("pytest", "pytest"),
    ]
    results = []
    for module_name, package_name in deps:
        try:
            __import__(module_name)  # noqa: F401
            results.append((package_name, True, "Installed"))
        except ImportError:
            results.append((package_name, False, "Not installed"))
    return results


def check_config(project_root: Path) -> Tuple[bool, str]:
    """Check if a2abase.yaml exists and is valid."""
    config_path = project_root / "a2abase.yaml"
    if not config_path.exists():
        return False, "a2abase.yaml not found"

    try:
        import yaml

        with open(config_path) as f:
            yaml.safe_load(f)
        return True, "Valid"
    except Exception as e:
        return False, f"Invalid: {e}"


def check_write_permissions(project_root: Path) -> Tuple[bool, str]:
    """Check write permissions."""
    test_file = project_root / ".a2abase_test_write"
    try:
        test_file.touch()
        test_file.unlink()
        return True, "Writable"
    except Exception as e:
        return False, f"Not writable: {e}"


def check_package_manager() -> Tuple[bool, str, str]:
    """Check available package managers."""
    uv_available = shutil.which("uv") is not None
    pip_available = shutil.which("pip") is not None

    if uv_available:
        return True, "uv", "Available"
    elif pip_available:
        return True, "pip", "Available"
    return False, "none", "Neither uv nor pip found"


def doctor_command() -> None:
    """Validate environment and configuration, show actionable errors."""
    console.print(Panel.fit("[bold blue]A2ABase Doctor[/bold blue]", border_style="blue"))

    issues = []
    table = Table(title="Environment Check", show_header=True, header_style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    # Python version
    ok, details = check_python_version()
    table.add_row("Python Version", "✓" if ok else "✗", details)
    if not ok:
        issues.append("Python 3.11+ required. Upgrade Python.")

    # Virtual environment
    ok, details = check_venv()
    table.add_row("Virtual Environment", "✓" if ok else "⚠", details)
    if not ok:
        issues.append("Not in a virtual environment. Create one with: python -m venv venv")

    # Dependencies
    deps = check_dependencies()
    for dep_name, ok, details in deps:
        table.add_row(f"Dependency: {dep_name}", "✓" if ok else "✗", details)
        if not ok:
            issues.append(f"Install {dep_name}: pip install {dep_name}")

    # Project root
    project_root = find_project_root()
    if project_root:
        table.add_row("Project Root", "✓", str(project_root))

        # Config
        ok, details = check_config(project_root)
        table.add_row("Config File", "✓" if ok else "✗", details)
        if not ok:
            issues.append(f"Fix config: {details}")

        # Write permissions
        ok, details = check_write_permissions(project_root)
        table.add_row("Write Permissions", "✓" if ok else "✗", details)
        if not ok:
            issues.append(f"Fix permissions: {details}")
    else:
        table.add_row("Project Root", "✗", "Not in an A2ABase project")
        issues.append("Run 'a2abase init' to create a project")

    # Package manager
    ok, pm_name, details = check_package_manager()
    table.add_row("Package Manager", "✓" if ok else "✗", f"{pm_name}: {details}")
    if not ok:
        issues.append("Install pip or uv")

    console.print(table)

    if issues:
        fix_panel = Panel(
            "\n".join(f"[cyan]{i+1}.[/cyan] {issue}" for i, issue in enumerate(issues)),
            title="[yellow]Issues Found[/yellow]",
            border_style="yellow",
        )
        console.print(fix_panel)
        raise typer.Exit(1)
    else:
        console.print("\n[green]✓[/green] All checks passed!")
        raise typer.Exit(0)

