from typing import AsyncGenerator

from .api.threads import ThreadsClient
from .api.utils import stream_from_url, MessageResponseUtil
from .api.threads import MessageLineResponse


class Thread:
    def __init__(self, client: ThreadsClient, thread_id: str):
        self._client = client
        self._thread_id = thread_id

    def get_thread_id(self):
        return self._thread_id

    async def get_account_id(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.account_id

    async def get_project_id(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.project_id

    async def get_project_name(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.project_id["name"]
    
    async def get_project_description(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.project_id["description"]

    async def is_public(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.project_id["is_public"]

    async def get_created_at(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.created_at

    async def get_updated_at(self):
        thread = await self._client.get_thread(self._thread_id)
        return thread.updated_at

    async def add_message(self, message: str):
        response = await self._client.add_message_to_thread(self._thread_id, message)
        return response.message_id

    async def del_message(self, message_id: str):
        await self._client.delete_message_from_thread(self._thread_id, message_id)

    async def get_messages(self):
        response = await self._client.get_thread_messages(self._thread_id)
        return response.messages

    async def get_agent_runs(self, agent_run_id: str | None = None):
        data = await self._client.client.get(f"/threads/{self._thread_id}")
        if data.status_code >= 400:
            return None
        thread_data = data.json()
        recent_runs = thread_data.get("recent_agent_runs", [])
        print(recent_runs)
        if not recent_runs:
            return None
        
        agent_runs = [AgentRun(self, run.get("id") or run.get("agent_run_id")) for run in recent_runs]
        
        # Filter by ID if provided
        if agent_run_id:
            filtered = [run for run in agent_runs if run._agent_run_id == agent_run_id]
            return filtered[0] if filtered else None
        
        return agent_runs
    
    async def get_agent_run(self, agent_run_id: str):
        return await self.get_agent_runs(agent_run_id=agent_run_id)

class AgentRun:
    def __init__(self, thread: Thread, agent_run_id: str):
        self._thread = thread
        self._agent_run_id = agent_run_id
        self._agent_run_data = None  # Cache for API response

    async def _get_agent_run_data(self):
        """Fetch agent run data from API and cache it."""
        if self._agent_run_data is None:
            response = await self._thread._client.client.get(f"/agent-run/{self._agent_run_id}")
            
            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", f"HTTP {response.status_code}")
                except:
                    error_detail = f"HTTP {response.status_code}"
                raise Exception(f"Failed to fetch agent run {self._agent_run_id}: {error_detail}")
            self._agent_run_data = response.json()
        return self._agent_run_data

    async def get_agent_run_id(self):
        return self._agent_run_id

    async def get_threadId(self):
        data = await self._get_agent_run_data()
        return data["threadId"]

    async def get_status(self):
        data = await self._get_agent_run_data()
        return data["status"]

    async def get_started_at(self):
        data = await self._get_agent_run_data()
        return data["startedAt"]

    async def get_completed_at(self):
        data = await self._get_agent_run_data()
        return data["completedAt"]

    async def get_error(self):
        data = await self._get_agent_run_data()
        return data["error"]

    async def get_stream(self) -> AsyncGenerator[str, None]:
        stream_url = self._thread._client.get_agent_run_stream_url(self._agent_run_id)
        stream = stream_from_url(stream_url, headers=self._thread._client.headers)
        async for line in stream:
            yield MessageResponseUtil.to_model(line)

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
