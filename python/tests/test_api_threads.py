"""
Test suite for api/threads.py - Comprehensive coverage
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from a2abase.api.threads import (
    MessageCreateRequest,
    AgentStartRequest,
    Thread,
    Message,
    PaginationInfo,
    ThreadsResponse,
    MessagesResponse,
    CreateThreadResponse,
    AgentStartResponse,
    to_dict,
    from_dict,
    ThreadsClient,
    create_threads_client,
)
from a2abase.models import MessageType


class TestMessageCreateRequest:
    """Test class for MessageCreateRequest"""

    def test_init_default(self):
        """Test MessageCreateRequest with defaults"""
        request = MessageCreateRequest(content="Hello")
        assert request.content == "Hello"
        assert request.type == "user"
        assert request.is_llm_message == True

    def test_init_custom(self):
        """Test MessageCreateRequest with custom values"""
        request = MessageCreateRequest(content="Hello", type="assistant", is_llm_message=False)
        assert request.type == "assistant"
        assert request.is_llm_message == False

    def test_init_invalid_type(self):
        """Test MessageCreateRequest with invalid type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid message type"):
            MessageCreateRequest(content="Hello", type="invalid")

    def test_create_user_message(self):
        """Test MessageCreateRequest.create_user_message()"""
        request = MessageCreateRequest.create_user_message("Hello")
        assert request.content == "Hello"
        assert request.type == MessageType.USER.value
        assert request.is_llm_message == True

    def test_create_system_message(self):
        """Test MessageCreateRequest.create_system_message()"""
        # Note: "system" is not a valid MessageType enum value, so this will raise ValueError
        # The method exists but will fail validation
        with pytest.raises(ValueError, match="Invalid message type"):
            MessageCreateRequest.create_system_message("System message")


class TestAgentStartRequest:
    """Test class for AgentStartRequest"""

    def test_init_default(self):
        """Test AgentStartRequest with defaults"""
        request = AgentStartRequest()
        assert request.model_name is None
        assert request.enable_thinking == False
        assert request.reasoning_effort == "low"
        assert request.stream == True
        assert request.enable_context_manager == False
        assert request.agent_id is None

    def test_init_custom(self):
        """Test AgentStartRequest with custom values"""
        request = AgentStartRequest(
            model_name="gpt-4",
            enable_thinking=True,
            reasoning_effort="high",
            stream=False,
            enable_context_manager=True,
            agent_id="agent_123"
        )
        assert request.model_name == "gpt-4"
        assert request.enable_thinking == True
        assert request.reasoning_effort == "high"
        assert request.stream == False
        assert request.enable_context_manager == True
        assert request.agent_id == "agent_123"


class TestThread:
    """Test class for Thread dataclass"""

    def test_init(self):
        """Test Thread initialization"""
        thread = Thread(
            thread_id="t1",
            account_id="a1",
            project_id="p1",
            metadata={},
            is_public=False,
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )
        assert thread.thread_id == "t1"
        assert thread.project_id == "p1"


class TestMessage:
    """Test class for Message dataclass"""

    def test_init(self):
        """Test Message initialization"""
        message = Message(
            message_id="m1",
            thread_id="t1",
            type="user",
            is_llm_message=True,
            content="Hello",
            created_at="2023-01-01",
            updated_at="2023-01-02",
            agent_id="a1",
            agent_version_id="v1",
            metadata={}
        )
        assert message.message_id == "m1"
        assert message.type == "user"


class TestPaginationInfo:
    """Test class for PaginationInfo"""

    def test_init(self):
        """Test PaginationInfo initialization"""
        pagination = PaginationInfo(page=1, limit=20, total=100, pages=5)
        assert pagination.page == 1
        assert pagination.limit == 20


class TestThreadsResponse:
    """Test class for ThreadsResponse"""

    def test_init(self):
        """Test ThreadsResponse initialization"""
        thread = Thread(
            thread_id="t1",
            account_id="a1",
            project_id=None,
            metadata={},
            is_public=False,
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )
        pagination = PaginationInfo(page=1, limit=20, total=1, pages=1)
        response = ThreadsResponse(threads=[thread], pagination=pagination)
        assert len(response.threads) == 1


class TestMessagesResponse:
    """Test class for MessagesResponse"""

    def test_init(self):
        """Test MessagesResponse initialization"""
        message = Message(
            message_id="m1",
            thread_id="t1",
            type="user",
            is_llm_message=True,
            content="Hello",
            created_at="2023-01-01",
            updated_at="2023-01-02",
            agent_id="a1",
            agent_version_id="v1",
            metadata={}
        )
        response = MessagesResponse(messages=[message])
        assert len(response.messages) == 1


class TestCreateThreadResponse:
    """Test class for CreateThreadResponse"""

    def test_init(self):
        """Test CreateThreadResponse initialization"""
        response = CreateThreadResponse(thread_id="t1", project_id="p1")
        assert response.thread_id == "t1"
        assert response.project_id == "p1"


