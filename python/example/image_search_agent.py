"""
Example: Image Search Agent
Demonstrates IMAGE_SEARCH_TOOL for searching images on the web.
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
    desired_name = "Image Search Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are an image search assistant. You can search for images on the web based on "
                "descriptions, keywords, or specific requirements. Help users find relevant images "
                "for their projects, presentations, or research."
            ),
            mcp_tools=[BaseAITool.IMAGE_SEARCH_TOOL],
        )
        created = True

    # Example: Search for images
    run = await agent.run(
        "Search for high-quality images of modern office spaces suitable for a company website. "
        "Find 5-10 relevant images and provide their URLs and descriptions.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

