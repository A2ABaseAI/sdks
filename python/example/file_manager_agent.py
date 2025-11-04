"""
Example: File Manager Agent
Demonstrates FILES_TOOL for reading, writing, and managing files.
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
    desired_name = "File Manager Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a file management assistant. You can read, write, edit, and organize files. "
                "Help users manage their file system, create documentation, organize files into directories, "
                "and perform file operations safely."
            ),
            mcp_tools=[BaseAITool.FILES_TOOL],
        )
        created = True

    # Example: Organize project files and create documentation
    run = await agent.run(
        "Create a README.md file for this project describing the file structure, "
        "then organize any loose files into appropriate directories.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

