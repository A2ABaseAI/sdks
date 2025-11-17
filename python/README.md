# A2ABaseAI Python SDK

<p align="center">
  <img src="https://a2abase.ai/belarabyai-symbol.svg" alt="A2ABaseAI" width="110" />
</p>

<p align="center">
  <b>One import: tools, auth, sandboxes and deployment included.</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/a2abase/"><img src="https://img.shields.io/pypi/v/a2abase?label=Python%20SDK" alt="PyPI"></a>
  <a href="https://a2abase.ai/settings/api-keys"><img src="https://img.shields.io/badge/API-Key%20Dashboard-blue" alt="API Keys"></a>
  <img src="https://img.shields.io/badge/status-open%20source-success" alt="Open Source">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT License">
</p>

---

> A2ABaseAI Python SDK for building and shipping production grade AI agents.  
> One line gives you access to 50+ tools, 300+ integrations, and all major LLMs through a single unified platform.

A2ABaseAI SDK handles authentication, tool execution, sandboxes, and integrations so you can stay focused on agent logic.  
Bring your own tool subscriptions or use ours. Migrate between providers without touching your agent code.

## 🔍 What is A2ABaseAI SDK?

```python
from a2abase.tools import A2ABaseTools

# Hundreds of ready to use integration and tools for agents
tool = A2ABaseTools.*
```

- One import gives your agents access to a large tool catalog  
- One API key unlocks better rates with the providers you already use  
- Ship faster with batteries included workflows, sandboxes, and deployments  

## 🔑 Get your API key

