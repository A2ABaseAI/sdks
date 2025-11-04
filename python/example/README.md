# BaseAI Python SDK Examples

This directory contains comprehensive examples demonstrating all available tools and common use cases for the BaseAI Python SDK.

## Tool-Specific Examples

Each example demonstrates a specific tool from the BaseAITool enum:

### File Management
- **`file_manager_agent.py`** - Demonstrates `FILES_TOOL` for reading, writing, and managing files
- **`file_upload_agent.py`** - Demonstrates `UPLOAD_FILE_TOOL` for uploading files to the sandbox

### Development Tools
- **`shell_automation_agent.py`** - Demonstrates `SHELL_TOOL` for executing system commands and automation
- **`web_development_agent.py`** - Demonstrates `WEB_DEV_TOOL` for creating Next.js applications
- **`deployment_agent.py`** - Demonstrates `DEPLOY_TOOL` for deploying web applications
- **`expose_service_agent.py`** - Demonstrates `EXPOSE_TOOL` for exposing local services to the internet

### Image Tools
- **`vision_analysis_agent.py`** - Demonstrates `VISION_TOOL` for analyzing and understanding images
- **`image_search_agent.py`** - Demonstrates `IMAGE_SEARCH_TOOL` for searching images on the web
- **`image_editing_agent.py`** - Demonstrates `IMAGE_EDIT_TOOL` for editing and manipulating images

### Content Creation
- **`document_agent.py`** - Demonstrates `DOCS_TOOL` for creating and managing documents
- **`spreadsheet_agent.py`** - Demonstrates `SHEETS_TOOL` for creating and managing spreadsheets
- **`presentation_outline_agent.py`** - Demonstrates `PRESENTATION_OUTLINE_TOOL` for creating presentation outlines
- **`presentation_agent.py`** - Demonstrates `PRESENTATION_TOOL` for creating full presentations
- **`design_agent.py`** - Demonstrates `DESIGN_TOOL` for creating visual content and designs

### Knowledge and Data
- **`knowledge_base_agent.py`** - Demonstrates `KB_TOOL` for accessing and managing knowledge bases
- **`data_provider_agent.py`** - Demonstrates `DATA_PROVIDERS_TOOL` for accessing structured data

### Search and Browser
- **`customer_support_triage.py`** - Demonstrates `WEB_SEARCH_TOOL`
- **`lead_enrichment_outreach.py`** - Demonstrates `WEB_SEARCH_TOOL` and `BROWSER_TOOL`

## Common Use Case Examples

These examples demonstrate real-world scenarios using multiple tools:

### Research and Analysis
- **`research_agent.py`** - Comprehensive research using web search and browser tools
- **`market_research_agent.py`** - Market research with data analysis and reporting
- **`data_analysis_agent.py`** - Data analysis with files, spreadsheets, and data providers

### Development and Quality Assurance
- **`code_review_agent.py`** - Code review and analysis using files and shell tools
- **`qa_testing_agent.py`** - Quality assurance and testing automation
- **`complex_multi_agent_pipeline.py`** - Multi-agent workflow (already exists)

### Content Creation
- **`content_creation_agent.py`** - Comprehensive content creation workflow
- **`visual_content_agent.py`** - Visual content creation and analysis
- **`social_media_agent.py`** - Social media content creation and management
- **`documentation_agent.py`** - Comprehensive documentation creation

### Automation and Workflows
- **`automation_agent.py`** - Task automation using multiple tools
- **`email_automation_agent.py`** - Email processing and automation
- **`web_scraping_agent.py`** - Web scraping and data extraction

### Business Operations
- **`customer_support_triage.py`** - Customer support automation
- **`product_analytics_report.py`** - Product analytics and reporting
- **`contract_summary_risk.py`** - Contract analysis
- **`lead_enrichment_outreach.py`** - Lead enrichment
- **`daily_support_digest.py`** - Daily support digest
- **`report_generation_agent.py`** - Comprehensive report generation

## Usage

All examples require the `BASEAI_API_KEY` environment variable to be set:

```bash
export BASEAI_API_KEY="pk_xxx:sk_xxx"
cd python
PYTHONPATH=. python3 example/<example_name>.py
```

## Running in Google Colab

Run examples directly in Google Colab:

**[Open Quick Start Notebook in Google Colab](https://colab.research.google.com/github/A2ABaseAI/sdks/blob/main/python/example/quick_start.ipynb)**

**Available Example Files (Google Colab can open Python files directly):**
- [Customer Support Triage](https://colab.research.google.com/github/A2ABaseAI/sdks/blob/main/python/example/customer_support_triage.py)
- [Research Agent](https://colab.research.google.com/github/A2ABaseAI/sdks/blob/main/python/example/research_agent.py)
- [File Manager Agent](https://colab.research.google.com/github/A2ABaseAI/sdks/blob/main/python/example/file_manager_agent.py)
- [Web Development Agent](https://colab.research.google.com/github/A2ABaseAI/sdks/blob/main/python/example/web_development_agent.py)

**Quick Start in Colab:**

```python
# Install the SDK
!pip install baseai-sdk

import os
from baseai import BaseAI
from baseai.tools import BaseAITool

# Set API key (use Colab's secrets or environment variables)
os.environ['BASEAI_API_KEY'] = 'pk_xxx:sk_xxx'

# Create client
client = BaseAI(api_key=os.getenv("BASEAI_API_KEY"), api_url="https://a2abase.ai/api")

# Create thread
thread = await client.Thread.create()

# Create agent
agent = await client.Agent.create(
    name="Research Agent",
    system_prompt="You are a research assistant.",
    mcp_tools=[BaseAITool.WEB_SEARCH_TOOL, BaseAITool.BROWSER_TOOL],
)

# Run agent
run = await agent.run("Research the latest AI developments", thread)

# Stream results
async for chunk in run.get_stream():
    print(chunk, end="")
```

**Note:** In Google Colab, you can use `await` directly in cells. Click any notebook link above to open it directly in Colab.

## Example Structure

Each example follows this pattern:

1. Import required modules
2. Check for API key (fail fast with helpful error)
3. Create or find an agent with appropriate tools
4. Run the agent with a specific task
5. Stream and print the results
6. Clean up if the agent was created

## Tool Coverage

All tools from `BaseAITool` enum are covered:

- ✅ FILES_TOOL
- ✅ SHELL_TOOL
- ✅ WEB_DEV_TOOL
- ✅ DEPLOY_TOOL
- ✅ EXPOSE_TOOL
- ✅ VISION_TOOL
- ✅ BROWSER_TOOL
- ✅ WEB_SEARCH_TOOL
- ✅ IMAGE_SEARCH_TOOL
- ✅ IMAGE_EDIT_TOOL
- ✅ KB_TOOL
- ✅ DESIGN_TOOL
- ✅ PRESENTATION_OUTLINE_TOOL
- ✅ PRESENTATION_TOOL
- ✅ SHEETS_TOOL
- ✅ UPLOAD_FILE_TOOL
- ✅ DOCS_TOOL
- ✅ DATA_PROVIDERS_TOOL

## Common Use Cases Covered

- ✅ Research and Information Gathering
- ✅ Data Analysis and Reporting
- ✅ Code Review and Quality Assurance
- ✅ Content Creation (Documents, Presentations, Designs)
- ✅ Automation and Workflows
- ✅ Web Scraping and Data Extraction
- ✅ Social Media Management
- ✅ Email Automation
- ✅ Market Research
- ✅ Documentation Generation
- ✅ Visual Content Creation
- ✅ Multi-Agent Pipelines

