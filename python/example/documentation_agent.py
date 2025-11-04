"""
Example: Documentation Agent - Common Use Case
Demonstrates comprehensive documentation creation.
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
    desired_name = "Documentation Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a documentation assistant. You can read code files, create documents, "
                "presentations, and maintain knowledge bases. Help users create comprehensive, "
                "well-organized documentation for their projects."
            ),
            mcp_tools=[
                BaseAITool.FILES_TOOL,
                BaseAITool.DOCS_TOOL,
                BaseAITool.PRESENTATION_TOOL,
                BaseAITool.KB_TOOL,
            ],
        )
        created = True

    # Example: Create documentation
    run = await agent.run(
        "Analyze the codebase in the current directory and create comprehensive documentation "
        "including: README.md with setup instructions, API documentation, architecture overview "
        "document, and a presentation for onboarding new developers.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

