"""
Example: Content Creation Agent - Common Use Case
Demonstrates content creation using multiple tools.
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
    desired_name = "Content Creation Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a content creation assistant. You can create documents, presentations, "
                "designs, and visual content. Help users create professional, engaging content "
                "for various purposes including marketing, education, and documentation."
            ),
            a2abase_tools=[
                A2ABaseTools.SB_FILES_TOOL,
                ],
        )
        created = True

    # Example: Create comprehensive content
    run = await agent.run(
        "Create a complete marketing package including: a document with marketing copy, "
        "a presentation deck, visual designs for social media, and a summary spreadsheet with "
        "content calendar and metrics tracking.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

