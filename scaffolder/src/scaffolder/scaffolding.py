"""
Project scaffolding module for creating projects based on templates and cursor rules.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Optional
import json


class ProjectScaffolder:
    """Handles project scaffolding based on templates and cursor rules."""

    def __init__(self):
        self.templates = {
            "python": self._create_python_project,
            "fastapi": self._create_fastapi_project,
            "react": self._create_react_project,
            "nextjs": self._create_nextjs_project,
            "node": self._create_node_project,
            "flask": self._create_flask_project,
            "django": self._create_django_project,
            "hexagonal": self._create_hexagonal_project,
        }

    def _get_class_names(self, module_name: Optional[str] = None) -> Dict[str, str]:
        """Generate class names and identifiers from module name."""
        if not module_name:
            module_name = "Example"
        
        # Normalize the input - split on common separators and join with spaces
        normalized = module_name.replace("-", " ").replace("_", " ")
        words = [word.strip() for word in normalized.split() if word.strip()]
        
        # Convert to PascalCase for class names
        pascal_case = "".join(word.capitalize() for word in words)
        
        # Convert to snake_case for file/variable names
        snake_case = "_".join(word.lower() for word in words)
        
        # Convert to kebab-case for URLs
        kebab_case = "-".join(word.lower() for word in words)
        
        return {
            "entity_class": f"{pascal_case}Entity",
            "dbo_class": f"{pascal_case}DBO",
            "service_class": f"{pascal_case}Service",
            "repository_class": f"{pascal_case}RepositoryAdapter",
            "mapper_class": f"{pascal_case}Mapper",
            "admin_class": f"{pascal_case}Admin",
            "service_port_class": f"{pascal_case}ServicePort",
            "repository_port_class": f"{pascal_case}RepositoryPort",
            "file_name": snake_case,
            "variable_name": snake_case,
            "url_name": kebab_case,
            "display_name": pascal_case,
            "table_name": f"{snake_case}s",  # pluralized
        }

    async def scaffold_project(
        self,
        project_path: str,
        project_name: str,
        template_type: str,
        cursor_rules: Optional[str] = None,
        module_name: Optional[str] = None,
    ) -> str:
        """Scaffold a new project based on the template type and cursor rules."""
        
        if template_type.lower() not in self.templates:
            available_types = ", ".join(self.templates.keys())
            raise ValueError(
                f"Unsupported template type: {template_type}. "
                f"Available types: {available_types}"
            )

        project_dir = Path(project_path) / project_name
        
        if project_dir.exists():
            raise FileExistsError(f"Project directory already exists: {project_dir}")

        # Create the project directory
        project_dir.mkdir(parents=True, exist_ok=False)

        try:
            # Create the project based on template
            template_func = self.templates[template_type.lower()]
            if template_type.lower() == "hexagonal":
                await template_func(project_dir, project_name, module_name)
            else:
                await template_func(project_dir, project_name)

            # Add cursor rules if provided
            if cursor_rules:
                await self._add_cursor_rules(project_dir, cursor_rules)

            return f"Successfully scaffolded {template_type} project '{project_name}' at {project_dir}"
        
        except Exception as e:
            # Clean up on failure
            if project_dir.exists():
                shutil.rmtree(project_dir)
            raise e

    async def _create_python_project(self, project_dir: Path, project_name: str):
        """Create a basic Python project structure."""
        
        # Create directory structure
        (project_dir / "src" / project_name).mkdir(parents=True)
        (project_dir / "tests").mkdir()
        (project_dir / "docs").mkdir()

        # Create pyproject.toml
        pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A Python project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
        with open(project_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_content)

        # Create main module
        main_content = f'''"""
{project_name} - A Python project
"""

def main():
    """Main entry point."""
    print("Hello from {project_name}!")


if __name__ == "__main__":
    main()
'''
        with open(project_dir / "src" / project_name / "__init__.py", "w") as f:
            f.write('"""Main package."""\n')
        
        with open(project_dir / "src" / project_name / "main.py", "w") as f:
            f.write(main_content)

        # Create test file
        test_content = f'''"""
Tests for {project_name}
"""

import pytest
from {project_name}.main import main


def test_main():
    """Test main function."""
    # This is a placeholder test
    assert True
'''
        with open(project_dir / "tests" / "test_main.py", "w") as f:
            f.write(test_content)

        # Create README
        readme_content = f"""# {project_name}

A Python project created with the MCP scaffolder.

## Installation

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
uv pip install -e .
```

## Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint code
ruff check .
```

## Usage

```python
from {project_name}.main import main

main()
```
"""
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)

        # Create .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        with open(project_dir / ".gitignore", "w") as f:
            f.write(gitignore_content)

    async def _create_fastapi_project(self, project_dir: Path, project_name: str):
        """Create a FastAPI project structure."""
        
        # Create directory structure
        (project_dir / "src" / project_name).mkdir(parents=True)
        (project_dir / "tests").mkdir()
        (project_dir / "docs").mkdir()

        # Create pyproject.toml with FastAPI dependencies
        pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A FastAPI project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
"""
        with open(project_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_content)

        # Create FastAPI main application
        main_content = f'''"""
{project_name} - A FastAPI application
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any


app = FastAPI(
    title="{project_name}",
    description="A FastAPI application created with MCP scaffolder",
    version="0.1.0"
)


class Item(BaseModel):
    """Example item model."""
    id: int
    name: str
    description: str = ""


# In-memory storage for demo purposes
items: Dict[int, Item] = {{}}


@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "Hello from {project_name}!"}}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy"}}


@app.get("/items", response_model=List[Item])
async def get_items():
    """Get all items."""
    return list(items.values())


@app.get("/items/{{item_id}}", response_model=Item)
async def get_item(item_id: int):
    """Get a specific item."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """Create a new item."""
    if item.id in items:
        raise HTTPException(status_code=400, detail="Item already exists")
    items[item.id] = item
    return item


@app.put("/items/{{item_id}}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """Update an item."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    item.id = item_id
    items[item_id] = item
    return item


@app.delete("/items/{{item_id}}")
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {{"message": "Item deleted successfully"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        with open(project_dir / "src" / project_name / "__init__.py", "w") as f:
            f.write('"""FastAPI application package."""\n')
        
        with open(project_dir / "src" / project_name / "main.py", "w") as f:
            f.write(main_content)

        # Create test file
        test_content = f'''"""
Tests for {project_name} FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from {project_name}.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {{"status": "healthy"}}


def test_get_items_empty():
    """Test getting items when none exist."""
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_item():
    """Test creating and retrieving an item."""
    item_data = {{
        "id": 1,
        "name": "Test Item",
        "description": "A test item"
    }}
    
    # Create item
    response = client.post("/items", json=item_data)
    assert response.status_code == 200
    assert response.json() == item_data
    
    # Get item
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == item_data
    
    # Clean up
    client.delete("/items/1")
'''
        with open(project_dir / "tests" / "test_main.py", "w") as f:
            f.write(test_content)

        # Create README
        readme_content = f"""# {project_name}

