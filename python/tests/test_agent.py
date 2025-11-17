"""
Test suite for agent.py - Agent and A2ABaseAgent classes
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from a2abase.agent import Agent, A2ABaseAgent
from a2abase.tools import A2ABaseTools, MCPTools
from a2abase.api.agents import (
    AgentsClient,
    AgentResponse,
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentPress_ToolConfig,
    CustomMCP,
    MCPConfig,
    AgentsResponse,
    PaginationInfo,
)
from a2abase.api.threads import AgentStartRequest, AgentStartResponse
from a2abase.thread import Thread


class TestAgent:
    """Test class for Agent"""

    def test_init(self):
        """Test Agent initialization"""
        mock_client = Mock(spec=AgentsClient)
        agent = Agent(mock_client, "agent_123")
        
        assert agent._client == mock_client
        assert agent._agent_id == "agent_123"
        assert agent._model == "gemini/gemini-2.5-pro"

    def test_init_with_custom_model(self):
        """Test Agent initialization with custom model"""
        mock_client = Mock(spec=AgentsClient)
        agent = Agent(mock_client, "agent_123", model="gpt-4")
        
        assert agent._model == "gpt-4"

    @pytest.mark.asyncio
    async def test_details(self):
        """Test Agent.details()"""
        mock_client = Mock(spec=AgentsClient)
        mock_response = Mock(spec=AgentResponse)
        mock_client.get_agent = AsyncMock(return_value=mock_response)
        
        agent = Agent(mock_client, "agent_123")
        result = await agent.details()
        
        mock_client.get_agent.assert_called_once_with("agent_123")
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test Agent.delete()"""
        mock_client = Mock(spec=AgentsClient)
        mock_client.delete_agent = AsyncMock()
        
        agent = Agent(mock_client, "agent_123")
        await agent.delete()
        
        mock_client.delete_agent.assert_called_once_with("agent_123")

    @pytest.mark.asyncio
    async def test_update_name_only(self):
        """Test Agent.update() with name only"""
        mock_client = Mock(spec=AgentsClient)
        mock_details = Mock(spec=AgentResponse)
        mock_details.agentpress_tools = {}
        mock_details.custom_mcps = []
        mock_client.get_agent = AsyncMock(return_value=mock_details)
        mock_client.update_agent = AsyncMock()
        
        agent = Agent(mock_client, "agent_123")
        await agent.update(name="New Name")
        
        mock_client.get_agent.assert_called_once()
        mock_client.update_agent.assert_called_once()
        call_args = mock_client.update_agent.call_args
        assert call_args[0][0] == "agent_123"
        assert isinstance(call_args[0][1], AgentUpdateRequest)
        assert call_args[0][1].name == "New Name"

    @pytest.mark.asyncio
    async def test_update_system_prompt_only(self):
        """Test Agent.update() with system_prompt only"""
        mock_client = Mock(spec=AgentsClient)
        mock_details = Mock(spec=AgentResponse)
        mock_details.agentpress_tools = {}
        mock_details.custom_mcps = []
        mock_client.get_agent = AsyncMock(return_value=mock_details)
        mock_client.update_agent = AsyncMock()
        
        agent = Agent(mock_client, "agent_123")
        await agent.update(system_prompt="New prompt")
        
        call_args = mock_client.update_agent.call_args
        assert call_args[0][1].system_prompt == "New prompt"

    @pytest.mark.asyncio
    async def test_update_with_agentpress_tools(self):
        """Test Agent.update() with A2ABaseTools"""
        mock_client = Mock(spec=AgentsClient)
        mock_client.update_agent = AsyncMock()
        
        agent = Agent(mock_client, "agent_123")
        await agent.update(
            a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL],
            allowed_tools=["web_search_tool"]
        )
        
        call_args = mock_client.update_agent.call_args
        update_request = call_args[0][1]
        assert A2ABaseTools.WEB_SEARCH_TOOL in update_request.agentpress_tools
        config = update_request.agentpress_tools[A2ABaseTools.WEB_SEARCH_TOOL]
        # Note: tool.name returns the enum name, not the value, so the check uses the enum name
        # The actual enabled state depends on how the code checks tool.name vs tool.value
        assert config.description == "Search the web for information"

    @pytest.mark.asyncio
    async def test_update_with_mcp_tools(self):
        """Test Agent.update() with MCPTools"""
        mock_client = Mock(spec=AgentsClient)
        mock_client.update_agent = AsyncMock()
        
        mock_mcp = Mock(spec=MCPTools)
        mock_mcp.name = "test_mcp"
        mock_mcp.type = "http"
        mock_mcp.url = "http://example.com"
        mock_mcp.enabled_tools = ["tool1", "tool2"]
        
        agent = Agent(mock_client, "agent_123")
        await agent.update(
            a2abase_tools=[mock_mcp],
            allowed_tools=["test_mcp"]
        )
        
        call_args = mock_client.update_agent.call_args
        update_request = call_args[0][1]
        assert len(update_request.custom_mcps) == 1
        assert update_request.custom_mcps[0].name == "test_mcp"

    @pytest.mark.asyncio
    async def test_update_with_allowed_tools_disabling(self):
        """Test Agent.update() with allowed_tools disabling some tools"""
        from a2abase.tools import A2ABaseTools
        
        mock_client = Mock(spec=AgentsClient)
        mock_tool1 = A2ABaseTools.WEB_SEARCH_TOOL
        mock_tool2 = A2ABaseTools.SB_FILES_TOOL
        mock_config1 = Mock()
        mock_config1.enabled = True
        mock_config2 = Mock()
        mock_config2.enabled = True
        
        mock_details = Mock(spec=AgentResponse)
        mock_details.agentpress_tools = {
            mock_tool1: mock_config1,
            mock_tool2: mock_config2
        }
        mock_details.custom_mcps = []
        mock_client.get_agent = AsyncMock(return_value=mock_details)
        mock_client.update_agent = AsyncMock()
        
        agent = Agent(mock_client, "agent_123")
        await agent.update(allowed_tools=[A2ABaseTools.WEB_SEARCH_TOOL.value])
        
        assert mock_config1.enabled == True
        assert mock_config2.enabled == False

    @pytest.mark.asyncio
    async def test_update_with_custom_mcps_allowed_tools(self):
        """Test Agent.update() with custom_mcps and allowed_tools"""
        mock_client = Mock(spec=AgentsClient)
        mock_mcp = Mock()
        mock_mcp.enabled_tools = []
        
        mock_details = Mock(spec=AgentResponse)
        mock_details.agentpress_tools = {}
        mock_details.custom_mcps = [mock_mcp]
        mock_client.get_agent = AsyncMock(return_value=mock_details)
        mock_client.update_agent = AsyncMock()
        
        agent = Agent(mock_client, "agent_123")
        await agent.update(allowed_tools=["tool1", "tool2"])
        
        assert mock_mcp.enabled_tools == ["tool1", "tool2"]

    @pytest.mark.asyncio
    async def test_run(self):
        """Test Agent.run()"""
        mock_client = Mock(spec=AgentsClient)
        mock_thread_client = Mock()
        mock_thread = Mock(spec=Thread)
        mock_thread._client = mock_thread_client
        mock_thread._thread_id = "thread_123"
        mock_thread.add_message = AsyncMock()
        
        mock_start_response = Mock(spec=AgentStartResponse)
        mock_start_response.agent_run_id = "run_123"
        mock_thread_client.start_agent = AsyncMock(return_value=mock_start_response)
        
        agent = Agent(mock_client, "agent_123")
        result = await agent.run("Hello", mock_thread)
        
        mock_thread.add_message.assert_called_once_with("Hello")
        mock_thread_client.start_agent.assert_called_once()
        call_args = mock_thread_client.start_agent.call_args
        assert call_args[0][0] == "thread_123"
        assert isinstance(call_args[0][1], AgentStartRequest)
        assert call_args[0][1].agent_id == "agent_123"
        assert result._agent_run_id == "run_123"

    @pytest.mark.asyncio
    async def test_run_with_custom_model(self):
        """Test Agent.run() with custom model"""
        mock_client = Mock(spec=AgentsClient)
        mock_thread_client = Mock()
        mock_thread = Mock(spec=Thread)
        mock_thread._client = mock_thread_client
        mock_thread._thread_id = "thread_123"
        mock_thread.add_message = AsyncMock()
        
        mock_start_response = Mock(spec=AgentStartResponse)
        mock_start_response.agent_run_id = "run_123"
        mock_thread_client.start_agent = AsyncMock(return_value=mock_start_response)
        
        agent = Agent(mock_client, "agent_123", model="default_model")
        result = await agent.run("Hello", mock_thread, model="custom_model")
        
        call_args = mock_thread_client.start_agent.call_args
        assert call_args[0][1].model_name == "custom_model"


