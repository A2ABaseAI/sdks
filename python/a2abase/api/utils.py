from typing import AsyncGenerator, Dict, Any, Optional
import httpx
import json
from a2abase.api.threads import (
    MessageLineResponse,
    StatusMessageLineResponse,
    AssistantResponseEndMessageLineResponse,
    AssistantMessageLineResponse,
    UserMessageLineResponse,
)


class MessageResponseUtil:
    """Utility class for message response operations."""
    
    @staticmethod
    def to_model(json_str: str) -> Optional[MessageLineResponse]:
        """Convert JSON string to appropriate MessageLineResponse sub-type model."""
        try:
            line = json_str.replace("data: ", "")
            data = json.loads(line)
            
            # Handle completion status
            if "status" in data and data["status"] == "completed":
                return line
            
            # Parse the base message to get all fields
            base_message = MessageLineResponse.from_dict(data)
            
            # Determine and return the appropriate sub-type based on message type
            message_type = data.get("type", "")
            
            if message_type == "status":
                return StatusMessageLineResponse(
                    message_id=base_message.message_id,
                    thread_id=base_message.thread_id,
                    is_llm_message=base_message.is_llm_message,
                    content=base_message.content,
                    metadata=base_message.metadata,
                    created_at=base_message.created_at,
                    updated_at=base_message.updated_at,
                    agent_id=base_message.agent_id,
                    agent_version_id=base_message.agent_version_id,
                )
            elif message_type == "assistant_response_end":
                return AssistantResponseEndMessageLineResponse(
                    message_id=base_message.message_id,
                    thread_id=base_message.thread_id,
                    is_llm_message=base_message.is_llm_message,
                    content=base_message.content,
                    metadata=base_message.metadata,
                    created_at=base_message.created_at,
                    updated_at=base_message.updated_at,
                    agent_id=base_message.agent_id,
                    agent_version_id=base_message.agent_version_id,
                )
            elif message_type == "assistant":
                return AssistantMessageLineResponse(
                    message_id=base_message.message_id,
                    thread_id=base_message.thread_id,
                    is_llm_message=base_message.is_llm_message,
                    content=base_message.content,
                    metadata=base_message.metadata,
                    created_at=base_message.created_at,
                    updated_at=base_message.updated_at,
                    agent_id=base_message.agent_id,
                    agent_version_id=base_message.agent_version_id,
                )
            elif message_type == "user":
                return UserMessageLineResponse(
                    message_id=base_message.message_id,
                    thread_id=base_message.thread_id,
                    is_llm_message=base_message.is_llm_message,
                    content=base_message.content,
                    metadata=base_message.metadata,
                    created_at=base_message.created_at,
                    updated_at=base_message.updated_at,
                    agent_id=base_message.agent_id,
                    agent_version_id=base_message.agent_version_id,
                )
            else:
                # Return base type for unknown types
                return base_message
                
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print(f"Error converting JSON string to MessageLineResponse: {e}")
            print(f"JSON string: {json_str}")
            return None


async def stream_from_url(url: str, **kwargs) -> AsyncGenerator[str, None]:
    """
    Helper function that takes a URL and returns an async generator yielding lines.

    Args:
        url: The URL to stream from
        **kwargs: Additional arguments to pass to httpx.AsyncClient.stream()

    Yields:
        str: Each line from the streaming response
    """
    # Configure timeout settings to prevent ReadTimeout errors
    timeout = httpx.Timeout(
        connect=30.0,
        read=300.0,
        write=30.0,
        pool=30.0,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("GET", url, **kwargs) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.strip():
                    yield line.strip()

