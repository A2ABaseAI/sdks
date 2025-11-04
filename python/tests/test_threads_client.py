import pytest
import respx

from baseai.api.threads import create_threads_client, MessageCreateRequest


@pytest.mark.asyncio
async def test_thread_lifecycle():
    base_url = "https://a2abase.ai/api"
    async with create_threads_client(base_url=base_url, auth_token="pk_test") as client:
        with respx.mock(base_url=base_url) as mock:
            mock.post("/threads").respond(200, json={"thread_id": "th_123", "project_id": "proj_1"})
            mock.post("/threads/th_123/messages").respond(200, json={
                "message_id": "msg_1",
                "thread_id": "th_123",
                "type": "user",
                "is_llm_message": True,
                "content": {"content": "Hello"},
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "agent_id": "",
                "agent_version_id": "",
                "metadata": {}
            })

            created = await client.create_thread()
            assert created.thread_id == "th_123"

            msg = await client.create_message("th_123", MessageCreateRequest.create_user_message("Hello"))
            assert msg.message_id == "msg_1"

