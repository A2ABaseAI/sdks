import asyncio
import os
from a2abase import A2ABaseClient
from a2abase.tools import A2ABaseTools


async def main():
    api_key = os.getenv("BASEAI_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        raise ValueError("Please set BASEAI_API_KEY environment variable or update the api_key in the script")
    client = A2ABaseClient(api_key=api_key, api_url="https://a2abase.ai/api")

    # Create thread
    thread = await client.Thread.create()

    # Get or create agent
    desired_name = "Daily Support Digest"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "Summarize top issues from Gmail and post to Slack with a Google Sheet log."
            ),
            a2abase_tools=[A2ABaseTools.BROWSER_TOOL, A2ABaseTools.WEB_SEARCH_TOOL],
        )
        created = True

    # Run the agent
    run = await agent.run("Process today's support digest.", thread)

    # Stream updates
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

