"""
Example: Service Expose Agent
Demonstrates EXPOSE_TOOL for exposing local services to the internet.
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
    desired_name = "Service Expose Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a service exposure assistant. You can expose local services to the internet "
                "for testing, sharing, or collaboration. Help users create secure tunnels and share "
                "access to their local development servers."
            ),
            a2abase_tools=[A2ABaseTools.SB_EXPOSE_TOOL],
        )
        created = True

    # Example: Expose a local service
    run = await agent.run(
        "Expose the local development server running on port 3000 to the internet. "
        "Provide the public URL and any necessary access information.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

