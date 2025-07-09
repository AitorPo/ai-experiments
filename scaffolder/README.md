# File Operations MCP Server

A comprehensive MCP (Model Context Protocol) server built with FastAPI for managing file operations and project scaffolding. This server provides tools to create, read, update, delete, move, and manage files and directories on your system.

## Features

### File Operations
- **Create Folders**: Create new directories with parent directory support
- **Create Files**: Create new files with optional initial content
- **Read Files**: Read file contents
- **Write Files**: Write or append content to files
- **Move/Rename**: Move files and folders or rename them
- **Copy**: Copy files and folders with overwrite options
- **Delete**: Delete files and folders with recursive options
- **List Contents**: List directory contents with hidden file support

### Project Scaffolding
- **Template-based Project Creation**: Support for multiple project types
  - Python projects with proper package structure
  - FastAPI applications with CRUD examples
  - React applications with modern setup
  - More templates coming soon (Next.js, Django, Flask, Node.js)
- **Cursor Rules Integration**: Automatically add `.cursor/rules` files to projects
- **Development-ready**: Includes testing, linting, and formatting configurations

## Installation

### Prerequisites
- Python 3.13 or higher
- uv (for package management)

### Setup

1. **Clone or create the project**:
   ```bash
   # If you have the code
   cd scaffolder
   
   # Or create from scratch following the structure
   ```

2. **Create virtual environment with uv**:
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -e .
   ```

4. **For development**:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Usage

The server can run in two modes:

### 1. MCP Server Mode (Default)
Run as an MCP server with stdio transport:
```bash
python main.py --mode mcp
```

### 2. FastAPI REST API Mode
Run as a REST API server:
```bash
python main.py --mode api --host 0.0.0.0 --port 8000
```

Then visit http://localhost:8000/docs for the interactive API documentation.

## MCP Tools

The server provides the following MCP tools:

### File Operations
- `create_folder`: Create a new folder
- `create_file`: Create a new file with content
- `read_file`: Read file contents
- `write_file`: Write content to a file
- `rename`: Rename a file or folder
- `move`: Move a file or folder
- `copy`: Copy a file or folder
- `delete`: Delete a file or folder
- `list_contents`: List directory contents

### Project Scaffolding
- `scaffold_project`: Create a new project from templates

## Project Templates

### Python Template
Creates a standard Python project with:
- `src/` package structure
- `tests/` directory with pytest setup
- `pyproject.toml` with modern Python packaging
- Development tools (black, ruff, pytest)
- Proper `.gitignore`

### FastAPI Template
Creates a FastAPI application with:
- CRUD API example with items
- Pydantic models
- API documentation setup
- Testing with TestClient
- Development and production configurations

### React Template
Creates a React application with:
- Modern React 18 setup
- Component structure
- CSS styling
- npm scripts for development

### Hexagonal Template
Creates a Django project following hexagonal architecture with:
- Clean separation of domain, application, driven, and driving layers
- Pydantic domain entities with business logic
- Port interfaces for dependency inversion
- Repository and service patterns
- Comprehensive testing suite
- REST API with proper DTO mapping
- Django admin integration
- Async-ready implementation

## API Examples

### Create a Python Project
```json
POST /tools/scaffold_project
{
  "project_path": "/path/to/projects",
  "project_name": "my_awesome_project",
  "template_type": "python",
  "cursor_rules": "Follow PEP 8 standards and use type hints"
}
```

### Create a Hexagonal Architecture Project
```json
POST /tools/scaffold_project
{
  "project_path": "/path/to/projects",
  "project_name": "my_hexagonal_api",
  "template_type": "hexagonal",
  "cursor_rules": "Follow hexagonal architecture patterns with clean separation of concerns"
}
```

### Create a File
```json
POST /tools/create_file
{
  "path": "/path/to/directory",
  "name": "example.py",
  "content": "print('Hello, World!')",
  "overwrite": false
}
```

### Read a File
```json
POST /tools/read_file
{
  "path": "/path/to/file.txt"
}
```

## Development

### Project Structure
```
scaffolder/
├── src/
│   └── scaffolder/
│       ├── __init__.py
│       ├── mcp_server.py      # Core MCP server implementation
│       ├── scaffolding.py     # Project scaffolding logic
│       └── api.py             # FastAPI REST wrapper
├── tests/                     # Test files
├── main.py                    # Entry point
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
ruff check .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run formatting and linting
6. Submit a pull request

## License

This project is open source and available under the MIT License.

## Cursor Rules Integration

When scaffolding projects, you can provide custom cursor rules that will be automatically added to a `.cursor/rules` file in the project root. This helps maintain consistent coding standards and practices across your projects.

Example cursor rules:
- "Use type hints for all function parameters and return values"
- "Prefer composition over inheritance"
- "Write comprehensive docstrings for all public methods"
- "Use descriptive variable names and avoid abbreviations"
