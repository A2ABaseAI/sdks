"""
Example: QA Testing Agent - Common Use Case
Demonstrates quality assurance and testing automation.
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

    # thread = await client.Thread.create()
    desired_name = "QA Testing Agent"
    agent = await client.Agent.find_by_name(desired_name)
    print(agent)
    # created = False
    # if agent is None:
    #     agent = await client.Agent.create(
    #         name=desired_name,
    #         system_prompt=(
    #             "You are a QA testing assistant. You can read code files, execute tests, "
    #             "analyze results, and create test reports. Help developers ensure code quality "
    #             "and catch bugs before deployment."
    #         ),
    #         mcp_tools=[BaseAITool.FILES_TOOL, BaseAITool.SHELL_TOOL],
    #     )
    #     created = True

    # # Example: QA testing
    # run = await agent.run(
    #     "Review the test files in the current directory. Run the test suite, analyze the results, "
    #     "identify any failures or issues, and create a comprehensive test report with "
    #     "recommendations for improvement.",
    #     thread
    # )
    # stream = await run.get_stream()
    # async for line in stream:
    #     print(line)

    # if created:
        # await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

