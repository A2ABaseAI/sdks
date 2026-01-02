"""Edge case tests for commands/version.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from a2abase_cli.commands.version import get_sdk_version, version_command


def test_get_sdk_version_pyproject_not_found():
    """Test get_sdk_version when pyproject.toml doesn't exist."""
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("pathlib.Path.cwd", return_value=Path("/nonexistent")):
            version = get_sdk_version()
            assert version == "not installed"


def test_get_sdk_version_pyproject_tomli_error(temp_dir):
    """Test get_sdk_version when tomli fails."""
    pyproject = temp_dir / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "2.0.0"\n')
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        if name == "tomli":
            raise ImportError()  # tomli not available
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("pathlib.Path.cwd", return_value=temp_dir):
            version = get_sdk_version()
            assert version == "not installed"


def test_version_command():
    """Test version_command execution."""
    with patch("a2abase_cli.commands.version.console") as mock_console:
        with patch("a2abase_cli.commands.version.get_sdk_version", return_value="1.0.0"):
            version_command()
            mock_console.print.assert_called_once()

