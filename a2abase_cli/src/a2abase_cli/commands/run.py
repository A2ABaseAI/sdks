"""Run command - execute project once."""
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from a2abase_cli.generators.shared import ensure_a2abase_sdk_installed, find_project_root

console = Console()
err_console = Console(file=sys.stderr)


def run_command(
    input_text: Optional[str] = typer.Option(None, "--input", "-i", help="Input text for the agent"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Run the project once."""
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
    main_module = f"{package_name}.main"

    # Check if main.py exists
    main_file = project_root / "src" / package_name / "main.py"
    if not main_file.exists():
        console.print(f"[red]Error:[/red] {main_file} not found.")
        raise typer.Exit(1)

    # Ensure a2abase SDK is installed (automatically installs if missing)
    console.print("[cyan]Checking a2abase SDK installation...[/cyan]")
    success, message = ensure_a2abase_sdk_installed(project_root, auto_install=True)
    if success:
        if "installed successfully" in message.lower():
            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[green]✓[/green] {message}")
    else:
        console.print(f"[red]✗[/red] {message}")
        console.print("[yellow]Continuing with stub SDK (limited functionality)[/yellow]")

    # Prepare command
    cmd = [sys.executable, "-m", main_module]
    if input_text:
        cmd.extend(["--input", input_text])
    if json_output:
        cmd.append("--json")

    # Set up environment with PYTHONPATH
    import os
    env = os.environ.copy()
    # Add src directory to PYTHONPATH so Python can find the module
    src_path = str(project_root / "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            capture_output=not json_output,
            text=True,
        )

        if json_output:
            try:
                output = json.loads(result.stdout)
                console.print_json(json.dumps(output, indent=2))
            except json.JSONDecodeError:
                console.print(result.stdout)
        else:
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                err_console.print(f"[red]{result.stderr}[/red]")

        raise typer.Exit(result.returncode)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        err_console.print(f"[red]Error running project:[/red] {e}")
        raise typer.Exit(1)

