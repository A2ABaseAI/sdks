"""Shared utilities for generators."""
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional


def get_available_a2abase_tools() -> list[tuple[str, str]]:
    """
    Get list of available A2ABase API tools with descriptions.
    
    Returns:
        List of tuples (tool_value, description)
    """
    tools = []
    
    # Try to import from real SDK first
    try:
        from a2abase.tools import A2ABaseTools
        
        for tool in A2ABaseTools:
            try:
                description = tool.get_description()
                tools.append((tool.value, description))
            except (ValueError, AttributeError):
                # Skip tools without descriptions
                pass
    except ImportError:
        # Fallback to hardcoded list if SDK not available
        fallback_tools = {
            "sb_files_tool": "Read, write, and edit files",
            "sb_shell_tool": "Execute shell commands",
            "sb_deploy_tool": "Deploy web applications",
            "sb_expose_tool": "Expose local services to the internet",
            "sb_vision_tool": "Analyze and understand images",
            "browser_tool": "Browse websites and interact with web pages",
            "web_search_tool": "Search the web for information",
            "sb_image_edit_tool": "Edit and manipulate images",
            "data_providers_tool": "Access structured data from various providers",
        }
        tools = list(fallback_tools.items())
    
    return tools


def slugify(text: str) -> str:
    """Convert text to a valid slug."""
    # Convert to lowercase and replace spaces/special chars with underscores
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "_", text)
    return text


def validate_package_name(name: str) -> str:
    """Validate and normalize Python package name."""
    # Remove invalid characters
    name = re.sub(r"[^a-z0-9_]", "", name.lower())
    # Must start with letter or underscore
    if name and name[0].isdigit():
        name = "_" + name
    if not name:
        name = "package"
    return name


def find_project_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find the project root by looking for a2abase.yaml."""
    if start is None:
        start = Path.cwd()

    current = start.resolve()
    while current != current.parent:
        config_file = current / "a2abase.yaml"
        if config_file.exists():
            return current
        current = current.parent

    return None


def safe_write(file_path: Path, content: str, force: bool = False) -> None:
    """Safely write a file, creating backup if it exists."""
    if file_path.exists() and not force:
        raise FileExistsError(f"File {file_path} already exists. Use --force to overwrite.")

    # Create parent directories
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write using temp file
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, dir=file_path.parent, suffix=".tmp"
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    # Atomic move
    shutil.move(str(tmp_path), str(file_path))


def render_template(template_str: str, **kwargs) -> str:
    """Render a template string with variables."""
    from jinja2 import Template

    template = Template(template_str)
    return template.render(**kwargs)


def find_agent_files(agents_dir: Path) -> list[tuple[str, Path]]:
    """
    Find all agent files in the agents directory.

    Returns:
        List of tuples (agent_name, agent_file_path)
    """
    agents = []
    if not agents_dir.exists():
        return agents

    for agent_file in agents_dir.glob("*_agent.py"):
        agent_name = agent_file.stem.replace("_agent", "")
        agents.append((agent_name, agent_file))

    return agents


def update_agent_with_tool(
    agent_file: Path, tool_name: str, tool_schema_name: str, package_name: str
) -> bool:
    """
    Update an agent file to import and register a tool.

    Args:
        agent_file: Path to the agent file
        tool_name: Name of the tool (e.g., "web_search")
        tool_schema_name: Name of the schema constant (e.g., "WEB_SEARCH_SCHEMA")
        package_name: Package name for imports

    Returns:
        True if file was updated, False if no changes needed
    """
    if not agent_file.exists():
        return False

    content = agent_file.read_text()
    original_content = content

    # Check if import already exists
    import_line = f'from {package_name}.tools.{tool_name} import {tool_schema_name}'
    import_exists = import_line in content
    
    # Check if tool is already mentioned in the file
    tool_already_registered = (
        f'"{tool_name}"' in content 
        or f"'{tool_name}'" in content
        or tool_schema_name in content
    )

    if import_exists and tool_already_registered:
        return False  # Already imported and registered

    # Add import if not present
    if not import_exists:
        # Find existing tool imports
        tool_import_pattern = r"(from\s+[^\s]+\.tools\.[^\s]+\s+import\s+[A-Z_]+\s*SCHEMA)"
        tool_import_match = re.search(tool_import_pattern, content)
        
        if tool_import_match:
            # Add after existing tool imports
            insert_pos = tool_import_match.end()
            next_newline = content.find("\n", insert_pos)
            if next_newline != -1:
                content = (
                    content[: next_newline + 1]
                    + f"{import_line}\n"
                    + content[next_newline + 1 :]
                )
        else:
            # Add after SDK imports
            sdk_import_pattern = r"(from a2abase_sdk_stub import[^\n]+|from a2abase import[^\n]+)"
            sdk_match = re.search(sdk_import_pattern, content)
            if sdk_match:
                insert_pos = sdk_match.end()
                next_newline = content.find("\n", insert_pos)
                if next_newline != -1:
                    content = (
                        content[: next_newline + 1]
                        + f"\n{import_line}\n"
                        + content[next_newline + 1 :]
                    )
            else:
                # Add at top after docstring
                docstring_end = content.find('"""', content.find('"""') + 3)
                if docstring_end != -1:
                    next_newline = content.find("\n", docstring_end)
                    if next_newline != -1:
                        content = (
                            content[: next_newline + 1]
                            + f"{import_line}\n"
                            + content[next_newline + 1 :]
                        )

    # Add comment about the tool in the agent creation function
    tool_comment = f"    # Custom tool: {tool_name} (schema: {tool_schema_name})"
    
    # Check if comment already exists
    if tool_comment not in content:
        # Add comment near the a2abase_tools line
        if "a2abase_tools=" in content:
            # Add comment before a2abase_tools line
            content = re.sub(
                r"(\s+a2abase_tools=\[)",
                f"{tool_comment}\n\\1",
                content,
                count=1,
            )
        elif "# Option 2:" in content:
            # Add comment before Option 2 section
            content = re.sub(
                r"(# Option 2:)",
                f"{tool_comment}\n    \\1",
                content,
                count=1,
            )

    # Update the MCP tools comment section if it exists
    mcp_comment_pattern = r"(allowed_tools=\[)([^\]]*?)(\])"
    mcp_match = re.search(mcp_comment_pattern, content)
    if mcp_match:
        tools_list = mcp_match.group(2).strip()
        # Check if tool is already in the list
        if f'"{tool_name}"' not in tools_list and f"'{tool_name}'" not in tools_list:
            if tools_list and tools_list.strip():
                # Add to existing list
                new_tools_list = tools_list.rstrip().rstrip(",") + f', "{tool_name}"'
            else:
                # Create new list
                new_tools_list = f'"{tool_name}"'
            content = re.sub(
                mcp_comment_pattern,
                rf"\1{new_tools_list}\3",
                content,
                count=1,
            )

    # Only write if content changed
    if content != original_content:
        agent_file.write_text(content)
        return True

    return False
