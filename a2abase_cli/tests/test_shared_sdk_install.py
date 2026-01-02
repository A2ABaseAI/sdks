"""Tests for ensure_a2abase_sdk_installed edge cases."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from a2abase_cli.generators.shared import ensure_a2abase_sdk_installed


def test_ensure_a2abase_sdk_installed_config_yaml_error(temp_dir):
    """Test ensure_a2abase_sdk_installed when config YAML has error."""
    project_root = temp_dir / "project"
    project_root.mkdir()
    config_file = project_root / "a2abase.yaml"
    config_file.write_text("invalid: yaml: [")
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("a2abase_cli.generators.shared.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            success, message = ensure_a2abase_sdk_installed(project_root, auto_install=True)
            # Should fall back to pip when yaml error occurs
            assert success is True
            # Verify pip was called (not uv)
            call_args = mock_run.call_args[0][0]
            assert "pip" in str(call_args) or "-m" in call_args


def test_ensure_a2abase_sdk_installed_config_no_package_manager(temp_dir):
    """Test ensure_a2abase_sdk_installed when config has no package_manager."""
    project_root = temp_dir / "project"
    project_root.mkdir()
    config_file = project_root / "a2abase.yaml"
    with open(config_file, "w") as f:
        yaml.dump({"template": "basic"}, f)  # No package_manager
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("a2abase_cli.generators.shared.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            success, message = ensure_a2abase_sdk_installed(project_root, auto_install=True)
            assert success is True
            # Should default to pip
            call_args = mock_run.call_args[0][0]
            assert "pip" in str(call_args) or "-m" in call_args

