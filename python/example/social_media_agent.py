"""
Example: Social Media Agent - Common Use Case
Demonstrates social media content creation and management.
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
    desired_name = "Social Media Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a social media assistant. You can search for images, create designs, "
                "write content, and create spreadsheets. Help users create engaging social media "
                "content, plan campaigns, and manage their social media presence."
            ),
            mcp_tools=[
                BaseAITool.IMAGE_SEARCH_TOOL,
                BaseAITool.DESIGN_TOOL,
                BaseAITool.DOCS_TOOL,
                BaseAITool.SHEETS_TOOL,
            ],
        )
        created = True

    # Example: Social media content
    run = await agent.run(
        "Create a week's worth of social media content for a tech startup. Include: "
        "7 image posts with designs, captions for each post, a content calendar spreadsheet, "
        "and a document with hashtag suggestions and engagement strategies.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

