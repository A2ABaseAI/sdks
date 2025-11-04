"""
Example: Market Research Agent - Common Use Case
Demonstrates comprehensive market research.
"""
import asyncio
import os
from baseai import BaseAI
from baseai.tools import BaseAITool


async def main():
    api_key = os.getenv("BASEAI_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        raise ValueError("Please set BASEAI_API_KEY environment variable or update the api_key in the script")
    client = BaseAI(api_key=api_key, api_url="https://a2abase.ai/api")

    thread = await client.Thread.create()
    desired_name = "Market Research Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a market research assistant. You can search the web, browse websites, "
                "access data providers, and create comprehensive research reports. Help users "
                "understand markets, competitors, and opportunities."
            ),
            mcp_tools=[
                BaseAITool.WEB_SEARCH_TOOL,
                BaseAITool.BROWSER_TOOL,
                BaseAITool.DATA_PROVIDERS_TOOL,
                BaseAITool.SHEETS_TOOL,
            ],
        )
        created = True

    # Example: Market research
    run = await agent.run(
        "Conduct market research for a new SaaS product in the project management space. "
        "Research competitors, pricing models, market size, and customer needs. Create a "
        "comprehensive report with a spreadsheet of findings and recommendations.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

