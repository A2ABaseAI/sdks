"""
Example: Web Development Agent
Demonstrates WEB_DEV_TOOL for creating and managing web applications.
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
    desired_name = "Web Development Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a web development assistant specializing in modern web applications. "
                "You can create Next.js applications with shadcn/ui components, set up routing, "
                "create responsive layouts, and implement best practices for web development."
            ),
            mcp_tools=[BaseAITool.WEB_DEV_TOOL],
        )
        created = True

    # Example: Create a modern web application
    run = await agent.run(
        "Create a Next.js application with a landing page that includes a hero section, "
        "features section, and contact form using shadcn/ui components.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

