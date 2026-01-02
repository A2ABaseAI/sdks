"""Tests for add.py tool command flows."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from a2abase_cli.commands.add import add_tool_command


def test_add_tool_command_custom_name_selection(project_root):
    """Test add_tool_command with custom name selection."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[("sb_files_tool", "Description")]):
            with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "custom_tool_name"  # Custom name instead of number
                
                with patch("a2abase_cli.commands.add.find_agent_files", return_value=[]):
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.console"):
                            with patch("a2abase_cli.commands.add.Table"):
                                try:
                                    add_tool_command(from_api=True, agent=None)
                                except typer.Exit:
                                    pass  # May exit


def test_add_tool_command_invalid_selection(project_root):
    """Test add_tool_command with invalid tool selection."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[("sb_files_tool", "Description")]):
            with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "999"  # Invalid selection
                
                with patch("a2abase_cli.commands.add.console") as mock_console:
                    with patch("a2abase_cli.commands.add.Table"):
                        with pytest.raises(typer.Exit):
                            add_tool_command(from_api=True, agent=None)
                        mock_console.print.assert_called()


def test_add_tool_command_no_selection(project_root):
    """Test add_tool_command with no selection."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[("sb_files_tool", "Description")]):
            with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = ""  # Empty selection
                
                with patch("a2abase_cli.commands.add.console") as mock_console:
                    with patch("a2abase_cli.commands.add.Table"):
                        with pytest.raises(typer.Exit):
                            add_tool_command(from_api=True, agent=None)
                        mock_console.print.assert_called()


def test_add_tool_command_no_api_tools(project_root):
    """Test add_tool_command when no API tools available."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "custom_tool"
                
                with patch("a2abase_cli.commands.add.find_agent_files", return_value=[]):
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.console"):
                            try:
                                add_tool_command(from_api=True, agent=None)
                            except typer.Exit:
                                pass


def test_add_tool_command_agent_selection_all(project_root):
    """Test add_tool_command with agent selection 'all'."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file1 = agents_dir / "agent1_agent.py"
    agent_file2 = agents_dir / "agent2_agent.py"
    agent_file1.touch()
    agent_file2.touch()
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.find_agent_files", return_value=[("agent1", agent_file1), ("agent2", agent_file2)]):
                with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                    mock_prompt.ask.return_value = "all"
                    
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.update_agent_with_tool", return_value=True):
                            with patch("a2abase_cli.commands.add.console"):
                                with patch("a2abase_cli.commands.add.Table"):
                                    try:
                                        add_tool_command(name="test_tool", agent=None)
                                    except typer.Exit:
                                        pass


def test_add_tool_command_agent_selection_none(project_root):
    """Test add_tool_command with agent selection 'none'."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file = agents_dir / "agent1_agent.py"
    agent_file.touch()
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.find_agent_files", return_value=[("agent1", agent_file)]):
                with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                    mock_prompt.ask.return_value = "none"
                    
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.console"):
                            with patch("a2abase_cli.commands.add.Table"):
                                try:
                                    add_tool_command(name="test_tool", agent=None)
                                except typer.Exit:
                                    pass


def test_add_tool_command_agent_selection_numbers(project_root):
    """Test add_tool_command with agent selection by numbers."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file1 = agents_dir / "agent1_agent.py"
    agent_file2 = agents_dir / "agent2_agent.py"
    agent_file1.touch()
    agent_file2.touch()
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.find_agent_files", return_value=[("agent1", agent_file1), ("agent2", agent_file2)]):
                with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                    mock_prompt.ask.return_value = "1,2"
                    
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.update_agent_with_tool", return_value=True):
                            with patch("a2abase_cli.commands.add.console"):
                                with patch("a2abase_cli.commands.add.Table"):
                                    try:
                                        add_tool_command(name="test_tool", agent=None)
                                    except typer.Exit:
                                        pass


def test_add_tool_command_agent_selection_invalid(project_root):
    """Test add_tool_command with invalid agent selection."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file = agents_dir / "agent1_agent.py"
    agent_file.touch()
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.find_agent_files", return_value=[("agent1", agent_file)]):
                with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                    mock_prompt.ask.return_value = "invalid,numbers"
                    
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.console"):
                            with patch("a2abase_cli.commands.add.Table"):
                                try:
                                    add_tool_command(name="test_tool", agent=None)
                                except typer.Exit:
                                    pass


def test_add_tool_command_update_agent_exception(project_root):
    """Test add_tool_command when updating agent raises exception."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file = agents_dir / "agent1_agent.py"
    agent_file.touch()
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.find_agent_files", return_value=[("agent1", agent_file)]):
                with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                    mock_prompt.ask.return_value = "all"
                    
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.update_agent_with_tool", side_effect=Exception("Update error")):
                            with patch("a2abase_cli.commands.add.console") as mock_console:
                                with patch("a2abase_cli.commands.add.Table"):
                                    try:
                                        add_tool_command(name="test_tool", agent=None)
                                    except typer.Exit:
                                        pass
                                    # Should print warning about update error
                                    assert mock_console.print.called


def test_add_tool_command_update_agent_not_updated(project_root):
    """Test add_tool_command when agent update returns False."""
    tools_dir = project_root / "src" / "test_package" / "tools"
    tools_dir.mkdir(parents=True)
    agents_dir = project_root / "src" / "test_package" / "agents"
    agents_dir.mkdir(parents=True)
    agent_file = agents_dir / "agent1_agent.py"
    agent_file.touch()
    
    with patch("a2abase_cli.commands.add.find_project_root", return_value=project_root):
        with patch("a2abase_cli.commands.add.get_available_a2abase_tools", return_value=[]):
            with patch("a2abase_cli.commands.add.find_agent_files", return_value=[("agent1", agent_file)]):
                with patch("a2abase_cli.commands.add.Prompt") as mock_prompt:
                    mock_prompt.ask.return_value = "all"
                    
                    with patch("a2abase_cli.commands.add.ToolGenerator") as mock_generator:
                        mock_generator_instance = MagicMock()
                        mock_generator.return_value = mock_generator_instance
                        
                        with patch("a2abase_cli.commands.add.update_agent_with_tool", return_value=False):
                            with patch("a2abase_cli.commands.add.console"):
                                with patch("a2abase_cli.commands.add.Table"):
                                    try:
                                        add_tool_command(name="test_tool", agent=None)
                                    except typer.Exit:
                                        pass

