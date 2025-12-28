"""Tool generator - create new tool modules."""
import re
from pathlib import Path

from a2abase_cli.generators.shared import safe_write, slugify


class ToolGenerator:
    """Generate a new tool module."""

    def __init__(
        self,
        tool_name: str,
        package_name: str,
        project_root: Path,
        force: bool = False,
        is_api_tool: bool = False,
        api_tool_value: str | None = None,
    ):
        self.tool_name = slugify(tool_name)
        self.package_name = package_name
        self.project_root = project_root
        self.force = force
        self.is_api_tool = is_api_tool
        self.api_tool_value = api_tool_value

    def generate(self) -> None:
        """Generate the tool module."""
        tools_dir = self.project_root / "src" / self.package_name / "tools"
        tool_file = tools_dir / f"{self.tool_name}.py"

        if self.is_api_tool and self.api_tool_value:
            # Generate wrapper for A2ABase API tool
            content = self._generate_api_tool_wrapper()
        else:
            # Generate custom tool
            content = self._generate_custom_tool()

        safe_write(tool_file, content, self.force)

    def _generate_api_tool_wrapper(self) -> str:
        """Generate a wrapper for an A2ABase API tool."""
        # Get description from API if available
        description = f"{self.tool_name.replace('_', ' ').title()} tool"
        try:
            from a2abase.tools import A2ABaseTools

            for tool in A2ABaseTools:
                if tool.value == self.api_tool_value:
                    description = tool.get_description()
                    break
        except ImportError:
            pass

        # Map API tool value to enum member name
        enum_member_name = self.api_tool_value.upper()
        # Convert to enum member format (e.g., "sb_files_tool" -> "SB_FILES_TOOL")
        
        return f'''"""{self.tool_name.replace("_", " ").title()} tool - A2ABase API tool wrapper."""
from typing import Dict, Any

try:
    from a2abase.tools import A2ABaseTools
except ImportError:
    import sys
    from pathlib import Path
    vendor_path = Path(__file__).parent.parent.parent.parent / "vendor"
    sys.path.insert(0, str(vendor_path))
    from a2abase_sdk_stub import A2ABaseTools  # type: ignore


# OpenAI function calling schema for {self.tool_name}
{self.tool_name.upper()}_SCHEMA = {{
    "type": "function",
    "function": {{
        "name": "{self.tool_name}",
        "description": "{description}",
        "parameters": {{
            "type": "object",
            "properties": {{
                # Add tool-specific parameters here based on A2ABase API documentation
            }},
            "required": []
        }}
    }}
}}


# Get A2ABase API tool enum value dynamically
# The tool value is: {self.api_tool_value}
# To use this tool, add the corresponding A2ABaseTools enum member to your agent's a2abase_tools list
# Example:
#   from a2abase.tools import A2ABaseTools
#   agent = await client.Agent.create(
#       name="My Agent",
#       system_prompt="...",
#       a2abase_tools=[A2ABaseTools.{enum_member_name}],
#   )


async def {self.tool_name}(**kwargs) -> Dict[str, Any]:
    """
    {self.tool_name.replace("_", " ").title()} tool implementation.
    
    This is a wrapper around the A2ABase API tool: {self.api_tool_value}
    
    Args:
        **kwargs: Tool-specific arguments (see A2ABase API documentation)

    Returns:
        Dictionary with tool results
    """
    # This tool uses the A2ABase API tool: {self.api_tool_value}
    # To use it, add A2ABaseTools.{enum_member_name} to your agent's a2abase_tools list
    return {{
        "status": "info",
        "message": "This tool uses A2ABase API tool: {self.api_tool_value}",
        "tool": "{self.api_tool_value}",
        "note": "Add A2ABaseTools.{enum_member_name} to agent's a2abase_tools list to use it",
    }}


# Export schema for registration
__all__ = ["{self.tool_name.upper()}_SCHEMA", "{self.tool_name}"]
'''

    def _generate_custom_tool(self) -> str:
        """Generate a custom tool with OpenAI schema."""
        return f'''"""{self.tool_name.replace("_", " ").title()} tool with OpenAI schema."""
from typing import Dict, Any


# OpenAI function calling schema
{self.tool_name.upper()}_SCHEMA = {{
    "type": "function",
    "function": {{
        "name": "{self.tool_name}",
        "description": "{self.tool_name.replace("_", " ").title()} tool - implement your description here",
        "parameters": {{
            "type": "object",
            "properties": {{
                "input": {{
                    "type": "string",
                    "description": "Input parameter for {self.tool_name}"
                }}
            }},
            "required": ["input"]
        }}
    }}
}}


async def {self.tool_name}(input: str, **kwargs) -> Dict[str, Any]:
    """
    {self.tool_name.replace("_", " ").title()} tool implementation.

    Args:
        input: Input parameter
        **kwargs: Additional tool-specific arguments

    Returns:
        Dictionary with tool results
    """
    # TODO: Implement tool logic
    # This is a placeholder. Integrate with A2ABase SDK tools or external APIs.
    return {{
        "status": "success",
        "message": "{self.tool_name.replace("_", " ").title()} tool - implement your logic here",
        "input": input,
        "data": kwargs,
    }}


# Export schema for registration
__all__ = ["{self.tool_name.upper()}_SCHEMA", "{self.tool_name}"]
'''

        # Update tool registry if it exists
        registry_file = self.project_root / "src" / self.package_name / "registry" / "tools.py"
        if registry_file.exists():
            self._update_tool_registry(registry_file)

    def _update_tool_registry(self, registry_file: Path) -> None:
        """Update the tool registry to include the new tool."""
        try:
            content = registry_file.read_text()

            # Add import if not present
            import_line = f'from {self.package_name}.tools.{self.tool_name} import {self.tool_name.upper()}_SCHEMA'
            if import_line not in content:
                # Find the imports section and add after existing tool imports
                import_pattern = r"(from\s+[^\s]+\.tools\.[^\s]+\s+import\s+[^\n]+)"
                if re.search(import_pattern, content):
                    content = re.sub(
                        import_pattern + r"\n",
                        rf"\1\n{import_line}",
                        content,
                        count=1,
                    )
                else:
                    # Add after WEB_SEARCH_SCHEMA import
                    content = re.sub(
                        r"(from [^\s]+\.tools\.web_search import WEB_SEARCH_SCHEMA)",
                        rf"\1\n{import_line}",
                        content,
                    )

            # Add to TOOL_REGISTRY if not present
            registry_pattern = r'(TOOL_REGISTRY:\s*Dict\[str,\s*Dict\[str,\s*Any\]\]\s*=\s*\{)([^}]+)(\})'
            registry_match = re.search(registry_pattern, content, re.DOTALL)
            if registry_match:
                registry_content = registry_match.group(2)
                if f'"{self.tool_name}"' not in registry_content and f"'{self.tool_name}'" not in registry_content:
                    # Add tool to registry
                    tool_entry = f'    "{self.tool_name}": {self.tool_name.upper()}_SCHEMA,'
                    # Add before the closing brace
                    new_registry_content = registry_content.rstrip() + f"\n{tool_entry}\n"
                    content = re.sub(
                        registry_pattern,
                        rf"\1{new_registry_content}\3",
                        content,
                        flags=re.DOTALL,
                    )

            registry_file.write_text(content)
        except Exception:
            # If registry update fails, that's okay - tool is still created
            pass

