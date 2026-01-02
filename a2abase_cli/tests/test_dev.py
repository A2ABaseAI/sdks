"""Tests for commands/dev.py."""
import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from a2abase_cli.commands.dev import dev_command


def test_dev_command_no_project():
    """Test dev_command when not in a project."""
    with patch("a2abase_cli.commands.dev.find_project_root", return_value=None):
        with patch("a2abase_cli.commands.dev.console") as mock_console:
            with pytest.raises(typer.Exit):
                dev_command()
            mock_console.print.assert_called()


def test_dev_command_basic_template(project_root):
    """Test dev_command with basic template."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    def mock_asyncio_run(coro):
        # Immediately raise KeyboardInterrupt to exit the async function
        raise KeyboardInterrupt()
    
    with patch("a2abase_cli.commands.dev.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.dev.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            # Patch asyncio.run in the asyncio module (where it will be imported)
            with patch.object(asyncio, "run", side_effect=mock_asyncio_run):
                with patch("a2abase_cli.commands.dev.console"):
                    try:
                        dev_command()
                    except typer.Exit:
                        pass  # Expected - KeyboardInterrupt is converted to typer.Exit(130)


def test_dev_command_advanced_template_no_mcp(project_root):
    """Test dev_command with advanced template but no MCP."""
    import yaml
    
    config_file = project_root / "a2abase.yaml"
    with open(config_file, "w") as f:
        yaml.dump({"template": "advanced", "package_name": "test_package"}, f)
    
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    def mock_asyncio_run(coro):
        # Immediately raise KeyboardInterrupt to exit the async function
        raise KeyboardInterrupt()
    
    with patch("a2abase_cli.commands.dev.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.dev.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            # Patch asyncio.run in the asyncio module (where it will be imported)
            with patch.object(asyncio, "run", side_effect=mock_asyncio_run):
                with patch("a2abase_cli.commands.dev.console"):
                    try:
                        dev_command(no_mcp=True)
                    except typer.Exit:
                        pass  # Expected - KeyboardInterrupt is converted to typer.Exit(130)


def test_dev_command_basic_template_with_mcp_flags(project_root):
    """Test dev_command with basic template but MCP flags (should error)."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.dev.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.dev.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.dev.console") as mock_console:
                with pytest.raises(typer.Exit):
                    dev_command(ngrok_auth_token="test_token")
                mock_console.print.assert_called()


def test_dev_command_no_main_file(project_root):
    """Test dev_command when main.py doesn't exist."""
    with patch("a2abase_cli.commands.dev.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.dev.console") as mock_console:
            with pytest.raises(typer.Exit):
                dev_command()
            mock_console.print.assert_called()


def test_dev_command_error_reading_config(project_root):
    """Test dev_command when config file is invalid."""
    config_file = project_root / "a2abase.yaml"
    config_file.write_text("invalid: yaml: content")
    
    with patch("a2abase_cli.commands.dev.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.dev.console") as mock_console:
            with pytest.raises(typer.Exit):
                dev_command()
            mock_console.print.assert_called()

