"""
Example: Research Agent - Common Use Case
Demonstrates comprehensive research using multiple tools.
"""
import asyncio
import os
from a2abase import A2ABaseClient
from a2abase.tools import A2ABaseTools


async def main():
    api_key = os.getenv("BASEAI_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        raise ValueError("Please set BASEAI_API_KEY environment variable or update the api_key in the script")
    client = A2ABaseClient(api_key=api_key, api_url="https://a2abase.ai/api")

    thread = await client.Thread.create()
    desired_name = "Research Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a research assistant. You can search the web, browse websites, and gather "
                "information from multiple sources. Help users conduct thorough research, find reliable "
                "sources, and compile comprehensive reports."
            ),
            a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL, A2ABaseTools.BROWSER_TOOL],
        )
        created = True

    # Example: Comprehensive research
    run = await agent.run(
        "Research the latest trends in artificial intelligence and machine learning for 2025. "
        "Find information from at least 5 different sources, compare perspectives, and create "
        "a comprehensive report with citations.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