class TestAgentStartResponse:
    """Test class for AgentStartResponse"""

    def test_init(self):
        """Test AgentStartResponse initialization"""
        response = AgentStartResponse(agent_run_id="r1", status="running")
        assert response.agent_run_id == "r1"
        assert response.status == "running"


class TestToDict:
    """Test class for to_dict function"""

    def test_to_dict_with_dataclass(self):
        """Test to_dict with dataclass"""
        request = MessageCreateRequest(content="Hello")
        result = to_dict(request)
        assert isinstance(result, dict)
        assert result["content"] == "Hello"

    def test_to_dict_with_non_dataclass(self):
        """Test to_dict with non-dataclass"""
        result = to_dict("string")
        assert result == "string"


class TestFromDict:
    """Test class for from_dict function"""

    def test_from_dict_with_dataclass(self):
        """Test from_dict with dataclass"""
        data = {
            "thread_id": "t1",
            "account_id": "a1",
            "project_id": "p1",
            "metadata": {},
            "is_public": False,
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02"
        }
        result = from_dict(Thread, data)
        assert isinstance(result, Thread)
        assert result.thread_id == "t1"

    def test_from_dict_with_project_field_mapping(self):
        """Test from_dict maps 'project' to 'project_id' for Thread"""
        data = {
            "thread_id": "t1",
            "account_id": "a1",
            "project": "p1",  # API returns 'project' not 'project_id'
            "metadata": {},
            "is_public": False,
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02"
        }
        result = from_dict(Thread, data)
        assert result.project_id == "p1"

    def test_from_dict_filters_unknown_fields(self):
        """Test from_dict filters unknown fields"""
        data = {
            "thread_id": "t1",
            "account_id": "a1",
            "project_id": "p1",
            "metadata": {},
            "is_public": False,
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02",
            "message_count": 5,  # Unknown field
            "recent_agent_runs": []  # Unknown field
        }
        result = from_dict(Thread, data)
        assert not hasattr(result, "message_count")
        assert not hasattr(result, "recent_agent_runs")

    def test_from_dict_with_missing_required_fields(self):
        """Test from_dict handles missing required fields with defaults"""
        data = {
            "thread_id": "t1"
            # Missing all other required fields
        }
        result = from_dict(Thread, data)
        assert result.account_id == ""  # Default
        assert result.project_id is None  # Default
        assert result.metadata == {}  # Default
        assert result.is_public == False  # Default
        assert result.created_at == ""  # Default (covers line 133)
        assert result.updated_at == ""  # Default (covers line 135)

    def test_from_dict_with_non_dataclass(self):
        """Test from_dict with non-dataclass"""
        result = from_dict(str, "test")
        assert result == "test"


