"""
Example: File Upload Agent
Demonstrates UPLOAD_FILE_TOOL for uploading files to the sandbox.
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
    desired_name = "File Upload Agent"
    agent = await client.Agent.find_by_name(desired_name)
    created = False
    if agent is None:
        agent = await client.Agent.create(
            name=desired_name,
            system_prompt=(
                "You are a file upload assistant. You can upload files to the sandbox environment "
                "for processing, analysis, or collaboration. Help users manage file uploads and "
                "ensure files are properly organized and accessible."
            ),
            a2abase_tools=[A2ABaseTools.SB_FILES_TOOL],
        )
        created = True

    # Example: Upload and process files
    run = await agent.run(
        "Upload any CSV files from the local directory to the sandbox. Then analyze the data "
        "and create a summary report of the findings.",
        thread
    )
    stream = await run.get_stream()
    async for line in stream:
        print(line)

    if created:
        await agent.delete()


if __name__ == "__main__":
    asyncio.run(main())

