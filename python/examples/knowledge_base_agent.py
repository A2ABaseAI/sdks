"""
Example: Knowledge Base Agent
Demonstrates KB_TOOL for accessing and managing knowledge base.
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
    desired_name = "Knowledge Base Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a knowledge base assistant. You can access, search, and manage information "
                "in knowledge bases. Help users find relevant information, answer questions based on "
                "documented knowledge, and maintain organized knowledge repositories."
            ),
            a2abase_tools=[A2ABaseTools.SB_FILES_TOOL],
        )
        created = True

    # Example: Query knowledge base
    run = await agent.run(
        "Search the knowledge base for information about API best practices and authentication methods. "
        "Create a summary document with the key findings.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

