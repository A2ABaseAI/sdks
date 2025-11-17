"""
Test suite for api/agents.py - Comprehensive coverage of all classes and functions
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from a2abase.api.agents import (
    MCPConfig,
    CustomMCP,
    AgentPress_ToolConfig,
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentVersionResponse,
    AgentResponse,
    PaginationInfo,
    AgentsResponse,
    AgentTool,
    AgentToolsResponse,
    DeleteAgentResponse,
    to_dict,
    from_dict,
    AgentsClient,
    create_agents_client,
)
from a2abase.tools import A2ABaseTools


class TestMCPConfig:
    """Test class for MCPConfig dataclass"""

    def test_init(self):
        """Test MCPConfig initialization"""
        config = MCPConfig(url="http://example.com")
        assert config.url == "http://example.com"


class TestCustomMCP:
    """Test class for CustomMCP dataclass"""

    def test_init(self):
        """Test CustomMCP initialization"""
        mcp_config = MCPConfig(url="http://example.com")
        custom_mcp = CustomMCP(
            name="test_mcp",
            type="http",
            config=mcp_config,
            enabled_tools=["tool1", "tool2"]
        )
        assert custom_mcp.name == "test_mcp"
        assert custom_mcp.type == "http"
        assert custom_mcp.config == mcp_config
        assert custom_mcp.enabled_tools == ["tool1", "tool2"]


class TestAgentPress_ToolConfig:
    """Test class for AgentPress_ToolConfig dataclass"""

    def test_init(self):
        """Test AgentPress_ToolConfig initialization"""
        config = AgentPress_ToolConfig(enabled=True, description="Test tool")
        assert config.enabled == True
        assert config.description == "Test tool"


class TestAgentCreateRequest:
    """Test class for AgentCreateRequest dataclass"""

    def test_init_minimal(self):
        """Test AgentCreateRequest with minimal fields"""
        request = AgentCreateRequest(name="Test", system_prompt="Prompt")
        assert request.name == "Test"
        assert request.system_prompt == "Prompt"
        assert request.description is None
        assert request.is_default == False

    def test_init_all_fields(self):
        """Test AgentCreateRequest with all fields"""
        mcp_config = MCPConfig(url="http://example.com")
        custom_mcp = CustomMCP(name="mcp", type="http", config=mcp_config, enabled_tools=[])
        tool_config = AgentPress_ToolConfig(enabled=True, description="Tool")
        
        request = AgentCreateRequest(
            name="Test",
            system_prompt="Prompt",
            description="Desc",
            custom_mcps=[custom_mcp],
            agentpress_tools={A2ABaseTools.WEB_SEARCH_TOOL: tool_config},
            is_default=True,
            avatar="avatar.png",
            avatar_color="#000000",
            profile_image_url="profile.png",
            icon_name="icon",
            icon_color="#ffffff",
            icon_background="#000000"
        )
        assert request.name == "Test"
        assert request.description == "Desc"
        assert len(request.custom_mcps) == 1
        assert A2ABaseTools.WEB_SEARCH_TOOL in request.agentpress_tools


class TestAgentUpdateRequest:
    """Test class for AgentUpdateRequest dataclass"""

    def test_init_all_none(self):
        """Test AgentUpdateRequest with all None"""
        request = AgentUpdateRequest()
        assert request.name is None
        assert request.system_prompt is None

    def test_init_some_fields(self):
        """Test AgentUpdateRequest with some fields"""
        request = AgentUpdateRequest(name="New Name", system_prompt="New Prompt")
        assert request.name == "New Name"
        assert request.system_prompt == "New Prompt"


class TestAgentVersionResponse:
    """Test class for AgentVersionResponse dataclass"""

    def test_init(self):
        """Test AgentVersionResponse initialization"""
        mcp_config = MCPConfig(url="http://example.com")
        custom_mcp = CustomMCP(name="mcp", type="http", config=mcp_config, enabled_tools=[])
        tool_config = AgentPress_ToolConfig(enabled=True, description="Tool")
        
        version = AgentVersionResponse(
            version_id="v1",
            agent_id="a1",
            version_number=1,
            version_name="v1.0",
            system_prompt="Prompt",
            custom_mcps=[custom_mcp],
            agentpress_tools={A2ABaseTools.WEB_SEARCH_TOOL: tool_config},
            is_active=True,
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )
        assert version.version_id == "v1"
        assert version.created_by is None


class TestAgentResponse:
    """Test class for AgentResponse dataclass"""

    def test_init_minimal(self):
        """Test AgentResponse with minimal fields"""
        response = AgentResponse(
            agent_id="a1",
            name="Agent",
            system_prompt="Prompt",
            custom_mcps=[],
            agentpress_tools={},
            is_default=False,
            created_at="2023-01-01"
        )
        assert response.account_id is None
        assert response.is_public == False
        assert response.download_count == 0


class TestPaginationInfo:
    """Test class for PaginationInfo dataclass"""

    def test_init(self):
        """Test PaginationInfo initialization"""
        pagination = PaginationInfo(page=1, limit=20, total=100, pages=5)
        assert pagination.page == 1
        assert pagination.limit == 20
        assert pagination.total == 100
        assert pagination.pages == 5


class TestAgentsResponse:
    """Test class for AgentsResponse dataclass"""

    def test_init(self):
        """Test AgentsResponse initialization"""
        agent = AgentResponse(
            agent_id="a1",
            name="Agent",
            system_prompt="Prompt",
            custom_mcps=[],
            agentpress_tools={},
            is_default=False,
            created_at="2023-01-01"
        )
        pagination = PaginationInfo(page=1, limit=20, total=1, pages=1)
        response = AgentsResponse(agents=[agent], pagination=pagination)
        assert len(response.agents) == 1
        assert response.pagination == pagination


class TestAgentTool:
    """Test class for AgentTool dataclass"""

    def test_init_minimal(self):
        """Test AgentTool with minimal fields"""
        tool = AgentTool(name="tool1", enabled=True)
        assert tool.name == "tool1"
        assert tool.enabled == True
        assert tool.server is None
        assert tool.description is None

    def test_init_all_fields(self):
        """Test AgentTool with all fields"""
        tool = AgentTool(name="tool1", enabled=True, server="server1", description="Desc")
        assert tool.server == "server1"
        assert tool.description == "Desc"


class TestAgentToolsResponse:
    """Test class for AgentToolsResponse dataclass"""

    def test_init(self):
        """Test AgentToolsResponse initialization"""
        tool1 = AgentTool(name="tool1", enabled=True)
        tool2 = AgentTool(name="tool2", enabled=False)
        response = AgentToolsResponse(agentpress_tools=[tool1], mcp_tools=[tool2])
        assert len(response.agentpress_tools) == 1
        assert len(response.mcp_tools) == 1


class TestDeleteAgentResponse:
    """Test class for DeleteAgentResponse dataclass"""

    def test_init(self):
        """Test DeleteAgentResponse initialization"""
        response = DeleteAgentResponse(message="Deleted")
        assert response.message == "Deleted"


class TestToDict:
    """Test class for to_dict function"""

    def test_to_dict_with_dataclass(self):
        """Test to_dict with dataclass"""
        config = MCPConfig(url="http://example.com")
        result = to_dict(config)
        assert result == {"url": "http://example.com"}

    def test_to_dict_with_none_values(self):
        """Test to_dict filters None values"""
        request = AgentCreateRequest(name="Test", system_prompt="Prompt")
        result = to_dict(request)
        assert "description" not in result or result["description"] is None
        assert "name" in result

    def test_to_dict_with_non_dataclass(self):
        """Test to_dict with non-dataclass object"""
        result = to_dict("string")
        assert result == "string"

    def test_to_dict_with_dict(self):
        """Test to_dict with dict"""
        result = to_dict({"key": "value"})
        assert result == {"key": "value"}


class TestFromDict:
    """Test class for from_dict function"""

    def test_from_dict_empty_data(self):
        """Test from_dict with empty data"""
        result = from_dict(AgentResponse, {})
        assert result is None

    def test_from_dict_agents_response(self):
        """Test from_dict with AgentsResponse"""
        data = {
            "agents": [{
                "agent_id": "a1",
                "name": "Agent",
                "system_prompt": "Prompt",
                "custom_mcps": [],
                "agentpress_tools": {},
                "is_default": False,
                "created_at": "2023-01-01"
            }],
            "pagination": {
                "page": 1,
                "limit": 20,
                "total": 1,
                "pages": 1
            }
        }
        result = from_dict(AgentsResponse, data)
        assert isinstance(result, AgentsResponse)
        assert len(result.agents) == 1

    def test_from_dict_agents_response_missing_pagination(self):
        """Test from_dict with AgentsResponse missing pagination"""
        data = {
            "agents": [],
            "page": 1,
            "limit": 20
        }
        result = from_dict(AgentsResponse, data)
        assert isinstance(result, AgentsResponse)

    def test_from_dict_agents_response_pagination_error(self):
        """Test from_dict with AgentsResponse pagination parsing error"""
        data = {
            "agents": [],
            "pagination": {"invalid": "data"}
        }
        result = from_dict(AgentsResponse, data)
        assert isinstance(result, AgentsResponse)

    def test_from_dict_agent_response_with_tools(self):
        """Test from_dict with AgentResponse including tools"""
        data = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {
                "web_search_tool": {
                    "enabled": True,
                    "description": "Search tool"
                }
            },
            "is_default": False,
            "created_at": "2023-01-01"
        }
        result = from_dict(AgentResponse, data)
        assert isinstance(result, AgentResponse)
        assert A2ABaseTools.WEB_SEARCH_TOOL in result.agentpress_tools

    def test_from_dict_agent_response_with_invalid_tool(self):
        """Test from_dict with AgentResponse with invalid tool key"""
        data = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {
                "invalid_tool": {"enabled": True}
            },
            "is_default": False,
            "created_at": "2023-01-01"
        }
        result = from_dict(AgentResponse, data)
        assert isinstance(result, AgentResponse)
        assert len(result.agentpress_tools) == 0

    def test_from_dict_agent_response_with_non_dict_tool_config(self):
        """Test from_dict with AgentResponse with non-dict tool config (covers line 186)"""
        from a2abase.api.agents import AgentPress_ToolConfig
        tool_config_obj = AgentPress_ToolConfig(enabled=True, description="Test")
        data = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {
                "web_search_tool": tool_config_obj  # Already an object, not a dict
            },
            "is_default": False,
            "created_at": "2023-01-01"
        }
        result = from_dict(AgentResponse, data)
        assert isinstance(result, AgentResponse)
        assert A2ABaseTools.WEB_SEARCH_TOOL in result.agentpress_tools

    def test_from_dict_agent_response_with_current_version(self):
        """Test from_dict with AgentResponse with current_version"""
        data = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {},
            "is_default": False,
            "created_at": "2023-01-01",
            "current_version": {
                "version_id": "v1",
                "agent_id": "a1",
                "version_number": 1,
                "version_name": "v1",
                "system_prompt": "Prompt",
                "custom_mcps": [],
                "agentpress_tools": {},
                "is_active": True,
                "created_at": "2023-01-01",
                "updated_at": "2023-01-01"
            }
        }
        result = from_dict(AgentResponse, data)
        assert result.current_version is not None

    def test_from_dict_agent_response_with_custom_mcps(self):
        """Test from_dict with AgentResponse with custom_mcps"""
        data = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [{
                "name": "mcp",
                "type": "http",
                "config": {"url": "http://example.com"},
                "enabled_tools": []
            }],
            "agentpress_tools": {},
            "is_default": False,
            "created_at": "2023-01-01"
        }
        result = from_dict(AgentResponse, data)
        assert len(result.custom_mcps) == 1

    def test_from_dict_simple_dataclass(self):
        """Test from_dict with simple dataclass"""
        data = {"url": "http://example.com"}
        result = from_dict(MCPConfig, data)
        assert isinstance(result, MCPConfig)
        assert result.url == "http://example.com"

    def test_from_dict_non_dataclass(self):
        """Test from_dict with non-dataclass"""
        result = from_dict(str, "test")
        assert result == "test"


class TestAgentsClient:
    """Test class for AgentsClient"""

    def test_init_without_auth(self):
        """Test AgentsClient initialization without auth"""
        with patch('a2abase.api.agents.httpx.AsyncClient') as mock_client:
            client = AgentsClient("http://api.com")
            assert client.base_url == "http://api.com"
            assert client.timeout == 30.0

    def test_init_with_auth(self):
        """Test AgentsClient initialization with auth"""
        with patch('a2abase.api.agents.httpx.AsyncClient') as mock_client:
            client = AgentsClient("http://api.com", auth_token="token123")
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert "X-API-Key" in call_kwargs["headers"]

    def test_init_with_custom_headers(self):
        """Test AgentsClient initialization with custom headers"""
        with patch('a2abase.api.agents.httpx.AsyncClient') as mock_client:
            client = AgentsClient("http://api.com", custom_headers={"Custom": "Header"})
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["headers"]["Custom"] == "Header"

    def test_init_strips_trailing_slash(self):
        """Test AgentsClient strips trailing slash from base_url"""
        with patch('a2abase.api.agents.httpx.AsyncClient'):
            client = AgentsClient("http://api.com/")
            assert client.base_url == "http://api.com"

    def test_init_with_timeout(self):
        """Test AgentsClient initialization with custom timeout"""
        with patch('a2abase.api.agents.httpx.AsyncClient') as mock_client:
            client = AgentsClient("http://api.com", timeout=60.0)
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["timeout"] == 60.0

    @pytest.mark.asyncio
    async def test_close(self):
        """Test AgentsClient.close()"""
        mock_client = AsyncMock()
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            await client.close()
            mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test AgentsClient as context manager"""
        mock_client = AsyncMock()
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            async with AgentsClient("http://api.com") as client:
                assert isinstance(client, AgentsClient)
            mock_client.aclose.assert_called_once()

    def test_handle_response_success(self):
        """Test _handle_response with successful response"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        client = AgentsClient("http://api.com")
        result = client._handle_response(mock_response)
        assert result == {"data": "test"}

    def test_handle_response_error_with_json(self):
        """Test _handle_response with error response containing JSON"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Error message"}
        mock_response.request = Mock()
        
        client = AgentsClient("http://api.com")
        with pytest.raises(httpx.HTTPStatusError):
            client._handle_response(mock_response)

    def test_handle_response_error_without_json(self):
        """Test _handle_response with error response without JSON"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception()
        mock_response.request = Mock()
        
        client = AgentsClient("http://api.com")
        with pytest.raises(httpx.HTTPStatusError):
            client._handle_response(mock_response)

    @pytest.mark.asyncio
    async def test_get_agents(self):
        """Test get_agents()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [],
            "pagination": {"page": 1, "limit": 20, "total": 0, "pages": 1}
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            result = await client.get_agents()
            assert isinstance(result, AgentsResponse)

    @pytest.mark.asyncio
    async def test_get_agents_with_search(self):
        """Test get_agents() with search parameter"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [],
            "pagination": {"page": 1, "limit": 20, "total": 0, "pages": 1}
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            await client.get_agents(search="test")
            call_args = mock_client.get.call_args
            assert "search" in call_args[1]["params"]

    @pytest.mark.asyncio
    async def test_get_agent(self):
        """Test get_agent()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {},
            "is_default": False,
            "created_at": "2023-01-01"
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            result = await client.get_agent("a1")
            assert isinstance(result, AgentResponse)

    @pytest.mark.asyncio
    async def test_create_agent(self):
        """Test create_agent()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agent_id": "a1",
            "name": "Agent",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {},
            "is_default": False,
            "created_at": "2023-01-01"
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            request = AgentCreateRequest(name="Agent", system_prompt="Prompt")
            result = await client.create_agent(request)
            assert isinstance(result, AgentResponse)

    @pytest.mark.asyncio
    async def test_update_agent(self):
        """Test update_agent()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agent_id": "a1",
            "name": "Updated",
            "system_prompt": "Prompt",
            "custom_mcps": [],
            "agentpress_tools": {},
            "is_default": False,
            "created_at": "2023-01-01"
        }
        
        mock_client = AsyncMock()
        mock_client.put = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            request = AgentUpdateRequest(name="Updated")
            result = await client.update_agent("a1", request)
            assert isinstance(result, AgentResponse)

    @pytest.mark.asyncio
    async def test_delete_agent(self):
        """Test delete_agent()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Deleted"}
        
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            result = await client.delete_agent("a1")
            assert isinstance(result, DeleteAgentResponse)
            assert result.message == "Deleted"

    @pytest.mark.asyncio
    async def test_delete_agent_default_message(self):
        """Test delete_agent() with default message"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.agents.httpx.AsyncClient', return_value=mock_client):
            client = AgentsClient("http://api.com")
            result = await client.delete_agent("a1")
            assert result.message == "ok"


class TestCreateAgentsClient:
    """Test class for create_agents_client function"""

    def test_create_agents_client(self):
        """Test create_agents_client()"""
        with patch('a2abase.api.agents.AgentsClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            result = create_agents_client("http://api.com", "token")
            assert result == mock_client
            mock_client_class.assert_called_once_with(
                base_url="http://api.com",
                auth_token="token",
                custom_headers=None,
                timeout=30.0
            )

    def test_create_agents_client_with_all_params(self):
        """Test create_agents_client() with all parameters"""
        with patch('a2abase.api.agents.AgentsClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            result = create_agents_client(
                "http://api.com",
                "token",
                custom_headers={"Custom": "Header"},
                timeout=60.0
            )
            mock_client_class.assert_called_once_with(
                base_url="http://api.com",
                auth_token="token",
                custom_headers={"Custom": "Header"},
                timeout=60.0
            )

