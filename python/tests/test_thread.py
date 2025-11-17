"""
Test suite for thread.py - Thread, AgentRun, and A2ABaseThread classes
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from a2abase.thread import Thread, AgentRun, A2ABaseThread
from a2abase.api.threads import ThreadsClient, CreateThreadResponse, Message, MessagesResponse


class TestThread:
    """Test class for Thread"""

    def test_init(self):
        """Test Thread initialization"""
        mock_client = Mock(spec=ThreadsClient)
        thread = Thread(mock_client, "thread_123")
        
        assert thread._client == mock_client
        assert thread._thread_id == "thread_123"

    @pytest.mark.asyncio
    async def test_add_message(self):
        """Test Thread.add_message()"""
        mock_client = Mock(spec=ThreadsClient)
        mock_message = Mock(spec=Message)
        mock_message.message_id = "msg_123"
        mock_client.add_message_to_thread = AsyncMock(return_value=mock_message)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.add_message("Hello")
        
        mock_client.add_message_to_thread.assert_called_once_with("thread_123", "Hello")
        assert result == "msg_123"

    @pytest.mark.asyncio
    async def test_del_message(self):
        """Test Thread.del_message()"""
        mock_client = Mock(spec=ThreadsClient)
        mock_client.delete_message_from_thread = AsyncMock()
        
        thread = Thread(mock_client, "thread_123")
        await thread.del_message("msg_123")
        
        mock_client.delete_message_from_thread.assert_called_once_with("thread_123", "msg_123")

    @pytest.mark.asyncio
    async def test_get_messages(self):
        """Test Thread.get_messages()"""
        mock_client = Mock(spec=ThreadsClient)
        mock_message1 = Mock(spec=Message)
        mock_message2 = Mock(spec=Message)
        mock_response = Mock(spec=MessagesResponse)
        mock_response.messages = [mock_message1, mock_message2]
        mock_client.get_thread_messages = AsyncMock(return_value=mock_response)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.get_messages()
        
        mock_client.get_thread_messages.assert_called_once_with("thread_123")
        assert result == [mock_message1, mock_message2]

    @pytest.mark.asyncio
    async def test_get_agent_runs_success(self):
        """Test Thread.get_agent_runs() with successful response"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recent_agent_runs": [
                {"id": "run_1", "status": "completed"},
                {"id": "run_2", "status": "running"}
            ]
        }
        mock_client.client = Mock()
        mock_client.client.get = AsyncMock(return_value=mock_response)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.get_agent_runs()
        
        assert result is not None
        assert len(result) == 2
        assert result[0]._agent_run_id == "run_1"
        assert result[1]._agent_run_id == "run_2"

    @pytest.mark.asyncio
    async def test_get_agent_runs_with_agent_run_id_field(self):
        """Test Thread.get_agent_runs() with agent_run_id field"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recent_agent_runs": [
                {"agent_run_id": "run_1", "status": "completed"}
            ]
        }
        mock_client.client = Mock()
        mock_client.client.get = AsyncMock(return_value=mock_response)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.get_agent_runs()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]._agent_run_id == "run_1"

    @pytest.mark.asyncio
    async def test_get_agent_runs_error_response(self):
        """Test Thread.get_agent_runs() with error response"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.client = Mock()
        mock_client.client.get = AsyncMock(return_value=mock_response)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.get_agent_runs()
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_agent_runs_no_runs(self):
        """Test Thread.get_agent_runs() with no runs"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recent_agent_runs": []
        }
        mock_client.client = Mock()
        mock_client.client.get = AsyncMock(return_value=mock_response)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.get_agent_runs()
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_agent_runs_missing_field(self):
        """Test Thread.get_agent_runs() with missing recent_agent_runs field"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_client.client = Mock()
        mock_client.client.get = AsyncMock(return_value=mock_response)
        
        thread = Thread(mock_client, "thread_123")
        result = await thread.get_agent_runs()
        
        assert result is None


class TestAgentRun:
    """Test class for AgentRun"""

    def test_init(self):
        """Test AgentRun initialization"""
        mock_thread = Mock(spec=Thread)
        agent_run = AgentRun(mock_thread, "run_123")
        
        assert agent_run._thread == mock_thread
        assert agent_run._agent_run_id == "run_123"

    @pytest.mark.asyncio
    async def test_get_stream(self):
        """Test AgentRun.get_stream()"""
        mock_thread = Mock(spec=Thread)
        mock_client = Mock(spec=ThreadsClient)
        mock_client.get_agent_run_stream_url = Mock(return_value="http://example.com/stream")
        mock_client.headers = {"Authorization": "Bearer token"}
        mock_thread._client = mock_client
        
        mock_stream = AsyncMock()
        mock_stream.__aiter__ = Mock(return_value=iter(["chunk1", "chunk2"]))
        
        with patch('a2abase.thread.stream_from_url', return_value=mock_stream) as mock_stream_func:
            agent_run = AgentRun(mock_thread, "run_123")
            stream = await agent_run.get_stream()
            
            mock_client.get_agent_run_stream_url.assert_called_once_with("run_123")
            mock_stream_func.assert_called_once_with("http://example.com/stream", headers=mock_client.headers)
            assert stream == mock_stream


class TestA2ABaseThread:
    """Test class for A2ABaseThread"""

    def test_init(self):
        """Test A2ABaseThread initialization"""
        mock_client = Mock(spec=ThreadsClient)
        thread_manager = A2ABaseThread(mock_client)
        
        assert thread_manager._client == mock_client

    @pytest.mark.asyncio
    async def test_create_with_name(self):
        """Test A2ABaseThread.create() with name"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock(spec=CreateThreadResponse)
        mock_response.thread_id = "thread_123"
        mock_client.create_thread = AsyncMock(return_value=mock_response)
        
        thread_manager = A2ABaseThread(mock_client)
        thread = await thread_manager.create("Test Thread")
        
        mock_client.create_thread.assert_called_once_with("Test Thread")
        assert isinstance(thread, Thread)
        assert thread._thread_id == "thread_123"
        assert thread._client == mock_client

    @pytest.mark.asyncio
    async def test_create_without_name(self):
        """Test A2ABaseThread.create() without name"""
        mock_client = Mock(spec=ThreadsClient)
        mock_response = Mock(spec=CreateThreadResponse)
        mock_response.thread_id = "thread_123"
        mock_client.create_thread = AsyncMock(return_value=mock_response)
        
        thread_manager = A2ABaseThread(mock_client)
        thread = await thread_manager.create()
        
        mock_client.create_thread.assert_called_once_with(None)
        assert isinstance(thread, Thread)
        assert thread._thread_id == "thread_123"

    @pytest.mark.asyncio
    async def test_get(self):
        """Test A2ABaseThread.get()"""
        mock_client = Mock(spec=ThreadsClient)
        thread_manager = A2ABaseThread(mock_client)
        thread = await thread_manager.get("thread_123")
        
        assert isinstance(thread, Thread)
        assert thread._thread_id == "thread_123"
        assert thread._client == mock_client

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test A2ABaseThread.delete()"""
        mock_client = Mock(spec=ThreadsClient)
        mock_client.delete_thread = AsyncMock()
        
        thread_manager = A2ABaseThread(mock_client)
        await thread_manager.delete("thread_123")
        
        mock_client.delete_thread.assert_called_once_with("thread_123")