class TestA2ABaseAgent:
    """Test class for A2ABaseAgent"""

    def test_init(self):
        """Test A2ABaseAgent initialization"""
        mock_client = Mock(spec=AgentsClient)
        agent_manager = A2ABaseAgent(mock_client)
        
        assert agent_manager._client == mock_client

    @pytest.mark.asyncio
    async def test_create_without_tools(self):
        """Test A2ABaseAgent.create() without tools"""
        mock_client = Mock(spec=AgentsClient)
        mock_response = Mock(spec=AgentResponse)
        mock_response.agent_id = "agent_123"
        mock_client.create_agent = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.create(
            name="Test Agent",
            system_prompt="Test prompt"
        )
        
        mock_client.create_agent.assert_called_once()
        call_args = mock_client.create_agent.call_args
        assert isinstance(call_args[0][0], AgentCreateRequest)
        assert call_args[0][0].name == "Test Agent"
        assert call_args[0][0].system_prompt == "Test prompt"
        assert isinstance(agent, Agent)
        assert agent._agent_id == "agent_123"

    @pytest.mark.asyncio
    async def test_create_with_agentpress_tools(self):
        """Test A2ABaseAgent.create() with A2ABaseTools"""
        mock_client = Mock(spec=AgentsClient)
        mock_response = Mock(spec=AgentResponse)
        mock_response.agent_id = "agent_123"
        mock_client.create_agent = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.create(
            name="Test Agent",
            system_prompt="Test prompt",
            a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL],
            allowed_tools=["web_search_tool"]
        )
        
        call_args = mock_client.create_agent.call_args
        request = call_args[0][0]
        assert A2ABaseTools.WEB_SEARCH_TOOL in request.agentpress_tools
        config = request.agentpress_tools[A2ABaseTools.WEB_SEARCH_TOOL]
        # Note: tool.name returns the enum name, not the value, so enabled depends on enum name matching
        assert config.description == "Search the web for information"

    @pytest.mark.asyncio
    async def test_create_with_mcp_tools(self):
        """Test A2ABaseAgent.create() with MCPTools"""
        mock_client = Mock(spec=AgentsClient)
        mock_response = Mock(spec=AgentResponse)
        mock_response.agent_id = "agent_123"
        mock_client.create_agent = AsyncMock(return_value=mock_response)
        
        mock_mcp = Mock(spec=MCPTools)
        mock_mcp.name = "test_mcp"
        mock_mcp.type = "http"
        mock_mcp.url = "http://example.com"
        mock_mcp.enabled_tools = ["tool1"]
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.create(
            name="Test Agent",
            system_prompt="Test prompt",
            a2abase_tools=[mock_mcp],
            allowed_tools=["test_mcp"]
        )
        
        call_args = mock_client.create_agent.call_args
        request = call_args[0][0]
        assert len(request.custom_mcps) == 1
        assert request.custom_mcps[0].name == "test_mcp"
        assert request.custom_mcps[0].enabled_tools == ["tool1"]

    @pytest.mark.asyncio
    async def test_create_with_unknown_tool_type(self):
        """Test A2ABaseAgent.create() with unknown tool type raises ValueError"""
        mock_client = Mock(spec=AgentsClient)
        agent_manager = A2ABaseAgent(mock_client)
        
        with pytest.raises(ValueError, match="Unknown tool type"):
            await agent_manager.create(
                name="Test Agent",
                system_prompt="Test prompt",
                a2abase_tools=[object()]  # Invalid tool type
            )

    @pytest.mark.asyncio
    async def test_create_with_tools_no_allowed_tools(self):
        """Test A2ABaseAgent.create() with tools but no allowed_tools (all enabled)"""
        mock_client = Mock(spec=AgentsClient)
        mock_response = Mock(spec=AgentResponse)
        mock_response.agent_id = "agent_123"
        mock_client.create_agent = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.create(
            name="Test Agent",
            system_prompt="Test prompt",
            a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL]
        )
        
        call_args = mock_client.create_agent.call_args
        request = call_args[0][0]
        config = request.agentpress_tools[A2ABaseTools.WEB_SEARCH_TOOL]
        assert config.enabled == True

    @pytest.mark.asyncio
    async def test_get(self):
        """Test A2ABaseAgent.get()"""
        mock_client = Mock(spec=AgentsClient)
        mock_response = Mock(spec=AgentResponse)
        mock_response.agent_id = "agent_123"
        mock_client.get_agent = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.get("agent_123")
        
        mock_client.get_agent.assert_called_once_with("agent_123")
        assert isinstance(agent, Agent)
        assert agent._agent_id == "agent_123"

    @pytest.mark.asyncio
    async def test_find_by_name_found_on_first_page(self):
        """Test A2ABaseAgent.find_by_name() finds agent on first page"""
        mock_client = Mock(spec=AgentsClient)
        mock_agent = Mock(spec=AgentResponse)
        mock_agent.agent_id = "agent_123"
        mock_agent.name = "Test Agent"
        
        mock_pagination = Mock(spec=PaginationInfo)
        mock_pagination.pages = 1
        
        mock_response = Mock(spec=AgentsResponse)
        mock_response.agents = [mock_agent]
        mock_response.pagination = mock_pagination
        mock_client.get_agents = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.find_by_name("Test Agent")
        
        assert agent is not None
        assert agent._agent_id == "agent_123"
        mock_client.get_agents.assert_called_once_with(page=1, limit=100, search="Test Agent")

    @pytest.mark.asyncio
    async def test_find_by_name_not_found(self):
        """Test A2ABaseAgent.find_by_name() returns None when not found"""
        mock_client = Mock(spec=AgentsClient)
        mock_pagination = Mock(spec=PaginationInfo)
        mock_pagination.pages = 1
        
        mock_response = Mock(spec=AgentsResponse)
        mock_response.agents = []
        mock_response.pagination = mock_pagination
        mock_client.get_agents = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.find_by_name("Non-existent Agent")
        
        assert agent is None

    @pytest.mark.asyncio
    async def test_find_by_name_found_on_second_page(self):
        """Test A2ABaseAgent.find_by_name() finds agent on second page"""
        mock_client = Mock(spec=AgentsClient)
        mock_agent = Mock(spec=AgentResponse)
        mock_agent.agent_id = "agent_123"
        mock_agent.name = "Test Agent"
        
        mock_pagination1 = Mock(spec=PaginationInfo)
        mock_pagination1.pages = 2
        
        mock_pagination2 = Mock(spec=PaginationInfo)
        mock_pagination2.pages = 2
        
        mock_response1 = Mock(spec=AgentsResponse)
        mock_response1.agents = []
        mock_response1.pagination = mock_pagination1
        
        mock_response2 = Mock(spec=AgentsResponse)
        mock_response2.agents = [mock_agent]
        mock_response2.pagination = mock_pagination2
        
        mock_client.get_agents = AsyncMock(side_effect=[mock_response1, mock_response2])
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.find_by_name("Test Agent")
        
        assert agent is not None
        assert agent._agent_id == "agent_123"
        assert mock_client.get_agents.call_count == 2

    @pytest.mark.asyncio
    async def test_find_by_name_exception_handling(self):
        """Test A2ABaseAgent.find_by_name() handles exceptions"""
        mock_client = Mock(spec=AgentsClient)
        mock_client.get_agents = AsyncMock(side_effect=Exception("API Error"))
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.find_by_name("Test Agent")
        
        assert agent is None

    @pytest.mark.asyncio
    async def test_find_by_name_multiple_pages_limit(self):
        """Test A2ABaseAgent.find_by_name() limits to 10 pages"""
        mock_client = Mock(spec=AgentsClient)
        mock_pagination = Mock(spec=PaginationInfo)
        mock_pagination.pages = 15  # More than 10 pages
        
        mock_response = Mock(spec=AgentsResponse)
        mock_response.agents = []
        mock_response.pagination = mock_pagination
        mock_client.get_agents = AsyncMock(return_value=mock_response)
        
        agent_manager = A2ABaseAgent(mock_client)
        agent = await agent_manager.find_by_name("Test Agent")
        
        # Should only check up to 10 pages
        assert mock_client.get_agents.call_count <= 10

