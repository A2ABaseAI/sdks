"""
Example: Web Scraping Agent - Common Use Case
Demonstrates web scraping and data extraction.
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
    desired_name = "Web Scraping Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a web scraping assistant. You can browse websites, search the web, "
                "extract data, and organize it into files and spreadsheets. Help users gather "
                "information from websites, extract structured data, and organize it for analysis."
            ),
            a2abase_tools=[A2ABaseTools.BROWSER_TOOL, A2ABaseTools.WEB_SEARCH_TOOL, A2ABaseTools.SB_FILES_TOOL],
        )
        created = True

    # Example: Web scraping
    run = await agent.run(
        "Scrape product information from an e-commerce website. Extract product names, "
        "prices, descriptions, and ratings. Organize the data into a CSV file and create "
        "a summary document with insights about the products.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