class TestThreadsClient:
    """Test class for ThreadsClient"""

    def test_init_without_auth(self):
        """Test ThreadsClient initialization without auth"""
        with patch('a2abase.api.threads.httpx.AsyncClient') as mock_client:
            client = ThreadsClient("http://api.com")
            assert client.base_url == "http://api.com"
            assert client.timeout == 30.0

    def test_init_with_auth(self):
        """Test ThreadsClient initialization with auth"""
        with patch('a2abase.api.threads.httpx.AsyncClient') as mock_client:
            client = ThreadsClient("http://api.com", auth_token="token123")
            call_kwargs = mock_client.call_args[1]
            assert "X-API-Key" in call_kwargs["headers"]  # ThreadsClient sets X-API-Key in headers
            assert call_kwargs["headers"]["X-API-Key"] == "token123"

    def test_init_with_custom_headers(self):
        """Test ThreadsClient initialization with custom headers (covers line 148)"""
        with patch('a2abase.api.threads.httpx.AsyncClient') as mock_client:
            client = ThreadsClient("http://api.com", custom_headers={"Custom": "Header"})
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["headers"]["Custom"] == "Header"
            # Verify custom headers are merged with default headers
            assert call_kwargs["headers"]["Content-Type"] == "application/json"

    def test_init_strips_trailing_slash(self):
        """Test ThreadsClient strips trailing slash"""
        with patch('a2abase.api.threads.httpx.AsyncClient'):
            client = ThreadsClient("http://api.com/")
            assert client.base_url == "http://api.com"

    @pytest.mark.asyncio
    async def test_close(self):
        """Test ThreadsClient.close()"""
        mock_client = AsyncMock()
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            await client.close()
            mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test ThreadsClient as context manager"""
        mock_client = AsyncMock()
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            async with ThreadsClient("http://api.com") as client:
                assert isinstance(client, ThreadsClient)
            mock_client.aclose.assert_called_once()

    def test_handle_response_success(self):
        """Test _handle_response with success"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        client = ThreadsClient("http://api.com")
        result = client._handle_response(mock_response)
        assert result == {"data": "test"}

    def test_handle_response_error_with_json(self):
        """Test _handle_response with error and JSON detail"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Error"}
        mock_response.text = "Error text"
        
        client = ThreadsClient("http://api.com")
        with pytest.raises(RuntimeError, match="API error"):
            client._handle_response(mock_response)

    def test_handle_response_error_without_json(self):
        """Test _handle_response with error without JSON"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception()
        mock_response.text = "Error text"
        
        client = ThreadsClient("http://api.com")
        with pytest.raises(RuntimeError, match="API error"):
            client._handle_response(mock_response)

    @pytest.mark.asyncio
    async def test_get_threads(self):
        """Test get_threads()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "threads": [{
                "thread_id": "t1",
                "account_id": "a1",
                "project_id": None,
                "metadata": {},
                "is_public": False,
                "created_at": "2023-01-01",
                "updated_at": "2023-01-02"
            }],
            "pagination": {"page": 1, "limit": 20, "total": 1, "pages": 1}
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            result = await client.get_threads()
            assert isinstance(result, ThreadsResponse)

    @pytest.mark.asyncio
    async def test_get_thread(self):
        """Test get_thread()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "thread_id": "t1",
            "account_id": "a1",
            "project_id": "p1",
            "metadata": {},
            "is_public": False,
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02"
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            result = await client.get_thread("t1")
            assert isinstance(result, Thread)

    @pytest.mark.asyncio
    async def test_get_thread_messages(self):
        """Test get_thread_messages()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [{
                "message_id": "m1",
                "thread_id": "t1",
                "type": "user",
                "is_llm_message": True,
                "content": "Hello",
                "created_at": "2023-01-01",
                "updated_at": "2023-01-02",
                "agent_id": "a1",
                "agent_version_id": "v1",
                "metadata": {}
            }]
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            result = await client.get_thread_messages("t1")
            assert isinstance(result, MessagesResponse)

    @pytest.mark.asyncio
    async def test_add_message_to_thread(self):
        """Test add_message_to_thread()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message_id": "m1",
            "thread_id": "t1",
            "type": "user",
            "is_llm_message": True,
            "content": "Hello",
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02",
            "agent_id": "a1",
            "agent_version_id": "v1",
            "metadata": {}
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            result = await client.add_message_to_thread("t1", "Hello")
            assert isinstance(result, Message)

    @pytest.mark.asyncio
    async def test_delete_message_from_thread(self):
        """Test delete_message_from_thread()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            await client.delete_message_from_thread("t1", "m1")
            mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_message(self):
        """Test create_message()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message_id": "m1",
            "thread_id": "t1",
            "type": "user",
            "is_llm_message": True,
            "content": "Hello",
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02",
            "agent_id": "a1",
            "agent_version_id": "v1",
            "metadata": {}
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            request = MessageCreateRequest(content="Hello")
            result = await client.create_message("t1", request)
            assert isinstance(result, Message)

    @pytest.mark.asyncio
    async def test_create_thread_with_name(self):
        """Test create_thread() with name"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"thread_id": "t1", "project_id": "p1"}
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            result = await client.create_thread("Test Thread")
            assert isinstance(result, CreateThreadResponse)
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args[1]
            assert "data" in call_kwargs

    @pytest.mark.asyncio
    async def test_create_thread_without_name(self):
        """Test create_thread() without name"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"thread_id": "t1", "project_id": "p1"}
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            result = await client.create_thread()
            assert isinstance(result, CreateThreadResponse)

    @pytest.mark.asyncio
    async def test_delete_thread(self):
        """Test delete_thread() raises NotImplementedError"""
        client = ThreadsClient("http://api.com")
        with pytest.raises(NotImplementedError):
            await client.delete_thread("t1")

    def test_get_agent_run_stream_url(self):
        """Test get_agent_run_stream_url()"""
        client = ThreadsClient("http://api.com")
        url = client.get_agent_run_stream_url("run_123")
        assert url == "http://api.com/agent-run/run_123/stream"

    def test_get_agent_run_stream_url_with_token(self):
        """Test get_agent_run_stream_url() with token"""
        client = ThreadsClient("http://api.com")
        url = client.get_agent_run_stream_url("run_123", token="token123")
        assert url == "http://api.com/agent-run/run_123/stream"

    @pytest.mark.asyncio
    async def test_start_agent(self):
        """Test start_agent()"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"agent_run_id": "r1", "status": "running"}
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('a2abase.api.threads.httpx.AsyncClient', return_value=mock_client):
            client = ThreadsClient("http://api.com")
            request = AgentStartRequest(agent_id="a1")
            result = await client.start_agent("t1", request)
            assert isinstance(result, AgentStartResponse)
            assert result.agent_run_id == "r1"


class TestCreateThreadsClient:
    """Test class for create_threads_client function"""

    def test_create_threads_client(self):
        """Test create_threads_client()"""
        with patch('a2abase.api.threads.ThreadsClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            result = create_threads_client("http://api.com", "token")
            assert result == mock_client
            mock_client_class.assert_called_once_with(
                base_url="http://api.com",
                auth_token="token",
                custom_headers=None,
                timeout=120.0
            )

