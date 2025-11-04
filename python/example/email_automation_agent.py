"""
Example: Email Automation Agent - Common Use Case
Demonstrates email automation and processing.
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
    desired_name = "Email Automation Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are an email automation assistant. You can browse web interfaces, read files, "
                "and create spreadsheets. Help users automate email processing, categorize messages, "
                "generate responses, and manage email workflows."
            ),
            mcp_tools=[BaseAITool.BROWSER_TOOL, BaseAITool.FILES_TOOL, BaseAITool.SHEETS_TOOL],
        )
        created = True

    # Example: Email automation
    run = await agent.run(
        "Process incoming emails from Gmail. Categorize them by priority, extract key information, "
        "create a summary spreadsheet with email metadata, and generate draft responses for urgent items.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