A FastAPI application created with the MCP scaffolder.

## Installation

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
uv pip install -e .
```

## Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the application
uvicorn {project_name}.main:app --reload

# Run tests
pytest

# Format code
black .

# Lint code
ruff check .
```

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Usage

The API provides CRUD operations for items with the following endpoints:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /items` - List all items
- `GET /items/{{id}}` - Get specific item
- `POST /items` - Create new item
- `PUT /items/{{id}}` - Update item
- `DELETE /items/{{id}}` - Delete item
"""
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)

        # Create .gitignore (same as Python project)
        await self._create_python_project(Path("/tmp/dummy"), "dummy")  # Reuse gitignore creation
        shutil.copy("/tmp/dummy/.gitignore", project_dir / ".gitignore")
        shutil.rmtree("/tmp/dummy")

    async def _create_react_project(self, project_dir: Path, project_name: str):
        """Create a React project structure."""
        
        # Create basic React structure
        (project_dir / "src" / "components").mkdir(parents=True)
        (project_dir / "public").mkdir()

        # Create package.json
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        with open(project_dir / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Create basic React app files
        index_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
        with open(project_dir / "public" / "index.html", "w") as f:
            f.write(index_html)

        # Create App.js
        app_js = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>A React application created with MCP scaffolder.</p>
      </header>
    </div>
  );
}}

export default App;
"""
        with open(project_dir / "src" / "App.js", "w") as f:
            f.write(app_js)

        # Create App.css
        app_css = """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
"""
        with open(project_dir / "src" / "App.css", "w") as f:
            f.write(app_css)

        # Create index.js
        index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        with open(project_dir / "src" / "index.js", "w") as f:
            f.write(index_js)

        # Create index.css
        index_css = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
"""
        with open(project_dir / "src" / "index.css", "w") as f:
            f.write(index_css)

        # Create README
        readme_content = f"""# {project_name}

A React application created with the MCP scaffolder.

## Installation

```bash
npm install
```

## Development

```bash
# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Project Structure

```
{project_name}/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```
"""
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)

    async def _create_nextjs_project(self, project_dir: Path, project_name: str):
        """Create a Next.js project structure."""
        # Similar to React but with Next.js specific structure
        pass  # Implement as needed

    async def _create_node_project(self, project_dir: Path, project_name: str):
        """Create a Node.js project structure."""
        # Basic Node.js project structure
        pass  # Implement as needed

    async def _create_flask_project(self, project_dir: Path, project_name: str):
        """Create a Flask project structure."""
        # Similar to FastAPI but with Flask
        pass  # Implement as needed

    async def _create_django_project(self, project_dir: Path, project_name: str):
        """Create a Django project structure."""
        # Django project structure
        pass  # Implement as needed

    async def _create_hexagonal_project(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create a Django project structure following hexagonal architecture patterns."""
        
        # Create hexagonal architecture directory structure
        (project_dir / "domain" / "entities").mkdir(parents=True)
        (project_dir / "application" / "services").mkdir(parents=True)
        (project_dir / "application" / "ports" / "driving").mkdir(parents=True)
        (project_dir / "application" / "ports" / "driven").mkdir(parents=True)
        (project_dir / "driven" / "db").mkdir(parents=True)
        (project_dir / "driven" / "external").mkdir(parents=True)
        (project_dir / "driving" / "api" / "v1").mkdir(parents=True)
        (project_dir / "config").mkdir()
        (project_dir / "tests" / "domain").mkdir(parents=True)
        (project_dir / "tests" / "application").mkdir(parents=True)
        (project_dir / "tests" / "driven").mkdir(parents=True)
        (project_dir / "tests" / "driving").mkdir(parents=True)

        # Create requirements.txt
        requirements_content = """Django>=4.2.0,<5.0.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
pydantic>=2.0.0
pytest>=7.4.0
pytest-django>=4.5.0
black>=23.0.0
ruff>=0.1.0
factory-boy>=3.3.0
"""
        with open(project_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)

        # Create pyproject.toml
        pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "Django project following hexagonal architecture"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "Django>=4.2.0,<5.0.0",
    "djangorestframework>=3.14.0",
    "django-cors-headers>=4.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-django>=4.5.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "factory-boy>=3.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
testpaths = ["tests"]
addopts = "--tb=short"
"""
        with open(project_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_content)

        # Create Domain Layer
        await self._create_domain_layer(project_dir, project_name, module_name)
        
        # Create Application Layer
        await self._create_application_layer(project_dir, project_name, module_name)
        
        # Create Driven Layer
        await self._create_driven_layer(project_dir, project_name, module_name)
        
        # Create Driving Layer
        await self._create_driving_layer(project_dir, project_name, module_name)
        
        # Create Configuration
        await self._create_config_layer(project_dir, project_name, module_name)
        
        # Create Test Files
        await self._create_test_files(project_dir, project_name, module_name)
        
        # Create Django management script
        manage_py_content = """#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""
        with open(project_dir / "manage.py", "w") as f:
            f.write(manage_py_content)
        
        # Make manage.py executable
        os.chmod(project_dir / "manage.py", 0o755)

        # Create README
        readme_content = f"""# {project_name}

A Django project following hexagonal architecture patterns.

## Architecture Overview

This project implements Clean Architecture principles with clear separation of concerns across four main layers:

### 1. Domain Layer (`domain/`)
- Contains business entities and domain logic
- No dependencies on external frameworks
- Pure business logic with Pydantic models

### 2. Application Layer (`application/`)
- Orchestrates business use cases
- Defines ports (interfaces) for external dependencies
- Services implement business workflows

### 3. Driven Layer (`driven/`)
- Implements outbound adapters (external systems)
- Database repositories, external APIs
- Concrete implementations of driven ports

### 4. Driving Layer (`driving/`)
- Implements inbound adapters (user interfaces)
- REST API controllers
- Web interface adapters

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint code
ruff check .

# Run Django checks
python manage.py check
```

## Project Structure

```
{project_name}/
├── domain/                 # Business entities and logic
│   └── entities/
├── application/            # Use cases and ports
│   ├── services/
│   └── ports/
│       ├── driving/        # Input ports
│       └── driven/         # Output ports
├── driven/                 # External integrations
│   ├── db/                # Database adapters
│   └── external/          # External service adapters
├── driving/               # User interfaces
│   └── api/
│       └── v1/
├── config/                # Django configuration
├── tests/                 # Test suites
└── manage.py             # Django management script
```

## Adding New Features

When adding new features, follow this pattern:

1. **Domain**: Define entities in `domain/entities/`
2. **Ports**: Create interfaces in `application/ports/`
3. **Services**: Implement business logic in `application/services/`
4. **Adapters**: Add implementations in `driven/` and `driving/`

## Key Patterns

- **Dependency Injection**: Services receive dependencies via constructor
- **Interface Segregation**: Clear separation between driving and driven ports
- **Repository Pattern**: Database access through repository interfaces
- **Clean API Design**: RESTful endpoints with proper DTO mapping

This architecture ensures testability, maintainability, and framework independence.
"""
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)

        # Create .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# Virtual environments
