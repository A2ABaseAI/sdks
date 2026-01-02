"""Tests for commands/doctor.py."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from a2abase_cli.commands.doctor import (
    check_config,
    check_dependencies,
    check_package_manager,
    check_python_version,
    check_venv,
    check_write_permissions,
    doctor_command,
)


def test_check_python_version_valid():
    """Test check_python_version with valid version."""
    with patch("sys.version_info", MagicMock(major=3, minor=11, micro=0)):
        ok, details = check_python_version()
        assert ok is True
        assert "3.11" in details


def test_check_python_version_invalid():
    """Test check_python_version with invalid version."""
    with patch("sys.version_info", MagicMock(major=3, minor=10, micro=0)):
        ok, details = check_python_version()
        assert ok is False
        assert "requires 3.11+" in details


def test_check_venv_in_venv():
    """Test check_venv when in virtual environment."""
    with patch("sys.real_prefix", "/venv", create=True):
        ok, details = check_venv()
        assert ok is True
        assert details == sys.prefix


def test_check_venv_not_in_venv():
    """Test check_venv when not in virtual environment."""
    # Remove real_prefix attribute if it exists
    real_prefix_attr = getattr(sys, "real_prefix", None)
    if hasattr(sys, "real_prefix"):
        delattr(sys, "real_prefix")
    
    try:
        # Set base_prefix to same as prefix (not in venv)
        original_base_prefix = sys.base_prefix
        sys.base_prefix = sys.prefix
        
        ok, details = check_venv()
        assert ok is False
        assert "Not in" in details
    finally:
        # Restore
        sys.base_prefix = original_base_prefix
        if real_prefix_attr is not None:
            sys.real_prefix = real_prefix_attr


def test_check_dependencies():
    """Test check_dependencies."""
    results = check_dependencies()
    assert len(results) > 0
    # Should check for typer, rich, etc.
    dep_names = [r[0] for r in results]
    assert "typer" in dep_names


def test_check_config_valid(project_root):
    """Test check_config with valid config."""
    ok, details = check_config(project_root)
    assert ok is True
    assert details == "Valid"


def test_check_config_invalid(project_root):
    """Test check_config with invalid config."""
    config_file = project_root / "a2abase.yaml"
    config_file.write_text("invalid: yaml: content")
    
    ok, details = check_config(project_root)
    assert ok is False
    assert "Invalid" in details


def test_check_config_not_found(temp_dir):
    """Test check_config when config file doesn't exist."""
    project_root = temp_dir / "project"
    project_root.mkdir()
    
    ok, details = check_config(project_root)
    assert ok is False
    assert "not found" in details


def test_check_write_permissions(project_root):
    """Test check_write_permissions."""
    ok, details = check_write_permissions(project_root)
    assert ok is True
    assert "Writable" in details


def test_check_package_manager_uv():
    """Test check_package_manager when uv is available."""
    with patch("shutil.which") as mock_which:
        mock_which.side_effect = lambda cmd: "/usr/bin/uv" if cmd == "uv" else None
        ok, pm_name, details = check_package_manager()
        assert ok is True
        assert pm_name == "uv"


def test_check_package_manager_pip():
    """Test check_package_manager when only pip is available."""
    with patch("shutil.which") as mock_which:
        mock_which.side_effect = lambda cmd: "/usr/bin/pip" if cmd == "pip" else None
        ok, pm_name, details = check_package_manager()
        assert ok is True
        assert pm_name == "pip"


def test_check_package_manager_none():
    """Test check_package_manager when neither is available."""
    with patch("shutil.which", return_value=None):
        ok, pm_name, details = check_package_manager()
        assert ok is False
        assert pm_name == "none"


def test_doctor_command_success(project_root):
    """Test doctor_command with all checks passing."""
    with patch("a2abase_cli.commands.doctor.console") as mock_console:
        with patch("a2abase_cli.commands.doctor.find_project_root", return_value=project_root):
            with patch("a2abase_cli.commands.doctor.check_python_version", return_value=(True, "3.11")):
                with patch("a2abase_cli.commands.doctor.check_venv", return_value=(True, "/venv")):
                    with patch("a2abase_cli.commands.doctor.check_dependencies", return_value=[("typer", True, "Installed")]):
                        with patch("a2abase_cli.commands.doctor.check_config", return_value=(True, "Valid")):
                            with patch("a2abase_cli.commands.doctor.check_write_permissions", return_value=(True, "Writable")):
                                with patch("a2abase_cli.commands.doctor.check_package_manager", return_value=(True, "pip", "Available")):
                                    with pytest.raises(typer.Exit) as exc_info:
                                        doctor_command()
                                    assert exc_info.value.exit_code == 0


def test_doctor_command_with_issues(project_root):
    """Test doctor_command with issues found."""
    with patch("a2abase_cli.commands.doctor.console") as mock_console:
        with patch("a2abase_cli.commands.doctor.find_project_root", return_value=project_root):
            with patch("a2abase_cli.commands.doctor.check_python_version", return_value=(False, "3.10")):
                with patch("a2abase_cli.commands.doctor.check_venv", return_value=(False, "Not in venv")):
                    with patch("a2abase_cli.commands.doctor.check_dependencies", return_value=[("typer", False, "Not installed")]):
                        with patch("a2abase_cli.commands.doctor.check_config", return_value=(True, "Valid")):
                            with patch("a2abase_cli.commands.doctor.check_write_permissions", return_value=(True, "Writable")):
                                with patch("a2abase_cli.commands.doctor.check_package_manager", return_value=(True, "pip", "Available")):
                                    with pytest.raises(typer.Exit) as exc_info:
                                        doctor_command()
                                    assert exc_info.value.exit_code == 1


def test_doctor_command_no_project():
    """Test doctor_command when not in a project."""
    with patch("a2abase_cli.commands.doctor.console") as mock_console:
        with patch("a2abase_cli.commands.doctor.find_project_root", return_value=None):
            with patch("a2abase_cli.commands.doctor.check_python_version", return_value=(True, "3.11")):
                with patch("a2abase_cli.commands.doctor.check_venv", return_value=(True, "/venv")):
                    with patch("a2abase_cli.commands.doctor.check_dependencies", return_value=[("typer", True, "Installed")]):
                        with patch("a2abase_cli.commands.doctor.check_package_manager", return_value=(True, "pip", "Available")):
                            with pytest.raises(typer.Exit) as exc_info:
                                doctor_command()
                            assert exc_info.value.exit_code == 1

