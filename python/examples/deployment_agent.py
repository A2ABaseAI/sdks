"""
Example: Deployment Agent
Demonstrates DEPLOY_TOOL for deploying web applications.
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
    desired_name = "Deployment Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a deployment assistant. You can deploy web applications to various platforms, "
                "configure environment variables, set up CI/CD pipelines, and ensure applications are "
                "production-ready."
            ),
            a2abase_tools=[A2ABaseTools.SB_DEPLOY_TOOL],
        )
        created = True

    # Example: Deploy an application
    run = await agent.run(
        "Deploy the web application in the current directory. Check for any build errors, "
        "configure necessary environment variables, and provide the deployment URL once complete.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