.venv/
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
"""
        with open(project_dir / ".gitignore", "w") as f:
            f.write(gitignore_content)

    async def _create_domain_layer(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create the domain layer with entities and business logic."""
        
        names = self._get_class_names(module_name)
        
        # Create __init__.py files
        with open(project_dir / "domain" / "__init__.py", "w") as f:
            f.write('"""Domain layer - Business entities and logic."""\n')
        
        with open(project_dir / "domain" / "entities" / "__init__.py", "w") as f:
            f.write('"""Domain entities."""\n')

        # Create base mixins
        mixins_content = '''"""
Base mixins for domain entities.
"""

from typing import Dict, Any
from abc import ABC


class ToDictMixin(ABC):
    """Mixin to add to_dict functionality to entities."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        if hasattr(self, 'model_dump'):
            # Pydantic model
            return self.model_dump()
        elif hasattr(self, '__dict__'):
            # Regular class
            return self.__dict__.copy()
        else:
            raise NotImplementedError("to_dict not implemented for this entity type")
'''
        with open(project_dir / "domain" / "entities" / "mixins.py", "w") as f:
            f.write(mixins_content)

        # Create parameterized entity
        entity_content = f'''"""
{names["display_name"]} business entity following domain patterns.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .mixins import ToDictMixin


class {names["entity_class"]}(BaseModel, ToDictMixin):
    """{names["display_name"]} business entity."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        arbitrary_types_allowed = True
'''
        with open(project_dir / "domain" / "entities" / f"{names['file_name']}.py", "w") as f:
            f.write(entity_content)

    async def _create_application_layer(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create the application layer with services and ports."""
        
        names = self._get_class_names(module_name)
        
        # Create __init__.py files
        with open(project_dir / "application" / "__init__.py", "w") as f:
            f.write('"""Application layer - Use cases and orchestration."""\n')
        
        with open(project_dir / "application" / "services" / "__init__.py", "w") as f:
            f.write('"""Application services."""\n')
        
        with open(project_dir / "application" / "ports" / "__init__.py", "w") as f:
            f.write('"""Port interfaces."""\n')
        
        with open(project_dir / "application" / "ports" / "driving" / "__init__.py", "w") as f:
            f.write('"""Driving ports (input interfaces)."""\n')
        
        with open(project_dir / "application" / "ports" / "driven" / "__init__.py", "w") as f:
            f.write('"""Driven ports (output interfaces)."""\n')

        # Create driving port interface
        driving_port_content = f'''"""
{names["display_name"]} driving port interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.{names["file_name"]} import {names["entity_class"]}


class {names["service_port_class"]}(ABC):
    """Port interface for {names["variable_name"]} service operations."""
    
    @abstractmethod
    async def create(self, entity: {names["entity_class"]}) -> {names["entity_class"]}:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def retrieve(self, entity_id: int) -> Optional[{names["entity_class"]}]:
        """Retrieve an entity by ID."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[{names["entity_class"]}]:
        """List all entities."""
        pass
    
    @abstractmethod
    async def update(self, entity_id: int, entity: {names["entity_class"]}) -> Optional[{names["entity_class"]}]:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Delete an entity."""
        pass
'''
        with open(project_dir / "application" / "ports" / "driving" / f"{names['file_name']}_service_port.py", "w") as f:
            f.write(driving_port_content)

        # Create driven port interface
        driven_port_content = f'''"""
{names["display_name"]} driven port interface for database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.{names["file_name"]} import {names["entity_class"]}


class {names["repository_port_class"]}(ABC):
    """Port interface for {names["variable_name"]} entity repository operations."""
    
    @abstractmethod
    async def save(self, entity: {names["entity_class"]}) -> {names["entity_class"]}:
        """Save an entity to the database."""
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_id: int) -> Optional[{names["entity_class"]}]:
        """Find an entity by ID."""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[{names["entity_class"]}]:
        """Find all entities."""
        pass
    
    @abstractmethod
    async def update(self, entity_id: int, entity: {names["entity_class"]}) -> Optional[{names["entity_class"]}]:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete_by_id(self, entity_id: int) -> bool:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: int) -> bool:
        """Check if an entity exists."""
        pass
'''
        with open(project_dir / "application" / "ports" / "driven" / f"{names['file_name']}_repository_port.py", "w") as f:
            f.write(driven_port_content)

        # Create application service
        service_content = f'''"""
{names["display_name"]} application service implementing business logic.
"""

from typing import List, Optional

from application.ports.driving.{names["file_name"]}_service_port import {names["service_port_class"]}
from application.ports.driven.{names["file_name"]}_repository_port import {names["repository_port_class"]}
from domain.entities.{names["file_name"]} import {names["entity_class"]}


class {names["service_class"]}({names["service_port_class"]}):
    """Service implementing {names["variable_name"]} business operations."""
    
    def __init__(self, repository: {names["repository_port_class"]}):
        """Initialize service with repository dependency."""
        self.repository = repository
    
    async def create(self, entity: {names["entity_class"]}) -> {names["entity_class"]}:
        """Create a new entity with business validation."""
        # Business logic validation
        if not entity.name or not entity.name.strip():
            raise ValueError("Entity name cannot be empty")
        
        # Delegate to repository
        return await self.repository.save(entity)
    
    async def retrieve(self, entity_id: int) -> Optional[{names["entity_class"]}]:
        """Retrieve an entity by ID."""
        if entity_id <= 0:
            raise ValueError("Entity ID must be positive")
        
        return await self.repository.find_by_id(entity_id)
    
    async def list_all(self) -> List[{names["entity_class"]}]:
        """List all active entities."""
        all_entities = await self.repository.find_all()
        # Business logic: only return active entities
        return [entity for entity in all_entities if entity.is_active]
    
    async def update(self, entity_id: int, entity: {names["entity_class"]}) -> Optional[{names["entity_class"]}]:
        """Update an existing entity."""
        if entity_id <= 0:
            raise ValueError("Entity ID must be positive")
        
        # Check if entity exists
        existing = await self.repository.find_by_id(entity_id)
        if not existing:
            return None
        
        # Business validation
        if not entity.name or not entity.name.strip():
            raise ValueError("Entity name cannot be empty")
        
        return await self.repository.update(entity_id, entity)
    
    async def delete(self, entity_id: int) -> bool:
        """Delete an entity (soft delete by marking inactive)."""
        if entity_id <= 0:
            raise ValueError("Entity ID must be positive")
        
        # Business rule: soft delete by marking inactive
        existing = await self.repository.find_by_id(entity_id)
        if not existing:
            return False
        
        existing.is_active = False
        await self.repository.update(entity_id, existing)
        return True
'''
        with open(project_dir / "application" / "services" / f"{names['file_name']}_service.py", "w") as f:
            f.write(service_content)

    async def _create_driven_layer(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create the driven layer with external adapters."""
        
        names = self._get_class_names(module_name)
        
        # Create __init__.py files
        with open(project_dir / "driven" / "__init__.py", "w") as f:
            f.write('"""Driven layer - External system adapters."""\n')
        
        with open(project_dir / "driven" / "db" / "__init__.py", "w") as f:
            f.write('"""Database adapters."""\n')
        
        with open(project_dir / "driven" / "external" / "__init__.py", "w") as f:
            f.write('"""External service adapters."""\n')

        # Create Django model (DBO)
        models_content = f'''"""
Django models (Database Objects) for the {names["variable_name"]} domain.
"""

from django.db import models


class {names["dbo_class"]}(models.Model):
    """Django model for {names["display_name"]} entity."""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "{names["table_name"]}"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.name
'''
        with open(project_dir / "driven" / "db" / "models.py", "w") as f:
            f.write(models_content)

        # Create mapper for DBO <-> Entity conversion
        mapper_content = f'''"""
Mapper for converting between Django models (DBOs) and domain entities.
"""

from typing import Optional

from domain.entities.{names["file_name"]} import {names["entity_class"]}
from .models import {names["dbo_class"]}


class {names["mapper_class"]}:
    """Maps between {names["entity_class"]} and {names["dbo_class"]}."""
    
    @staticmethod
    def to_entity(dbo: {names["dbo_class"]}) -> {names["entity_class"]}:
        """Convert Django model to domain entity."""
        return {names["entity_class"]}(
            id=dbo.id,
            name=dbo.name,
            description=dbo.description,
            is_active=dbo.is_active,
            created_at=dbo.created_at,
            updated_at=dbo.updated_at,
        )
    
    @staticmethod
    def to_dbo(entity: {names["entity_class"]}) -> {names["dbo_class"]}:
        """Convert domain entity to Django model."""
        dbo = {names["dbo_class"]}(
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )
        
        if entity.id:
            dbo.id = entity.id
        if entity.created_at:
            dbo.created_at = entity.created_at
        if entity.updated_at:
            dbo.updated_at = entity.updated_at
        
        return dbo
    
    @staticmethod
    def update_dbo_from_entity(dbo: {names["dbo_class"]}, entity: {names["entity_class"]}) -> {names["dbo_class"]}:
        """Update existing DBO with entity data."""
        dbo.name = entity.name
        dbo.description = entity.description
        dbo.is_active = entity.is_active
        return dbo
'''
        with open(project_dir / "driven" / "db" / "mapper.py", "w") as f:
            f.write(mapper_content)

        # Create repository adapter
        adapter_content = f'''"""
Database repository adapter implementing the driven port.
"""

from typing import List, Optional
from django.core.exceptions import ObjectDoesNotExist

from application.ports.driven.{names["file_name"]}_repository_port import {names["repository_port_class"]}
from domain.entities.{names["file_name"]} import {names["entity_class"]}
from .models import {names["dbo_class"]}
from .mapper import {names["mapper_class"]}


class {names["repository_class"]}({names["repository_port_class"]}):
    """Django ORM implementation of {names["repository_port_class"]}."""
    
    def __init__(self):
        """Initialize the repository adapter."""
        self.mapper = {names["mapper_class"]}()
    
    async def save(self, entity: {names["entity_class"]}) -> {names["entity_class"]}:
        """Save an entity to the database."""
        dbo = self.mapper.to_dbo(entity)
        await dbo.asave()
        return self.mapper.to_entity(dbo)
    
    async def find_by_id(self, entity_id: int) -> Optional[{names["entity_class"]}]:
        """Find an entity by ID."""
        try:
            dbo = await {names["dbo_class"]}.objects.aget(id=entity_id)
            return self.mapper.to_entity(dbo)
        except ObjectDoesNotExist:
            return None
    
    async def find_all(self) -> List[{names["entity_class"]}]:
        """Find all entities."""
        dbos = {names["dbo_class"]}.objects.all()
        entities = []
        async for dbo in dbos:
            entities.append(self.mapper.to_entity(dbo))
        return entities
    
    async def update(self, entity_id: int, entity: {names["entity_class"]}) -> Optional[{names["entity_class"]}]:
        """Update an existing entity."""
        try:
            dbo = await {names["dbo_class"]}.objects.aget(id=entity_id)
            updated_dbo = self.mapper.update_dbo_from_entity(dbo, entity)
            await updated_dbo.asave()
            return self.mapper.to_entity(updated_dbo)
        except ObjectDoesNotExist:
            return None
    
    async def delete_by_id(self, entity_id: int) -> bool:
        """Delete an entity by ID."""
        try:
            dbo = await {names["dbo_class"]}.objects.aget(id=entity_id)
            await dbo.adelete()
            return True
        except ObjectDoesNotExist:
            return False
    
    async def exists(self, entity_id: int) -> bool:
        """Check if an entity exists."""
        return await {names["dbo_class"]}.objects.filter(id=entity_id).aexists()
'''
        with open(project_dir / "driven" / "db" / "adapter.py", "w") as f:
            f.write(adapter_content)

        # Create Django admin
        admin_content = f'''"""
Django admin configuration for {names["variable_name"]} models.
"""

from django.contrib import admin
from .models import {names["dbo_class"]}


@admin.register({names["dbo_class"]})
class {names["admin_class"]}(admin.ModelAdmin):
    """Admin interface for {names["display_name"]} entities."""
    
    list_display = ["name", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        (None, {{
            "fields": ("name", "description", "is_active")
        }}),
        ("Timestamps", {{
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }}),
    )
'''
        with open(project_dir / "driven" / "db" / "admin.py", "w") as f:
            f.write(admin_content)

        # Create apps.py for Django app
        apps_content = '''"""
Django app configuration for the database layer.
"""

from django.apps import AppConfig


class DbConfig(AppConfig):
    """Configuration for the database app."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "driven.db"
    verbose_name = "Database Layer"
'''
        with open(project_dir / "driven" / "db" / "apps.py", "w") as f:
            f.write(apps_content)

        # Create migrations directory
        (project_dir / "driven" / "db" / "migrations").mkdir()
        with open(project_dir / "driven" / "db" / "migrations" / "__init__.py", "w") as f:
            f.write('"""Database migrations."""\n')

    async def _create_driving_layer(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create the driving layer with API adapters."""
        
        names = self._get_class_names(module_name)
        
        # Create __init__.py files
        with open(project_dir / "driving" / "__init__.py", "w") as f:
            f.write('"""Driving layer - User interface adapters."""\n')
        
        with open(project_dir / "driving" / "api" / "__init__.py", "w") as f:
            f.write('"""API adapters."""\n')
        
        with open(project_dir / "driving" / "api" / "v1" / "__init__.py", "w") as f:
            f.write('"""API version 1."""\n')

        # Create DTOs (Data Transfer Objects)
        models_content = f'''"""
API models (DTOs) for external communication.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class {names["display_name"]}DTO(BaseModel):
    """Full DTO for {names["display_name"]} entity."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class {names["display_name"]}CreateDTO(BaseModel):
    """DTO for creating {names["display_name"]} entities."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    is_active: bool = True


class {names["display_name"]}UpdateDTO(BaseModel):
    """DTO for updating {names["display_name"]} entities."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class {names["display_name"]}ListDTO(BaseModel):
    """Reduced DTO for listing {names["display_name"]} entities."""
    
    id: int
    name: str
    is_active: bool
    created_at: datetime
'''
        with open(project_dir / "driving" / "api" / "v1" / "models.py", "w") as f:
            f.write(models_content)

        # Create API mapper
        mapper_content = f'''"""
Mapper for converting between domain entities and API DTOs.
"""

from typing import List

from domain.entities.{names["file_name"]} import {names["entity_class"]}
from .models import {names["display_name"]}DTO, {names["display_name"]}CreateDTO, {names["display_name"]}UpdateDTO, {names["display_name"]}ListDTO


class {names["display_name"]}APIMapper:
    """Maps between {names["entity_class"]} and API DTOs."""
    
    @staticmethod
    def entity_to_dto(entity: {names["entity_class"]}) -> {names["display_name"]}DTO:
        """Convert domain entity to full DTO."""
        return {names["display_name"]}DTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def entity_to_list_dto(entity: {names["entity_class"]}) -> {names["display_name"]}ListDTO:
        """Convert domain entity to list DTO."""
        return {names["display_name"]}ListDTO(
            id=entity.id,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
    
    @staticmethod
    def create_dto_to_entity(dto: {names["display_name"]}CreateDTO) -> {names["entity_class"]}:
        """Convert create DTO to domain entity."""
        return {names["entity_class"]}(
            name=dto.name,
            description=dto.description,
            is_active=dto.is_active,
        )
    
    @staticmethod
    def update_dto_to_entity(dto: {names["display_name"]}UpdateDTO, existing: {names["entity_class"]}) -> {names["entity_class"]}:
        """Update existing entity with update DTO data."""
        updated_data = existing.model_dump()
        
        if dto.name is not None:
            updated_data["name"] = dto.name
        if dto.description is not None:
            updated_data["description"] = dto.description
        if dto.is_active is not None:
            updated_data["is_active"] = dto.is_active
        
        return {names["entity_class"]}(**updated_data)
    
    @staticmethod
    def entities_to_list_dtos(entities: List[{names["entity_class"]}]) -> List[{names["display_name"]}ListDTO]:
        """Convert list of entities to list DTOs."""
        return [{names["display_name"]}APIMapper.entity_to_list_dto(entity) for entity in entities]
'''
        with open(project_dir / "driving" / "api" / "v1" / "mapper.py", "w") as f:
            f.write(mapper_content)

        # Create API adapter (views)
        adapter_content = f'''"""
Django REST Framework API adapter implementing REST endpoints.
"""

from typing import Dict, Any
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from application.services.{names["file_name"]}_service import {names["service_class"]}
from driven.db.adapter import {names["repository_class"]}
from .models import {names["display_name"]}CreateDTO, {names["display_name"]}UpdateDTO
from .mapper import {names["display_name"]}APIMapper


# Service factory - in production, use proper DI container
def get_{names["variable_name"]}_service() -> {names["service_class"]}:
    """Factory method to create {names["service_class"]} with dependencies."""
    repository = {names["repository_class"]}()
    return {names["service_class"]}(repository)


@api_view(["GET", "POST"])
async def {names["variable_name"]}_list_create(request):
    """List all {names["variable_name"]}s or create a new one."""
    service = get_{names["variable_name"]}_service()
    mapper = {names["display_name"]}APIMapper()
    
    if request.method == "GET":
        # List all {names["variable_name"]}s
        entities = await service.list_all()
        list_dtos = mapper.entities_to_list_dtos(entities)
        return Response([dto.model_dump() for dto in list_dtos])
    
    elif request.method == "POST":
        # Create new {names["variable_name"]}
        try:
            create_dto = {names["display_name"]}CreateDTO(**request.data)
            entity = mapper.create_dto_to_entity(create_dto)
            created_entity = await service.create(entity)
            result_dto = mapper.entity_to_dto(created_entity)
            return Response(result_dto.model_dump(), status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({{"error": str(e)}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({{"error": "Internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "PUT", "DELETE"])
async def {names["variable_name"]}_detail(request, pk: int):
    """Retrieve, update, or delete a {names["variable_name"]}."""
    service = get_{names["variable_name"]}_service()
    mapper = {names["display_name"]}APIMapper()
    
    if request.method == "GET":
        # Retrieve {names["variable_name"]}
        entity = await service.retrieve(pk)
        if not entity:
            raise Http404("{names["display_name"]} not found")
        
        result_dto = mapper.entity_to_dto(entity)
        return Response(result_dto.model_dump())
    
    elif request.method == "PUT":
        # Update {names["variable_name"]}
        try:
            existing_entity = await service.retrieve(pk)
            if not existing_entity:
                raise Http404("{names["display_name"]} not found")
            
            update_dto = {names["display_name"]}UpdateDTO(**request.data)
            updated_entity = mapper.update_dto_to_entity(update_dto, existing_entity)
            result_entity = await service.update(pk, updated_entity)
            
            if not result_entity:
                raise Http404("{names["display_name"]} not found")
            
            result_dto = mapper.entity_to_dto(result_entity)
            return Response(result_dto.model_dump())
        except ValueError as e:
            return Response({{"error": str(e)}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({{"error": "Internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == "DELETE":
        # Delete {names["variable_name"]}
        try:
            success = await service.delete(pk)
            if not success:
                raise Http404("{names["display_name"]} not found")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({{"error": "Internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''
        with open(project_dir / "driving" / "api" / "v1" / "adapter.py", "w") as f:
            f.write(adapter_content)

        # Create URL configuration
        urls_content = f'''"""
URL configuration for {names["variable_name"]} API endpoints.
"""

from django.urls import path
from . import adapter

urlpatterns = [
    path("{names["url_name"]}s/", adapter.{names["variable_name"]}_list_create, name="{names["url_name"]}-list-create"),
    path("{names["url_name"]}s/<int:pk>/", adapter.{names["variable_name"]}_detail, name="{names["url_name"]}-detail"),
]
'''
        with open(project_dir / "driving" / "api" / "v1" / "urls.py", "w") as f:
            f.write(urls_content)

        # Create main API URLs
        main_urls_content = '''"""
Main API URL configuration.
"""

from django.urls import path, include

urlpatterns = [
    path("v1/", include("driving.api.v1.urls")),
]
'''
        with open(project_dir / "driving" / "api" / "urls.py", "w") as f:
            f.write(main_urls_content)

    async def _create_config_layer(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create Django configuration layer."""
        
        # Create __init__.py
        with open(project_dir / "config" / "__init__.py", "w") as f:
            f.write('"""Django configuration."""\n')

        # Create Django settings
        settings_content = f'''"""
Django settings for {project_name} project following hexagonal architecture.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-change-this-in-production"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
]

LOCAL_APPS = [
    "driven.db",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {{
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        }},
    }},
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {{
    "default": {{
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}
}}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {{
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    }},
    {{
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    }},
    {{
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    }},
    {{
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    }},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework configuration
REST_FRAMEWORK = {{
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Logging
LOGGING = {{
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {{
        "console": {{
            "class": "logging.StreamHandler",
        }},
    }},
    "root": {{
        "handlers": ["console"],
        "level": "INFO",
    }},
    "loggers": {{
        "django": {{
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }},
    }},
}}
'''
        with open(project_dir / "config" / "settings.py", "w") as f:
            f.write(settings_content)

        # Create main URL configuration
        urls_content = '''"""
Main URL configuration for the project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("driving.api.urls")),
]
'''
        with open(project_dir / "config" / "urls.py", "w") as f:
            f.write(urls_content)

        # Create WSGI application
        wsgi_content = f'''"""
WSGI config for {project_name} project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
'''
        with open(project_dir / "config" / "wsgi.py", "w") as f:
            f.write(wsgi_content)

        # Create ASGI application
        asgi_content = f'''"""
ASGI config for {project_name} project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
'''
        with open(project_dir / "config" / "asgi.py", "w") as f:
            f.write(asgi_content)

    async def _create_test_files(self, project_dir: Path, project_name: str, module_name: Optional[str] = None):
        """Create comprehensive test files following hexagonal architecture."""
        
        # Create test __init__.py files
        with open(project_dir / "tests" / "__init__.py", "w") as f:
            f.write('"""Test suite for hexagonal architecture project."""\n')
        
        with open(project_dir / "tests" / "domain" / "__init__.py", "w") as f:
            f.write('"""Domain layer tests."""\n')
        
        with open(project_dir / "tests" / "application" / "__init__.py", "w") as f:
            f.write('"""Application layer tests."""\n')
        
        with open(project_dir / "tests" / "driven" / "__init__.py", "w") as f:
            f.write('"""Driven layer tests."""\n')
        
        with open(project_dir / "tests" / "driving" / "__init__.py", "w") as f:
            f.write('"""Driving layer tests."""\n')

        # Create pytest configuration
        conftest_content = '''"""
Pytest configuration for hexagonal architecture tests.
"""

import pytest
from django.conf import settings
from django.test import TransactionTestCase
import django


def pytest_configure():
    """Configure Django settings for pytest."""
    if not settings.configured:
        settings.configure(
            **{
                'DATABASES': {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                'INSTALLED_APPS': [
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'driven.db',
                ],
                'SECRET_KEY': 'test-secret-key',
                'USE_TZ': True,
            }
        )
        django.setup()


@pytest.fixture
def example_entity():
    """Fixture providing a test example entity."""
    from domain.entities.example import ExampleEntity
    return ExampleEntity(
        name="Test Example",
        description="A test example entity",
        is_active=True
    )


@pytest.fixture
def example_repository():
    """Fixture providing a test repository."""
    from driven.db.adapter import ExampleRepositoryAdapter
    return ExampleRepositoryAdapter()


@pytest.fixture
def example_service(example_repository):
    """Fixture providing a test service."""
    from application.services.example_service import ExampleService
    return ExampleService(example_repository)
'''
        with open(project_dir / "tests" / "conftest.py", "w") as f:
            f.write(conftest_content)

        # Create domain tests
        domain_test_content = '''"""
Tests for domain entities.
"""

import pytest
from datetime import datetime
from domain.entities.example import ExampleEntity


class TestExampleEntity:
    """Test cases for ExampleEntity."""
    
    def test_entity_creation(self):
        """Test creating a valid entity."""
        entity = ExampleEntity(
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        assert entity.name == "Test Entity"
        assert entity.description == "Test description"
        assert entity.is_active is True
        assert entity.id is None
        assert entity.created_at is None
    
    def test_entity_with_id_and_timestamps(self):
        """Test entity with ID and timestamps."""
        now = datetime.now()
        entity = ExampleEntity(
            id=1,
            name="Test Entity",
            description="Test description",
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        assert entity.id == 1
        assert entity.created_at == now
        assert entity.updated_at == now
    
    def test_entity_validation_empty_name(self):
        """Test validation fails for empty name."""
        with pytest.raises(ValueError):
            ExampleEntity(name="")
    
    def test_entity_to_dict(self):
        """Test converting entity to dictionary."""
        entity = ExampleEntity(
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        entity_dict = entity.to_dict()
        
        assert entity_dict["name"] == "Test Entity"
        assert entity_dict["description"] == "Test description"
        assert entity_dict["is_active"] is True
    
    def test_entity_defaults(self):
        """Test entity default values."""
        entity = ExampleEntity(name="Test")
        
        assert entity.description == ""
        assert entity.is_active is True
'''
        with open(project_dir / "tests" / "domain" / "test_entities.py", "w") as f:
            f.write(domain_test_content)

        # Create application service tests
        service_test_content = '''"""
Tests for application services.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from application.services.example_service import ExampleService
from domain.entities.example import ExampleEntity


class TestExampleService:
    """Test cases for ExampleService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing."""
        repository = Mock()
        repository.save = AsyncMock()
        repository.find_by_id = AsyncMock()
        repository.find_all = AsyncMock()
        repository.update = AsyncMock()
        repository.delete_by_id = AsyncMock()
        return repository
    
    @pytest.fixture
    def service(self, mock_repository):
        """Service instance with mocked repository."""
        return ExampleService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_valid_entity(self, service, mock_repository):
        """Test creating a valid entity."""
        entity = ExampleEntity(name="Test Entity", description="Test")
        created_entity = ExampleEntity(id=1, name="Test Entity", description="Test")
        
        mock_repository.save.return_value = created_entity
        
        result = await service.create(entity)
        
        assert result.id == 1
        assert result.name == "Test Entity"
        mock_repository.save.assert_called_once_with(entity)
    
    @pytest.mark.asyncio
    async def test_create_empty_name_fails(self, service):
        """Test creating entity with empty name fails."""
        entity = ExampleEntity(name="", description="Test")
        
        with pytest.raises(ValueError, match="Entity name cannot be empty"):
            await service.create(entity)
    
    @pytest.mark.asyncio
    async def test_retrieve_valid_id(self, service, mock_repository):
        """Test retrieving entity with valid ID."""
        entity = ExampleEntity(id=1, name="Test Entity")
        mock_repository.find_by_id.return_value = entity
        
        result = await service.retrieve(1)
        
        assert result.id == 1
        assert result.name == "Test Entity"
        mock_repository.find_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_retrieve_invalid_id_fails(self, service):
        """Test retrieving entity with invalid ID fails."""
        with pytest.raises(ValueError, match="Entity ID must be positive"):
            await service.retrieve(0)
    
    @pytest.mark.asyncio
    async def test_list_all_only_active(self, service, mock_repository):
        """Test listing returns only active entities."""
        entities = [
            ExampleEntity(id=1, name="Active", is_active=True),
            ExampleEntity(id=2, name="Inactive", is_active=False),
            ExampleEntity(id=3, name="Another Active", is_active=True),
        ]
        mock_repository.find_all.return_value = entities
        
        result = await service.list_all()
        
        assert len(result) == 2
        assert all(entity.is_active for entity in result)
    
    @pytest.mark.asyncio
    async def test_update_valid_entity(self, service, mock_repository):
        """Test updating a valid entity."""
        existing = ExampleEntity(id=1, name="Old Name")
        updated = ExampleEntity(id=1, name="New Name")
        
        mock_repository.find_by_id.return_value = existing
        mock_repository.update.return_value = updated
        
        update_data = ExampleEntity(name="New Name")
        result = await service.update(1, update_data)
        
        assert result.name == "New Name"
        mock_repository.update.assert_called_once_with(1, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_soft_delete(self, service, mock_repository):
        """Test delete performs soft delete by marking inactive."""
        existing = ExampleEntity(id=1, name="Test", is_active=True)
        mock_repository.find_by_id.return_value = existing
        mock_repository.update.return_value = existing
        
        result = await service.delete(1)
        
        assert result is True
        # Verify the entity was marked as inactive
        call_args = mock_repository.update.call_args
        assert call_args[0][0] == 1  # entity_id
        assert call_args[0][1].is_active is False  # updated entity
'''
        with open(project_dir / "tests" / "application" / "test_services.py", "w") as f:
            f.write(service_test_content)

        # Create driven layer tests
        driven_test_content = '''"""
Tests for driven layer adapters.
"""

import pytest
from django.test import TransactionTestCase
from domain.entities.example import ExampleEntity
from driven.db.models import ExampleDBO
from driven.db.mapper import ExampleMapper
from driven.db.adapter import ExampleRepositoryAdapter


class TestExampleMapper(TransactionTestCase):
    """Test cases for ExampleMapper."""
    
    def test_to_entity(self):
        """Test converting DBO to entity."""
        dbo = ExampleDBO(
            id=1,
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        entity = ExampleMapper.to_entity(dbo)
        
        assert entity.id == 1
        assert entity.name == "Test Entity"
        assert entity.description == "Test description"
        assert entity.is_active is True
    
    def test_to_dbo(self):
        """Test converting entity to DBO."""
        entity = ExampleEntity(
            id=1,
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        dbo = ExampleMapper.to_dbo(entity)
        
        assert dbo.name == "Test Entity"
        assert dbo.description == "Test description"
        assert dbo.is_active is True
    
    def test_update_dbo_from_entity(self):
        """Test updating DBO with entity data."""
        dbo = ExampleDBO(name="Old Name", description="Old description")
        entity = ExampleEntity(name="New Name", description="New description")
        
        updated_dbo = ExampleMapper.update_dbo_from_entity(dbo, entity)
        
        assert updated_dbo.name == "New Name"
        assert updated_dbo.description == "New description"


class TestExampleRepositoryAdapter(TransactionTestCase):
    """Test cases for ExampleRepositoryAdapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = ExampleRepositoryAdapter()
    
    @pytest.mark.asyncio
    async def test_save_entity(self):
        """Test saving an entity."""
        entity = ExampleEntity(
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        saved_entity = await self.repository.save(entity)
        
        assert saved_entity.id is not None
        assert saved_entity.name == "Test Entity"
        assert saved_entity.description == "Test description"
    
    @pytest.mark.asyncio
    async def test_find_by_id_existing(self):
        """Test finding existing entity by ID."""
        # Create entity first
        dbo = await ExampleDBO.objects.acreate(
            name="Test Entity",
            description="Test description"
        )
        
        entity = await self.repository.find_by_id(dbo.id)
        
        assert entity is not None
        assert entity.id == dbo.id
        assert entity.name == "Test Entity"
    
    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent(self):
        """Test finding non-existent entity returns None."""
        entity = await self.repository.find_by_id(99999)
        assert entity is None
    
    @pytest.mark.asyncio
    async def test_find_all(self):
        """Test finding all entities."""
        # Create test entities
        await ExampleDBO.objects.acreate(name="Entity 1")
        await ExampleDBO.objects.acreate(name="Entity 2")
        
        entities = await self.repository.find_all()
        
        assert len(entities) >= 2
        entity_names = [entity.name for entity in entities]
        assert "Entity 1" in entity_names
        assert "Entity 2" in entity_names
    
    @pytest.mark.asyncio
    async def test_exists(self):
        """Test checking if entity exists."""
        dbo = await ExampleDBO.objects.acreate(name="Test Entity")
        
        exists = await self.repository.exists(dbo.id)
        not_exists = await self.repository.exists(99999)
        
        assert exists is True
        assert not_exists is False
'''
        with open(project_dir / "tests" / "driven" / "test_adapters.py", "w") as f:
            f.write(driven_test_content)

        # Create driving layer tests
        driving_test_content = '''"""
Tests for driving layer adapters.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from rest_framework.test import APITestCase
from django.urls import reverse
from domain.entities.example import ExampleEntity
from driving.api.v1.mapper import ExampleAPIMapper
from driving.api.v1.models import ExampleDTO, ExampleCreateDTO, ExampleUpdateDTO


class TestExampleAPIMapper:
    """Test cases for ExampleAPIMapper."""
    
    def test_entity_to_dto(self):
        """Test converting entity to DTO."""
        entity = ExampleEntity(
            id=1,
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        dto = ExampleAPIMapper.entity_to_dto(entity)
        
        assert dto.id == 1
        assert dto.name == "Test Entity"
        assert dto.description == "Test description"
        assert dto.is_active is True
    
    def test_create_dto_to_entity(self):
        """Test converting create DTO to entity."""
        dto = ExampleCreateDTO(
            name="Test Entity",
            description="Test description",
            is_active=True
        )
        
        entity = ExampleAPIMapper.create_dto_to_entity(dto)
        
        assert entity.name == "Test Entity"
        assert entity.description == "Test description"
        assert entity.is_active is True
        assert entity.id is None
    
    def test_update_dto_to_entity(self):
        """Test updating entity with update DTO."""
        existing = ExampleEntity(
            id=1,
            name="Old Name",
            description="Old description",
            is_active=True
        )
        
        update_dto = ExampleUpdateDTO(
            name="New Name",
            description="New description"
        )
        
        updated_entity = ExampleAPIMapper.update_dto_to_entity(update_dto, existing)
        
        assert updated_entity.name == "New Name"
        assert updated_entity.description == "New description"
        assert updated_entity.is_active is True  # Unchanged
        assert updated_entity.id == 1  # Unchanged


class TestExampleAPIViews(APITestCase):
    """Test cases for Example API views."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.list_url = "/api/v1/examples/"
        
    @patch('driving.api.v1.adapter.get_example_service')
    async def test_list_examples(self, mock_get_service):
        """Test listing examples."""
        # Mock service
        mock_service = Mock()
        mock_service.list_all = AsyncMock(return_value=[
            ExampleEntity(id=1, name="Entity 1", is_active=True),
            ExampleEntity(id=2, name="Entity 2", is_active=True),
        ])
        mock_get_service.return_value = mock_service
        
        response = await self.async_client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Entity 1")
    
    @patch('driving.api.v1.adapter.get_example_service')
    async def test_create_example(self, mock_get_service):
        """Test creating an example."""
        # Mock service
        mock_service = Mock()
        mock_service.create = AsyncMock(return_value=ExampleEntity(
            id=1,
            name="New Entity",
            description="New description",
            is_active=True
        ))
        mock_get_service.return_value = mock_service
        
        data = {
            "name": "New Entity",
            "description": "New description",
            "is_active": True
        }
        
        response = await self.async_client.post(
            self.list_url, 
            data=data,
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["name"], "New Entity")
        self.assertEqual(response_data["id"], 1)
    
    @patch('driving.api.v1.adapter.get_example_service')
    async def test_get_example_detail(self, mock_get_service):
        """Test retrieving example detail."""
        # Mock service
        mock_service = Mock()
        mock_service.retrieve = AsyncMock(return_value=ExampleEntity(
            id=1,
            name="Test Entity",
            description="Test description",
            is_active=True
        ))
        mock_get_service.return_value = mock_service
        
        response = await self.async_client.get(f"{self.list_url}1/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Test Entity")
        self.assertEqual(data["id"], 1)
    
    @patch('driving.api.v1.adapter.get_example_service')
    async def test_get_nonexistent_example(self, mock_get_service):
        """Test retrieving non-existent example returns 404."""
        # Mock service
        mock_service = Mock()
        mock_service.retrieve = AsyncMock(return_value=None)
        mock_get_service.return_value = mock_service
        
        response = await self.async_client.get(f"{self.list_url}999/")
        
        self.assertEqual(response.status_code, 404)
'''
        with open(project_dir / "tests" / "driving" / "test_api.py", "w") as f:
            f.write(driving_test_content)

    async def _add_cursor_rules(self, project_dir: Path, cursor_rules: str):
        """Add cursor rules to the project."""
        cursor_dir = project_dir / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        cursor_rules_path = cursor_dir / "rules"
        
        with open(cursor_rules_path, "w") as f:
            f.write(cursor_rules) 