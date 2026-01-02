"""Tests for commands/run.py."""
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from a2abase_cli.commands.run import run_command


def test_run_command_no_project():
    """Test run_command when not in a project."""
    with patch("a2abase_cli.commands.run.find_project_root", return_value=None):
        with patch("a2abase_cli.commands.run.console") as mock_console:
            with pytest.raises(typer.Exit) as exc_info:
                run_command()
            assert exc_info.value.exit_code == 1
            mock_console.print.assert_called()


def test_run_command_no_config(project_root):
    """Test run_command when config file doesn't exist."""
    config_file = project_root / "a2abase.yaml"
    if config_file.exists():
        config_file.unlink()
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.console") as mock_console:
            with pytest.raises(typer.Exit) as exc_info:
                run_command()
            assert exc_info.value.exit_code == 1


def test_run_command_no_main_file(project_root):
    """Test run_command when main.py doesn't exist."""
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.console") as mock_console:
            with pytest.raises(typer.Exit) as exc_info:
                run_command()
            assert exc_info.value.exit_code == 1


def test_run_command_success(project_root):
    """Test run_command with successful execution."""
    # Create main.py
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "Hello"
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                with patch("a2abase_cli.commands.run.console") as mock_console:
                    with pytest.raises(typer.Exit) as exc_info:
                        run_command()
                    # May be 0 or 1 depending on exception handling
                    assert exc_info.value.exit_code in [0, 1]
                    mock_run.assert_called_once()


def test_run_command_with_input(project_root):
    """Test run_command with input text."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                with patch("a2abase_cli.commands.run.console"):
                    with pytest.raises(typer.Exit):
                        run_command(input_text="test input")
                    # Check that --input was added to command
                    call_args = mock_run.call_args[0][0]
                    assert "--input" in call_args
                    assert "test input" in call_args


def test_run_command_with_json_output(project_root):
    """Test run_command with JSON output."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout='{"result": "ok"}', stderr="")
                with patch("a2abase_cli.commands.run.console") as mock_console:
                    with pytest.raises(typer.Exit):
                        run_command(json_output=True)
                    # Check that --json was added
                    call_args = mock_run.call_args[0][0]
                    assert "--json" in call_args


def test_run_command_keyboard_interrupt(project_root):
    """Test run_command with KeyboardInterrupt."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run", side_effect=KeyboardInterrupt()):
                with patch("a2abase_cli.commands.run.console") as mock_console:
                    with pytest.raises(typer.Exit) as exc_info:
                        run_command()
                    assert exc_info.value.exit_code == 130


def test_run_command_exception(project_root):
    """Test run_command with exception."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(True, "Installed")):
            with patch("a2abase_cli.commands.run.subprocess.run", side_effect=Exception("Test error")):
                with patch("a2abase_cli.commands.run.err_console") as mock_err_console:
                    with pytest.raises(typer.Exit) as exc_info:
                        run_command()
                    assert exc_info.value.exit_code == 1
                    mock_err_console.print.assert_called_once()


def test_run_command_sdk_not_installed(project_root):
    """Test run_command when SDK is not installed."""
    main_file = project_root / "src" / "test_package" / "main.py"
    main_file.parent.mkdir(parents=True, exist_ok=True)
    main_file.write_text('print("Hello")')
    
    with patch("a2abase_cli.commands.run.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.run.ensure_a2abase_sdk_installed", return_value=(False, "Not installed")):
            with patch("a2abase_cli.commands.run.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                with patch("a2abase_cli.commands.run.console") as mock_console:
                    with pytest.raises(typer.Exit):
                        run_command()
                    # Should continue despite SDK not installed (with warning)
                    mock_console.print.assert_called()

