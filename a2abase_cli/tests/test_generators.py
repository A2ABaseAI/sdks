"""Tests for generators."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from a2abase_cli.generators.agent import AgentGenerator
from a2abase_cli.generators.project import ProjectGenerator
from a2abase_cli.generators.tool import ToolGenerator


def test_project_generator_basic(temp_dir):
    """Test ProjectGenerator with basic template."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator.generate()
    
    # Verify structure was created
    assert (project_path / "src" / "test_package").exists()
    assert (project_path / "a2abase.yaml").exists()
    assert (project_path / "pyproject.toml").exists()


def test_project_generator_advanced(temp_dir):
    """Test ProjectGenerator with advanced template."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="advanced",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator.generate()
    
    # Verify advanced structure
    assert (project_path / "src" / "test_package" / "tools").exists()


def test_project_generator_complex(temp_dir):
    """Test ProjectGenerator with complex template."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="complex",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator.generate()
    
    # Verify complex structure
    assert (project_path / "src" / "test_package" / "orchestrator").exists()


def test_project_generator_unknown_template(temp_dir):
    """Test ProjectGenerator with unknown template (defaults to basic)."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="unknown",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator.generate()
    
    # Should default to basic
    assert (project_path / "src" / "test_package").exists()


def test_agent_generator(project_root):
    """Test AgentGenerator."""
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    
    generator = AgentGenerator(
        agent_name="test_agent",
        package_name="test_package",
        project_root=project_root,
        force=True,
    )
    
    generator.generate()
    
    agent_file = agents_dir / "test_agent_agent.py"
    assert agent_file.exists()
    assert "test_agent" in agent_file.read_text()


def test_agent_generator_force_false_existing(project_root):
    """Test AgentGenerator with existing file and force=False."""
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file = agents_dir / "test_agent_agent.py"
    agent_file.touch()
    
    generator = AgentGenerator(
        agent_name="test_agent",
        package_name="test_package",
        project_root=project_root,
        force=False,
    )
    
    with pytest.raises(FileExistsError):
        generator.generate()


def test_tool_generator_custom(project_root):
    """Test ToolGenerator for custom tool."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    generator = ToolGenerator(
        tool_name="custom_tool",
        package_name="test_package",
        project_root=project_root,
        force=True,
        is_api_tool=False,
    )
    
    generator.generate()
    
    tool_file = tools_dir / "custom_tool.py"
    assert tool_file.exists()
    content = tool_file.read_text()
    assert "CUSTOM_TOOL_SCHEMA" in content


def test_tool_generator_api_tool(project_root):
    """Test ToolGenerator for API tool wrapper."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
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
    assert "A2ABase API tool wrapper" in content or "sb_files_tool" in content


def test_tool_generator_force_false_existing(project_root):
    """Test ToolGenerator with existing file and force=False."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    tool_file = tools_dir / "custom_tool.py"
    tool_file.touch()
    
    generator = ToolGenerator(
        tool_name="custom_tool",
        package_name="test_package",
        project_root=project_root,
        force=False,
    )
    
    with pytest.raises(FileExistsError):
        generator.generate()

