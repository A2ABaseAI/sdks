"""
Example: Automation Agent - Common Use Case
Demonstrates task automation using multiple tools.
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
    desired_name = "Automation Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are an automation assistant. You can automate repetitive tasks using files, "
                "shell commands, and web interactions. Help users save time by automating workflows, "
                "data processing, and routine operations."
            ),
            mcp_tools=[BaseAITool.FILES_TOOL, BaseAITool.SHELL_TOOL, BaseAITool.BROWSER_TOOL],
        )
        created = True

    # Example: Automate tasks
    run = await agent.run(
        "Automate the following tasks: 1) Scan the current directory for log files, "
        "2) Extract error messages from the last 24 hours, 3) Create a summary report, "
        "4) Archive old log files older than 7 days. Complete all steps and report the results.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

