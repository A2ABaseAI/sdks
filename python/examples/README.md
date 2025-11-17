# A2ABase Python SDK Examples

This directory contains comprehensive examples demonstrating all available tools and common use cases for the A2ABase Python SDK.

## Tool-Specific Examples

Each example demonstrates a specific tool from the A2ABaseTools enum:

### File Management
- **`file_manager_agent.py`** - Demonstrates `SB_FILES_TOOL` for reading, writing, and managing files
- **`file_upload_agent.py`** - Demonstrates file operations using `SB_FILES_TOOL` (note: uses available alternative)

### Development Tools
- **`shell_automation_agent.py`** - Demonstrates `SB_SHELL_TOOL` for executing system commands and automation
- **`web_development_agent.py`** - Demonstrates file operations (note: WEB_DEV_TOOL is deactivated, uses `SB_FILES_TOOL` as alternative)
- **`deployment_agent.py`** - Demonstrates `SB_DEPLOY_TOOL` for deploying web applications
- **`expose_service_agent.py`** - Demonstrates `SB_EXPOSE_TOOL` for exposing local services to the internet

### Image Tools
- **`vision_analysis_agent.py`** - Demonstrates `SB_VISION_TOOL` for analyzing and understanding images
- **`image_search_agent.py`** - Demonstrates file operations (note: IMAGE_SEARCH_TOOL not available, uses `SB_FILES_TOOL` as alternative)
- **`image_editing_agent.py`** - Demonstrates `SB_IMAGE_EDIT_TOOL` for editing and manipulating images

### Content Creation
- **`document_agent.py`** - Demonstrates file operations (note: DOCS_TOOL not available, uses `SB_FILES_TOOL` as alternative)
- **`spreadsheet_agent.py`** - Demonstrates file operations (note: SHEETS_TOOL not available, uses `SB_FILES_TOOL` as alternative)
- **`presentation_outline_agent.py`** - Demonstrates file operations (note: PRESENTATION_OUTLINE_TOOL not available, uses `SB_FILES_TOOL` as alternative)
- **`presentation_agent.py`** - Demonstrates file operations (note: PRESENTATION_TOOL not available, uses `SB_FILES_TOOL` as alternative)
- **`design_agent.py`** - Demonstrates file operations (note: DESIGN_TOOL not available, uses `SB_FILES_TOOL` as alternative)

### Knowledge and Data
- **`knowledge_base_agent.py`** - Demonstrates file operations (note: KB_TOOL not available, uses `SB_FILES_TOOL` as alternative)
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

To run examples in Google Colab:

**Option 1: Open from GitHub**
1. Go to [Google Colab](https://colab.research.google.com/)
2. Click "File" → "Open notebook"
3. Select the "GitHub" tab
4. Enter: `A2ABaseAI/sdks`
5. Navigate to `python/example/quick_start.ipynb` or any example file

**Option 2: Manual Setup**
1. Open [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Copy code from any example file in this directory
4. Adapt for notebook use (remove `if __name__ == "__main__"` and use `await` directly)

**Quick Start in Colab:**

```python
# Install the SDK
!pip install a2abase-sdk

import os
from a2abase import A2ABaseClient
from a2abase.tools import A2ABaseTools

# Set API key (use Colab's secrets or environment variables)
os.environ['BASEAI_API_KEY'] = 'pk_xxx:sk_xxx'

# Create client
client = A2ABaseClient(api_key=os.getenv("BASEAI_API_KEY"), api_url="https://a2abase.ai/api")

# Create thread
thread = await client.Thread.create()

# Create agent
agent = await client.Agent.create(
    name="Research Agent",
    system_prompt="You are a research assistant.",
    a2abase_tools=[A2ABaseTools.WEB_SEARCH_TOOL, A2ABaseTools.BROWSER_TOOL],
)

# Run agent
run = await agent.run("Research the latest AI developments", thread)

# Stream results
stream = await run.get_stream()
async for chunk in stream:
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

All available tools from `A2ABaseTools` enum are covered:

- ✅ SB_FILES_TOOL
- ✅ SB_SHELL_TOOL
- ✅ SB_DEPLOY_TOOL
- ✅ SB_EXPOSE_TOOL
- ✅ SB_VISION_TOOL
- ✅ SB_IMAGE_EDIT_TOOL
- ✅ BROWSER_TOOL
- ✅ WEB_SEARCH_TOOL
- ✅ DATA_PROVIDERS_TOOL

**Note:** Some tools from the previous SDK version are not currently available (WEB_DEV_TOOL, SHEETS_TOOL, DOCS_TOOL, PRESENTATION_TOOL, etc.). Examples that previously used these tools have been updated to use available alternatives (primarily SB_FILES_TOOL).

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

