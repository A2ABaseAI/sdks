"""Run command - execute project once."""
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from a2abase_cli.generators.shared import find_project_root

console = Console()


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

    # Prepare command
    cmd = [sys.executable, "-m", main_module]
    if input_text:
        cmd.extend(["--input", input_text])
    if json_output:
        cmd.append("--json")

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
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
                console.print(f"[red]{result.stderr}[/red]", err=True)

        raise typer.Exit(result.returncode)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error running project:[/red] {e}", err=True)
        raise typer.Exit(1)

