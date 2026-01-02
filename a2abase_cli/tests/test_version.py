"""Tests for commands/version.py."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from a2abase_cli.commands.version import get_sdk_version, version_command


def _mock_import(name, *args, **kwargs):
    """Mock import function."""
    if name == "a2abase":
        raise ImportError()
    return __import__(name, *args, **kwargs)


def test_get_sdk_version_installed():
    """Test get_sdk_version when SDK is installed."""
    mock_module = MagicMock()
    mock_module.__version__ = "1.0.0"
    with patch("builtins.__import__", return_value=mock_module):
        version = get_sdk_version()
        assert version == "1.0.0"


def test_get_sdk_version_not_installed():
    """Test get_sdk_version when SDK is not installed."""
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("pathlib.Path.cwd", return_value=Path("/nonexistent")):
            version = get_sdk_version()
            assert version == "not installed"


def test_get_sdk_version_from_pyproject(temp_dir):
    """Test get_sdk_version when reading from pyproject.toml."""
    pyproject = temp_dir / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "2.0.0"\n')
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        # Allow tomli import
        if name == "tomli":
            mock_tomli = MagicMock()
            mock_tomli.load.return_value = {"project": {"version": "2.0.0"}}
            return mock_tomli
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("pathlib.Path.cwd", return_value=temp_dir):
            version = get_sdk_version()
            assert version == "2.0.0"


def test_get_sdk_version_unknown():
    """Test get_sdk_version when version is unknown."""
    mock_module = MagicMock()
    # Remove __version__ attribute
    if hasattr(mock_module, "__version__"):
        delattr(mock_module, "__version__")
    with patch("builtins.__import__", return_value=mock_module):
        version = get_sdk_version()
        assert version == "unknown"


def test_version_command():
    """Test version_command."""
    with patch("a2abase_cli.commands.version.console") as mock_console:
        with patch("a2abase_cli.commands.version.get_sdk_version", return_value="1.0.0"):
            version_command()
            mock_console.print.assert_called_once()

