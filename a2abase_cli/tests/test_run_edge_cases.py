"""Edge case tests for commands/run.py."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from a2abase_cli.commands.run import run_command


def test_run_command_json_output_invalid_json(project_root):
    """Test run_command with JSON output but invalid JSON."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "not json"
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                
                with patch("a2abase_cli.commands.run.console") as mock_console:
                    with pytest.raises(typer.Exit):
                        run_command(json_output=True)
                    # Should print stdout when JSON decode fails
                    mock_console.print.assert_called()


def test_run_command_with_stderr(project_root):
    """Test run_command with stderr output."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "output"
                mock_result.stderr = "error"
                mock_run.return_value = mock_result
                
                with patch("a2abase_cli.commands.run.console"):
                    with patch("a2abase_cli.commands.run.err_console") as mock_err_console:
                        with pytest.raises(typer.Exit):
                            run_command()
                        mock_err_console.print.assert_called()


def test_run_command_sdk_installed_successfully(project_root):
    """Test run_command when SDK is installed successfully."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "installed successfully")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                
                with patch("a2abase_cli.commands.run.console"):
                    with pytest.raises(typer.Exit):
                        run_command()


def test_run_command_pythonpath_exists(project_root):
    """Test run_command when PYTHONPATH already exists."""
    import os
    
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                
                with patch.dict(os.environ, {"PYTHONPATH": "/existing/path"}):
                    with patch("a2abase_cli.commands.run.console"):
                        with pytest.raises(typer.Exit):
                            run_command()
                    
                    # Verify PYTHONPATH was updated
                    call_kwargs = mock_run.call_args[1]
                    env = call_kwargs.get("env", {})
                    assert "PYTHONPATH" in env
                    assert str(project_root / "src") in env["PYTHONPATH"]


def test_run_command_config_error(project_root):
    """Test run_command when config file has error."""
    config_file = project_root / "a2abase.yaml"
    config_file.write_text("invalid: yaml: content: [")
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.console") as mock_console:
            with pytest.raises(typer.Exit):
                run_command()
            mock_console.print.assert_called()

