"""Tests for generators/tool.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

from a2abase_cli.generators.tool import ToolGenerator


def test_tool_generator_api_tool_with_sdk(project_root):
    """Test ToolGenerator for API tool with SDK available."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    mock_tool = MagicMock()
    mock_tool.value = "sb_files_tool"
    mock_tool.get_description.return_value = "File operations"
    
    mock_tools_module = MagicMock()
    mock_tools_module.A2ABaseTools = [mock_tool]
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase.tools":
            return mock_tools_module
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        generator = ToolGenerator(
            tool_name="files_tool",
            package_name="test_package",
            project_root=project_root,
            force=True,
            is_api_tool=True,
            api_tool_value="sb_files_tool",
        )
        
        generator.generate()
        
        tool_file = tools_dir / "files_tool.py"
        assert tool_file.exists()
        content = tool_file.read_text()
        assert "A2ABase API tool wrapper" in content


def test_tool_generator_api_tool_without_sdk(project_root):
    """Test ToolGenerator for API tool without SDK."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    def _mock_import(name, *args, **kwargs):
        if name == "a2abase.tools":
            raise ImportError()
        return __import__(name, *args, **kwargs)
    
    with patch("builtins.__import__", side_effect=_mock_import):
        generator = ToolGenerator(
            tool_name="files_tool",
            package_name="test_package",
            project_root=project_root,
            force=True,
            is_api_tool=True,
            api_tool_value="sb_files_tool",
        )
        
        generator.generate()
        
        tool_file = tools_dir / "files_tool.py"
        assert tool_file.exists()

