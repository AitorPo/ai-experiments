"""
Unit tests for the scaffolding functionality.
"""

import asyncio
import tempfile
from pathlib import Path
import pytest
import sys

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from scaffolder.scaffolding import ProjectScaffolder


@pytest.mark.asyncio
async def test_python_project_scaffolding():
    """Test creating a Python project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scaffolder = ProjectScaffolder()
        
        result = await scaffolder.scaffold_project(
            project_path=temp_dir,
            project_name="test_python_project",
            template_type="python",
            cursor_rules="Use type hints and follow PEP 8"
        )
        
        assert "Successfully scaffolded python project" in result
        
        project_dir = Path(temp_dir) / "test_python_project"
        assert project_dir.exists()
        
        # Check essential files
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / ".gitignore").exists()
        assert (project_dir / ".cursor/rules").exists()
        assert (project_dir / "src" / "test_python_project" / "__init__.py").exists()
        assert (project_dir / "src" / "test_python_project" / "main.py").exists()
        assert (project_dir / "tests" / "test_main.py").exists()


@pytest.mark.asyncio
async def test_fastapi_project_scaffolding():
    """Test creating a FastAPI project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scaffolder = ProjectScaffolder()
        
        result = await scaffolder.scaffold_project(
            project_path=temp_dir,
            project_name="test_fastapi_project",
            template_type="fastapi"
        )
        
        assert "Successfully scaffolded fastapi project" in result
        
        project_dir = Path(temp_dir) / "test_fastapi_project"
        assert project_dir.exists()
        
        # Check essential files
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "src" / "test_fastapi_project" / "main.py").exists()
        
        # Check FastAPI specific content
        main_py = project_dir / "src" / "test_fastapi_project" / "main.py"
        content = main_py.read_text()
        assert "FastAPI" in content
        assert "uvicorn" in content


@pytest.mark.asyncio
async def test_hexagonal_project_scaffolding():
    """Test creating a hexagonal architecture project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scaffolder = ProjectScaffolder()
        
        result = await scaffolder.scaffold_project(
            project_path=temp_dir,
            project_name="test_hexagonal_project",
            template_type="hexagonal",
            cursor_rules="Follow hexagonal architecture patterns",
            module_name="user"
        )
        
        assert "Successfully scaffolded hexagonal project" in result
        
        project_dir = Path(temp_dir) / "test_hexagonal_project"
        assert project_dir.exists()
        
        # Check essential architecture directories
        assert (project_dir / "domain" / "entities").exists()
        assert (project_dir / "application" / "services").exists()
        assert (project_dir / "application" / "ports" / "driving").exists()
        assert (project_dir / "application" / "ports" / "driven").exists()
        assert (project_dir / "driven" / "db").exists()
        assert (project_dir / "driving" / "api" / "v1").exists()
        assert (project_dir / "config").exists()
        assert (project_dir / "tests").exists()
        
        # Check essential files
        assert (project_dir / "requirements.txt").exists()
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "manage.py").exists()
        assert (project_dir / ".cursor/rules").exists()
        
        # Check domain layer files
        assert (project_dir / "domain" / "entities" / "example.py").exists()
        assert (project_dir / "domain" / "entities" / "mixins.py").exists()
        
        # Check application layer files
        assert (project_dir / "application" / "services" / "example_service.py").exists()
        assert (project_dir / "application" / "ports" / "driving" / "example_service_port.py").exists()
        assert (project_dir / "application" / "ports" / "driven" / "example_repository_port.py").exists()
        
        # Check driven layer files
        assert (project_dir / "driven" / "db" / "models.py").exists()
        assert (project_dir / "driven" / "db" / "adapter.py").exists()
        assert (project_dir / "driven" / "db" / "mapper.py").exists()
        assert (project_dir / "driven" / "db" / "admin.py").exists()
        
        # Check driving layer files
        assert (project_dir / "driving" / "api" / "v1" / "models.py").exists()
        assert (project_dir / "driving" / "api" / "v1" / "adapter.py").exists()
        assert (project_dir / "driving" / "api" / "v1" / "mapper.py").exists()
        assert (project_dir / "driving" / "api" / "v1" / "urls.py").exists()
        
        # Check Django configuration
        assert (project_dir / "config" / "settings.py").exists()
        assert (project_dir / "config" / "urls.py").exists()
        assert (project_dir / "config" / "wsgi.py").exists()
        assert (project_dir / "config" / "asgi.py").exists()
        
        # Check test files
        assert (project_dir / "tests" / "conftest.py").exists()
        assert (project_dir / "tests" / "domain" / "test_entities.py").exists()
        assert (project_dir / "tests" / "application" / "test_services.py").exists()
        assert (project_dir / "tests" / "driven" / "test_adapters.py").exists()
        assert (project_dir / "tests" / "driving" / "test_api.py").exists()
        
        # Check that files contain expected content
        domain_entity = project_dir / "domain" / "entities" / "example.py"
        domain_content = domain_entity.read_text()
        assert "ExampleEntity" in domain_content
        assert "BaseModel" in domain_content
        assert "ToDictMixin" in domain_content
        
        # Check Django settings content
        settings_file = project_dir / "config" / "settings.py"
        settings_content = settings_file.read_text()
        assert "rest_framework" in settings_content
        assert "driven.db" in settings_content


@pytest.mark.asyncio
async def test_react_project_scaffolding():
    """Test creating a React project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scaffolder = ProjectScaffolder()
        
        result = await scaffolder.scaffold_project(
            project_path=temp_dir,
            project_name="test_react_project",
            template_type="react"
        )
        
        assert "Successfully scaffolded react project" in result
        
        project_dir = Path(temp_dir) / "test_react_project"
        assert project_dir.exists()
        
        # Check essential files
        assert (project_dir / "package.json").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "public" / "index.html").exists()
        assert (project_dir / "src" / "App.js").exists()


@pytest.mark.asyncio
async def test_invalid_template_type():
    """Test handling of invalid template type."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scaffolder = ProjectScaffolder()
        
        with pytest.raises(ValueError, match="Unsupported template type"):
            await scaffolder.scaffold_project(
                project_path=temp_dir,
                project_name="test_project",
                template_type="invalid_template"
            )


@pytest.mark.asyncio
async def test_project_already_exists():
    """Test handling when project directory already exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scaffolder = ProjectScaffolder()
        
        # Create a directory with the same name
        project_dir = Path(temp_dir) / "existing_project"
        project_dir.mkdir()
        
        with pytest.raises(FileExistsError):
            await scaffolder.scaffold_project(
                project_path=temp_dir,
                project_name="existing_project",
                template_type="python"
            ) 