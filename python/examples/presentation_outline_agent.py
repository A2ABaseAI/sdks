"""
Example: Presentation Outline Agent
Demonstrates PRESENTATION_OUTLINE_TOOL for creating presentation outlines.
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
    desired_name = "Presentation Outline Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a presentation outline assistant. You can create structured outlines for "
                "presentations, organize content logically, and help users plan effective presentations. "
                "Focus on clarity, flow, and engaging content structure."
            ),
            a2abase_tools=[A2ABaseTools.SB_FILES_TOOL],
        )
        created = True

    # Example: Create presentation outline
    run = await agent.run(
        "Create a presentation outline for a product launch. The presentation should include: "
        "introduction, problem statement, solution overview, key features, pricing, and call to action. "
        "Make it engaging and suitable for a 15-minute presentation.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

