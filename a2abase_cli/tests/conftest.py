"""Pytest configuration and fixtures."""
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def project_root(temp_dir):
    """Create a mock project root with a2abase.yaml."""
    project_root = temp_dir / "test_project"
    project_root.mkdir()
    
    # Create a2abase.yaml
    config = {
        "project_name": "test_project",
        "package_name": "test_package",
        "template": "basic",
        "package_manager": "pip",
    }
    
    import yaml
    
    config_file = project_root / "a2abase.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    
    # Create src structure
    src_dir = project_root / "src" / "test_package"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").touch()
    
    return project_root

