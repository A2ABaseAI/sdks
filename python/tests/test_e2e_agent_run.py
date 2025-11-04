import pytest
import respx

from baseai import BaseAI
from baseai.api.threads import AgentStartRequest


@pytest.mark.asyncio
async def test_e2e_agent_run_flow():
    base_url = "https://a2abase.ai/api"
    client = BaseAI(api_key="pk_test", api_url=base_url)

    with respx.mock(base_url=base_url) as mock:
        mock.post("/agents").respond(200, json={
            "agent_id": "agent_123",
            "account_id": "acct_1",
            "name": "t",
            "system_prompt": "s",
            "custom_mcps": [],
            "agentpress_tools": {},
            "is_default": False,
            "created_at": "2025-01-01T00:00:00Z"
        })
        mock.post("/threads").respond(200, json={"thread_id": "th_123", "project_id": "proj_1"})
        mock.post("/threads/th_123/messages/add").respond(200, json={
            "message_id": "msg_1",
            "thread_id": "th_123",
            "type": "user",
            "is_llm_message": True,
            "content": {"content": "Ping"},
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "agent_id": "",
            "agent_version_id": "",
            "metadata": {}
        })
        mock.post("/thread/th_123/agent/start").respond(200, json={"agent_run_id": "run_1", "status": "started"})
        mock.get("/agent-run/run_1/stream").respond(200, text="data: {\"type\":\"assistant\",\"content\":\"{\\\"content\\\":\\\"Pong\\\"}\"}\n\n")

        thread = await client.Thread.create()
        agent = await client.Agent.create(name="t", system_prompt="s")
        run = await agent.run("Ping", thread)
        stream = await run.get_stream()

        chunks = []
        async for line in stream:
            chunks.append(line)

        assert any("Pong" in c for c in chunks)

