"""
Example: Spreadsheet Agent
Demonstrates SHEETS_TOOL for creating and managing spreadsheets.
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
    desired_name = "Spreadsheet Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a spreadsheet assistant. You can create, edit, and manage spreadsheets. "
                "Help users organize data, create formulas, generate charts, and perform data analysis. "
                "Focus on clarity, accuracy, and useful data visualization."
            ),
            a2abase_tools=[A2ABaseTools.SB_FILES_TOOL],
        )
        created = True

    # Example: Create a spreadsheet with data analysis
    run = await agent.run(
        "Create a spreadsheet to track monthly sales data. Include columns for: Date, Product, "
        "Quantity, Price, and Total. Add formulas to calculate totals and create a summary chart "
        "showing sales trends.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