1. Sign up at **[A2ABaseAI Dashboard](https://a2abase.ai/settings/api-keys)**
2. Create an API key
3. Set it locally

```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
```

**Install**: `pip install a2abase`

You are ready to build.

### Core capabilities

- Agent and workflow management  
- Tool orchestration and execution  
- Secure sandboxes for code, shells, and browsers  
- Long term knowledge and document storage  
- Deep integration library through MCP  

The SDK exposes high level concepts: `A2ABaseClient`, `Agent`, `Thread`, `Run`, and `A2ABaseTools`.

## 📊 Tool categories at a glance

| Category               | Examples                                           | Primary use cases                          |
| ---------------------- | -------------------------------------------------- | -------------------------------------------|
| File and workspace     | Files, Upload, Knowledge Base                      | Code, docs, configs, retrieval             |
| Development            | Shell, Web Dev, Deploy, Expose                     | Build and ship apps from inside agents     |
| Web and browser        | Browser, Advanced Browser, Web Search, Image Search| Scraping, research, end to end automation  |
| Content creation       | Docs, Sheets, Presentations, Design                | Reports, decks, dashboards, creative work  |
| AI and vision          | Vision, Image Edit                                 | Screenshot analysis, visual agents         |
| Data and integrations  | Data Providers, MCP integrations                   | Connect SaaS, CRMs, clouds, and databases  |
| Search                 | People Search, Company Search                      | Prospecting and enrichment                 |
| System automation      | Computer Automation                                | GUI and desktop control                    |

For the complete tool reference see the SDK specific docs.

## ✅ The A2ABaseAI solution

**One SDK. One API key. Everything wired together.**

- ✅ 50+ built in tools  
  Web search, browser control, files, web dev, docs, sheets, presentations, vision, images, and more  
- ✅ 300+ MCP integrations  
  Connect Gmail, Slack, GitHub, Notion, CRMs, databases, cloud, and hundreds of services  
- ✅ All major LLMs behind one interface  
  Swap models and providers without touching your agent code  
- ✅ Secure, isolated sandboxes  
  Run code, shells, browsers, and tools in contained environments  
- ✅ Pay as you go  
  Only pay for what runs. No platform lock in, no per seat fees  
- ✅ Type safe SDK  
  Full IntelliSense and autocomplete in Python  

No More:
- ❌ Juggling 10+ API keys and accounts  
- ❌ Gluing together multiple SDKs and libraries  
- ❌ Hunting for the right tools and benchmarking them  
- ❌ Writing fragile one off integrations  
- ❌ Owning all auth and security yourself  
- ❌ Paying for a pile of separate subscriptions  

**Install one SDK, call one client, ship a working agent in minutes.**

## 🚀 Quick start

```python
import asyncio
import os
from a2abase import A2ABaseClient
from a2abase.tools import A2ABaseTools

async def main():
    api_key = os.getenv("BASEAI_API_KEY")
    if not api_key:
        raise ValueError("Please set BASEAI_API_KEY environment variable")
    
    client = A2ABaseClient(api_key=api_key, api_url="https://a2abase.ai/api")

    thread = await client.Thread.create()
    agent = await client.Agent.create(
        name="My Assistant",
        system_prompt="You are a helpful AI assistant.",
        a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL],
    )

    run = await agent.run("Hello, how are you?", thread)
    stream = await run.get_stream()
    async for chunk in stream:
        print(chunk, end="")

asyncio.run(main())
```

## 🛠 Tooling overview

The SDK exposes a unified tool enum (`A2ABaseTools`) that covers the full tool catalog.

Instead of configuring dozens of separate tools, you enable categories and get a coherent surface:

### File and workspace

- File operations: create, read, edit, rewrite, delete  
- Upload files into the sandbox workspace  
- Knowledge base with semantic search, sync, and long term memory  

Typical uses: codegen, configuration files, document workflows, retrieval for agents.

### Development and deployment

- Shell tools in isolated environments  
- Web dev tools for React, Next.js, Vite, and shadcn based apps  
- Deployment helpers and port exposure for preview links  

Typical uses: build agents that scaffold apps, run migrations, deploy small services.

### Web and browser automation

- Standard web search and scraping  
- Browser automation with full DOM control  
- Multi tab flows, form filling, scrolling, screenshots  

Typical uses: research agents, competitor intelligence, test runners, web workflows.

### Content and productivity

- Docs, sheets, and presentations  
- Design and image editing tools  
- Presentation outlines and structured content planning  

Typical uses: report writers, slide generators, internal tooling, marketing assistants.

### AI and vision

- Vision tools for screenshots and document images  
- Image generation and editing  

Typical uses: UI review, PDF parsing, creative image agents.

### Data and integrations

Through data provider tools and MCP you can connect to:

- Productivity: Gmail, Calendar, Slack, Notion, Linear, Asana, Jira, Trello  
- Dev and cloud: GitHub, GitLab, Bitbucket, Docker Hub, AWS, GCP, Azure  
- CRM and sales: Salesforce, HubSpot, Pipedrive, Zoho, Intercom  
- Data and storage: Google Sheets, Drive, Dropbox, MongoDB, Postgres, MySQL  
- Marketing and social: X, LinkedIn, Facebook, Instagram, Mailchimp, SendGrid  
- Commerce and payments: Shopify, Stripe, PayPal, WooCommerce, Square  

Plug in via Composio MCP servers or your own MCP endpoints.  
A2ABaseAI manages auth, credentials, and routing for you.

### Search and automation

- People search and company search for lead gen and enrichment  
- Computer and desktop automation for full system level workflows  

## 📚 Examples

The SDK ships with real world examples in `./examples/`.

Run examples:

```bash
# Python
cd python
PYTHONPATH=. python3 examples/<name>.py
```

You can also run Python examples directly in Google Colab.  
See the examples directory for details.

## 📖 Documentation

- [Python SDK docs](./README.md)  
- [GitHub Repository](https://github.com/A2ABaseAI/sdks)  

## 💬 Support

- Discord: https://discord.gg/qAncfHmYUm  

Bug reports and feature requests are welcome through GitHub issues.

## 🤝 Contributing

Contributions are welcome.

- Open an issue to discuss larger changes  
- Submit pull requests for bug fixes or new examples  
- Follow the style and lint rules for the SDK  

## 📄 License

Released under the **MIT License**.  
See `LICENSE` for full details.
