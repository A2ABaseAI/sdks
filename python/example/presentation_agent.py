"""
Example: Presentation Agent
Demonstrates PRESENTATION_TOOL for creating and managing presentations.
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
    desired_name = "Presentation Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a presentation creation assistant. You can create full presentations with "
                "slides, visuals, and content. Help users create professional, engaging presentations "
                "for meetings, pitches, or educational purposes."
            ),
            mcp_tools=[BaseAITool.PRESENTATION_TOOL],
        )
        created = True

    # Example: Create full presentation
    run = await agent.run(
        "Create a complete presentation about 'The Future of AI in Healthcare'. Include 10-12 slides "
        "with visuals, statistics, and clear messaging. Make it suitable for a business audience.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

