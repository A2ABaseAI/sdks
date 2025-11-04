import pytest
import respx
import httpx

from baseai.api.agents import create_agents_client, AgentCreateRequest, AgentResponse


@pytest.mark.asyncio
async def test_create_and_get_agent():
    base_url = "https://a2abase.ai/api"
    async with create_agents_client(base_url=base_url, auth_token="pk_test") as client:
        with respx.mock(base_url=base_url) as mock:
            mock.post("/agents").respond(200, json={
                "agent_id": "agent_123",
                "account_id": "acct_1",
                "name": "Test Agent",
                "system_prompt": "You are helpful",
                "custom_mcps": [],
                "agentpress_tools": {},
                "is_default": False,
                "created_at": "2025-01-01T00:00:00Z"
            })

            mock.get("/agents/agent_123").respond(200, json={
                "agent_id": "agent_123",
                "account_id": "acct_1",
                "name": "Test Agent",
                "system_prompt": "You are helpful",
                "custom_mcps": [],
                "agentpress_tools": {},
                "is_default": False,
                "created_at": "2025-01-01T00:00:00Z"
            })

            created = await client.create_agent(AgentCreateRequest(name="Test Agent", system_prompt="You are helpful"))
            assert isinstance(created, AgentResponse)
            assert created.agent_id == "agent_123"

            fetched = await client.get_agent("agent_123")
            assert fetched.name == "Test Agent"

