"""
Example: Document Agent
Demonstrates DOCS_TOOL for creating and managing documents.
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
    desired_name = "Document Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a document creation assistant. You can create, edit, and manage documents "
                "with formatting, structure, and rich content. Help users create professional documents "
                "for reports, proposals, documentation, or any written content."
            ),
            mcp_tools=[BaseAITool.DOCS_TOOL],
        )
        created = True

    # Example: Create a comprehensive document
    run = await agent.run(
        "Create a project proposal document for a mobile app development project. Include sections "
        "for: Executive Summary, Project Overview, Technical Requirements, Timeline, Budget, and "
        "Team Structure. Make it professional and detailed.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

