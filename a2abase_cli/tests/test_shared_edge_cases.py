"""Edge case tests for generators/shared.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from a2abase_cli.generators.shared import (
    ensure_a2abase_sdk_installed,
    render_template,
    safe_write,
    update_agent_with_tool,
)


def test_safe_write_parent_creation(temp_dir):
    """Test safe_write creates parent directories."""
    file_path = temp_dir / "deep" / "nested" / "file.txt"
    safe_write(file_path, "content", force=True)
    assert file_path.exists()
    assert file_path.read_text() == "content"


def test_render_template_with_variables():
    """Test render_template with multiple variables."""
    template = "Hello {{ name }}, you are {{ age }} years old!"
    result = render_template(template, name="Alice", age=30)
    assert result == "Hello Alice, you are 30 years old!"


def test_update_agent_with_tool_no_a2abase_tools_line(temp_dir):
    """Test update_agent_with_tool when a2abase_tools line doesn't exist."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test agent."""\nfrom a2abase import Agent\n\n# Option 2:\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_with_mcp_comment(temp_dir):
    """Test update_agent_with_tool with MCP comment section."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test agent."""\nallowed_tools=["tool1"]\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_empty_mcp_list(temp_dir):
    """Test update_agent_with_tool with empty MCP tools list."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test agent."""\nallowed_tools=[]\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_ensure_a2abase_sdk_installed_exception(temp_dir):
    """Test ensure_a2abase_sdk_installed with exception during install."""
    project_root = temp_dir / "project"
    project_root.mkdir()
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase":
            raise ImportError()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        with patch("a2abase_cli.generators.shared.subprocess.run", side_effect=Exception("Unexpected error")):
            success, message = ensure_a2abase_sdk_installed(project_root, auto_install=True)
            assert success is False
            assert "Error" in message

