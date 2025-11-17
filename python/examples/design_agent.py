"""
Example: Design Agent
Demonstrates DESIGN_TOOL for creating visual content and designs.
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
    desired_name = "Design Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a design assistant. You can create visual content, design graphics, "
                "create mockups, and generate visual assets. Help users create professional designs "
                "for their projects, presentations, or marketing materials."
            ),
            a2abase_tools=[A2ABaseTools.SB_FILES_TOOL],
        )
        created = True

    # Example: Create design assets
    run = await agent.run(
        "Create a logo design for a tech startup called 'InnovateAI'. The logo should be modern, "
        "minimalist, and reflect innovation. Save it as a high-resolution image file.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

