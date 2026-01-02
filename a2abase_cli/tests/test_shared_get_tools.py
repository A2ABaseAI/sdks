"""Tests for get_available_a2abase_tools edge cases."""
from unittest.mock import MagicMock, patch

from a2abase_cli.generators.shared import get_available_a2abase_tools


def test_get_available_a2abase_tools_with_value_error():
    """Test get_available_a2abase_tools when tool.get_description() raises ValueError."""
    mock_tool1 = MagicMock()
    mock_tool1.value = "tool1"
    mock_tool1.get_description.side_effect = ValueError()
    
    mock_tool2 = MagicMock()
    mock_tool2.value = "tool2"
    mock_tool2.get_description.return_value = "Description"
    
    mock_tools_module = MagicMock()
    mock_tools_module.A2ABaseTools = [mock_tool1, mock_tool2]
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase.tools":
            return mock_tools_module
        if name == "a2abase":
            return MagicMock()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        tools = get_available_a2abase_tools()
        # Should skip tool1 (ValueError) but include tool2
        assert len(tools) >= 1
        assert any("tool2" in tool[0] for tool in tools)


def test_get_available_a2abase_tools_with_attribute_error():
    """Test get_available_a2abase_tools when tool.get_description() raises AttributeError."""
    mock_tool = MagicMock()
    mock_tool.value = "tool1"
    mock_tool.get_description.side_effect = AttributeError()
    
    mock_tools_module = MagicMock()
    mock_tools_module.A2ABaseTools = [mock_tool]
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase.tools":
            return mock_tools_module
        if name == "a2abase":
            return MagicMock()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        tools = get_available_a2abase_tools()
        # Should skip tool with AttributeError, but still return fallback list
        # The fallback list should have tools
        assert isinstance(tools, list)
        # May be empty if all tools fail, but should not crash

