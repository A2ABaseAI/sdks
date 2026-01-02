"""Tests for update_agent_with_tool edge cases."""
from pathlib import Path

from a2abase_cli.generators.shared import update_agent_with_tool


def test_update_agent_with_tool_no_docstring(temp_dir):
    """Test update_agent_with_tool when file has no docstring."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text("from a2abase import Agent\n")
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_with_sdk_import(temp_dir):
    """Test update_agent_with_tool with SDK import pattern."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test."""\nfrom a2abase import Agent\nfrom a2abase.tools import A2ABaseTools\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_with_existing_tool_import(temp_dir):
    """Test update_agent_with_tool with existing tool import."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test."""\nfrom test_package.tools.other_tool import OTHER_TOOL_SCHEMA\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_mcp_list_with_tool(temp_dir):
    """Test update_agent_with_tool when tool already in MCP list."""
    agent_file = temp_dir / "test_agent.py"
    # Need to also have the import for it to be considered "already registered"
    agent_file.write_text('"""Test."""\nfrom test_package.tools.test_tool import TEST_TOOL_SCHEMA\nallowed_tools=["test_tool"]\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    # Should return False since already imported and registered
    assert result is False


def test_update_agent_with_tool_mcp_list_empty(temp_dir):
    """Test update_agent_with_tool with empty MCP list."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test."""\nallowed_tools=[]\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_mcp_list_with_comma(temp_dir):
    """Test update_agent_with_tool with MCP list that has trailing comma."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test."""\nallowed_tools=["tool1",]\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    assert isinstance(result, bool)


def test_update_agent_with_tool_already_imported_and_registered(temp_dir):
    """Test update_agent_with_tool when tool is already imported and registered."""
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('"""Test."""\nfrom test_package.tools.test_tool import TEST_TOOL_SCHEMA\nallowed_tools=["test_tool"]\n')
    
    result = update_agent_with_tool(agent_file, "test_tool", "TEST_TOOL_SCHEMA", "test_package")
    # Should return False since already done
    assert result is False

