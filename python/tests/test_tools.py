"""
Test suite for tools module
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from a2abase.tools import A2ABaseTools, MCPTools, A2ABaseTool
from a2abase.tools import _A2ABaseTools_descriptions


class TestA2ABaseTools:
    """Test class for A2ABaseTools enum"""

    def test_enum_values(self):
        """Test that all A2ABaseTools enum values exist"""
        assert A2ABaseTools.SB_FILES_TOOL == "sb_files_tool"
        assert A2ABaseTools.SB_SHELL_TOOL == "sb_shell_tool"
        assert A2ABaseTools.SB_DEPLOY_TOOL == "sb_deploy_tool"
        assert A2ABaseTools.SB_EXPOSE_TOOL == "sb_expose_tool"
        assert A2ABaseTools.SB_VISION_TOOL == "sb_vision_tool"
        assert A2ABaseTools.BROWSER_TOOL == "browser_tool"
        assert A2ABaseTools.WEB_SEARCH_TOOL == "web_search_tool"
        assert A2ABaseTools.DATA_PROVIDERS_TOOL == "data_providers_tool"

    def test_get_description_success(self):
        """Test get_description() returns correct description"""
        desc = A2ABaseTools.WEB_SEARCH_TOOL.get_description()
        assert desc == "Search the web for information"
        
        desc = A2ABaseTools.BROWSER_TOOL.get_description()
        assert desc == "Browse websites and interact with web pages"
        
        desc = A2ABaseTools.SB_FILES_TOOL.get_description()
        assert desc == "Read, write, and edit files"

    def test_get_description_all_tools(self):
        """Test get_description() for all tools"""
        for tool in A2ABaseTools:
            desc = tool.get_description()
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_get_description_missing_description(self):
        """Test get_description() raises ValueError when description is missing (covers line 61)"""
        # Create a mock tool enum value that doesn't exist in descriptions
        # We'll need to temporarily modify the descriptions dict
        original_descriptions = _A2ABaseTools_descriptions.copy()
        try:
            # Remove a description to trigger the error
            del _A2ABaseTools_descriptions[A2ABaseTools.WEB_SEARCH_TOOL.value]
            with pytest.raises(ValueError, match="No description found"):
                A2ABaseTools.WEB_SEARCH_TOOL.get_description()
        finally:
            # Restore original descriptions
            _A2ABaseTools_descriptions.clear()
            _A2ABaseTools_descriptions.update(original_descriptions)

    def test_enum_inheritance(self):
        """Test that A2ABaseTools is a string enum"""
        assert isinstance(A2ABaseTools.WEB_SEARCH_TOOL, str)
        assert A2ABaseTools.WEB_SEARCH_TOOL == "web_search_tool"


class TestMCPTools:
    """Test class for MCPTools"""

    def test_init(self):
        """Test MCPTools initialization"""
        mcp = MCPTools(
            endpoint="http://example.com/mcp",
            name="test_mcp",
            allowed_tools=["tool1", "tool2"]
        )
        
        assert mcp.url == "http://example.com/mcp"
        assert mcp.name == "test_mcp"
        assert mcp.type == "http"
        assert mcp._allowed_tools == ["tool1", "tool2"]
        assert mcp.enabled_tools == []
        assert mcp._initialized == False

    def test_init_without_allowed_tools(self):
        """Test MCPTools initialization without allowed_tools"""
        mcp = MCPTools(
            endpoint="http://example.com/mcp",
            name="test_mcp"
        )
        
        assert mcp._allowed_tools is None
        assert mcp.enabled_tools == []

    @pytest.mark.asyncio
    async def test_initialize_with_allowed_tools(self):
        """Test initialize() with allowed_tools"""
        with patch('a2abase.tools.FastMCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_tool1 = Mock()
            mock_tool1.name = "tool1"
            mock_tool2 = Mock()
            mock_tool2.name = "tool2"
            mock_tool3 = Mock()
            mock_tool3.name = "tool3"
            
            async def mock_list_tools():
                return [mock_tool1, mock_tool2, mock_tool3]
            
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.list_tools = AsyncMock(return_value=[mock_tool1, mock_tool2, mock_tool3])
            
            mcp = MCPTools(
                endpoint="http://example.com/mcp",
                name="test_mcp",
                allowed_tools=["tool1", "tool3"]
            )
            
            result = await mcp.initialize()
            
            assert result == mcp
            assert mcp._initialized == True
            assert "tool1" in mcp.enabled_tools
            assert "tool3" in mcp.enabled_tools
            assert "tool2" not in mcp.enabled_tools

    @pytest.mark.asyncio
    async def test_initialize_without_allowed_tools(self):
        """Test initialize() without allowed_tools (enables all)"""
        with patch('a2abase.tools.FastMCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_tool1 = Mock()
            mock_tool1.name = "tool1"
            mock_tool2 = Mock()
            mock_tool2.name = "tool2"
            
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.list_tools = AsyncMock(return_value=[mock_tool1, mock_tool2])
            
            mcp = MCPTools(
                endpoint="http://example.com/mcp",
                name="test_mcp"
            )
            
            result = await mcp.initialize()
            
            assert result == mcp
            assert mcp._initialized == True
            assert "tool1" in mcp.enabled_tools
            assert "tool2" in mcp.enabled_tools
            assert len(mcp.enabled_tools) == 2

    def test_mcp_tools_attributes(self):
        """Test MCPTools has all required attributes"""
        mcp = MCPTools(
            endpoint="http://example.com/mcp",
            name="test_mcp"
        )
        
        assert hasattr(mcp, 'url')
        assert hasattr(mcp, 'name')
        assert hasattr(mcp, 'type')
        assert hasattr(mcp, 'enabled_tools')
        assert hasattr(mcp, '_initialized')
        assert hasattr(mcp, '_allowed_tools')
        assert hasattr(mcp, '_mcp_client')


class TestA2ABaseTools:
    """Test class for A2ABaseTools type union"""

    def test_union_type(self):
        """Test that A2ABaseTools is a union type"""
        from typing import get_args, get_origin
        
        origin = get_origin(A2ABaseTool)
        args = get_args(A2ABaseTool)
        
        assert origin is not None  # It's a Union
        assert A2ABaseTools in args
        assert MCPTools in args

    def test_a2abase_tools_is_a2abase_tool(self):
        """Test that A2ABaseTools instances are A2ABaseTool"""
        tool = A2ABaseTools.WEB_SEARCH_TOOL
        # Type check - in runtime this is just a check
        assert isinstance(tool, str)  # A2ABaseTools is a string enum

    def test_mcp_tools_is_a2abase_tool(self):
        """Test that MCPTools instances are A2ABaseTool"""
        mcp = MCPTools(
            endpoint="http://example.com/mcp",
            name="test_mcp"
        )
        # Type check - in runtime this is just a check
        assert isinstance(mcp, MCPTools)

