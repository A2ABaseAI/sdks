from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, AsyncGenerator
import httpx

from ..models import (
    Role,
    MessageType,
    BaseMessage,
    ChatMessage,
    AgentRun,
    ContentObject,
)


@dataclass
class MessageCreateRequest:
    content: str
    type: str = "user"
    is_llm_message: bool = True

    def __post_init__(self):
        try:
            MessageType(self.type)
        except ValueError:
            raise ValueError(f"Invalid message type: {self.type}")

    @classmethod
    def create_user_message(cls, content: str) -> "MessageCreateRequest":
        return cls(content=content, type=MessageType.USER.value, is_llm_message=True)

    @classmethod
    def create_system_message(cls, content: str) -> "MessageCreateRequest":
        return cls(content=content, type="system", is_llm_message=False)


@dataclass
class AgentStartRequest:
    model_name: Optional[str] = None
    enable_thinking: Optional[bool] = False
    reasoning_effort: Optional[str] = "low"
    stream: Optional[bool] = True
    enable_context_manager: Optional[bool] = False
    agent_id: Optional[str] = None


@dataclass
class Thread:
    thread_id: str
    account_id: str
    project_id: Optional[str]
    metadata: Dict[str, Any]
    is_public: bool
    created_at: str
    updated_at: str


@dataclass
class Message:
    message_id: str
    thread_id: str
    type: str
    is_llm_message: bool
    content: Any
    created_at: str
    updated_at: str
    agent_id: str
    agent_version_id: str
    metadata: Any


@dataclass
class PaginationInfo:
    page: int
    limit: int
    total: int
    pages: int


@dataclass
class ThreadsResponse:
    threads: List[Thread]
    pagination: PaginationInfo


@dataclass
class MessagesResponse:
    messages: List[Message]


@dataclass
class CreateThreadResponse:
    thread_id: str
    project_id: str


@dataclass
class AgentStartResponse:
    agent_run_id: str
    status: str


def to_dict(obj) -> Dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return obj


def from_dict(cls, data: Dict[str, Any]):
    if not hasattr(cls, "__dataclass_fields__"):
        return data
    field_types = {field.name: field.type for field in cls.__dataclass_fields__.values()}
    processed = {}
    for k, v in data.items():
        # Handle 'project' -> 'project_id' mapping for Thread
        if k == "project" and cls == Thread:
            processed["project_id"] = v
        # Only include fields that exist in the dataclass
        elif k in field_types:
            processed[k] = v
        # Skip unknown fields like 'message_count', 'recent_agent_runs', etc.
    
    # Handle missing required fields with defaults for Thread
    if cls == Thread:
        if "account_id" not in processed:
            processed["account_id"] = data.get("account_id", "")
        if "project_id" not in processed:
            processed["project_id"] = data.get("project_id", None)
        if "metadata" not in processed:
            processed["metadata"] = data.get("metadata", {})
        if "is_public" not in processed:
            processed["is_public"] = data.get("is_public", False)
        if "created_at" not in processed:
            processed["created_at"] = data.get("created_at", "")
        if "updated_at" not in processed:
            processed["updated_at"] = data.get("updated_at", "")
    
    return cls(**processed)


class ThreadsClient:
    def __init__(self, base_url: str, auth_token: Optional[str] = None, custom_headers: Optional[Dict[str, str]] = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["X-API-Key"] = auth_token
        if custom_headers:
            self.headers.update(custom_headers)
        self.client = httpx.AsyncClient(headers=self.headers, timeout=timeout, base_url=self.base_url)

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code in (200, 201):
            return response.json()
        try:
            error_message = response.json().get("detail", response.text)
        except:
            error_message = response.text
        raise RuntimeError(f"API error ({response.status_code}): {error_message}")

    async def get_threads(self, page: int = 1, limit: int = 1000) -> ThreadsResponse:
        params = {"page": page, "limit": limit}
        data = self._handle_response(await self.client.get("/threads", params=params))
        pagination = from_dict(PaginationInfo, data["pagination"])
        threads = [from_dict(Thread, t) for t in data["threads"]]
        return ThreadsResponse(threads=threads, pagination=pagination)

    async def get_thread(self, thread_id: str) -> Thread:
        data = self._handle_response(await self.client.get(f"/threads/{thread_id}"))
        return from_dict(Thread, data)

    async def get_thread_messages(self, thread_id: str, order: str = "desc") -> MessagesResponse:
        params = {"order": order}
        data = self._handle_response(await self.client.get(f"/threads/{thread_id}/messages", params=params))
        messages = [from_dict(Message, m) for m in data["messages"]]
        return MessagesResponse(messages=messages)

    async def add_message_to_thread(self, thread_id: str, message: str) -> Message:
        data = self._handle_response(await self.client.post(f"/threads/{thread_id}/messages/add", params={"message": message}, headers={k: v for k, v in self.headers.items() if k != "Content-Type"}))
        return from_dict(Message, data)

    async def delete_message_from_thread(self, thread_id: str, message_id: str) -> None:
        self._handle_response(await self.client.delete(f"/threads/{thread_id}/messages/{message_id}"))

    async def create_message(self, thread_id: str, request: MessageCreateRequest) -> Message:
        data = self._handle_response(await self.client.post(f"/threads/{thread_id}/messages", json=to_dict(request)))
        return from_dict(Message, data)

    async def create_thread(self, name: Optional[str] = None) -> CreateThreadResponse:
        # Backend expects Form data for name; send only when provided
        if name is None:
            resp = await self.client.post("/threads", headers={k: v for k, v in self.headers.items() if k != "Content-Type"})
        else:
            resp = await self.client.post("/threads", data={"name": name}, headers={k: v for k, v in self.headers.items() if k != "Content-Type"})
        data = self._handle_response(resp)
        return from_dict(CreateThreadResponse, data)

    async def delete_thread(self, thread_id: str) -> None:
        raise NotImplementedError("Not implemented")

    def get_agent_run_stream_url(self, agent_run_id: str, token: Optional[str] = None) -> str:
        return f"{self.base_url}/agent-run/{agent_run_id}/stream"

    async def start_agent(self, thread_id: str, request: "AgentStartRequest") -> AgentStartResponse:
        data = self._handle_response(
            await self.client.post(f"/thread/{thread_id}/agent/start", json=to_dict(request))
        )
        return from_dict(AgentStartResponse, data)


def create_threads_client(base_url: str, auth_token: Optional[str] = None, custom_headers: Optional[Dict[str, str]] = None, timeout: float = 120.0) -> ThreadsClient:
    return ThreadsClient(base_url=base_url, auth_token=auth_token, custom_headers=custom_headers, timeout=timeout)

