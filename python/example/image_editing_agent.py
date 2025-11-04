"""
Example: Image Editing Agent
Demonstrates IMAGE_EDIT_TOOL for editing and manipulating images.
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
    desired_name = "Image Editing Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are an image editing assistant. You can edit and manipulate images, apply filters, "
                "resize, crop, adjust colors, and perform various image transformations. Help users "
                "create professional-looking images for their projects."
            ),
            mcp_tools=[BaseAITool.IMAGE_EDIT_TOOL],
        )
        created = True

    # Example: Edit images
    run = await agent.run(
        "Find any images in the current directory, resize them to 800x600 pixels, "
        "apply a professional filter, and save them with a '_edited' suffix.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

