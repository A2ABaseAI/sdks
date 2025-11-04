"""
Example: Data Provider Agent
Demonstrates DATA_PROVIDERS_TOOL for accessing structured data from various providers.
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
    desired_name = "Data Provider Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a data provider assistant. You can access structured data from various "
                "providers including APIs, databases, and data services. Help users fetch, analyze, "
                "and integrate data from multiple sources."
            ),
            mcp_tools=[BaseAITool.DATA_PROVIDERS_TOOL],
        )
        created = True

    # Example: Fetch and analyze data
    run = await agent.run(
        "Fetch current market data for technology stocks from available data providers. "
        "Analyze the trends and create a summary report with key insights.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

