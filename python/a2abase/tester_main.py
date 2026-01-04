import asyncio  
import os
import sys
from pathlib import Path

# This allows tester.py to work when run from anywhere
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from a2abase import A2ABaseClient, thread
from a2abase.tools import A2ABaseTools
from a2abase.api.utils import MessageResponseUtil
from a2abase.api.threads import (
    MessageLineResponse,
    StatusMessageLineResponse,
    AssistantResponseEndMessageLineResponse,
    AssistantMessageLineResponse,
    UserMessageLineResponse,
    StatusType,
)

async def main():
    client = A2ABaseClient(api_key=os.getenv("BASEAI_API_KEY"), api_url="https://a2abase.ai/api")
    print("--------------------------")
    print("Testing agents functions")
    print("--------------------------")
    agents = await client.Agent.list_agents(page=1, limit=100)
    for agent in agents:
        details = await agent.get_details()
        print(details.name)
        # print(details.system_prompt)
        # print(details.custom_mcps)
        # print(details.agentpress_tools)
        # print(details.is_default)
        # print(details.created_at)
        # print(details.updated_at)
        # print(details.account_id)
        # print(details.description)
        # print(details.avatar)
        # print(details.avatar_color)
    agent = await client.Agent.find_by_name("FAQ agent")
    details = await agent.get_details()
    print(details.agent_id)
    # print(details.system_prompt)
    # print(details.custom_mcps)
    # print(details.agentpress_tools)
    # print(details.is_default)
    # print(details.created_at)
    # print(details.updated_at)
    # print(details.account_id)
    # print(details.description)
    # print(details.avatar)
    # print(details.avatar_color)
    agent = await client.Agent.get_get_id("2eb96f46-2e43-426c-9892-f23dcebd33f9")
    details = await agent.get_details()
    print(details.name)

    print("--------------------------")
    print("Testing threads functions")
    print("--------------------------")
    thread = await client.new_thread(details.agent_id)
    print(thread.get_thread_id())
    print(await thread.get_created_at())
    print(await thread.get_updated_at())
    print(await thread.get_account_id())
    print(await thread.get_project_id())
    print(await thread.get_project_name())
    print(await thread.get_project_description())
    print(await thread.is_public())

    print("--------------------------")
    print("Testing add message")
    print("--------------------------")
    await thread.add_message("msg 1")
    await thread.add_message("msg 2")
    messages = await thread.get_messages()
    for message in messages:
        print(f"Message ID: {message.message_id}")
        print(f"Content: {message.content}")
        print(f"Type: {message.type}")
        print(f"Is LLM Message: {message.is_llm_message}")
        print(f"Created At: {message.created_at}")
        print(f"Updated At: {message.updated_at}")
        print(f"Thread ID: {message.thread_id}")
        print(f"Agent ID: {message.agent_id}") # we're getting null here its bug 
        print(f"Agent Version ID: {message.agent_version_id}") # we're getting null here its bug 
        print(f"Metadata: {message.metadata}")

    print("--------------------------")
    print("Testing delete message")
    print("--------------------------")
    await thread.del_message(messages[0].message_id)
    messages = await thread.get_messages()
    for message in messages:
        print(f"Message ID: {message.message_id}")
        print(f"Content: {message.content}")
        print(f"Type: {message.type}")

    print("--------------------------")
    print("Testing get agent runs")
    print("--------------------------")
    agent_runs = await thread.get_agent_runs()
    if agent_runs:
        for agent_run in agent_runs:
            print(f"Agent Run ID: {agent_run.agent_run_id}")
            print(f"Agent ID: {agent_run.agent_id}")
            print(f"Agent Version ID: {agent_run.agent_version_id}")
            print(f"Created At: {agent_run.created_at}")
    else:
        print("No agent runs found")


    agent_run = await agent.run("Hello, how are you?", thread)
    print("--------------------------")
    print("Testing get stream")
    print("--------------------------")
    stream = agent_run.get_stream()
    async for message in stream:
        if message is None:
            continue
        
        # Handle completion status (string)
        if isinstance(message, str):
            print(f"Completion: {message}")
            continue
        
        # Handle different message types
        if isinstance(message, StatusMessageLineResponse):
            status_type = message.get_status_type()
            if status_type == StatusType.THREAD_RUN_START:
                print("🟢 Thread run started")
            elif status_type == StatusType.THREAD_RUN_END:
                print("🔴 Thread run ended")
            elif status_type == StatusType.ASSISTANT_RESPONSE_START:
                print("💬 Assistant response started")
            elif status_type == StatusType.FINISH:
                print("✅ Finished")
            else:
                print(f"📊 Status: {message.content}")
        
        elif isinstance(message, AssistantMessageLineResponse):
            content_text = message.get_content_text()
            if content_text:
                print(f"🤖 Assistant: {content_text}")
            else:
                print(f"🤖 Assistant: {message.content}")
        
        elif isinstance(message, UserMessageLineResponse):
            content_text = message.get_content_text()
            if content_text:
                print(f"👤 User: {content_text}")
            else:
                print(f"👤 User: {message.content}")
        
        elif isinstance(message, AssistantResponseEndMessageLineResponse):
            print("🏁 Assistant response ended")
        
        else:
            print(f"📨 [{message.type}]: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())