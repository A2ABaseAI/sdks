"""
Example: Data Analysis Agent - Common Use Case
Demonstrates data analysis using multiple tools.
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
    desired_name = "Data Analysis Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a data analysis assistant. You can read data files, create spreadsheets, "
                "perform calculations, generate charts, and provide insights. Help users understand "
                "their data and make data-driven decisions."
            ),
            a2abase_tools=[A2ABaseTools.SB_FILES_TOOL, A2ABaseTools.DATA_PROVIDERS_TOOL],
        )
        created = True

    # Example: Data analysis
    run = await agent.run(
        "Analyze any CSV or Excel files in the current directory. Identify key trends, "
        "calculate statistics, create visualizations, and generate a comprehensive analysis report "
        "with actionable insights.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

