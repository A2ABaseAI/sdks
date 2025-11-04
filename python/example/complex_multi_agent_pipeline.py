import asyncio
import os
from baseai import BaseAI
from baseai.tools import BaseAITool


async def main():
    api_key = os.getenv("BASEAI_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        raise ValueError("Please set BASEAI_API_KEY environment variable or update the api_key in the script")
    client = BaseAI(api_key=api_key, api_url="https://a2abase.ai/api")

    # Create thread shared across agents
    thread = await client.Thread.create()

    # Research agent
    research = await client.Agent.find_by_name("Market Research")
    created_research = False
    if research is None:
        research = await client.Agent.create(
            name="Market Research",
            system_prompt="Research competitors, gather pricing/features, and produce a summary table.",
            mcp_tools=[BaseAITool.WEB_SEARCH_TOOL, BaseAITool.BROWSER_TOOL],
        )
        created_research = True

    # Copywriter agent
    copy = await client.Agent.find_by_name("Copywriter")
    created_copy = False
    if copy is None:
        copy = await client.Agent.create(
            name="Copywriter",
            system_prompt="Write landing page copy based on research with headline, subhead, and CTA.",
            mcp_tools=[],
        )
        created_copy = True

    # Outreach agent
    outreach = await client.Agent.find_by_name("Outreach")
    created_outreach = False
    if outreach is None:
        outreach = await client.Agent.create(
            name="Outreach",
            system_prompt="Draft outreach emails for top 5 prospects with personalization snippets.",
            mcp_tools=[],
        )
        created_outreach = True

    # Step 1: run research
    run1 = await research.run("Do research for our product vs competitors.", thread)
    stream1 = await run1.get_stream()
    async for line in stream1:
        print(line)

    # Step 2: feed output into copywriter (simple example, in practice parse prior output)
    run2 = await copy.run("Create landing page copy from the research above.", thread)
    stream2 = await run2.get_stream()
    async for line in stream2:
        print(line)

    # Step 3: generate outreach
    run3 = await outreach.run("Create 5 outreach emails targeting top prospects.", thread)
    stream3 = await run3.get_stream()
    async for line in stream3:
        print(line)

    # Cleanup any agents created during this run
    if created_research:
        await research.delete()
    if created_copy:
        await copy.delete()
    if created_outreach:
        await outreach.delete()


if __name__ == "__main__":
    asyncio.run(main())

