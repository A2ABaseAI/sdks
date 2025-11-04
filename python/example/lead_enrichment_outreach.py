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

    desired_name = "Lead Enrichment & Outreach"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "Given a CSV of leads, enrich with LinkedIn/website, score, and generate outreach snippets."
            ),
            mcp_tools=[BaseAITool.WEB_SEARCH_TOOL, BaseAITool.BROWSER_TOOL],
        )
        created = True

    run = await agent.run("Enrich leads from latest CSV and prepare outreach.", thread)
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    # Cleanup if we created it
    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

