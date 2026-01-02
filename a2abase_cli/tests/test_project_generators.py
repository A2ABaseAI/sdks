"""Tests for project generator template methods."""
from pathlib import Path

from a2abase_cli.generators.project import ProjectGenerator


def test_project_generator_basic_agent(temp_dir):
    """Test _generate_basic_agent method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_basic_agent()
    
    agent_file = project_path / "src" / "test_package" / "agents" / "basic_agent.py"
    assert agent_file.exists()
    assert "Basic Agent" in agent_file.read_text()


def test_project_generator_basic_main(temp_dir):
    """Test _generate_basic_main method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_basic_main()
    
    main_file = project_path / "src" / "test_package" / "main.py"
    assert main_file.exists()
    assert "create_basic_agent" in main_file.read_text()


def test_project_generator_basic_card(temp_dir):
    """Test _generate_basic_card method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_basic_card()
    
    card_file = project_path / "src" / "test_package" / "registry" / "card.py"
    assert card_file.exists()
    assert "generate_card" in card_file.read_text()


def test_project_generator_basic_sdk_adapter(temp_dir):
    """Test _generate_basic_sdk_adapter method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_basic_sdk_adapter()
    
    adapter_file = project_path / "src" / "test_package" / "sdk_adapter.py"
    assert adapter_file.exists()


def test_project_generator_complex_source_files(temp_dir):
    """Test _generate_complex_source_files method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="complex",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_complex_source_files()
    
    # Should generate orchestrator
    orchestrator_file = project_path / "src" / "test_package" / "orchestrator" / "orchestrator.py"
    assert orchestrator_file.exists()
    
    # Should also generate advanced files
    assert (project_path / "src" / "test_package" / "tools" / "mcp_server.py").exists()


def test_project_generator_stub_sdk(temp_dir):
    """Test _generate_stub_sdk method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_stub_sdk()
    
    # Check stub files were created
    stub_dir = project_path / "vendor" / "a2abase_sdk_stub"
    assert (stub_dir / "__init__.py").exists()
    assert (stub_dir / "agent.py").exists()
    assert (stub_dir / "tools.py").exists()
    assert (stub_dir / "runner.py").exists()


def test_project_generator_tests(temp_dir):
    """Test _generate_tests method."""
    project_path = temp_dir / "test_project"
    
    generator = ProjectGenerator(
        project_name="test-project",
        package_name="test_package",
        template="basic",
        package_manager="pip",
        project_path=project_path,
        force=True,
    )
    
    generator._generate_tests()
    
    # Check test files were created
    assert (project_path / "tests" / "__init__.py").exists()
    assert (project_path / "tests" / "test_smoke.py").exists()

