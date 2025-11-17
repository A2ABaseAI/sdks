"""
Example: Visual Content Agent - Common Use Case
Demonstrates visual content creation and analysis.
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
    desired_name = "Visual Content Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a visual content assistant. You can analyze images, search for images, "
                "edit images, create designs, and generate visual content. Help users create "
                "professional visual materials for their projects."
            ),
            a2abase_tools=[
                A2ABaseTools.SB_VISION_TOOL,
                A2ABaseTools.SB_IMAGE_EDIT_TOOL,
            ],
        )
        created = True

    # Example: Visual content workflow
    run = await agent.run(
        "Search for high-quality stock images of business professionals. Analyze the images "
        "to understand composition and style, then create a custom design for a company website "
        "header that matches the professional aesthetic.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

