from typing import AsyncGenerator

from .api.threads import ThreadsClient
from .api.utils import stream_from_url


class Thread:
    def __init__(self, client: ThreadsClient, thread_id: str):
        self._client = client
        self._thread_id = thread_id

    async def add_message(self, message: str):
        response = await self._client.add_message_to_thread(self._thread_id, message)
        return response.message_id

    async def del_message(self, message_id: str):
        await self._client.delete_message_from_thread(self._thread_id, message_id)

    async def get_messages(self):
        response = await self._client.get_thread_messages(self._thread_id)
        return response.messages

    async def get_agent_runs(self):
        # Get thread data directly to access recent_agent_runs
        data = await self._client.client.get(f"/threads/{self._thread_id}")
        if data.status_code >= 400:
            return None
        thread_data = data.json()
        recent_runs = thread_data.get("recent_agent_runs", [])
        if not recent_runs:
            return None
        return [AgentRun(self, run.get("id") or run.get("agent_run_id")) for run in recent_runs]


class AgentRun:
    def __init__(self, thread: Thread, agent_run_id: str):
        self._thread = thread
        self._agent_run_id = agent_run_id

    async def get_stream(self) -> AsyncGenerator[str, None]:
        stream_url = self._thread._client.get_agent_run_stream_url(self._agent_run_id)
        stream = stream_from_url(stream_url, headers=self._thread._client.headers)
        return stream


class A2ABaseThread:
    def __init__(self, client: ThreadsClient):
        self._client = client

    async def create(self, name: str | None = None) -> Thread:
        thread_data = await self._client.create_thread(name)
        return Thread(self._client, thread_data.thread_id)

    async def get(self, thread_id: str) -> Thread:
        return Thread(self._client, thread_id)

    async def delete(self, thread_id: str) -> None:
        await self._client.delete_thread(thread_id)
