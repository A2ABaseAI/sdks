import importlib
import types
import pytest
import respx


BASE_URL = "https://a2abase.ai/api"


def setup_common_mocks(mock: respx.MockRouter):
    # Common thread creation
    mock.post("/threads").respond(200, json={"thread_id": "th_123", "project_id": "proj_1"})
    # Add message via /add
    mock.post("/threads/th_123/messages/add").respond(200, json={
        "message_id": "msg_1",
        "thread_id": "th_123",
        "type": "user",
        "is_llm_message": True,
        "content": {"content": "OK"},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "agent_id": "",
        "agent_version_id": "",
        "metadata": {}
    })
    # Start agent
    mock.post("/thread/th_123/agent/start").respond(200, json={"agent_run_id": "run_1", "status": "started"})
    # Stream
    mock.get("/agent-run/run_1/stream").respond(200, text="data: {\"type\":\"assistant\",\"content\":\"{\\\"content\\\":\\\"OK\\\"}\"}\n\n")


def setup_agent_create(mock: respx.MockRouter, name: str, system_prompt: str):
    mock.post("/agents").respond(200, json={
        "agent_id": f"agent_{name}",
        "account_id": "acct_1",
        "name": name,
        "system_prompt": system_prompt,
        "custom_mcps": [],
        "agentpress_tools": {},
        "is_default": False,
        "created_at": "2025-01-01T00:00:00Z"
    })


async def run_example(module: types.ModuleType):
    # Patch API URL inside the example by setting env or replacing client creation.
    # Our examples construct BaseAI(api_url=...) explicitly, so just run main().
    await module.main()


@pytest.mark.asyncio
async def test_daily_support_digest_example():
    ex = importlib.import_module("example.daily_support_digest")
    with respx.mock(base_url=BASE_URL) as mock:
        setup_agent_create(mock, "Daily Support Digest", "Summarize top issues from Gmail and post to Slack with a Google Sheet log.")
        setup_common_mocks(mock)
        await run_example(ex)


@pytest.mark.asyncio
async def test_lead_enrichment_outreach_example():
    ex = importlib.import_module("example.lead_enrichment_outreach")
    with respx.mock(base_url=BASE_URL) as mock:
        setup_agent_create(mock, "Lead Enrichment & Outreach", "Given a CSV of leads, enrich with LinkedIn/website, score, and generate outreach snippets.")
        setup_common_mocks(mock)
        await run_example(ex)


@pytest.mark.asyncio
async def test_product_analytics_report_example():
    ex = importlib.import_module("example.product_analytics_report")
    with respx.mock(base_url=BASE_URL) as mock:
        setup_agent_create(mock, "Weekly Product Analytics", "Fetch product metrics, generate charts, and summarize key trends for the week.")
        setup_common_mocks(mock)
        await run_example(ex)


@pytest.mark.asyncio
async def test_customer_support_triage_example():
    ex = importlib.import_module("example.customer_support_triage")
    with respx.mock(base_url=BASE_URL) as mock:
        setup_agent_create(mock, "Customer Support Triage", "Monitor support inbox, label priority, suggest responses, and escalate critical issues.")
        setup_common_mocks(mock)
        await run_example(ex)


@pytest.mark.asyncio
async def test_contract_summary_risk_example():
    ex = importlib.import_module("example.contract_summary_risk")
    with respx.mock(base_url=BASE_URL) as mock:
        setup_agent_create(mock, "Contract Summary & Risk", "Summarize contracts, extract key terms, and flag risks with rationale.")
        setup_common_mocks(mock)
        await run_example(ex)


@pytest.mark.asyncio
async def test_complex_multi_agent_pipeline_example():
    ex = importlib.import_module("example.complex_multi_agent_pipeline")
    with respx.mock(base_url=BASE_URL) as mock:
        # Multiple agent creates (3 times)
        setup_agent_create(mock, "Market Research", "Research competitors, gather pricing/features, and produce a summary table.")
        setup_agent_create(mock, "Copywriter", "Write landing page copy based on research with headline, subhead, and CTA.")
        setup_agent_create(mock, "Outreach", "Draft outreach emails for top 5 prospects with personalization snippets.")
        setup_common_mocks(mock)
        # Reuse same thread/run endpoints for simplicity in the example
        await run_example(ex)


