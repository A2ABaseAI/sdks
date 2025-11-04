"""
Example: Code Review Agent - Common Use Case
Demonstrates code analysis and review using file and shell tools.
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
    desired_name = "Code Review Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a code review assistant. You can read and analyze code files, run tests, "
                "and provide feedback on code quality, best practices, and potential improvements. "
                "Help developers write better, more maintainable code."
            ),
            mcp_tools=[BaseAITool.FILES_TOOL, BaseAITool.SHELL_TOOL],
        )
        created = True

    # Example: Code review
    run = await agent.run(
        "Review all Python files in the current directory. Check for code quality issues, "
        "potential bugs, performance problems, and adherence to best practices. Create a "
        "detailed review report with recommendations.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

