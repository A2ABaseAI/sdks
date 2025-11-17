"""
Example: Shell Automation Agent
Demonstrates SHELL_TOOL for executing system commands and automation.
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
    desired_name = "Shell Automation Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a system automation assistant. You can execute shell commands to automate tasks, "
                "install packages, manage processes, and perform system maintenance. Always verify commands "
                "before execution and explain what you're doing."
            ),
            a2abase_tools=[A2ABaseTools.SB_SHELL_TOOL],
        )
        created = True

    # Example: System maintenance and package management
    run = await agent.run(
        "Check the system disk usage and list the top 10 largest files in the current directory. "
        "Then create a summary report of the findings.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

