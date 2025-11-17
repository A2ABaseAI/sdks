"""
Test suite for models.py - All model classes and enums
"""
import pytest

from a2abase.models import (
    Role,
    ContentObject,
    MessageType,
    BaseMessage,
    UserMessage,
    AssistantMessage,
    ToolResultMessage,
    StatusMessage,
    AssistantResponseEndMessage,
    ChatMessage,
    AgentRun,
)


class TestRole:
    """Test class for Role enum"""

    def test_role_values(self):
        """Test Role enum values"""
        assert Role.USER == "user"
        assert Role.ASSISTANT == "assistant"
        assert Role.SYSTEM == "system"

    def test_role_is_string_enum(self):
        """Test Role is a string enum"""
        assert isinstance(Role.USER, str)


class TestContentObject:
    """Test class for ContentObject dataclass"""

    def test_init_minimal(self):
        """Test ContentObject with minimal fields"""
        content = ContentObject(role=Role.USER, content="Hello")
        assert content.role == Role.USER
        assert content.content == "Hello"
        assert content.tool_calls is None

    def test_init_with_tool_calls(self):
        """Test ContentObject with tool_calls"""
        content = ContentObject(
            role=Role.ASSISTANT,
            content="Response",
            tool_calls=[{"name": "tool1", "arguments": {}}]
        )
        assert content.tool_calls is not None


class TestMessageType:
    """Test class for MessageType enum"""

    def test_message_type_values(self):
        """Test MessageType enum values"""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"
        assert MessageType.TOOL == "tool"
        assert MessageType.STATUS == "status"
        assert MessageType.ASSISTANT_RESPONSE_END == "assistant_response_end"

    def test_message_type_is_string_enum(self):
        """Test MessageType is a string enum"""
        assert isinstance(MessageType.USER, str)


class TestBaseMessage:
    """Test class for BaseMessage dataclass"""

    def test_init(self):
        """Test BaseMessage initialization"""
        message = BaseMessage(
            message_id="m1",
            thread_id="t1",
            type=MessageType.USER,
            is_llm_message=True,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )
        assert message.message_id == "m1"
        assert message.type == MessageType.USER


class TestUserMessage:
    """Test class for UserMessage dataclass"""

    def test_init(self):
        """Test UserMessage initialization"""
        message = UserMessage(
            message_id="m1",
            thread_id="t1",
            is_llm_message=True,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02",
            content="Hello"
        )
        assert message.type == MessageType.USER
        assert message.content == "Hello"

    def test_type_is_automatically_set(self):
        """Test UserMessage type is automatically set"""
        message = UserMessage(
            message_id="m1",
            thread_id="t1",
            is_llm_message=True,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02",
            content="Hello"
        )
        # Type should be set automatically, not passed
        assert message.type == MessageType.USER


class TestAssistantMessage:
    """Test class for AssistantMessage dataclass"""

    def test_init(self):
        """Test AssistantMessage initialization"""
        content_obj = ContentObject(role=Role.ASSISTANT, content="Response")
        message = AssistantMessage(
            message_id="m1",
            thread_id="t1",
            is_llm_message=True,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02",
            content=content_obj
        )
        assert message.type == MessageType.ASSISTANT
        assert isinstance(message.content, ContentObject)


class TestToolResultMessage:
    """Test class for ToolResultMessage dataclass"""

    def test_init(self):
        """Test ToolResultMessage initialization"""
        message = ToolResultMessage(
            message_id="m1",
            thread_id="t1",
            is_llm_message=False,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02",
            content={"tool": "result"}
        )
        assert message.type == MessageType.TOOL
        assert message.content == {"tool": "result"}


class TestStatusMessage:
    """Test class for StatusMessage dataclass"""

    def test_init(self):
        """Test StatusMessage initialization"""
        message = StatusMessage(
            message_id="m1",
            thread_id="t1",
            is_llm_message=False,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02",
            content={"status": "running"}
        )
        assert message.type == MessageType.STATUS
        assert message.content == {"status": "running"}


class TestAssistantResponseEndMessage:
    """Test class for AssistantResponseEndMessage dataclass"""

    def test_init(self):
        """Test AssistantResponseEndMessage initialization"""
        message = AssistantResponseEndMessage(
            message_id="m1",
            thread_id="t1",
            is_llm_message=False,
            metadata={},
            created_at="2023-01-01",
            updated_at="2023-01-02",
            content={"end": True}
        )
        assert message.type == MessageType.ASSISTANT_RESPONSE_END
        assert message.content == {"end": True}


class TestChatMessage:
    """Test class for ChatMessage type union"""

    def test_chat_message_union(self):
        """Test ChatMessage is a union type"""
        from typing import get_args, get_origin
        
        origin = get_origin(ChatMessage)
        args = get_args(ChatMessage)
        
        assert origin is not None  # It's a Union
        assert UserMessage in args
        assert AssistantMessage in args
        assert ToolResultMessage in args
        assert StatusMessage in args
        assert AssistantResponseEndMessage in args


class TestAgentRun:
    """Test class for AgentRun dataclass"""

    def test_init(self):
        """Test AgentRun initialization"""
        agent_run = AgentRun(
            id="r1",
            thread_id="t1",
            status="running",
            started_at="2023-01-01",
            completed_at=None,
            error=None,
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )
        assert agent_run.id == "r1"
        assert agent_run.status == "running"
        assert agent_run.completed_at is None
        assert agent_run.error is None

    def test_init_with_all_fields(self):
        """Test AgentRun with all fields"""
        agent_run = AgentRun(
            id="r1",
            thread_id="t1",
            status="completed",
            started_at="2023-01-01",
            completed_at="2023-01-02",
            error="Error message",
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )
        assert agent_run.completed_at == "2023-01-02"
        assert agent_run.error == "Error message"

