"""
Example: Vision Analysis Agent
Demonstrates VISION_TOOL for analyzing and understanding images.
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
    desired_name = "Vision Analysis Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a vision analysis assistant. You can analyze images, extract text from them, "
                "identify objects, understand diagrams, and provide detailed descriptions. Help users "
                "understand visual content and extract meaningful information."
            ),
            a2abase_tools=[A2ABaseTools.SB_VISION_TOOL],
        )
        created = True

    # Example: Analyze images and extract information
    run = await agent.run(
        "Analyze any images in the current directory. Describe what you see, extract any text, "
        "and provide insights about the content. If there are diagrams or charts, explain what they show.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

