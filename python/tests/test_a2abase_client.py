"""
Test suite for A2ABaseClient
"""
import pytest
from unittest.mock import Mock, patch

from a2abase.a2abase_client import A2ABaseClient
from a2abase.agent import A2ABaseAgent
from a2abase.thread import A2ABaseThread


class TestA2ABaseClient:
    """Test class for A2ABaseClient"""

    def test_init_with_default_url(self):
        """Test A2ABaseClient initialization with default URL"""
        with patch('a2abase.a2abase_client.agents.create_agents_client') as mock_agents, \
             patch('a2abase.a2abase_client.threads.create_threads_client') as mock_threads:
            mock_agents_client = Mock()
            mock_threads_client = Mock()
            mock_agents.return_value = mock_agents_client
            mock_threads.return_value = mock_threads_client
            
            client = A2ABaseClient(api_key="test_key")
            
            mock_agents.assert_called_once_with("https://a2abase.ai", "test_key")
            mock_threads.assert_called_once_with("https://a2abase.ai", "test_key")
            assert isinstance(client.Agent, A2ABaseAgent)
            assert isinstance(client.Thread, A2ABaseThread)
            assert client._agents_client == mock_agents_client
            assert client._threads_client == mock_threads_client

    def test_init_with_custom_url(self):
        """Test A2ABaseClient initialization with custom URL"""
        with patch('a2abase.a2abase_client.agents.create_agents_client') as mock_agents, \
             patch('a2abase.a2abase_client.threads.create_threads_client') as mock_threads:
            mock_agents_client = Mock()
            mock_threads_client = Mock()
            mock_agents.return_value = mock_agents_client
            mock_threads.return_value = mock_threads_client
            
            client = A2ABaseClient(api_key="test_key", api_url="https://custom.api.com")
            
            mock_agents.assert_called_once_with("https://custom.api.com", "test_key")
            mock_threads.assert_called_once_with("https://custom.api.com", "test_key")
            assert isinstance(client.Agent, A2ABaseAgent)
            assert isinstance(client.Thread, A2ABaseThread)

    def test_agent_property(self):
        """Test that Agent property returns A2ABaseAgent instance"""
        with patch('a2abase.a2abase_client.agents.create_agents_client') as mock_agents, \
             patch('a2abase.a2abase_client.threads.create_threads_client') as mock_threads:
            mock_agents_client = Mock()
            mock_threads_client = Mock()
            mock_agents.return_value = mock_agents_client
            mock_threads.return_value = mock_threads_client
            
            client = A2ABaseClient(api_key="test_key")
            
            assert isinstance(client.Agent, A2ABaseAgent)
            assert client.Agent._client == mock_agents_client

    def test_thread_property(self):
        """Test that Thread property returns A2ABaseThread instance"""
        with patch('a2abase.a2abase_client.agents.create_agents_client') as mock_agents, \
             patch('a2abase.a2abase_client.threads.create_threads_client') as mock_threads:
            mock_agents_client = Mock()
            mock_threads_client = Mock()
            mock_agents.return_value = mock_agents_client
            mock_threads.return_value = mock_threads_client
            
            client = A2ABaseClient(api_key="test_key")
            
            assert isinstance(client.Thread, A2ABaseThread)
            assert client.Thread._client == mock_threads_client

