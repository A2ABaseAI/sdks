"""Dev command - run project in development mode with auto-reload and MCP server."""
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from a2abase_cli.generators.shared import ensure_a2abase_sdk_installed, find_project_root

console = Console()


def dev_command(
    watch: bool = typer.Option(True, "--watch/--no-watch", help="Enable auto-reload"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port (if applicable)"),
    mcp_port: Optional[int] = typer.Option(8000, "--mcp-port", help="MCP server port (advanced template only)"),
    no_mcp: bool = typer.Option(False, "--no-mcp", help="Don't start MCP server (advanced template only)"),
    ngrok: bool = typer.Option(True, "--ngrok/--no-ngrok", help="Expose MCP server via ngrok (advanced template only, required for remote agents)"),
    ngrok_auth_token: Optional[str] = typer.Option(None, "--ngrok-token", help="Ngrok auth token (or set NGROK_AUTH_TOKEN env var)"),
) -> None:
    """Run the project in development mode with auto-reload and MCP server.
    
    IMPORTANT: MCP server and ngrok are only available for 'advanced' template projects.
    For 'basic' template projects, only native A2ABase tools are available.
    
    For advanced templates: Since A2ABase agents run on remote servers, ngrok is REQUIRED
    to expose your local MCP server to the internet. The MCP server must be publicly accessible
    for agents to use your custom tools.
    
    Ngrok is enabled by default for advanced templates. Use --no-ngrok only if testing locally without remote agents.
    """
    console.print(Panel.fit("[bold blue]Development Mode[/bold blue]", border_style="blue"))

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
    template = config.get("template", "basic")
    main_module = f"{package_name}.main"
    mcp_module = f"{package_name}.tools.mcp_server"

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

    # MCP server and ngrok are only available for advanced template
    if template != "advanced":
        # For non-advanced templates, disable MCP and ngrok
        # Only show error if user explicitly tried to use MCP features
        # We can't easily detect if flags were explicitly passed, so we check if:
        # 1. User passed --ngrok-token (explicit MCP usage)
        # 2. User passed custom --mcp-port (explicit MCP usage)
        # Otherwise, silently disable MCP/ngrok for basic templates
        if ngrok_auth_token is not None or (mcp_port is not None and mcp_port != 8000):
            console.print("[red]Error:[/red] MCP server and ngrok are only available for 'advanced' template projects.")
            console.print(f"[yellow]Current template:[/yellow] {template}")
            console.print("[dim]To use custom tools with MCP server, create a new project with:[/dim]")
            console.print("[cyan]  a2abase init --template advanced[/cyan]")
            raise typer.Exit(1)
        # Silently disable MCP and ngrok for non-advanced templates
        no_mcp = True
        ngrok = False

    # Check if MCP server exists (only for advanced template)
    mcp_file = project_root / "src" / package_name / "tools" / "mcp_server.py"
    start_mcp = template == "advanced" and not no_mcp and mcp_file.exists()

    console.print(f"[cyan]Starting dev server for {package_name}...[/cyan]")
    if start_mcp:
        console.print(f"[cyan]MCP server will start on port {mcp_port}[/cyan]")
        if ngrok:
            console.print("[bold green]✓[/bold green] [bold]Ngrok enabled[/bold] - MCP server will be publicly accessible")
            console.print("[dim]Required for remote A2ABase agents to access your custom tools[/dim]")
        else:
            console.print("[bold yellow]⚠[/bold yellow] [bold]Ngrok disabled[/bold] - MCP server only accessible locally")
            console.print("[yellow]Remote agents cannot access your tools without ngrok![/yellow]")
            console.print("[dim]Use --ngrok to enable (required for A2ABase agents)[/dim]")
    console.print(f"[dim]Watching: {project_root / 'src'}[/dim]")
    
    # Initialize ngrok if requested
    ngrok_tunnel = None
    ngrok_url = None
    if ngrok and start_mcp:
        try:
            from pyngrok import ngrok, conf
            import os
            
            auth_token = ngrok_auth_token or os.getenv("NGROK_AUTH_TOKEN")
            if auth_token:
                conf.get_default().auth_token = auth_token
            elif not os.path.exists(os.path.expanduser("~/.ngrok2/ngrok.yml")):
                console.print("[yellow]⚠[/yellow] No ngrok auth token found.")
                console.print("[yellow]Get your free token from: https://dashboard.ngrok.com/get-started/your-authtoken[/yellow]")
                console.print("[dim]Set NGROK_AUTH_TOKEN env var or use --ngrok-token[/dim]")
                console.print("[dim]Continuing with free tier (limited sessions)...[/dim]")
            
            # Start ngrok tunnel
            console.print(f"[green]Starting ngrok tunnel for port {mcp_port}...[/green]")
            ngrok_tunnel = ngrok.connect(mcp_port, "http")
            ngrok_url = ngrok_tunnel.public_url
            console.print(f"[bold green]✓[/bold green] Ngrok tunnel active: [cyan]{ngrok_url}[/cyan]")
            console.print(f"[dim]MCP endpoint: {ngrok_url}/mcp[/dim]")
            
        except ImportError:
            console.print("[red]Error:[/red] pyngrok not installed.")
            console.print("[yellow]Installing pyngrok is required for remote agent access![/yellow]")
            console.print()
            console.print("[cyan]Quick install options:[/cyan]")
            console.print(f"  1. [bold]pip install pyngrok[/bold]")
            console.print(f"  2. [bold]pip install -e '.[ngrok]'[/bold] (from project root: {project_root})")
            console.print(f"  3. [bold]uv pip install pyngrok[/bold]")
            console.print()
            if Confirm.ask("[bold cyan]Install pyngrok now?[/bold cyan]", default=True):
                try:
                    console.print("[cyan]Installing pyngrok...[/cyan]")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "pyngrok>=7.0.0"],
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        console.print("[green]✓[/green] pyngrok installed successfully!")
                        # Retry importing
                        from pyngrok import ngrok, conf
                        import os
                        auth_token = ngrok_auth_token or os.getenv("NGROK_AUTH_TOKEN")
                        if auth_token:
                            conf.get_default().auth_token = auth_token
                        elif not os.path.exists(os.path.expanduser("~/.ngrok2/ngrok.yml")):
                            console.print("[yellow]⚠[/yellow] No ngrok auth token found.")
                            console.print("[yellow]Get your free token from: https://dashboard.ngrok.com/get-started/your-authtoken[/yellow]")
                            console.print("[dim]Set NGROK_AUTH_TOKEN env var or use --ngrok-token[/dim]")
                            console.print("[dim]Continuing with free tier (limited sessions)...[/dim]")
                        
                        # Start ngrok tunnel
                        console.print(f"[green]Starting ngrok tunnel for port {mcp_port}...[/green]")
                        ngrok_tunnel = ngrok.connect(mcp_port, "http")
                        ngrok_url = ngrok_tunnel.public_url
                        mcp_endpoint_url = f"{ngrok_url}/mcp"
                        console.print(f"[bold green]✓[/bold green] Ngrok tunnel active: [cyan]{ngrok_url}[/cyan]")
                        console.print(f"[dim]MCP endpoint: {mcp_endpoint_url}[/dim]")
                        # Set environment variable so agent code can use it
                        import os
                        os.environ["MCP_ENDPOINT"] = mcp_endpoint_url
                    else:
                        console.print(f"[red]Installation failed:[/red] {result.stderr}")
                        raise ImportError("pyngrok installation failed")
                except Exception as e:
                    console.print(f"[red]Failed to install pyngrok:[/red] {e}")
                    console.print("[yellow]Please install manually: pip install pyngrok[/yellow]")
                    if not Confirm.ask("\n[bold yellow]Continue without ngrok?[/bold yellow] (remote agents won't work)", default=False):
                        raise typer.Exit(1)
                    ngrok = False
            else:
                if not Confirm.ask("\n[bold yellow]Continue without ngrok?[/bold yellow] (remote agents won't work)", default=False):
                    raise typer.Exit(1)
                ngrok = False
        except Exception as e:
            console.print(f"[red]Error starting ngrok:[/red] {e}")
            console.print("[yellow]Ngrok is required for remote agents to access your MCP server![/yellow]")
            if not Confirm.ask("\n[bold yellow]Continue without ngrok?[/bold yellow] (remote agents won't work)", default=False):
                raise typer.Exit(1)
            ngrok = False

    try:
        if watch:
            # Use watchfiles for auto-reload
            try:
                import asyncio
                from watchfiles import awatch

                # Capture ngrok variables in closure
                ngrok_tunnel_ref = [ngrok_tunnel]
                ngrok_url_ref = [ngrok_url]
                
                async def run_with_reload():
                    mcp_process = None
                    main_process = None
                    try:
                        while True:
                            # Terminate existing processes (only if they're still running)
                            if main_process and main_process.returncode is None:
                                main_process.terminate()
                                await asyncio.sleep(0.5)
                            if mcp_process and mcp_process.returncode is None:
                                mcp_process.terminate()
                                await asyncio.sleep(0.5)

                            # Start MCP server if needed (only if not already running)
                            if start_mcp and mcp_process is None:
                                console.print(f"[green]Starting MCP server on port {mcp_port}...[/green]")
                                # Set up environment with PYTHONPATH
                                import os
                                mcp_env = os.environ.copy()
                                src_path = str(project_root / "src")
                                if "PYTHONPATH" in mcp_env:
                                    mcp_env["PYTHONPATH"] = f"{src_path}{os.pathsep}{mcp_env['PYTHONPATH']}"
                                else:
                                    mcp_env["PYTHONPATH"] = src_path
                                # Start MCP server in background
                                mcp_process = await asyncio.create_subprocess_exec(
                                    sys.executable,
                                    "-m",
                                    "uvicorn",
                                    f"{mcp_module}:app",
                                    "--host",
                                    "0.0.0.0",
                                    "--port",
                                    str(mcp_port),
                                    "--reload",
                                    cwd=project_root,
                                    env=mcp_env,
                                    stdout=subprocess.DEVNULL,  # Suppress MCP server output
                                    stderr=subprocess.DEVNULL,
                                    start_new_session=True,  # Run in new session to prevent blocking
                                )
                                # Wait for MCP server to be ready - check if port is listening
                                import socket
                                max_retries = 20
                                server_ready = False
                                
                                console.print("[dim]Waiting for MCP server to start...[/dim]", end="")
                                for i in range(max_retries):
                                    try:
                                        # Check if port is open
                                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        sock.settimeout(0.5)
                                        result = sock.connect_ex(('localhost', mcp_port))
                                        sock.close()
                                        
                                        if result == 0:
                                            # Port is open, server is starting
                                            console.print(" [green]✓[/green]")
                                            await asyncio.sleep(3)  # Give server time to fully initialize
                                            server_ready = True
                                            break
                                    except Exception:
                                        pass
                                    
                                    if i < max_retries - 1:
                                        await asyncio.sleep(0.5)
                                        if i % 4 == 0:  # Show progress every 2 seconds
                                            console.print(".", end="")
                                
                                if not server_ready:
                                    console.print(" [yellow]⚠[/yellow]")
                                    console.print("[yellow]Warning:[/yellow] MCP server may not be ready, but continuing...")
                                else:
                                    console.print("[green]✓[/green] MCP server is ready")
                                
                                # Display connection info
                                table = Table(title="MCP Server Connection", show_header=False, box=None)
                                table.add_column("Type", style="cyan", no_wrap=True)
                                table.add_column("URL", style="white")
                                
                                table.add_row("Local", f"http://localhost:{mcp_port}/mcp")
                                if ngrok_url_ref[0]:
                                    mcp_endpoint = f"{ngrok_url_ref[0]}/mcp"
                                    table.add_row("Public (ngrok)", mcp_endpoint)
                                    # Set environment variable so agent code can use it
                                    import os
                                    os.environ["MCP_ENDPOINT"] = mcp_endpoint
                                
                                console.print()
                                console.print(table)
                                console.print()
                                
                                if ngrok_url_ref[0]:
                                    mcp_endpoint = f"{ngrok_url_ref[0]}/mcp"
                                    console.print("[bold yellow]⚠[/bold yellow] [bold]Public URL active![/bold] Your MCP server is accessible from the internet.")
                                    console.print(f"[dim]MCP endpoint (auto-configured): {mcp_endpoint}[/dim]")
                                    # Set environment variable so agent code automatically uses ngrok URL
                                    import os
                                    os.environ["MCP_ENDPOINT"] = mcp_endpoint

                            # Start main application
                            console.print("[green]Starting main application...[/green]")
                            # Pass environment with MCP_ENDPOINT if ngrok is active
                            import os
                            env = os.environ.copy()
                            # Add src directory to PYTHONPATH so Python can find the module
                            src_path = str(project_root / "src")
                            if "PYTHONPATH" in env:
                                env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
                            else:
                                env["PYTHONPATH"] = src_path
                            if ngrok_url_ref[0]:
                                env["MCP_ENDPOINT"] = f"{ngrok_url_ref[0]}/mcp"
                            
                            main_process = await asyncio.create_subprocess_exec(
                                sys.executable,
                                "-m",
                                main_module,
                                stdout=sys.stdout,
                                stderr=sys.stderr,
                                cwd=project_root,
                                env=env,
                            )

                            # Watch for file changes
                            async def watch_changes():
                                async for _changes in awatch(project_root / "src"):
                                    console.print("[yellow]Files changed, reloading...[/yellow]")
                                    if main_process:
                                        main_process.terminate()
                                    if mcp_process:
                                        mcp_process.terminate()
                                    return

                            # Wait for either process to finish or file changes
                            watch_task = asyncio.create_task(watch_changes())
                            process_task = asyncio.create_task(main_process.wait())

                            done, pending = await asyncio.wait(
                                [process_task, watch_task],
                                return_when=asyncio.FIRST_COMPLETED,
                            )

                            # Check which task completed
                            main_finished = False
                            file_changed = False
                            
                            for task in done:
                                if task == process_task:
                                    # Main process finished
                                    main_finished = True
                                    console.print("\n[green]✓[/green] Main application finished.")
                                    if start_mcp:
                                        # Only show MCP message if MCP server is actually running
                                        console.print("[cyan]MCP server and ngrok tunnel remain active for remote agents.[/cyan]")
                                        console.print("[dim]Press Ctrl+C to stop all services, or edit files to reload.[/dim]")
                                    else:
                                        console.print("[dim]Press Ctrl+C to stop, or edit files to reload.[/dim]")
                                elif task == watch_task:
                                    # File changed - restart everything
                                    file_changed = True
                            
                            if file_changed:
                                # File changed - restart everything
                                # Cancel pending tasks
                                for task in pending:
                                    task.cancel()
                                break
                            elif main_finished:
                                # Main finished - restart it after a short delay
                                # Cancel the watch_task since it's done, but keep MCP server running
                                for task in pending:
                                    task.cancel()
                                
                                # Main process finished, clear it so it can be restarted
                                main_process = None
                                # Small delay before restarting
                                await asyncio.sleep(1.0)
                                # Continue the loop to restart the main process
                                continue
                            
                            # Small delay before restart
                            await asyncio.sleep(0.5)

                    except KeyboardInterrupt:
                        console.print("\n[yellow]Stopping all services...[/yellow]")
                        # Terminate main process
                        if main_process:
                            try:
                                main_process.terminate()
                                await asyncio.sleep(0.5)
                                if main_process.returncode is None:
                                    main_process.kill()
                            except Exception:
                                pass
                        # Terminate MCP server
                        if mcp_process:
                            try:
                                mcp_process.terminate()
                                await asyncio.sleep(0.5)
                                if mcp_process.returncode is None:
                                    mcp_process.kill()
                            except Exception:
                                pass
                        # Disconnect ngrok tunnel
                        if ngrok_tunnel_ref[0]:
                            try:
                                from pyngrok import ngrok
                                ngrok.disconnect(ngrok_tunnel_ref[0].public_url)
                                console.print("[dim]Ngrok tunnel closed[/dim]")
                            except Exception:
                                pass
                        console.print("[green]✓[/green] All services stopped")

                asyncio.run(run_with_reload())
            except ImportError:
                # Fallback to simple mode without watchfiles
                console.print("[yellow]watchfiles not available, using simple mode[/yellow]")
                
                # Start MCP server if needed
                if start_mcp:
                    console.print(f"[green]Starting MCP server on port {mcp_port}...[/green]")
                    # Set up environment with PYTHONPATH
                    import os
                    mcp_env = os.environ.copy()
                    src_path = str(project_root / "src")
                    if "PYTHONPATH" in mcp_env:
                        mcp_env["PYTHONPATH"] = f"{src_path}{os.pathsep}{mcp_env['PYTHONPATH']}"
                    else:
                        mcp_env["PYTHONPATH"] = src_path
                    mcp_proc = subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "uvicorn",
                            f"{mcp_module}:app",
                            "--host",
                            "0.0.0.0",
                            "--port",
                            str(mcp_port),
                        ],
                        cwd=project_root,
                        env=mcp_env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    import time
                    time.sleep(5)  # Give MCP server time to start
                    # Wait for MCP server to be ready - check if port is listening
                    import socket
                    max_retries = 20
                    server_ready = False
                    for i in range(max_retries):
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(0.5)
                            result = sock.connect_ex(('localhost', mcp_port))
                            sock.close()
                            if result == 0:
                                # Port is open, wait a bit more for server to fully initialize
                                time.sleep(1)
                                server_ready = True
                                break
                        except Exception:
                            pass
                        if i < max_retries - 1:
                            time.sleep(0.5)
                    
                    if not server_ready:
                        console.print("[yellow]Warning:[/yellow] MCP server may not be ready yet, but continuing...")
                    else:
                        console.print("[green]✓[/green] MCP server is ready")
                
                # Run main application
                try:
                    # Pass environment with MCP_ENDPOINT if ngrok is active
                    import os
                    env = os.environ.copy()
                    # Add src directory to PYTHONPATH so Python can find the module
                    src_path = str(project_root / "src")
                    if "PYTHONPATH" in env:
                        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
                    else:
                        env["PYTHONPATH"] = src_path
                    if ngrok_url:
                        env["MCP_ENDPOINT"] = f"{ngrok_url}/mcp"
                    subprocess.run([sys.executable, "-m", main_module], cwd=project_root, env=env)
                finally:
                    if start_mcp and mcp_proc:
                        mcp_proc.terminate()
        else:
            # No watch mode - start MCP server and run main app
            if start_mcp:
                console.print(f"[green]Starting MCP server on port {mcp_port}...[/green]")
                # Set up environment with PYTHONPATH
                import os
                mcp_env = os.environ.copy()
                src_path = str(project_root / "src")
                if "PYTHONPATH" in mcp_env:
                    mcp_env["PYTHONPATH"] = f"{src_path}{os.pathsep}{mcp_env['PYTHONPATH']}"
                else:
                    mcp_env["PYTHONPATH"] = src_path
                mcp_proc = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        f"{mcp_module}:app",
                        "--host",
                        "0.0.0.0",
                        "--port",
                        str(mcp_port),
                    ],
                    cwd=project_root,
                    env=mcp_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,  # Run in new session to prevent blocking
                )
                import time
                time.sleep(2)  # Give MCP server a moment to start
                # Wait for MCP server to be ready
                try:
                    import httpx
                    max_retries = 10
                    for i in range(max_retries):
                        try:
                            response = httpx.get(f"http://localhost:{mcp_port}/mcp", timeout=1.0)
                            if response.status_code in (200, 404):  # 404 is OK for MCP endpoint
                                break
                        except Exception:
                            if i < max_retries - 1:
                                time.sleep(0.5)
                            else:
                                console.print("[yellow]Warning:[/yellow] MCP server may not be ready yet")
                    else:
                        console.print("[yellow]Warning:[/yellow] MCP server health check failed, but continuing...")
                except ImportError:
                    console.print("[dim]httpx not available, skipping health check[/dim]")
            
            try:
                # Set up environment with PYTHONPATH
                import os
                env = os.environ.copy()
                # Add src directory to PYTHONPATH so Python can find the module
                src_path = str(project_root / "src")
                if "PYTHONPATH" in env:
                    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
                else:
                    env["PYTHONPATH"] = src_path
                subprocess.run([sys.executable, "-m", main_module], cwd=project_root, env=env)
            finally:
                if start_mcp and mcp_proc:
                    mcp_proc.terminate()

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping all services...[/yellow]")
        # Terminate MCP server if running
        if start_mcp and 'mcp_proc' in locals() and mcp_proc:
            try:
                mcp_proc.terminate()
                import time
                time.sleep(0.5)
                if mcp_proc.poll() is None:
                    mcp_proc.kill()
            except Exception:
                pass
        # Disconnect ngrok tunnel
        if ngrok_tunnel:
            try:
                from pyngrok import ngrok
                ngrok.disconnect(ngrok_tunnel.public_url)
                console.print("[dim]Ngrok tunnel closed[/dim]")
            except Exception:
                pass
        console.print("[green]✓[/green] All services stopped")
        raise typer.Exit(130)
    except Exception as e:
        if ngrok_tunnel:
            try:
                from pyngrok import ngrok
                ngrok.disconnect(ngrok_tunnel.public_url)
            except Exception:
                pass
        console.print(f"[red]Error running dev server:[/red] {e}")
        raise typer.Exit(1)

